"""
PUT, POST, GET 에 대한 다양한 API 예시를 작성해놨으니 참고해서 개발을 진행한다.
되도록이면 Swagger에서 API를 쉽게 파악하기 위해 API 및 Body, Path, Query에 대한 설명을 작성한다.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.schemas.correlations import DummyCorrelation, SchemaMatchingResponseModel, SchemaMatchingRequestModel
from app.src.correlations.endpoints import run
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
            title="아이템 업데이트를 위한 아이템명 설정",
            description="아이템 이름, 상태, 재고 입력",
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
    return SchemaMatchingResponseModel(result=DummyCorrelation(response=response), description="스키마 매칭 성공")
