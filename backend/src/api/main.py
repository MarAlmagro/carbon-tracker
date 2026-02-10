"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.error_handler import add_exception_handlers
from api.routes import activities, emission_factors, health
from infrastructure.config.settings import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="Carbon Footprint Tracker API",
        description="API for tracking personal carbon footprint",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        redirect_slashes=False,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    add_exception_handlers(app)

    # Mount routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(
        activities.router, prefix="/api/v1/activities", tags=["activities"]
    )
    app.include_router(
        emission_factors.router,
        prefix="/api/v1/emission-factors",
        tags=["emission-factors"],
    )

    return app


# Create app instance
app = create_app()
