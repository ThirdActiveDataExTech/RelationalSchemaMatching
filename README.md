# 인공지능 기반 데이터 상호 연관성 분석 모듈 프로토타입 v1

[![Python Version](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/)
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

- [Python](https://www.python.org/) `3.10`
- [Poetry](https://python-poetry.org/) `>= 1.4`
- [FastAPI Web Framework](https://fastapi.tiangolo.com/ko/)

```bash
$ pip3 isntall -U poetry
$ poetry install --no-root
```

### 2. Run app (HTTP API Server)

```bash
# [방법 1] 가상환경 사용 구동
$ poetry run uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

```bash
# [방법 2] 가상환경 활성화 & 구동
$ poetry shell
(python-fastapi-template-py3.10) $ uvicorn app.main:app --host 0.0.0.0 --port <port number>
```

### 3. Run Analysis

> api-docs 확인 : [swagger-ui](http://localhost:8000/docs), [redoc](http://localhost:8000/redoc), 


#### 1. 성능지표 테스트 "4. 관계형 데이터 유사 속성 탐지율" 

1. 테스트 데이터 분석 요청

    ```bash
    curl -X 'GET' \
      'http://localhost:8000/correlations/dataset' \
      -H 'accept: application/json' \
      -H 'x-token: wisenut' \
      -H 'Content-Type: application/json' \
      -d '{
      "dataset": "./test_data/movies1/"
    }'

    {"code":100200,"message":"스키마 매칭 응답 성공 (v1.2411.22-dev-abc3f68)","result":{"Id":{"Id":0.8217380046844482,"Name":0.05394599959254265,"Year":5.208406219026074e-05,"Release Date":0.0009153647115454078,"Director":0.0010792695684358478,"Creator":0.0009771406184881926,"Actors":0.0006888013449497521,"Cast":0.001676862477324903,"Language":0.0029903335962444544,"Country":0.0007220573606900871,"Duration":0.0002537824329920113,"RatingValue":9.103531920118257e-05,"RatingCount":0.0003362825373187661,"ReviewCount":0.0007847846136428416,"Genre":0.0018691543955355883,"Filming Locations":0.00290671456605196,"Description":0.0007282430306077003},"Name":{"Id":3.052955071325414e-05,"Name":0.9995723962783813,"Year":0.00019361772865522653,"Release Date":0.0013657029485329986,"Director":0.01127122063189745,"Creator":0.0014008446596562862,"Actors":0.00046347887837328017,"Cast":0.0014896171633154154,"Language":0.04516031593084335,"Country":0.0016668530879542232,"Duration":0.00018028056365437806,"RatingValue":0.0001518118951935321,"RatingCount":4.1030303691513836e-05,"ReviewCount":0.0008090435294434428,"Genre":0.007330780848860741,"Filming Locations":0.0018509943038225174,"Description":0.005690664052963257},"YearRange":{"Id":0.00436922162771225,"Name":0.00013897029566578567,"Year":0.9575390219688416,"Release Date":0.002025420544669032,"Director":0.0001938093191711232,"Creator":0.00020572073117364198,"Actors":7.017397729214281e-05,"Cast":5.153236634214409e-05,"Language":0.0001962737151188776,"Country":6.553788989549503e-05,"Duration":0.0013039689511060715,"RatingValue":0.012615401297807693,"RatingCount":0.0014080038527026772,"ReviewCount":0.00012808406609110534,"Genre":0.0002783218224067241,"Filming Locations":4.682549479184672e-05,"Description":5.9823716583196074e-05},"ReleaseDate":{"Id":4.3988748075207695e-05,"Name":0.0004804563941434026,"Year":0.00021084152103867382,"Release Date":0.5725968480110168,"Director":0.0006420650752261281,"Creator":0.0004223614523652941,"Actors":0.001404475886374712,"Cast":0.0014670686796307564,"Language":0.0006065178895369172,"Country":0.00016763694293331355,"Duration":0.03231149539351463,"RatingValue":0.00027057394618168473,"RatingCount":0.000584071094635874,"ReviewCount":0.1346752941608429,"Genre":0.0007916839676909149,"Filming Locations":0.0005418405053205788,"Description":0.00039876921800896525},"Director":{"Id":3.9240465412149206e-05,"Name":0.06240612640976906,"Year":0.0002112807851517573,"Release Date":0.0018261353252455592,"Director":0.9975708723068237,"Creator":0.6231250762939453,"Actors":0.04575466364622116,"Cast":0.006434077396988869,"Language":0.006229545921087265,"Country":0.0009941181633621454,"Duration":0.0002946749737020582,"RatingValue":8.297011663671583e-05,"RatingCount":9.834404045250267e-05,"ReviewCount":0.0011805781396105886,"Genre":0.003395728999748826,"Filming Locations":0.018577180802822113,"Description":0.012166243977844715},"Creator":{"Id":2.987227708217688e-05,"Name":0.09675154834985733,"Year":0.00028169501456432045,"Release Date":0.0039877016097307205,"Director":0.5258767008781433,"Creator":0.9997254610061646,"Actors":0.40491783618927,"Cast":0.02289573848247528,"Language":0.0104746725410223,"Country":0.009291469119489193,"Duration":0.0004893921432085335,"RatingValue":0.0001904487726278603,"RatingCount":9.832655632635579e-05,"ReviewCount":0.0018506946507841349,"Genre":0.005008992273360491,"Filming Locations":0.03865917772054672,"Description":0.009103789925575256},"Cast":{"Id":3.885919431922957e-05,"Name":0.0002939875703305006,"Year":0.00014920960529707372,"Release Date":0.0005800784565508366,"Director":0.00016739920829422772,"Creator":0.0003865573962684721,"Actors":0.02031378634274006,"Cast":0.9942446947097778,"Language":0.00012836283713113517,"Country":0.0001852402783697471,"Duration":0.0006317819934338331,"RatingValue":6.85519989929162e-05,"RatingCount":5.55861224711407e-05,"ReviewCount":0.0008515659137628973,"Genre":0.00018988325609825552,"Filming Locations":0.00030214383150450885,"Description":0.0023800204508006573},"Duration":{"Id":4.493341839406639e-05,"Name":0.0005943386349827051,"Year":0.0006364150322042406,"Release Date":0.008478881791234016,"Director":0.000879356695804745,"Creator":0.0004061192739754915,"Actors":0.0006966687506064773,"Cast":0.0006125947111286223,"Language":0.001383365597575903,"Country":0.00020104717987123877,"Duration":0.9863700270652771,"RatingValue":0.0040615033358335495,"RatingCount":0.0037582237273454666,"ReviewCount":0.039543889462947845,"Genre":0.0006751996115781367,"Filming Locations":0.0013078019255772233,"Description":0.0015837489627301693},"RatingValue":{"Id":0.00010135788033949211,"Name":0.0004052616422995925,"Year":0.0035882932133972645,"Release Date":0.0038791634142398834,"Director":0.0014018263900652528,"Creator":0.0015344171551987529,"Actors":0.00014429038856178522,"Cast":0.00017407501582056284,"Language":0.0005342532531358302,"Country":0.00012653683370444924,"Duration":0.02818167395889759,"RatingValue":0.909328281879425,"RatingCount":0.19704677164554596,"ReviewCount":0.09248288720846176,"Genre":0.0024344490375369787,"Filming Locations":0.000604783243034035,"Description":0.00074330426286906},"ContentRating":{"Id":2.9034988983767107e-05,"Name":0.04955875501036644,"Year":0.00012547709047794342,"Release Date":0.001171987853012979,"Director":0.002491129795089364,"Creator":0.002334138611331582,"Actors":0.002349401358515024,"Cast":0.0010756533592939377,"Language":0.027920782566070557,"Country":0.0006972092087380588,"Duration":0.0010913158766925335,"RatingValue":0.0017777500906959176,"RatingCount":0.0005571244983002543,"ReviewCount":0.000650404195766896,"Genre":0.0013202255358919501,"Filming Locations":0.01227619033306837,"Description":0.002353101037442684},"Genre":{"Id":3.417932748561725e-05,"Name":0.0139625184237957,"Year":0.0002900729305110872,"Release Date":0.00035055886837653816,"Director":0.005078299902379513,"Creator":0.03283953294157982,"Actors":0.0061468444764614105,"Cast":0.0017146384343504906,"Language":0.0102308988571167,"Country":0.02742442488670349,"Duration":0.00014344938972499222,"RatingValue":9.230187424691394e-05,"RatingCount":3.9787661080481485e-05,"ReviewCount":0.0003921401221305132,"Genre":0.9974920749664307,"Filming Locations":0.0028245842549949884,"Description":0.005605107173323631},"Url":{"Id":4.0422753954771906e-05,"Name":0.0007140616653487086,"Year":0.0004124702827539295,"Release Date":0.00038722832687199116,"Director":0.0008657780126668513,"Creator":0.0007469399715773761,"Actors":0.0008562869625166059,"Cast":0.000794732419308275,"Language":0.0002661400940269232,"Country":0.0013921348145231605,"Duration":0.0006780354888178408,"RatingValue":0.0002786901604849845,"RatingCount":4.553767939796671e-05,"ReviewCount":0.00019343645544722676,"Genre":0.00044842701754532754,"Filming Locations":0.0007738674175925553,"Description":0.0008254130370914936},"Description":{"Id":3.152578210574575e-05,"Name":0.0006519596208818257,"Year":7.278734119608998e-05,"Release Date":0.0018399842083454132,"Director":0.00028465932700783014,"Creator":0.0003795059456024319,"Actors":0.0003392226353753358,"Cast":0.0038062140811234713,"Language":0.0002691796107683331,"Country":0.0003016324480995536,"Duration":0.004470753949135542,"RatingValue":0.0002187520731240511,"RatingCount":0.00013566554116550833,"ReviewCount":0.0006733184563927352,"Genre":0.0001479548664065078,"Filming Locations":0.0004498195194173604,"Description":0.9664610624313354}},"description":"스키마 매칭 성 공"}

    ```

2. 유사 속성 탐지율 매트릭 출력 결과 확인 


    ```bash
    TIME_LOGGER: 'schema_matching': 21.4312 seconds
    value.csv saved to ./test_data/movies1/similarity_matrix_value.csv
    label.csv saved to ./test_data/movies1/similarity_matrix_label.csv
    Predicted Pairs:
    ('Id', 'Id', 0.821738)
    ('Name', 'Name', 0.9995724)
    ('Year', 'YearRange', 0.957539)
    ('Release Date', 'ReleaseDate', 0.57259685)
    ('Director', 'Director', 0.9975709)
    ('Director', 'Creator', 0.5258767)
    ('Creator', 'Director', 0.6231251)
    ('Creator', 'Creator', 0.99972546)
    ('Actors', 'Creator', 0.40491784)
    ('Cast', 'Cast', 0.9942447)
    ('Duration', 'Duration', 0.98637)
    ('RatingValue', 'RatingValue', 0.9093283)
    ('RatingCount', 'RatingValue', 0.19704677)
    ('Genre', 'Genre', 0.9974921)
    ('Description', 'Description', 0.96646106)
    Precision: 0.26666666666666666
    Recall: 1.0
    F1 Score: 0.4210526315789474
    24-11-29 14:17:27.868 | INFO     | uvicorn.protocols.http.httptools_impl:send:468 - 19348 31232  127.0.0.1:45133 - "GET /correlations/dataset HTTP/1.1" 200
    ```



#### 2. 상호 연관성 분석 모듈 프로토타입 기능 사용

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