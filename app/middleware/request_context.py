import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.requests import Request


from app.core.log_config import get_logger

logger = get_logger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration = round((time.perf_counter() - start) * 1000, 2)

        response.headers['X-Request-ID'] = request_id
        logger.info(
            "request completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration
        )

        return response


