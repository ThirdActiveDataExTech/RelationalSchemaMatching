import json
import logging
import traceback

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.exceptions.base import ApplicationError


def get_client_info(request: Request) -> str:
    """프록시 환경 대응 클라이언트 정보 추출

    프록시 헤더 우선으로 실제 클라이언트 IP와 User-Agent 추출.
    로깅용 클라이언트 식별자 생성.

    Returns:
        str: "client:{ip} ua:{user_agent}..." 형식
    """
    real_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
        request.headers.get("x-real-ip", "") or
        request.headers.get("cf-connecting-ip", "") or
        request.headers.get("x-forwarded-proto", "") or
        str(request.client.host if request.client else "unknown")
    )

    user_agent = request.headers.get("user-agent", "unknown")
    return f"client:{real_ip} ua:{user_agent[:50]}..."


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    client_info = get_client_info(request)
    logging.error(f"{client_info} {request.method} {request.url} → HTTPException({exc.status_code}): {exc.detail}")

    status_code = int(f"{settings.SERVICE_CODE}{exc.status_code}")
    if exc.status_code == 404:
        return JSONResponse(status_code=200, content=ApplicationError(
            code=status_code, message="Invalid URL. see api-doc `/docs` or `/openapi.json`",
            result={"detail": exc.detail}).to_dict())
    return JSONResponse(
        status_code=200, content=ApplicationError(
            code=status_code, message=exc.detail, result={"headers": exc.headers}).to_dict())


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    client_info = get_client_info(request)
    error_detail = f"{exc.errors()[0]['msg']} (type: {exc.errors()[0]['type']}) at {exc.errors()[0]['loc']}"
    logging.error(f"{client_info} {request.method} {request.url} → ValidationError: {error_detail}")

    try:
        json.dumps(exc.body)
        safe_body = exc.body
    except (TypeError, ValueError):
        if isinstance(exc.body, bytes):
            try:
                safe_body = exc.body.decode('utf-8')
            except UnicodeDecodeError:
                safe_body = f"<binary:{len(exc.body)}bytes>"
        else:
            safe_body = repr(exc.body)

    return JSONResponse(
        status_code=200, content=ApplicationError(
            code=int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            message=f"Invalid Request: {error_detail}",
            result=safe_body
        ).to_dict())


async def validation_exception_handler(request: Request, exc: ValidationError):
    client_info = get_client_info(request)
    error_summary = f"{len(exc.errors())} validation errors: {exc.errors()[0]['msg'] if exc.errors() else 'unknown'}"
    logging.error(f"{client_info} {request.method} {request.url} → PydanticValidationError: {error_summary}")

    return JSONResponse(
        status_code=200, content=ApplicationError(
            code=int(f"{settings.SERVICE_CODE}{status.HTTP_422_UNPROCESSABLE_ENTITY}"),
            message="Pydantic Model ValidationError", result=exc.errors()).to_dict())


async def application_error_handler(request: Request, exc: ApplicationError):
    client_info = get_client_info(request)
    logging.error(f"{client_info} {request.method} {request.url} → ApplicationError(code:{exc.code}): {exc.message}")

    return JSONResponse(status_code=200, content=ApplicationError(
        code=exc.code, result=exc.result, message=exc.message).to_dict())


def get_exception_message(exc: Exception) -> str:
    """안전한 예외 메시지 추출"""
    try:
        return ''.join(traceback.format_exception_only(type(exc), exc)).strip()
    except Exception:
        if hasattr(exc, 'args') and exc.args:
            return str(exc.args[0])
        return repr(exc)


async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리기

    처리되지 않은 예외 캐치 및 안전한 메시지 추출.
    스택 트레이스 없는 깔끔한 로깅 제공.

    - traceback.format_exception_only() 우선 사용
    - INFO 레벨: 예외 정보만 로깅
    - DEBUG 레벨: 전체 스택 트레이스 추가
    - 프록시 환경 클라이언트 정보 포함

    Returns:
        JSONResponse: ApplicationError 형식 409 응답
    """
    exception_class = exc.__class__.__name__

    exception_message = get_exception_message(exc) or f"Unable to get exception message for {exception_class}"

    client_info = get_client_info(request)
    logging.error(f"{client_info} {request.method} {request.url} → {exception_class}: {exception_message}")

    if settings.LEVEL == "DEBUG":
        full_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logging.debug(f"Full traceback for {exception_class}:\n{full_traceback}")

    return JSONResponse(
        status_code=409,
        content=ApplicationError(
            code=int(f"{settings.SERVICE_CODE}409"),
            message="Unhandled Error",
            result={
                "exception_type": exception_class,
                "exception_message": exception_message
            }
        ).to_dict()
    )
