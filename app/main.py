from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app.api.routers import router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.log_config import get_logger, configure_logging
from app.middleware.request_context import RequestContextMiddleware

from app.models.all import User, Note, Tag, note_tags
from app.database.session import init_db

from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(f"App {settings.PROJECT_TITLE} has started...")
    await init_db()

    yield
    logger.info(f"App {settings.PROJECT_TITLE} has stopped...")


def get_app():

    app = FastAPI(
        lifespan=lifespan, docs_url=settings.DOCS_URL, redoc_url=settings.REDOC_URL
    )

    app.include_router(router)
    register_exception_handlers(app)
    app.add_middleware(RequestContextMiddleware)

    add_pagination(app)

    disable_installed_extensions_check()

    return app


app = get_app()
