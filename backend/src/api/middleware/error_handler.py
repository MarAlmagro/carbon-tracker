"""Global exception handlers for FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


def add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers to FastAPI app.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions.

        Args:
            request: FastAPI request
            exc: ValueError exception

        Returns:
            JSON response with 400 Bad Request
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unhandled exceptions.

        Args:
            request: FastAPI request
            exc: Exception

        Returns:
            JSON response with 500 Internal Server Error
        """
        # In production, log the full exception here
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
