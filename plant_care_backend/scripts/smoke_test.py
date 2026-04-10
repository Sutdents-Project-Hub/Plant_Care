import os
import sys
from pathlib import Path
from datetime import date

os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL") or "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = os.environ.get("JWT_SECRET") or "smoke-secret"
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY") or ""
os.environ["OPENAI_BASE_URL"] = os.environ.get("OPENAI_BASE_URL") or "https://free.v36.cm"
os.environ["OPENAI_MODEL"] = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.database import SessionLocal, engine
from app.main import app
from app.models import Announcement, Base


def _assert(res, status: int) -> None:
    if res.status_code != status:
        raise RuntimeError(f"Expected {status}, got {res.status_code}: {res.text}")


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add(
            Announcement(
                title="Smoke Announcement",
                date=date(2026, 1, 1),
                content="Hello",
            )
        )
        db.commit()

    client = TestClient(app)

    r = client.get("/health")
    _assert(r, 200)

    email = "smoke@example.com"
    password = "password1234"

    r = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Smoke",
            "email": email,
            "password": password,
            "phone": "000",
            "birthday": "19900101",
        },
    )
    _assert(r, 200)

    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    _assert(r, 200)
    tokens = r.json()["tokens"]
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    _assert(r, 200)

    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post(
        "/api/v1/plant/create_plant",
        headers=headers,
        json={
            "plant_variety": "Monstera",
            "plant_name": "M1",
            "plant_state": "growing",
            "setup_time": "20260101",
            "email": email,
        },
    )
    _assert(r, 200)

    r = client.post("/api/v1/plant/get_plant_info", headers=headers, json={"email": email})
    _assert(r, 200)
    plants = r.json()["results"]
    if not plants:
        raise RuntimeError("Expected at least 1 plant")
    uuid = plants[0]["uuid"]

    r = client.post(
        "/api/v1/plant/initialize_plant",
        headers=headers,
        json={
            "uuid": uuid,
            "email": email,
            "today_state": "ok",
            "last_watering_time": "20260101000000",
        },
    )
    _assert(r, 200)

    r = client.post(
        "/api/v1/ai/generate_tasks",
        headers=headers,
        json={
            "plant_variety": "Monstera",
            "plant_state": "growing",
            "count": 3,
            "locale": "zh-TW",
        },
    )
    _assert(r, 200)
    tasks = r.json()["tasks"]
    if not isinstance(tasks, dict) or not tasks:
        raise RuntimeError("Expected tasks")

    r = client.post(
        "/api/v1/plant/update_plant_task",
        headers=headers,
        json={"uuid": uuid, "email": email, "task": tasks},
    )
    _assert(r, 200)

    r = client.post("/api/v1/homepage/search_announcements", json={})
    _assert(r, 200)
    anns = r.json()["results"]
    if not anns:
        raise RuntimeError("Expected announcements")

    print("SMOKE_OK")


if __name__ == "__main__":
    main()
