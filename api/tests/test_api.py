import os
os.environ["TESTING"] = "1"

from unittest.mock import patch, MagicMock  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from api.main import app  # noqa: E402


class FakeRedis:
    """Mock Redis client for unit testing."""
    def ping(self):
        return True

    def lpush(self, *args, **kwargs):
        return 1

    def hset(self, *args, **kwargs):
        return 1

    def hget(self, *args, **kwargs):
        return "queued"


client = TestClient(app)


@patch("api.main.r", FakeRedis())
def test_health_endpoint():
    """Test that /health returns 200 with healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch("api.main.r", FakeRedis())
def test_create_job():
    """Test that POST /jobs returns 200 with a job_id."""
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


@patch("api.main.r", FakeRedis())
def test_get_job_status():
    """Test that GET /jobs/:id returns the mocked status."""
    response = client.get("/jobs/fake-job-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["job_id"] == "fake-job-id"


@patch("api.main.r", FakeRedis())
def test_get_job_not_found():
    """Test that GET /jobs/:id returns 404 when job doesn't exist."""
    fake = FakeRedis()
    fake.hget = MagicMock(return_value=None)
    with patch("api.main.r", fake):
        response = client.get("/jobs/nonexistent-id")
        assert response.status_code == 404


@patch("api.main.r", FakeRedis())
def test_health_redis_failure():
    """Test that /health returns 503 when Redis is down."""
    import redis as redis_lib
    broken = FakeRedis()
    broken.ping = MagicMock(side_effect=redis_lib.RedisError("down"))
    with patch("api.main.r", broken):
        response = client.get("/health")
        assert response.status_code == 503
