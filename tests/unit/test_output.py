"""Tests for CLI output formatting."""

from datetime import datetime, timedelta

from src.cli.output import format_session_output
from src.orchestration.models import CompletionReason, IterationSession, Turn


class TestFormatSessionOutput:
    """Tests for format_session_output function."""

    def test_incomplete_session_warning(self):
        """Test that incomplete sessions show warning."""
        session = IterationSession(
            user_input="test product",
            model_name="llama3.2:latest",
        )

        output = format_session_output(session)

        assert "⚠️" in output
        assert "not completed" in output.lower()

    def test_approved_session_basic_format(self):
        """Test basic formatting for approved session."""
        session = IterationSession(
            user_input="cloud platform",
            model_name="qwen3:8b",
        )
        session.add_turn(
            slogan="Scale Smarter, Grow Faster",
            feedback=None,
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=False)

        # Check all major sections
        assert "🎯 SLOGAN GENERATION RESULTS" in output
        assert "✨ Final Slogan: Scale Smarter, Grow Faster" in output
        assert "✅" in output  # Approved emoji
        assert "Status: Approved" in output
        assert "📊 Statistics:" in output
        assert "Total iterations: 1" in output
        assert "Model: qwen3:8b" in output
        assert "Input: cloud platform" in output

    def test_max_turns_completion_status(self):
        """Test max turns completion shows correct status."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        for i in range(5):
            session.add_turn(
                slogan=f"Slogan {i+1}",
                feedback="Needs work" if i < 4 else None,
                approved=False,
            )
        session.complete(CompletionReason.MAX_TURNS)

        output = format_session_output(session)

        assert "⏱️" in output
        assert "Status: Max Turns" in output
        assert "Total iterations: 5" in output

    def test_error_completion_status(self):
        """Test error completion shows correct status."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(slogan="Test slogan", approved=False)
        session.complete(CompletionReason.ERROR)

        output = format_session_output(session)

        assert "❌" in output
        assert "Status: Error" in output

    def test_verbose_mode_shows_iteration_details(self):
        """Test verbose mode includes turn-by-turn details."""
        session = IterationSession(
            user_input="eco bottle",
            model_name="llama3.2:latest",
        )
        session.add_turn(
            slogan="First try",
            feedback="Make it catchier",
            approved=False,
        )
        session.add_turn(
            slogan="Second try",
            feedback="Perfect!",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        # Check iteration details section
        assert "📝 Iteration Details:" in output
        assert "Turn 1" in output
        assert "Turn 2" in output
        assert "First try" in output
        assert "Second try" in output
        assert "Make it catchier" in output
        assert "Perfect!" in output

    def test_non_verbose_mode_hides_iteration_details(self):
        """Test non-verbose mode does not show turn details."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(
            slogan="Test slogan",
            feedback="Some feedback",
            approved=False,
        )
        session.add_turn(
            slogan="Final slogan",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=False)

        # Should NOT contain iteration details
        assert "📝 Iteration Details:" not in output
        assert "Turn 1" not in output
        assert "Some feedback" not in output
        # But should contain final slogan
        assert "Final slogan" in output

    def test_single_turn_approval(self):
        """Test session approved on first turn."""
        session = IterationSession(
            user_input="brilliant product",
            model_name="mistral",
        )
        session.add_turn(
            slogan="Brilliant: Shine Bright",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        assert "Total iterations: 1" in output
        assert "Turn 1" in output
        assert "Brilliant: Shine Bright" in output
        assert "✅" in output

    def test_max_turns_boundary(self):
        """Test session with maximum 10 turns."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        for i in range(10):
            session.add_turn(
                slogan=f"Slogan attempt {i+1}",
                feedback="Try again" if i < 9 else None,
                approved=False,
            )
        session.complete(CompletionReason.MAX_TURNS)

        output = format_session_output(session, verbose=True)

        assert "Total iterations: 10" in output
        assert "Turn 1" in output
        assert "Turn 10" in output

    def test_multiline_feedback_display(self):
        """Test that multiline feedback is displayed correctly."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        multiline_feedback = """The slogan lacks specificity.
Consider these improvements:
1. Add concrete benefits
2. Use emotional language
3. Keep it under 100 characters"""

        session.add_turn(
            slogan="Generic Slogan",
            feedback=multiline_feedback,
            approved=False,
        )
        session.add_turn(
            slogan="Better Slogan",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        # All feedback lines should be present
        assert "lacks specificity" in output
        assert "Consider these improvements" in output
        assert "Add concrete benefits" in output

    def test_turn_without_feedback(self):
        """Test turn with approval but no feedback."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(
            slogan="Perfect Slogan",
            feedback=None,
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        assert "Perfect Slogan" in output
        assert "Feedback:" not in output
        assert "✅" in output

    def test_very_long_slogan_display(self):
        """Test that long slogans are displayed correctly."""
        long_slogan = "A" * 400  # Near max length
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(
            slogan=long_slogan,
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session)

        assert long_slogan in output

    def test_timing_information_displayed(self):
        """Test that timing information is shown in statistics."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(slogan="Test", approved=True)
        session.complete(CompletionReason.APPROVED)

        # Ensure completed_at is set (it should be by complete())
        assert session.completed_at is not None

        output = format_session_output(session)

        assert "Duration:" in output
        assert "seconds" in output

    def test_average_turn_time_with_multiple_turns(self):
        """Test average per turn time is shown for multi-turn sessions."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )

        # Add multiple turns with slight time differences
        base_time = datetime.now()
        for i in range(3):
            turn = Turn(
                turn_number=i + 1,
                slogan=f"Slogan {i+1}",
                feedback="Needs improvement" if i < 2 else None,
                approved=(i == 2),
                timestamp=base_time + timedelta(seconds=i * 2),
            )
            session.turns.append(turn)

        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session)

        assert "Average per turn:" in output
        assert "seconds" in output

    def test_per_turn_timing_in_verbose_mode(self):
        """Test that individual turn times are shown in verbose mode."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )

        base_time = datetime.now()
        session.started_at = base_time

        # Add turns with specific timestamps
        for i in range(2):
            turn = Turn(
                turn_number=i + 1,
                slogan=f"Slogan {i+1}",
                feedback="Needs work" if i == 0 else None,
                approved=(i == 1),
                timestamp=base_time + timedelta(seconds=(i + 1) * 3),
            )
            session.turns.append(turn)

        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        # Should show timing for each turn
        assert "Turn 1" in output
        assert "Turn 2" in output
        # Timing should be in parentheses
        assert "s)" in output  # Format is like (3.0s)

    def test_approved_no_indicator_in_verbose(self):
        """Test approved/not approved indicators in verbose mode."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(
            slogan="First attempt",
            feedback="Needs work",
            approved=False,
        )
        session.add_turn(
            slogan="Second attempt",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        # Should show both approved and not approved indicators
        assert "✅ Yes" in output
        assert "❌ No" in output

    def test_separator_lines_present(self):
        """Test that separator lines are present for formatting."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(slogan="Test", approved=True)
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session)

        # Should have separator lines (60 equals signs)
        assert "=" * 60 in output

    def test_all_emojis_present(self):
        """Test that all expected emojis are used in output."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.add_turn(
            slogan="Test slogan",
            feedback="Some feedback",
            approved=False,
        )
        session.add_turn(
            slogan="Final slogan",
            approved=True,
        )
        session.complete(CompletionReason.APPROVED)

        output = format_session_output(session, verbose=True)

        # Check for expected emojis
        assert "🎯" in output  # Header
        assert "✨" in output  # Final slogan
        assert "✅" in output  # Approved status
        assert "📊" in output  # Statistics
        assert "📝" in output  # Iteration details

    def test_empty_session_with_error(self):
        """Test session with error and no turns."""
        session = IterationSession(
            user_input="test",
            model_name="test-model",
        )
        session.completed = True
        session.completion_reason = CompletionReason.ERROR
        session.completed_at = datetime.now()
        session.final_slogan = None

        output = format_session_output(session)

        assert "❌" in output
        assert "Status: Error" in output
        # Should not crash even with no turns
        assert "Total iterations: 0" in output
