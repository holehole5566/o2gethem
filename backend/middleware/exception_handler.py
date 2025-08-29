from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from utils.responses import error_response
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response("Internal server error")
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.detail)
    )

async def validation_exception_handler(request: Request, exc: Exception):
    """Handler for validation exceptions"""
    return JSONResponse(
        status_code=422,
        content=error_response("Validation error")
    )