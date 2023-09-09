import time

import structlog
from fastapi import Request


async def logging_middleware(request: Request, call_next):
    logger = structlog.get_logger()
    start_time = time.time()
    logger.info("Запрос начат", method=request.method, path=request.url.path)

    response = await call_next(request)

    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    logger.info("Запрос завершен", status_code=response.status_code, response_time=response_time_ms)

    return response
