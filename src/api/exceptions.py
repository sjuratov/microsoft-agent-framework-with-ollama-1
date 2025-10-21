"""Global exception handlers for the API."""

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors with detailed error messages.
    
    Args:
        request: The incoming request
        exc: The validation error
    
    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.warning(
        f"Validation error: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "errors": exc.errors(),
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={"X-Request-ID": request_id} if request_id else {},
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle HTTP exceptions with consistent format.
    
    Args:
        request: The incoming request
        exc: The HTTP exception
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log based on status code severity
    if exc.status_code >= 500:
        logger.error(
            f"HTTP {exc.status_code}: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail,
            }
        )
    else:
        logger.warning(
            f"HTTP {exc.status_code}: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail,
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Request-ID": request_id} if request_id else {},
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions with generic error message.
    
    Args:
        request: The incoming request
        exc: The unhandled exception
    
    Returns:
        JSONResponse with generic error message
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"Unhandled exception: {request.method} {request.url.path} - {str(exc)}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(exc),
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        },
        headers={"X-Request-ID": request_id} if request_id else {},
    )
