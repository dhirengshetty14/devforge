from fastapi.testclient import TestClient

from app.main import app


def test_health_ok(monkeypatch):
    async def _db_ok():
        return True

    async def _redis_ok():
        return True

    monkeypatch.setattr("app.main.check_database_health", _db_ok)
    monkeypatch.setattr("app.main.check_redis_health", _redis_ok)

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["db"] is True
        assert payload["redis"] is True


def test_ready_degraded(monkeypatch):
    async def _db_bad():
        return False

    async def _redis_ok():
        return True

    monkeypatch.setattr("app.main.check_database_health", _db_bad)
    monkeypatch.setattr("app.main.check_redis_health", _redis_ok)

    with TestClient(app) as client:
        response = client.get("/health/ready")
        assert response.status_code == 503
        payload = response.json()
        assert payload["ready"] is False
        assert payload["db"] is False
