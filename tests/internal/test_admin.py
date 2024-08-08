from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from tests.check_common_conditions import check_common_conditions

client = TestClient(app)


def test_update_admin():
    response = client.post(url="/admin", headers={"x-token": settings.X_TOKEN})
    check_common_conditions(response)
