# Python FastAPI Template

[![Python Version](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/fastapi-0.114.1-yellowgreen)](https://fastapi.tiangolo.com/release-notes/#01110)
[![Loguru Version](https://img.shields.io/badge/loguru-0.7.2-orange)](https://loguru.readthedocs.io/en/stable/project/changelog.html)
[![Gunicorn Version](https://img.shields.io/badge/gunicorn-23.0.0-red)](https://gunicorn.readthedocs.io/en/stable/project/changelog.html)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pre-commit/pre-commit/main.svg)](https://results.pre-commit.ci/latest/github/pre-commit/pre-commit/main)
[![Coverage](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/coverage.svg?job=coverage)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/-/graphs/main/charts)
[![Pipeline Status](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/pipeline.svg)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/commits/main)

> <b>Sentence Transformer와 XGBoost 기반의 스키마 매칭</b>
> 테이블을 문장 기반으로 임베딩하고 feature를 추출합니다.
> 추출된 feature와 사전 훈련된 XGBoost를 사용하여, 두 테이블 간 어떤 컬럼이 가장 유사한지 계산합니다.

### Requirements

- [Python](https://www.python.org/) `3.10`
- [Poetry](https://python-poetry.org/) `>= 1.4`
- [FastAPI Web Framework](https://fastapi.tiangolo.com/ko/)

### 1. Install Requirements

```bash
$ apt-get install -y python310 && python3 --version && pip3 --version
$ pip3 isntall -U poetry
```

### 2. Install Dependencies

```bash
$ poetry install --no-root
```

### 3. Run app

[방법 1] 가상환경 자동 진입

```bash
$ poetry run uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

[방법 2] 가상환경 직접 진입

```bash
# 가상환경 활성화 후 FastAPI uvicorn 실행
$ poetry shell
(python-fastapi-template-py3.9) $ uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

## Quick start with Docker

```bash
$ docker build -t python-fastapi-template:dev -f dev.Dockerfile .
$ docker run -d --rm --name python-fastapi-template -p 8000:8000 -e X_TOKEN=wisenut python-fastapi-template:dev
```

### 4. Schema Matching

[방법 1] 웹페이지에서 진행

- 자체 제공되는 [swagger 페이지](http://localhost:8000/docs) 확인

[방법 2] CLI 에서 진행

1. 전체 확률 테이블

```shell
curl -X 'GET' \
  'http://localhost:8000/correlations/dataset' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

2. 왼쪽 테이블 특정 컬럼 확률 테이블

```shell
curl -X 'GET' \
  'http://localhost:8000/correlations/dataset?l_column=Cast' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

3. 오른쪽 테이블 특정 컬럼 확률 테이블

```shell
curl -X 'GET' \
  'http://localhost:8000/correlations/dataset?r_column=Country' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```

4. 양 테이블 특정 컬럼 확률

```shell
curl -X 'GET' \
  'http://localhost:8000/correlations/dataset?l_column=RatingCount&r_column=RatingValue' \
  -H 'accept: application/json' \
  -H 'x-token: wisenut' \
  -H 'Content-Type: application/json' \
  -d '{
  "dataset": "./test_data/movies1/"
}'
```