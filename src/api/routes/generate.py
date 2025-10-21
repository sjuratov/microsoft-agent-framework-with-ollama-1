"""Generate endpoint for slogan generation."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.dependencies import get_config
from src.api.schemas.requests import GenerateRequest
from src.api.schemas.responses import GenerateResponse, TurnDetail
from src.config.settings import OllamaConfig, get_available_models
from src.orchestration.models import CompletionReason, IterationSession
from src.orchestration.workflow import run_slogan_generation

router = APIRouter(prefix="/api/v1", tags=["slogans"])

# Thread pool for running sync orchestration code
_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="slogan_gen")


async def run_generation_async(
    user_input: str,
    model_name: str | None,
    max_turns: int | None,
) -> IterationSession:
    """
    Run slogan generation in thread pool with timeout.

    Wraps the synchronous run_slogan_generation in a thread pool executor
    and applies the 600s timeout as specified in the architecture.

    Args:
        user_input: Product/topic description
        model_name: Optional model override
        max_turns: Optional max turns override

    Returns:
        Completed IterationSession

    Raises:
        asyncio.TimeoutError: If generation exceeds 600 seconds
        Exception: Any error from the underlying workflow
    """
    asyncio.get_event_loop()

    # The workflow is already async, so we just need to add timeout
    try:
        session = await asyncio.wait_for(
            run_slogan_generation(user_input, model_name, max_turns),
            timeout=600.0  # API_GENERATION_TIMEOUT from spec
        )
        return session
    except TimeoutError:
        raise TimeoutError(
            "Slogan generation exceeded maximum time limit (600 seconds)"
        )


def convert_session_to_response(
    session: IterationSession,
    original_input: str,
    verbose: bool,
    request_id: str,
    started_at: datetime,
) -> GenerateResponse:
    """
    Convert IterationSession to API response format.

    Args:
        session: Completed iteration session
        original_input: Original user input
        verbose: Whether to include turn details
        request_id: Request UUID
        started_at: Request start timestamp

    Returns:
        GenerateResponse with formatted data
    """
    # Calculate duration metrics
    if session.completed_at and session.started_at:
        total_duration = (session.completed_at - session.started_at).total_seconds()
    else:
        total_duration = (datetime.now() - session.started_at).total_seconds()

    avg_duration = total_duration / len(session.turns) if session.turns else 0

    # Convert turns if verbose
    turns_detail = None
    if verbose and session.turns:
        turns_detail = [
            TurnDetail(
                turn_number=turn.turn_number,
                slogan=turn.slogan,
                feedback=turn.feedback,
                approved=turn.approved,
                timestamp=turn.timestamp,
            )
            for turn in session.turns
        ]

    # Map completion reason
    completion_reason = "error"
    if session.completion_reason == CompletionReason.APPROVED:
        completion_reason = "approved"
    elif session.completion_reason == CompletionReason.MAX_TURNS:
        completion_reason = "max_turns"

    return GenerateResponse(
        slogan=session.final_slogan or "",
        input=original_input,
        completion_reason=completion_reason,  # type: ignore
        turn_count=len(session.turns),
        model_name=session.model_name,
        total_duration_seconds=round(total_duration, 2),
        average_duration_per_turn=round(avg_duration, 2),
        turns=turns_detail,
        created_at=started_at,
        request_id=uuid4() if request_id else None,
    )


@router.post("/slogans/generate", response_model=GenerateResponse)
async def generate_slogan(
    request_body: GenerateRequest,
    request: Request,
    config: OllamaConfig = Depends(get_config),
) -> GenerateResponse:
    """
    Generate a slogan through Writer-Reviewer collaboration.

    This endpoint orchestrates the multi-agent slogan generation workflow,
    where a Writer agent creates slogans and a Reviewer agent provides feedback
    until an acceptable slogan is approved or max iterations reached.

    Args:
        request_body: Generation request with input, optional model, max_turns, verbose
        request: FastAPI request object (for accessing request_id from middleware)
        config: Injected Ollama configuration

    Returns:
        GenerateResponse with final slogan and metadata

    Raises:
        HTTPException 400: Invalid model specified
        HTTPException 422: Validation error (handled by FastAPI)
        HTTPException 500: Generation error
        HTTPException 504: Generation timeout (>600s)
    """
    # Get request ID from middleware (or generate if middleware not active)
    request_id = getattr(request.state, "request_id", str(uuid4()))
    started_at = datetime.now()

    try:
        # Validate model if specified
        if request_body.model:
            try:
                available_models = get_available_models(base_url=config.base_url, timeout=10)
                if request_body.model not in available_models:
                    models_list = ', '.join(available_models)
                    error_msg = (
                        f"Model '{request_body.model}' not found. "
                        f"Available models: {models_list}"
                    )
                    raise HTTPException(status_code=400, detail=error_msg)
            except HTTPException:
                # Re-raise HTTPException (our validation error)
                raise
            except (ConnectionError, RuntimeError):
                # If we can't fetch models, let the generation proceed with the requested model
                # The generation itself will fail if the model truly doesn't exist
                pass

        # Run generation with timeout
        session = await run_generation_async(
            user_input=request_body.input,
            model_name=request_body.model,
            max_turns=request_body.max_turns,
        )

        # Convert to API response
        response = convert_session_to_response(
            session=session,
            original_input=request_body.input,
            verbose=request_body.verbose,
            request_id=request_id,
            started_at=started_at,
        )

        return response

    except HTTPException:
        # Re-raise HTTPException from validation or other explicit raises
        raise

    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "generation_timeout",
                "message": str(e),
                "request_id": request_id,
            }
        ) from e

    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": str(e),
                "request_id": request_id,
            }
        ) from e

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "message": str(e),
                "request_id": request_id,
            }
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Slogan generation failed: {str(e)}",
                "request_id": request_id,
            }
        ) from e
