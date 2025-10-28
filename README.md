# 인공지능 기반 데이터 상호 연관성 분석 모듈 프로토타입 v1

[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/fastapi-0.114.1-yellowgreen)](https://fastapi.tiangolo.com/release-notes/#01110)
[![Loguru Version](https://img.shields.io/badge/loguru-0.7.2-orange)](https://loguru.readthedocs.io/en/stable/project/changelog.html)
[![Gunicorn Version](https://img.shields.io/badge/gunicorn-23.0.0-red)](https://gunicorn.readthedocs.io/en/stable/project/changelog.html)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pre-commit/pre-commit/main.svg)](https://results.pre-commit.ci/latest/github/pre-commit/pre-commit/main)
[![Coverage](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/coverage.svg?job=coverage)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/-/graphs/main/charts)
[![Pipeline Status](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/pipeline.svg)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/commits/main)

인공지능 기술 기반으로의 관계형 데이터 간 상호 연관성 분석 & 유사 속성 탐지를 통해 최종적으로 유사 컬럼을 추천하는 모듈 

- Column2Column Correlation Analysis
  - transformer 기반 텍스트 임베딩 
  - xgboost 기반 스키마 분류 예측

## 사용 방법

### 1. Install Requirements

- [Python](https://www.python.org/) `3.11`
- [uv](https://docs.astral.sh/uv/) `>= 0.9`
- [FastAPI Web Framework](https://fastapi.tiangolo.com/ko/)

#### uv 설치

```bash
# macOS 및 Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 의존성 설치

다음 중 하나를 선택하여 설치:

```bash
# CUDA 의존성 (권장, amd64/arm64 호환)
$ uv sync --extra cu124

# CPU 의존성만 (amd64 호환)
$ uv sync --extra cpu
```

### 2. Run app (HTTP API Server)

다음 중 하나를 선택하여 실행:

```bash
# uv를 통한 직접 실행 (권장)
$ uv run uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

```bash
# 가상환경 수동 활성화 후 실행
$ source ./.venv/bin/activate
(correlation-analysis) $ uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

### 3. Run Analysis

> api-docs 확인 : [swagger-ui](http://localhost:8000/docs), [redoc](http://localhost:8000/redoc), 


#### 1. 성능지표 테스트 "4. 관계형 데이터 유사 속성 탐지율" 

1. 테스트 데이터 분석 요청

```bash
curl -X 'POST' \
  'http://localhost:8000/correlations/dataset' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

2. 유사 속성 탐지율 매트릭 출력 결과 확인

```json
{
  "code": 100200,
  "message": "스키마 매칭 응답 성공 (v1.2411.22-dev-abc3f68)",
  "result": {
    "matches": [
      {
        "source_column": "Table1.Name",
        "target_column": "Table2.Name",
        "correlation_coefficient": 0.9995723962783813
      },
      {
        "source_column": "Table1.Year",
        "target_column": "Table2.YearRange",
        "correlation_coefficient": 0.9575390219688416
      },
    ],
    "column_classifications": {
      "source": {
        "Table1.Name": "STRING",
        "Table1.Year": "STRICT_NUMERIC",
      },
      "target": {
        "Table2.Name": "STRING",
        "Table2.YearRange": "MAINLY_NUMERIC",
      }
    },
    "evaluation": {
      "ground_truth_pairs": [
        [
          "Name",
          "Name"
        ],
        [
          "Year",
          "YearRange"
        ]
      ],
      "metrics": {
        "precision": 0.2857142857142857,
        "recall": 1,
        "f1": 0.4444444444444444,
        "total_pairs": 14,
        "true_positive_count": 4,
        "false_positive_count": 10
      }
    }
  },
  "description": "스키마 매칭 성공"
}
```


#### 2. 상호 연관성 분석 모듈 프로토타입 기능 사용

1. 전체 확률 테이블

```bash
curl -X 'POST' \
  'http://localhost:8000/correlations/dataset' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

2. 왼쪽 테이블 특정 컬럼 확률 테이블

```bash
curl -X 'POST' \
  'http://localhost:8000/correlations/dataset?l_column=Cast' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

3. 오른쪽 테이블 특정 컬럼 확률 테이블

```bash
curl -X 'POST' \
  'http://localhost:8000/correlations/dataset?r_column=Country' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

4. 양 테이블 특정 컬럼 확률

```bash
curl -X 'POST' \
  'http://localhost:8000/correlations/dataset?l_column=RatingCount&r_column=RatingValue' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```