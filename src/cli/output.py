"""CLI output formatting."""

import click

from src.orchestration.models import CompletionReason, IterationSession


def format_session_output(session: IterationSession, verbose: bool = False) -> str:
    """Format session output for display.

    Args:
        session: The completed iteration session
        verbose: If True, include all iteration details

    Returns:
        Formatted output string
    """
    if not session.completed:
        return click.style("⚠️  Session not completed", fg="yellow")

    lines = []

    # Header
    separator = "=" * 60
    lines.append("\n" + separator)
    lines.append(click.style("🎯 SLOGAN GENERATION RESULTS", fg="cyan", bold=True))
    lines.append(separator)

    # Final slogan
    if session.final_slogan:
        slogan_text = f"✨ Final Slogan: {session.final_slogan}"
        lines.append("\n" + click.style(slogan_text, fg="green", bold=True))

    # Completion status
    completion_emoji = {
        CompletionReason.APPROVED: "✅",
        CompletionReason.MAX_TURNS: "⏱️ ",
        CompletionReason.ERROR: "❌",
    }
    completion_colors = {
        CompletionReason.APPROVED: "green",
        CompletionReason.MAX_TURNS: "yellow",
        CompletionReason.ERROR: "red",
    }
    emoji = completion_emoji.get(session.completion_reason, "") if session.completion_reason else ""
    reason_text = (
        session.completion_reason.value.replace("_", " ").title()
        if session.completion_reason
        else "Unknown"
    )
    color = (
        completion_colors.get(session.completion_reason, "white")
        if session.completion_reason
        else "white"
    )
    status_text = f"{emoji} Status: {reason_text}"
    lines.append("\n" + click.style(status_text, fg=color, bold=True))

    # Stats
    lines.append("\n" + click.style("📊 Statistics:", bold=True))
    lines.append(f"   • Total iterations: {len(session.turns)}")
    lines.append(f"   • Model: {session.model_name}")
    lines.append(f"   • Input: {session.user_input}")

    # Timing information
    if session.completed_at:
        duration = (session.completed_at - session.started_at).total_seconds()
        lines.append(click.style(f"   • Duration: {duration:.1f} seconds", dim=True))

        # Average turn time if multiple turns
        if len(session.turns) > 1:
            avg_time = duration / len(session.turns)
            lines.append(click.style(f"   • Average per turn: {avg_time:.1f} seconds", dim=True))

    # Iteration details (if verbose)
    if verbose and session.turns:
        lines.append("\n" + click.style("📝 Iteration Details:", bold=True))
        for turn in session.turns:
            turn_header = click.style(f"\n   Turn {turn.turn_number}", bold=True, dim=True)

            # Calculate per-turn duration
            if turn.turn_number > 1:
                prev_turn = session.turns[turn.turn_number - 2]
                turn_duration = (turn.timestamp - prev_turn.timestamp).total_seconds()
                turn_header += click.style(f" ({turn_duration:.1f}s)", dim=True)
            elif session.turns:
                # First turn duration from session start
                turn_duration = (turn.timestamp - session.started_at).total_seconds()
                turn_header += click.style(f" ({turn_duration:.1f}s)", dim=True)

            lines.append(turn_header + ":")

            lines.append(f"   Slogan: {turn.slogan}")

            if turn.feedback:
                feedback_label = click.style("Feedback:", fg="yellow")
                lines.append(f"   {feedback_label} {turn.feedback}")

            if turn.approved:
                approved_text = click.style("✅ Yes", fg="green", bold=True)
            else:
                approved_text = click.style("❌ No", fg="red")
            lines.append(f"   Approved: {approved_text}")

    lines.append("\n" + separator + "\n")

    return "\n".join(lines)
