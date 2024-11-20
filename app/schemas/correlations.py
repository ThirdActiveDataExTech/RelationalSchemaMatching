"""
pydantic BaseModel을 기본적으로 활용한다.

- 권장사항
    - Field(title, description, default, ...)를 사용하여 Swagger UI에 디폴트값, 설명, 예시 등을 작성한다.
    - @field_validator(...)를 사용하여 모델의 필드값을 검토하도록 한다.
    - @model_validator(...)를 사용하여 모델 적용 전과 후에 확인할 로직을 작성한다.
    > 자세한 사항은 pydantic 공식 문서 확인
"""
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.response import APIResponseModel
from app.version import VERSION


class SchemaMatchingRequestModel(BaseModel):
    l_table: str = Field(description="ltable path"),
    r_table: str = Field(description="rtable path"),
    result_path: str = Field(description="result path"),
    truth_json: Optional[str] = Field(description="truth json"),
    model: str = Field(description="model path", default="initial"),
    strategy: str = Field(description="strategy", default="many_to_many"),
    threshold: Optional[float] = Field(description="threshold", default=None)


class DatasetMatchingRequestModel(BaseModel):
    dataset: str = Field(description="dataset path")
    model: str = Field(description="model path", default="initial"),
    strategy: str = Field(description="strategy", default="many_to_many"),
    threshold: Optional[float] = Field(description="threshold", default=None)


class DummyCorrelation(BaseModel):
    response: bool


class SchemaMatchingResponseModel(APIResponseModel):
    message: str = Field(default=f"스키마 매칭 응답 성공 ({VERSION})")
