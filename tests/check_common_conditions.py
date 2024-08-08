from app.config import settings


def check_common_conditions(response):
    assert response.status_code == 200
    response_json = response.json()
    assert list(response_json.keys()) == ["code", "message", "result", "description"]
    assert response_json["code"] == int(f"{settings.SERVICE_CODE}200")
