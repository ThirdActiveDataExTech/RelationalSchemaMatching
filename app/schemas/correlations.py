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
from app.src.correlations.enums import Strategy
from app.version import VERSION


class SchemaMatchingRequestModel(BaseModel):
    # 사용할 데이터
    l_table: str = Field(..., description="`s3://{BUCKET}/{KEY}` 또는 로컬 파일 경로")
    r_table: str = Field(..., description="`s3://{BUCKET}/{KEY}` 또는 로컬 파일 경로")

    # 결과 반환 관련 파라미터
    truth_json: Optional[str] = Field(description="l_table, r_table에 대한 Groun Truth. `s3://{BUCKET}/{KEY}` 또는 로컬 파일 경로",
                                      default=None)

    # 하이퍼파라미터
    model: str = Field(description="model path", default="initial")
    strategy: str = Field(description="strategy", default=str(Strategy.MANY_TO_MANY))
    threshold: Optional[float] = Field(description="threshold", default=None)

    # S3/MinIO 관련 파라미터 (모두 Optional로 설정)
    endpoint_url: Optional[str] = Field(description="S3/MinIO endpoint url", default=None)
    access_key: Optional[str] = Field(description="access key", default=None)
    secret_key: Optional[str] = Field(description="secret key", default=None)
    region_name: Optional[str] = Field(description="region name", default=None)


class DatasetMatchingRequestModel(BaseModel):
    dataset: str = Field(description="dataset path")
    model: str = Field(description="model path", default="initial")
    strategy: str = Field(description="strategy", default=str(Strategy.MANY_TO_MANY))
    threshold: Optional[float] = Field(description="threshold", default=None)


class DummyCorrelation(BaseModel):
    response: bool | str | dict[str, str] | dict[str, float]


class SchemaMatchingResponseModel(APIResponseModel):
    message: str = Field(default=f"스키마 매칭 응답 성공 ({VERSION})")
