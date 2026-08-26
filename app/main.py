import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_session_factory, init_db
from app.core.exceptions import register_exception_handlers
from app.routes import api_router
from app.utils.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB and seed data on startup."""
    await init_db()
    async with async_session_factory() as session:
        await seed_database(session)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    origins = settings.cors_origins_list
    allow_all = "*" in origins or origins == ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else origins,
        allow_credentials=not allow_all,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Health check for monitoring and platforms like Render
    @app.get("/", tags=["Health"])
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "docs": "/docs",
        }

    # API Routes
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)
