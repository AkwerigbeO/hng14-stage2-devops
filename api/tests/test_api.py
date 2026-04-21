import os
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from unittest.mock import patch  # noqa: E402
from api.main import app  # noqa: E402


class FakeRedis:
    def ping(self):
        return True

    def lpush(self, *args, **kwargs):
        return True

    def hset(self, *args, **kwargs):
        return True

    def hget(self, *args, **kwargs):
        return "queued"


client = TestClient(app)


@patch("api.main.r", FakeRedis())
def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("api.main.r", FakeRedis())
def test_create_job():
    response = client.post("/jobs")
    assert response.status_code == 200


@patch("api.main.r", FakeRedis())
def test_get_job():
    response = client.get("/jobs/test-id")
    assert response.status_code in [200, 404]
