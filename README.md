# Python FastAPI Template

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/fastapi-0.114.1-yellowgreen)](https://fastapi.tiangolo.com/release-notes/#01110)
[![Loguru Version](https://img.shields.io/badge/loguru-0.7.2-orange)](https://loguru.readthedocs.io/en/stable/project/changelog.html)
[![Gunicorn Version](https://img.shields.io/badge/gunicorn-23.0.0-red)](https://gunicorn.readthedocs.io/en/stable/project/changelog.html)
[![Coverage](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/coverage.svg?job=coverage)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/-/graphs/main/charts)
[![Pipeline Status](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/badges/main/pipeline.svg)](https://gitlab.com/wisenut-research/lab/starter/python-fastapi-template/commits/main)

> **빠르고 쉽게 파이썬 기반의 HTTP API 웹 서버를 개발하기 위한 템플릿**  
> (API 명세는 와이즈넛 [Restful API 디자인 가이드](https://docs.google.com/document/d/1tSniwfrVaTIaTT4MxhBRAmv-S_ECcoSFAXlYrsg4K0Y/edit#heading=h.60fu2rc04bck)를 따른다)

<hr>

> **Documentation** : https://labs.wisenut.kr/clusters/local/namespaces/mkdocs/services/pft-mkdocs/public/latest/

<hr>

Python FastAPI Template 은 아래와 같은 특징을 갖고 있다.

1. **Python 3.9, 3.10, 3.11, 3.12**: 높은 호환성
2. **MSA 환경을 고려한 Cloud Native Application 설계**: [THE TWELVE-FACTOR APP](https://12factor.net/)
3. **간편한 Logging 설정**: [loguru](https://github.com/Delgan/loguru)
4. **최신 의존성 관리 툴 Poetry**: `pyproject.toml`으로 한 번에 관리
5. **App Properties Management**: 환경 변수를 통한 전체적인 프로젝트 변수를 간단하게 관리 ([.env](./.env))
6. **Containerizing with Gitlab CI**:
    - (Cloud Environment) 배포에 사용할 `Dockerfile`
    - (Non-Cloud environment) 분산 처리를 위한 Gunicorn 프리셋 구성을 위한 `gunicorn.Dockerfile`
    - 로컬에서 빠른 개발 환경 구동을 위한 `dev.Dockerfile`
7. **Gunicorn**: multi process 환경 구성
8. **파이썬 앱 개발부터 배포까지 필요한 GitOps와 문서 템플릿 제공**: secret detection, lint test(ruff, pyright, hadolint), unit test(pytest, SAST), deploy, container scanning

### Requirements

- [Python](https://www.python.org/) `>=3.9,<=3.12`
- [Poetry](https://python-poetry.org/) `>= 1.4`
- [FastAPI Web Framework](https://fastapi.tiangolo.com/ko/)

## Quick start

![quick start guide gif](static/guide/quick-start-guide.gif "quick start guide gif")

### 0. Create Project from template

> 빠른 프로젝트 생성을 위한 GitLab Template 사용법
> 

   1. GitLab `Create new project` 을 통해 새로운 프로젝트 생성
   2. `Create from template` 선택    
      <img src="static/guide/create-from-template.png" alt="create from template png" width="800" />
   3. `Group` 선택
   4. **FastAPI**에서 `Use template` 선택    
      <img src="static/guide/fastapi-use-template.png" alt="fastapi use template png" width="800" />
   5. _Project name, Project description (optional)_ 등을 작성하고 `Create project` 선택

> 🔴 **GitLab CI/CD Container Registry Deploy**를 위해 프로젝트 생성시 무조건 `Settings > Repository > Deploy tokens`에 **gitlab-deploy-token** 이름으로 `read_registry, write_registry` Scope 선택해서 토큰 생성하기
> 

### 1. Install Requirements

```bash
$ apt-get install -y python39 && python3 --version && pip3 --version
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

---

## Project Description

> 프로젝트 생성, 환경 세팅, 실행방법, 앱 구조, GitLab CI/CD 파이프라인, Gunicorn 및 내부망 환경에 대해  
> 더 자세히 알고싶으면 [PFT 문서](https://labs.wisenut.kr/clusters/local/namespaces/mkdocs/services/pft-mkdocs/public/latest/)를 확인하세요.
