from typing import Optional
from app.core.log_config import get_logger
from fastapi import status, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import StarletteHTTPException, RequestValidationError

logger = get_logger(__name__)


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "app_error"
    detail = None

    def __init__(self, detail: str, error_code: Optional[str] = None):
        self.detail = detail
        if error_code:
            self.error_code = error_code

        super().__init__(detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class AlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "already_exists"


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"


def _error_body(error_code: str, detail: str):
    return {"error": {"code": error_code, "detail": detail}}


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_error", detail=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.error_code, detail=exc.detail),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content=_error_body("http_error", exc.detail)
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {
                    "code": "validation error",
                    "message": "request validation error occurred.",
                    "details": jsonable_encoder(exc.errors()),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unknown_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                "internal_server_error", "An unexpected error occurred."
            ),
        )
