"""Integration tests for end-to-end workflow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from orchestration.models import CompletionReason
from orchestration.workflow import run_slogan_generation


class TestEndToEndWorkflow:
    """Integration tests for the complete slogan generation workflow."""

    @pytest.mark.asyncio
    async def test_successful_approval_first_turn(self):
        """Test workflow completes successfully on first turn approval."""
        # Mock agent responses
        mock_writer_response = MagicMock()
        mock_writer_response.text = "Eco-Smart: Hydrate Responsibly"

        mock_reviewer_response = MagicMock()
        mock_reviewer_response.text = "SHIP IT! This slogan is perfect."

        # Patch agent creation and run methods
        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            # Run workflow
            session = await run_slogan_generation("eco-friendly water bottle")

            # Assertions
            assert session.completed is True
            assert session.completion_reason == CompletionReason.APPROVED
            assert session.final_slogan == "Eco-Smart: Hydrate Responsibly"
            assert len(session.turns) == 1
            assert session.turns[0].approved is True
            assert session.turns[0].slogan == "Eco-Smart: Hydrate Responsibly"
            assert session.turns[0].feedback is not None
            assert "SHIP IT" in session.turns[0].feedback

    @pytest.mark.asyncio
    async def test_multiple_iterations_before_approval(self):
        """Test workflow with multiple iterations before approval."""
        # Mock responses for 3 iterations
        writer_responses = [
            MagicMock(text="Slogan v1"),
            MagicMock(text="Slogan v2"),
            MagicMock(text="Slogan v3 - Perfect!"),
        ]

        reviewer_responses = [
            MagicMock(text="Too generic, try again"),
            MagicMock(text="Better but still needs work"),
            MagicMock(text="SHIP IT! Now it's great."),
        ]

        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(side_effect=writer_responses)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(side_effect=reviewer_responses)
            mock_create_reviewer.return_value = mock_reviewer

            # Run workflow
            session = await run_slogan_generation("test product")

            # Assertions
            assert session.completed is True
            assert session.completion_reason == CompletionReason.APPROVED
            assert len(session.turns) == 3
            assert session.turns[0].approved is False
            assert session.turns[1].approved is False
            assert session.turns[2].approved is True
            assert session.final_slogan == "Slogan v3 - Perfect!"

    @pytest.mark.asyncio
    async def test_max_turns_reached(self):
        """Test workflow stops at max turns without approval."""
        # Mock responses that never approve
        mock_writer_response = MagicMock(text="Generic Slogan")
        mock_reviewer_response = MagicMock(text="Not good enough")

        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            # Run workflow with max_turns=3
            session = await run_slogan_generation("test", max_turns=3)

            # Assertions
            assert session.completed is True
            assert session.completion_reason == CompletionReason.MAX_TURNS
            assert len(session.turns) == 3
            assert all(not turn.approved for turn in session.turns)
            assert session.final_slogan == "Generic Slogan"  # Last attempt

    @pytest.mark.asyncio
    async def test_custom_model_name(self):
        """Test workflow uses custom model name."""
        mock_writer_response = MagicMock(text="Test Slogan")
        mock_reviewer_response = MagicMock(text="Ship it!")

        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer, \
             patch("orchestration.workflow.get_ollama_config") as mock_get_config:

            # Mock config
            mock_config = MagicMock()
            mock_config.model_name = "custom-model"
            mock_config.max_turns = 5
            mock_config.base_url = "http://localhost:11434/v1"
            mock_get_config.return_value = mock_config

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            # Run workflow with custom model
            session = await run_slogan_generation("test", model_name="custom-model")

            # Verify model name was set
            assert mock_config.model_name == "custom-model"
            assert session.model_name == "custom-model"

    @pytest.mark.asyncio
    async def test_empty_input_validation(self):
        """Test workflow rejects empty input."""
        with pytest.raises(ValueError, match="User input cannot be empty"):
            await run_slogan_generation("")

        with pytest.raises(ValueError, match="User input cannot be empty"):
            await run_slogan_generation("   ")

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow handles errors gracefully."""
        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer:
            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(side_effect=Exception("Connection failed"))
            mock_create_writer.return_value = mock_writer

            # Should raise RuntimeError wrapping the original exception
            with pytest.raises(RuntimeError, match="Workflow failed"):
                await run_slogan_generation("test product")

    @pytest.mark.asyncio
    async def test_approval_detection_case_insensitive(self):
        """Test that approval detection is case-insensitive."""
        test_cases = [
            "SHIP IT!",
            "ship it!",
            "Ship It!",
            "This is great, SHIP IT!",
            "ship   it! Perfect!",
        ]

        for approval_phrase in test_cases:
            mock_writer_response = MagicMock(text="Test Slogan")
            mock_reviewer_response = MagicMock(text=approval_phrase)

            with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
                 patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

                mock_writer = MagicMock()
                mock_writer.run = AsyncMock(return_value=mock_writer_response)
                mock_create_writer.return_value = mock_writer

                mock_reviewer = MagicMock()
                mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
                mock_create_reviewer.return_value = mock_reviewer

                session = await run_slogan_generation("test")

                assert session.completion_reason == CompletionReason.APPROVED, \
                    f"Failed to detect approval in: {approval_phrase}"

    @pytest.mark.asyncio
    async def test_turn_feedback_propagation(self):
        """Test that reviewer feedback is passed to writer in next iteration."""
        writer_calls = []
        reviewer_calls = []

        def writer_run_side_effect(prompt):
            writer_calls.append(prompt)
            if len(writer_calls) == 1:
                return MagicMock(text="First Slogan")
            else:
                return MagicMock(text="Improved Slogan")

        def reviewer_run_side_effect(prompt):
            reviewer_calls.append(prompt)
            if len(reviewer_calls) == 1:
                return MagicMock(text="Make it more catchy")
            else:
                return MagicMock(text="SHIP IT!")

        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(side_effect=writer_run_side_effect)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(side_effect=reviewer_run_side_effect)
            mock_create_reviewer.return_value = mock_reviewer

            session = await run_slogan_generation("test product")

            # Verify first writer call doesn't have feedback
            assert "Create a slogan for: test product" in writer_calls[0]
            assert "Feedback:" not in writer_calls[0]

            # Verify second writer call includes previous feedback
            assert "Previous slogan: First Slogan" in writer_calls[1]
            assert "Feedback: Make it more catchy" in writer_calls[1]
            assert "Create an improved slogan for: test product" in writer_calls[1]

            # Verify session captured both turns
            assert len(session.turns) == 2
            assert session.turns[0].feedback == "Make it more catchy"
            assert session.turns[1].feedback == "SHIP IT!"

    @pytest.mark.asyncio
    async def test_max_turns_custom_values(self):
        """Test workflow respects custom max_turns values."""
        mock_writer_response = MagicMock(text="Test Slogan")
        mock_reviewer_response = MagicMock(text="Try again")

        # Test with max_turns=1
        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            session = await run_slogan_generation("test", max_turns=1)
            assert len(session.turns) == 1
            assert session.completion_reason == CompletionReason.MAX_TURNS

        # Test with max_turns=10
        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            session = await run_slogan_generation("test", max_turns=10)
            assert len(session.turns) == 10
            assert session.completion_reason == CompletionReason.MAX_TURNS

    @pytest.mark.asyncio
    async def test_session_timestamps(self):
        """Test that session captures timestamps correctly."""
        mock_writer_response = MagicMock(text="Test Slogan")
        mock_reviewer_response = MagicMock(text="SHIP IT!")

        with patch("orchestration.workflow.create_writer_agent") as mock_create_writer, \
             patch("orchestration.workflow.create_reviewer_agent") as mock_create_reviewer:

            mock_writer = MagicMock()
            mock_writer.run = AsyncMock(return_value=mock_writer_response)
            mock_create_writer.return_value = mock_writer

            mock_reviewer = MagicMock()
            mock_reviewer.run = AsyncMock(return_value=mock_reviewer_response)
            mock_create_reviewer.return_value = mock_reviewer

            session = await run_slogan_generation("test")

            # Verify timestamps exist
            assert session.started_at is not None
            assert session.completed_at is not None
            assert session.turns[0].timestamp is not None

            # Verify logical order
            assert session.started_at <= session.turns[0].timestamp
            assert session.turns[0].timestamp <= session.completed_at
