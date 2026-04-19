import importlib
import logging
from contextlib import asynccontextmanager

importlib.import_module("app.runtime_bootstrap")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.orchestrator import router as orchestrator_router
from app.api.routes.users import router as users_router
from app.config import get_settings
from app.utils.logger import setup_logging

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(settings.log_level)
    logger.info("Starting %s (env=%s)", settings.app_name, settings.environment)
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "X-API-Token"],
)

app.include_router(users_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(orchestrator_router, prefix="/api")


@app.get("/health")
def health():
    tracing_on = bool(
        (settings.langchain_api_key or "").strip() and settings.langchain_tracing_v2
    )
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "langsmith_tracing": tracing_on,
        "langsmith_project": settings.langchain_project if tracing_on else None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7801,
        reload=settings.environment == "development",
    )
