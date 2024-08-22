import logging

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.exceptions.base import ApplicationError
from app.schemas.response import APIResponseModel


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logging.error(f"{request.client} {request.method} {request.url} → {repr(exc)}")
    status_code = int(f"{settings.SERVICE_CODE}{exc.status_code}")
    if exc.status_code == 404:
        return JSONResponse(status_code=200, content=APIResponseModel(
            code=status_code, message="Invalid URL. see api-doc `/docs` or `/openapi.json`",
            result={"detail": exc.detail}, description="API 응답 실패").to_dict())
    return JSONResponse(
        status_code=200, content=APIResponseModel(
            code=status_code, description=exc.detail,
            result={"headers": exc.headers}, message="API 응답 실패").to_dict())


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"{request.client} {request.method} {request.url} → {repr(exc)}")
    return JSONResponse(
        status_code=200, content=APIResponseModel(
            code=int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            description=f"Invalid Request: {exc.errors()[0]['msg']} (type: {exc.errors()[0]['type']}), "
                    f"Check {(exc.errors()[0]['loc'])}",
            result=exc.body, message="API 응답 실패").to_dict())


async def validation_exception_handler(request: Request, exc: ValidationError):
    logging.error(f"{request.client} {request.method} {request.url} → {repr(exc)}")
    return JSONResponse(
        status_code=200, content=APIResponseModel(
            code=int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            description="Pydantic Model ValidationError",
            result=exc.errors(), message="API 응답 실패").to_dict())


async def application_error_handler(request: Request, exc: ApplicationError):
    logging.error(f"{request.client} {request.method} {request.url} → {repr(exc)}")
    return JSONResponse(status_code=200, content=APIResponseModel(
        code=exc.code, description=exc.message, result=exc.result, message="API 응답 실패").to_dict())
