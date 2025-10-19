"""Workflow orchestration for Writer-Reviewer collaboration."""

import re

from agents import create_reviewer_agent, create_writer_agent
from config.settings import OllamaConfig, get_ollama_config
from orchestration.models import CompletionReason, IterationSession


def is_approved(reviewer_response: str) -> bool:
    """Check if reviewer approved the slogan.
    
    Looks for "SHIP IT!" as a standalone phrase or at the start of response.
    More strict than just searching anywhere to avoid false positives.
    
    Args:
        reviewer_response: The reviewer's feedback text
        
    Returns:
        True if approved, False otherwise
    """
    if not reviewer_response:
        return False
    
    # Normalize response: strip whitespace and convert to lowercase
    normalized = reviewer_response.strip().lower()
    
    # Check if response STARTS with "ship it" (most reliable indicator)
    if normalized.startswith("ship it"):
        return True
    
    # Check if "ship it!" appears on its own line (strong indicator)
    lines = [line.strip() for line in normalized.split('\n')]
    for line in lines:
        # Match lines that are exactly "ship it" or "ship it!" with optional punctuation
        if re.match(r'^ship\s+it[!.]*$', line):
            return True
    
    return False


def should_continue_iteration(
    session: IterationSession,
    config: OllamaConfig,
) -> bool:
    """Determine if iteration should continue.
    
    Iteration continues if:
    - We haven't reached max turns
    - The latest slogan hasn't been approved
    
    Args:
        session: Current iteration session
        config: Ollama configuration (for max_turns)
        
    Returns:
        True if iteration should continue, False to stop
    """
    if not session.turns:
        return True
    
    latest_turn = session.turns[-1]
    
    # Stop if approved
    if latest_turn.approved:
        return False
    
    # Stop if reached max turns
    if len(session.turns) >= config.max_turns:
        return False
    
    return True


async def run_slogan_generation(
    user_input: str,
    model_name: str | None = None,
    max_turns: int | None = None,
) -> IterationSession:
    """Run the slogan generation workflow.
    
    Orchestrates the Writer-Reviewer collaboration to generate an approved slogan.
    
    Args:
        user_input: Product/service description from user
        model_name: Override default Ollama model
        max_turns: Override default max iteration turns
        
    Returns:
        Completed IterationSession with all turns and final result
        
    Raises:
        ValueError: If user_input is empty
        RuntimeError: If workflow fails to complete
    """
    if not user_input or not user_input.strip():
        raise ValueError("User input cannot be empty")
    
    # Load configuration
    config = get_ollama_config()
    if model_name:
        config.model_name = model_name
    if max_turns is not None:
        config.max_turns = max_turns
    
    # Initialize session
    session = IterationSession(
        user_input=user_input.strip(),
        model_name=config.model_name,
    )
    
    # Create agents
    writer = create_writer_agent(config)
    reviewer = create_reviewer_agent(config)
    
    try:
        # Main iteration loop
        while should_continue_iteration(session, config):
            turn_number = len(session.turns) + 1
            
            # Build writer prompt
            if turn_number == 1:
                writer_prompt = f"Create a slogan for: {user_input}"
            else:
                previous_feedback = session.turns[-1].feedback
                previous_slogan = session.turns[-1].slogan
                writer_prompt = (
                    f"Previous slogan: {previous_slogan}\n"
                    f"Feedback: {previous_feedback}\n\n"
                    f"Create an improved slogan for: {user_input}"
                )
            
            # Get slogan from writer
            writer_response = await writer.run(writer_prompt)
            slogan = writer_response.text.strip()
            
            # Get feedback from reviewer
            reviewer_prompt = (
                f"Review this slogan for '{user_input}':\n\n"
                f"Slogan: {slogan}\n\n"
                f"Provide feedback or approve with 'SHIP IT!'"
            )
            reviewer_response = await reviewer.run(reviewer_prompt)
            feedback = reviewer_response.text.strip()
            
            # Check approval
            approved = is_approved(feedback)
            
            # Add turn to session
            session.add_turn(
                slogan=slogan,
                feedback=feedback,
                approved=approved,
            )
            
            # Stop if approved
            if approved:
                session.complete(CompletionReason.APPROVED)
                break
        
        # If not approved and loop ended, we hit max turns
        if not session.completed:
            session.complete(CompletionReason.MAX_TURNS)
        
        return session
        
    except Exception as e:
        session.complete(CompletionReason.ERROR)
        raise RuntimeError(f"Workflow failed: {e}") from e
