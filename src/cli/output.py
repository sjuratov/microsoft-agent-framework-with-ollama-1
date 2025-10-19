"""CLI output formatting."""

from orchestration.models import CompletionReason, IterationSession


def format_session_output(session: IterationSession, verbose: bool = False) -> str:
    """Format session output for display.
    
    Args:
        session: The completed iteration session
        verbose: If True, include all iteration details
        
    Returns:
        Formatted output string
    """
    if not session.completed:
        return "⚠️  Session not completed"
    
    lines = []
    
    # Header
    lines.append("\n" + "=" * 60)
    lines.append("🎯 SLOGAN GENERATION RESULTS")
    lines.append("=" * 60)
    
    # Final slogan
    if session.final_slogan:
        lines.append(f"\n✨ Final Slogan: {session.final_slogan}")
    
    # Completion status
    completion_emoji = {
        CompletionReason.APPROVED: "✅",
        CompletionReason.MAX_TURNS: "⏱️ ",
        CompletionReason.ERROR: "❌",
    }
    emoji = completion_emoji.get(session.completion_reason, "") if session.completion_reason else ""
    reason_text = session.completion_reason.value.replace("_", " ").title() if session.completion_reason else "Unknown"
    lines.append(f"\n{emoji} Status: {reason_text}")
    
    # Stats
    lines.append(f"\n📊 Statistics:")
    lines.append(f"   • Total iterations: {len(session.turns)}")
    lines.append(f"   • Model: {session.model_name}")
    lines.append(f"   • Input: {session.user_input}")
    
    # Iteration details (if verbose)
    if verbose and session.turns:
        lines.append(f"\n📝 Iteration Details:")
        for turn in session.turns:
            lines.append(f"\n   Turn {turn.turn_number}:")
            lines.append(f"   Slogan: {turn.slogan}")
            if turn.feedback:
                lines.append(f"   Feedback: {turn.feedback}")
            lines.append(f"   Approved: {'✅ Yes' if turn.approved else '❌ No'}")
    
    lines.append("\n" + "=" * 60 + "\n")
    
    return "\n".join(lines)
