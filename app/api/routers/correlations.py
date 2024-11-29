"""
PUT, POST, GET 에 대한 다양한 API 예시를 작성해놨으니 참고해서 개발을 진행한다.
되도록이면 Swagger에서 API를 쉽게 파악하기 위해 API 및 Body, Path, Query에 대한 설명을 작성한다.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.schemas.correlations import SchemaMatchingResponseModel, SchemaMatchingRequestModel, \
    DatasetMatchingRequestModel
from app.src.correlations.endpoints import run, match_from_test_dataset
from app.src.correlations.enums import MatchingModel, Strategy

router = APIRouter(
    prefix="/correlations",
    tags=["correlations"],
    dependencies=[Depends(get_token_header)],
)


# Swagger에서 API를 쉽게 파악하기 위해 API 및 parameter에 대한 Query 설명 달기
@router.get("/",
            response_model=SchemaMatchingResponseModel,
            response_class=JSONResponse)
async def schema_matching(
        request_body: Annotated[SchemaMatchingRequestModel, Body(
            title="상관관계 분석 기반 스키마 매칭",
            description="상관관계 분석 & 스키마 매칭 실행",
            media_type="application/json"
        )]
):
    l_table = request_body.l_table
    r_table = request_body.r_table

    # TODO: ENUM valueOf
    model = MatchingModel.INITIAL
    strategy = Strategy.MANY_TO_MANY

    result_path = request_body.result_path
    truth_json = request_body.truth_json
    threshold = request_body.threshold
    response = run(l_table, r_table, result_path, truth_json, model, strategy, threshold)
    return SchemaMatchingResponseModel(result=response, description="스키마 매칭 성공")


@router.get("/dataset",
            response_model=SchemaMatchingResponseModel,
            response_class=JSONResponse)
async def dataset_schema_matching(
        request_body: Annotated[DatasetMatchingRequestModel, Body(
            title="상관관계 분석 기반 스키마 매칭 - left,right 컬럼 지정",
            description="상관관계 분석 & 스키마 매칭 실행",
            media_type="application/json"
        )],
        l_column: Optional[str] = None,
        r_column: Optional[str] = None
):
    dataset = request_body.dataset

    pred_df = match_from_test_dataset(dataset)

    if l_column and r_column:
        response = pred_df.loc[l_column, r_column]
        response = {f"{l_column}_{r_column}": str(response)}
    elif l_column:
        response = pred_df[l_column].to_dict()
    elif r_column:
        response = pred_df.loc[r_column].to_dict()
    else:
        response = pred_df.to_dict()

    return SchemaMatchingResponseModel(result=response, description="스키마 매칭 성공")
