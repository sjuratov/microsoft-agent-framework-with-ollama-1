"""Unit tests for workflow logic."""

import pytest

from orchestration.models import CompletionReason, IterationSession, Turn
from orchestration.workflow import is_approved, should_continue_iteration
from config.settings import OllamaConfig


class TestIsApproved:
    """Test suite for is_approved() function."""

    def test_exact_match_uppercase(self):
        """Should detect exact 'SHIP IT!' phrase."""
        assert is_approved("SHIP IT!") is True

    def test_exact_match_lowercase(self):
        """Should detect 'ship it!' in lowercase."""
        assert is_approved("ship it!") is True

    def test_mixed_case(self):
        """Should detect 'ShIp It!' with mixed case."""
        assert is_approved("ShIp It!") is True

    def test_with_surrounding_text_after(self):
        """Should detect 'ship it' at start with text after."""
        feedback = "Ship it! This is excellent work. Great job on the slogan."
        assert is_approved(feedback) is True

    def test_with_extra_spaces(self):
        """Should detect 'ship  it' with extra spaces."""
        assert is_approved("ship  it!") is True

    def test_without_exclamation(self):
        """Should detect 'ship it' even without exclamation mark when starting."""
        assert is_approved("ship it") is True

    def test_at_start_of_text(self):
        """Should detect 'ship it' at the beginning."""
        assert is_approved("Ship it! This is perfect.") is True

    def test_on_own_line(self):
        """Should detect 'ship it' when on its own line."""
        assert is_approved("Great feedback here.\n\nSHIP IT!") is True
        assert is_approved("Some feedback\n\nship it!\n") is True

    def test_not_approved_at_end_after_feedback(self):
        """Should NOT approve when 'ship it' is at end of feedback paragraph."""
        # This is the bug we fixed - should not approve
        assert is_approved("Looks great, ship it!") is False
        assert is_approved("This is excellent work! Ship it! Great job.") is False

    def test_not_approved_similar_words(self):
        """Should not match similar but different words."""
        assert is_approved("Let's ship this item tomorrow") is False
        assert is_approved("The shipping date is tomorrow") is False

    def test_not_approved_partial_match(self):
        """Should not match partial phrases."""
        assert is_approved("ship") is False
        assert is_approved("it") is False

    def test_not_approved_no_match(self):
        """Should return False for feedback without approval phrase."""
        feedback = "This needs improvement. Try making it more catchy."
        assert is_approved(feedback) is False

    def test_empty_string(self):
        """Should return False for empty string."""
        assert is_approved("") is False

    def test_none_value(self):
        """Should return False for None."""
        assert is_approved(None) is False  # type: ignore[arg-type]

    def test_whitespace_only(self):
        """Should return False for whitespace only."""
        assert is_approved("   ") is False


class TestShouldContinueIteration:
    """Test suite for should_continue_iteration() function."""

    def test_continue_no_turns(self):
        """Should continue when no turns exist yet."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=5)
        assert should_continue_iteration(session, config) is True

    def test_continue_under_max_turns_not_approved(self):
        """Should continue when under max turns and not approved."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        session.add_turn(
            slogan="Test Slogan",
            feedback="Needs improvement",
            approved=False,
        )
        config = OllamaConfig(max_turns=5)
        assert should_continue_iteration(session, config) is True

    def test_stop_when_approved(self):
        """Should stop when slogan is approved."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        session.add_turn(
            slogan="Perfect Slogan",
            feedback="SHIP IT!",
            approved=True,
        )
        config = OllamaConfig(max_turns=5)
        assert should_continue_iteration(session, config) is False

    def test_stop_at_max_turns(self):
        """Should stop when reaching max turns."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=3)

        # Add 3 turns (reaching max)
        for i in range(3):
            session.add_turn(
                slogan=f"Slogan {i + 1}",
                feedback="Needs work",
                approved=False,
            )

        assert should_continue_iteration(session, config) is False

    def test_continue_one_before_max_turns(self):
        """Should continue when one turn below max."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=5)

        # Add 4 turns (one below max)
        for i in range(4):
            session.add_turn(
                slogan=f"Slogan {i + 1}",
                feedback="Keep trying",
                approved=False,
            )

        assert should_continue_iteration(session, config) is True

    def test_max_turns_boundary_min(self):
        """Should handle max_turns=1 correctly."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=1)

        # No turns yet - should continue
        assert should_continue_iteration(session, config) is True

        # After 1 turn - should stop
        session.add_turn(slogan="Slogan", feedback="Nope", approved=False)
        assert should_continue_iteration(session, config) is False

    def test_max_turns_boundary_max(self):
        """Should handle max_turns=10 correctly."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=10)

        # Add 9 turns - should continue
        for i in range(9):
            session.add_turn(slogan=f"Slogan {i + 1}", feedback="Try again", approved=False)
        assert should_continue_iteration(session, config) is True

        # Add 10th turn - should stop
        session.add_turn(slogan="Slogan 10", feedback="Still no", approved=False)
        assert should_continue_iteration(session, config) is False

    def test_approved_overrides_max_turns(self):
        """Should stop on approval even if under max turns."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        config = OllamaConfig(max_turns=10)

        # First turn gets approved
        session.add_turn(slogan="Amazing Slogan", feedback="SHIP IT!", approved=True)

        # Should stop even though we're well under max_turns
        assert should_continue_iteration(session, config) is False


