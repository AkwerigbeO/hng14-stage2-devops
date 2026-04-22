import os
os.environ["TESTING"] = "1"

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

class FakeRedis:
    def ping(self): return True
    def lpush(self, *args, **kwargs): return 1
    def hset(self, *args, **kwargs): return 1
    def hget(self, *args, **kwargs): return "queued"

client = TestClient(app)

@patch("api.main.r", FakeRedis())
def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200

@patch("api.main.r", FakeRedis())
def test_root_create_job():
    response = client.post("/jobs")
    assert response.status_code == 200

@patch("api.main.r", FakeRedis())
def test_root_get_job():
    response = client.get("/jobs/fake-id")
    assert response.status_code == 200
