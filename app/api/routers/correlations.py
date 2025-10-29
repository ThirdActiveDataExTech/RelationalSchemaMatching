"""
PUT, POST, GET 에 대한 다양한 API 예시를 작성해놨으니 참고해서 개발을 진행한다.
되도록이면 Swagger에서 API를 쉽게 파악하기 위해 API 및 Body, Path, Query에 대한 설명을 작성한다.
"""

import os
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.schemas.correlations import SchemaMatchingResponseModel
from app.src.correlations.endpoints import run
from app.src.correlations.enums import MatchingModel, Strategy, TestDataset

router = APIRouter(
    prefix="/correlations",
    tags=["correlations"],
    dependencies=[Depends(get_token_header)],
)


# Swagger에서 API를 쉽게 파악하기 위해 API 및 parameter에 대한 Query 설명 달기
@router.post("/", response_model=SchemaMatchingResponseModel, response_class=JSONResponse)
async def schema_matching(
    l_table: Annotated[str, Form(description="`s3://{BUCKET}/{KEY}` 또는 로컬 파일 경로")],
    r_table: Annotated[str, Form(description="`s3://{BUCKET}/{KEY}` 또는 로컬 파일 경로")],
    truth_json: Annotated[Optional[str], Form(description="Ground Truth JSON 파일 경로")] = None,
    model: Annotated[MatchingModel, Form(description="model path")] = MatchingModel.INITIAL,
    strategy: Annotated[Strategy, Form(description="strategy")] = Strategy.MANY_TO_MANY,
    threshold: Annotated[Optional[float], Form(description="threshold (0.0-1.0)", ge=0.0, le=1.0)] = None,
    endpoint_url: Annotated[Optional[str], Form(description="S3/MinIO endpoint url")] = None,
    access_key: Annotated[Optional[str], Form(description="access key")] = None,
    secret_key: Annotated[Optional[str], Form(description="secret key")] = None,
    region_name: Annotated[Optional[str], Form(description="region name")] = None,
):
    response = run(
        l_table_path=l_table,
        r_table_path=r_table,
        truth_json=truth_json,
        model=model,
        strategy=strategy,
        threshold=threshold,
        endpoint_url=endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        region_name=region_name,
    )

    return SchemaMatchingResponseModel(result=response, description="스키마 매칭 성공")


@router.post("/dataset", response_model=SchemaMatchingResponseModel, response_class=JSONResponse)
async def dataset_schema_matching(
    dataset: Annotated[TestDataset, Form(description="test dataset path")],
    model: Annotated[MatchingModel, Form(description="model path")] = MatchingModel.INITIAL,
    strategy: Annotated[Strategy, Form(description="strategy")] = Strategy.MANY_TO_MANY,
    threshold: Annotated[Optional[float], Form(description="threshold (0.0-1.0)", ge=0.0, le=1.0)] = None,
    # l_column: Optional[str] = None,
    # r_column: Optional[str] = None
):
    dataset_path = dataset.value

    # 테이블 파일 경로 구성
    l_table = os.path.join(dataset_path, "Table1.csv")
    r_table = os.path.join(dataset_path, "Table2.csv")

    # truth.json 파일 확인
    truth_json_path = os.path.join(dataset_path, "truth.json")
    truth_json = truth_json_path if os.path.exists(truth_json_path) else None

    # 스키마 매칭 실행
    pred_df = run(
        l_table_path=l_table,
        r_table_path=r_table,
        truth_json=truth_json,
        model=model,
        strategy=strategy,
        threshold=threshold,
    )

    return SchemaMatchingResponseModel(result=pred_df, description="스키마 매칭 성공")

# @router.get("/get_result")
# async def get_result(task_id: str, l_column: Optional[str] = None, r_column: Optional[str] = None):
#     task = get_task(uuid.UUID(task_id))
#
#     if task.status != TaskStatus.COMPLETED:
#         return SchemaMatchingResponseModel(result=task, description=task.status)
#
#     result = task.result
#
#     if l_column and r_column:
#         response = pred_df.loc[l_column, r_column]
#         response = {f"{l_column}_{r_column}": str(response)}
#     elif l_column:
#         response = pred_df[l_column].to_dict()
#     elif r_column:
#         response = pred_df.loc[r_column].to_dict()
#     else:
#         response = pred_df.to_dict()
