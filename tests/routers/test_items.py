from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from tests.check_common_conditions import check_common_conditions

client = TestClient(app)


def test_read_items():
    response = client.get("/items", headers={"x-token": settings.X_TOKEN})
    check_common_conditions(response)
    response_json = response.json()
    assert response_json['result']['plumbus']['name'] == 'Plumbus'
    assert response_json['result']['gun']['name'] == 'Portal Gun'


def test_read_item():
    item_id = "gun"
    response = client.get(f"/items/{item_id}", headers={"x-token": settings.X_TOKEN})
    check_common_conditions(response)
    response_json = response.json()
    assert response_json['result']['name'] == 'Portal Gun'
    assert response_json['result']['item_id'] == item_id


def test_update_item():
    item_id = "plumbus"
    response = client.put(f"/items/{item_id}", headers={"x-token": settings.X_TOKEN})
    check_common_conditions(response)
    response_json = response.json()
    assert response_json['result']['name'] == 'The great Plumbus'
    assert response_json['result']['item_id'] == item_id


def test_create_item():
    item = {
        "name": "apple",
        "status": "in stock",
        "stock": 10
    }
    response = client.post(url="/items", headers={"x-token": settings.X_TOKEN},
                           json=item)
    check_common_conditions(response)
    response_json = response.json()
    assert response_json["result"]["item"]["name"] == item["name"]
    assert response_json["result"]["item"]["status"] == item["status"]
    assert response_json["result"]["item"]["stock"] == item["stock"]
