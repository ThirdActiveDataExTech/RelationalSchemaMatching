from fastapi import APIRouter

from app.models import APIResponseModel

router = APIRouter()


@router.post("", response_model=APIResponseModel)
async def update_admin():
    return APIResponseModel(message="Admin getting schwifty", description="관리자 업데이트 성공")
