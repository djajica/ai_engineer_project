from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import api_router
from app.core.container import AppContainer, get_container
from app.core.events import lifespan


def create_app() -> FastAPI:
    container: AppContainer = get_container()

    app = FastAPI(
        title="LLM Query Service",
        description="FastAPI LLM query service with LangGraph, Weaviate RAG, and Tavily search",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=container.settings.api_prefix)
    register_exception_handlers(app)

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
