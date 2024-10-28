> 사용자는 PFT에 포함된 mkdocs CI/CD pipeline을 이용하여 MarkDown으로 작성한 문서를 빌드, 배포할 수 있습니다. 또한, 해당 프로젝트의 API Spec을 명시하는 페이지를 자동으로 생성할 수 있습니다.

## 요구사항

```REPOSITORY_ACCESS_TOKEN``` 이름으로 Access Token을 CI/CD Varialbe로 등록하세요.
> - Personal Access Token 또는 최상단 그룹(wisenut)의 Access Token을 발급받아 사용하세요. -> Admin 권한 X
> - 해당 토큰은 현재 [Admin 권한으로 파이프라인 실행시, git push 과정에서 403반환하는 버그](https://gitlab.com/gitlab-org/gitlab/-/issues/21700) 때문에 **(1)해당 버그를 우회**하기 위해, **(2)다른 프로젝트의 mkdocs ci template을 include**하기 위해 사용합니다. (사용자가 아닌 bot이 파이프라인을 트리거하면, include의 다른 프로젝트에 접근할 수 없는 버그 존재)
> - 버그가 해결된다면 템플릿의 변수 ```REMOTE_REPOSITORY: "https://oauth2:$REPOSITORY_ACCESS_TOKEN@$CI_SERVER_HOST/$CI_PROJECT_PATH.git"``` 대신 predefined variable인 ```CI_REPOSITORY_URL```을 사용하여 Access Token CI/CD Variable을 사용하지 않아도 됩니다.


## Getting started

1. docs/mkdocs.yml 파일 작성 - 문서 구조와 필요한 플러그인을 설정합니다.

2. 작성한 mkdocs.yml 파일에 맞춰 ```docs/``` 위치에 문서(.md) 작성 및 필요한 이미지를 생성합니다.

3. version.txt에 현재 문서의 버전 (최신 버전)을 작성합니다. (ex 0.1, 0.0.2 등 자유롭게)

4. 변경사항을 push 합니다.

5. CI 파이프라인이 동작하면서 작성한 문서를 deploy-pages에 배포합니다.

    > 클러스터에 해당 mkdocs 문서를 배포하기 전, 생성된 mkdocs문서를 확인할 수 있습니다. 
    > 'Settings - Deploy - pages'

6. pipelines에서 manual job인 ```build``` 를 수동으로 실행시켜 해당 문서 이미지를 빌드합니다.

7. 프로젝트 container registry에 등록된 mkdocs 이미지를 최종 배포합니다.


## 주의 사항

- access token 생성
  > - access token 이름에 따라 CI 스크립트에서 GitLab predefined variable 중 하나인 ```$GITLAB_USER_NAME``` 이 동작하지 않는 **버그**가 존재합니다.  
  > - **token 이름에는 특수문자를 지양하세요.** ( '-' 까지는 정상 동작하는 것을 확인)



- ```.dockerignore``` 작성
  > - Application Project의 ```.dockerignore``` 파일에 다음 경로를 포함해선 안됩니다.
  > - ```/docs ```, ```.git```


## Mkdocs CI/CD Pipeline

``` mermaid
graph TD
    B{'/app' 변경사항?} -->|Yes| C[job:get_spec - api.json];
    B --> |No| N1{'/docs' 변경사항?};
    N1 --> |Yes| H[job: test-mkdocs]
    N1 --> |No| K(end pipeline)
    C --> D[job:test_artifact - lint api.json];
    D --> E[job:render_html - docs.html];
    E --> F{'docs.html' 변경사항?};
    F --> |Yes| G[job:deploy_api - push docs.html to project];
    F --> |No| N1;
    G --> H
    H --> I[job: deploy_mkdocs - gitlab pages 배포]
    I --> |Manual| J[job: build_mkdocs - docker build & container registry push]
    J --> K
```
