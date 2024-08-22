"""
서비스 자체 로직에 관한 커스텀 예외처리 작성
"""

from starlette import status

from app.config import settings
from app.exceptions.base import ApplicationError


class TokenValidationError(ApplicationError):
    """유효하지 않은 토큰 설정"""

    def __init__(self, x_token):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_401_UNAUTHORIZED}")
        self.message = "Invalid x-token header"
        self.result = {"current_x_token": x_token}


class InvalidItemStock(ApplicationError):
    """유효하지 않은 아이템 재고값 설정"""

    def __init__(self, stock):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_400_BAD_REQUEST}")
        self.message = "Invalid stock"
        self.result = {"current_stock": stock}


class ItemNotFoundError(ApplicationError):
    """아이템을 찾을 수 없는 에러"""

    def __init__(self, item_id):
        self.code = int(f"{settings.SERVICE_CODE}{status.HTTP_404_NOT_FOUND}")
        self.message = "Item not found"
        self.result = {"current_item_id": item_id}
