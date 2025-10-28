"""
pydantic BaseModel을 기본적으로 활용한다.

- 권장사항
    - Field(title, description, default, ...)를 사용하여 Swagger UI에 디폴트값, 설명, 예시 등을 작성한다.
    - @field_validator(...)를 사용하여 모델의 필드값을 검토하도록 한다.
    - @model_validator(...)를 사용하여 모델 적용 전과 후에 확인할 로직을 작성한다.
    > 자세한 사항은 pydantic 공식 문서 확인
"""

from pydantic import BaseModel, Field

from app.schemas.response import APIResponseModel
from app.version import VERSION


class DummyCorrelation(BaseModel):
    response: bool | str | dict[str, str] | dict[str, float]


class SchemaMatchingResponseModel(APIResponseModel):
    message: str = Field(default=f"스키마 매칭 응답 성공 ({VERSION})")