class TestIterationSession:
    """Test suite for IterationSession model behavior."""

    def test_add_turn_increments_number(self):
        """Should automatically increment turn numbers."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")

        turn1 = session.add_turn("Slogan 1", "Feedback 1")
        turn2 = session.add_turn("Slogan 2", "Feedback 2")
        turn3 = session.add_turn("Slogan 3", "Feedback 3")

        assert turn1.turn_number == 1
        assert turn2.turn_number == 2
        assert turn3.turn_number == 3
        assert len(session.turns) == 3

    def test_complete_sets_fields(self):
        """Should properly set completion fields."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        session.add_turn("Final Slogan", "SHIP IT!", approved=True)

        assert session.completed is False
        assert session.completion_reason is None
        assert session.completed_at is None
        assert session.final_slogan is None

        session.complete(CompletionReason.APPROVED)

        assert session.completed is True
        assert session.completion_reason == CompletionReason.APPROVED
        assert session.completed_at is not None
        assert session.final_slogan == "Final Slogan"

    def test_complete_with_max_turns(self):
        """Should handle max_turns completion reason."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")

        for i in range(5):
            session.add_turn(f"Slogan {i + 1}", "Not good enough", approved=False)

        session.complete(CompletionReason.MAX_TURNS)

        assert session.completed is True
        assert session.completion_reason == CompletionReason.MAX_TURNS
        assert session.final_slogan == "Slogan 5"  # Last slogan

    def test_complete_with_error(self):
        """Should handle error completion reason."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")
        session.add_turn("Partial Slogan", None, approved=False)

        session.complete(CompletionReason.ERROR)

        assert session.completed is True
        assert session.completion_reason == CompletionReason.ERROR

    def test_turn_validation_sequential(self):
        """Should validate turns are in sequential order."""
        session = IterationSession(user_input="test", model_name="llama3.2:latest")

        # Valid sequential turns
        session.add_turn("Slogan 1")
        session.add_turn("Slogan 2")
        session.add_turn("Slogan 3")

        # Should not raise error
        assert len(session.turns) == 3

    def test_completion_validation_requires_fields(self):
        """Should validate completed sessions have required fields."""
        # This would be tested by Pydantic validation
        # Creating a completed session without final_slogan should fail
        with pytest.raises(ValueError):
            IterationSession(
                user_input="test",
                model_name="llama3.2:latest",
                completed=True,
                completion_reason=None,  # Missing required field
            )


class TestTurnModel:
    """Test suite for Turn model validation."""

    def test_turn_number_validation_min(self):
        """Should reject turn_number < 1."""
        with pytest.raises(ValueError):
            Turn(turn_number=0, slogan="Test", feedback=None)

    def test_turn_number_validation_max(self):
        """Should reject turn_number > 10."""
        with pytest.raises(ValueError):
            Turn(turn_number=11, slogan="Test", feedback=None)

    def test_slogan_length_validation(self):
        """Should reject slogans exceeding max length."""
        long_slogan = "x" * 501  # Max is 500
        with pytest.raises(ValueError):
            Turn(turn_number=1, slogan=long_slogan, feedback=None)

    def test_slogan_empty_validation(self):
        """Should reject empty slogans."""
        with pytest.raises(ValueError):
            Turn(turn_number=1, slogan="", feedback=None)

    def test_feedback_length_validation(self):
        """Should reject feedback exceeding max length."""
        long_feedback = "x" * 1001  # Max is 1000
        with pytest.raises(ValueError):
            Turn(turn_number=1, slogan="Test", feedback=long_feedback)

    def test_feedback_optional(self):
        """Should allow None feedback."""
        turn = Turn(turn_number=1, slogan="Test Slogan", feedback=None)
        assert turn.feedback is None
        assert turn.approved is False

    def test_timestamp_auto_generated(self):
        """Should automatically generate timestamp."""
        turn = Turn(turn_number=1, slogan="Test", feedback=None)
        assert turn.timestamp is not None
