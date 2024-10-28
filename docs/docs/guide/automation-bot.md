# Automation Bot

> Automation bot은 각종 이슈, 에픽, MR 등을 분류하고 관리합니다.   
> 미리 설정한 규칙에 따라 행동하며 사용자의 휴먼 에러를 포착하고, 그에 대한 피드백을 제공합니다.    
> 기본적으로 CI를 통해 활성화하고, 특정 이벤트의 발생이나 미리 설정된 스케줄에 따라 동작합니다.

## GitLab Triage

> Gitlab의 Epics, Issues, MR, Branch 등을 사용자 정의 규칙을 설정을 통해 분류하여, 그룹이나 프로젝트 단위에서 Issue나 MR의 분류를 자동화하는 것을 목표로 합니다.

### Requirements

> 💡 Settings > Access Tokens 발급받기    
> **api** Scope의 최소 **Reporter** 권한을 가진 Access Token을 생성 후, **API_TOKEN** 이름으로 CI/CD 변수를 생성합니다.    
> Access Token의 이름은 생성된 bot의 이름이 됩니다.  

> 💡 발급 받은 Access Token을 `Settings > CI/CD > Variables`에 생성한 토큰명을 설정합니다. (`.gitlab-ci.yml`에 설정된 토큰명)

```yaml
- component: $CI_SERVER_FQDN/components/gitlab-triage/gitlab-triage@0.1.2
    inputs:
      ...
      api_token: $API_TOKEN    # $API_TOKEN bot 실행을 위한 access token 이름
```

### Getting started

1. [gitlab triage project](https://gitlab.com/gitlab-org/ruby/gems/gitlab-triage)를 참고하여 `.triage-policies.yml` 파일에 규칙을 정의하세요. (rules & actions)
2. 필요하다면 ruby module 작성을 통해 사용자 지정 triage 표현식을 사용할 수 있습니다.
    - `.gitlab/triage/` 위치에 모듈 파일을 생성하세요.
    - `.gitlab/helpers.rb` 파일에 해당 모듈을 include 하세요.
3. gitlab ci 파이프라인의 `triage-dry-run` 작업을 통해 의도한대로 triage가 작동하는지 확인하세요. 
4. `Build - pipeline-schedules` 설정을 통해 `triage-run` 작업을 스케줄링 하거나 CI 파이프라인에 포함시켜 사용하세요.


## Danger review (추가 예정)

> MR이 생성되거나 변경사항이 발생하는 경우, 미리 설정한 규칙을 지키지 않은 경우, 이를 comment로 경고합니다.  
> comment는 danger-bot이 동작할 때마다 comment를 추가하지 않고, 수정합니다.

### Requirements

**API** Scope의 최소 **Maintainer** 권한을 가진 Access Token을 생성 후, **DANGER_GITLAB_API_TOKEN** 이름으로 CI/CD 변수를 생성합니다.

> Access Token의 이름은 생성된 bot의 이름이 됩니다.

Danger review 1.4.1 기준 해당 변수는 적용되지 않으므로 **DANGER_GITLAB_API_TOKEN** 이름으로 CI/CD 변수를 생성하세요.

```yaml
- component: gitlab.com/gitlab-org/components/danger-review/danger-review@1.4.1
    inputs:
      gitlab_api_token_variable_name: $DANGER_GITLAB_API_TOKEN
```
