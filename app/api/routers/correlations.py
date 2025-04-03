"""
PUT, POST, GET 에 대한 다양한 API 예시를 작성해놨으니 참고해서 개발을 진행한다.
되도록이면 Swagger에서 API를 쉽게 파악하기 위해 API 및 Body, Path, Query에 대한 설명을 작성한다.
"""
import logging
import os.path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse

from app.dependencies import get_token_header
from app.schemas.correlations import SchemaMatchingResponseModel, SchemaMatchingRequestModel, \
    DatasetMatchingRequestModel, ExternalSchemaMatchingRequestModel
from app.src.correlations.endpoints import run, match_from_test_dataset
from app.src.correlations.enums import MatchingModel, Strategy
from app.src.fetcher.s3 import S3Connector

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


@router.post(
    "/external",
    response_model=SchemaMatchingResponseModel,
    response_class=JSONResponse
)
async def external_schema_matching(
        request_body: Annotated[ExternalSchemaMatchingRequestModel, Body(
            title="상관관계 분석 기반 스키마 매칭",
            description="상관관계 분석 & 스키마 매칭 실행",
            media_type="application/json"
        )]
):
    l_external_table = request_body.l_table
    r_external_table = request_body.r_table

    model = MatchingModel.INITIAL
    strategy = Strategy.MANY_TO_MANY

    # 임시 디렉토리 생성
    tmp_dir = "/tmp/s3_downloads"
    os.makedirs(tmp_dir, exist_ok=True)

    l_path = os.path.join(tmp_dir, "l.csv")
    r_path = os.path.join(tmp_dir, "r.csv")

    try:
        s3_connector = S3Connector(endpoint_url=request_body.endpoint_url, access_key=request_body.access_key,
                                   secret_key=request_body.secret_key, region_name=request_body.region_name)

        if not s3_connector.download_file(bucket_name=request_body.bucket, object_name=l_external_table,
                                          file_path=l_path):
            raise Exception("l_table download failed")

        if not s3_connector.download_file(bucket_name=request_body.bucket, object_name=r_external_table,
                                          file_path=r_path):
            raise Exception("r_table download failed")

        request_body.l_table = l_path
        request_body.r_table = r_path

        return run(l_table=request_body.l_table,
                   r_table=request_body.r_table,
                   result_path=request_body.result_path,
                   truth_json=request_body.truth_json,
                   model=model,
                   strategy=strategy,
                   )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if os.path.exists(l_path):
            os.remove(l_path)
        if os.path.exists(r_path):
            os.remove(r_path)


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
