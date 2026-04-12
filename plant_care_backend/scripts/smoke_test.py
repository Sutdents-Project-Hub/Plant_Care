import os
import sys
from pathlib import Path
from datetime import date

os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL") or "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = os.environ.get("JWT_SECRET") or "smoke-secret"
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY") or ""
os.environ["OPENAI_BASE_URL"] = os.environ.get("OPENAI_BASE_URL") or "https://free.v36.cm"
os.environ["OPENAI_MODEL"] = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
os.environ["APP_NAME"] = os.environ.get("APP_NAME") or "Plant Care"
os.environ["EMAIL_BACKEND"] = os.environ.get("EMAIL_BACKEND") or "disabled"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.main import app
from app.models import Announcement, Base, RefreshToken, User


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

    r = client.post("/api/v1/auth/me", headers=headers, json={})
    _assert(r, 200)

    new_email = "smoke2@example.com"
    r = client.post(
        "/api/v1/auth/update_profile",
        headers=headers,
        json={
            "name": "Smoke2",
            "email": new_email,
            "phone": "111",
            "birthday": "19910101",
        },
    )
    _assert(r, 200)
    email = new_email

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
            "locale": "en-US",
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

    new_password = "password5678"
    r = client.post(
        "/api/v1/auth/change_password",
        headers=headers,
        json={"old_password": password, "new_password": new_password},
    )
    _assert(r, 200)
    access_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.post("/api/v1/auth/me", headers=headers, json={})
    _assert(r, 200)

    email2 = "smoke_reset@example.com"
    password2 = "password1234"
    r = client.post(
        "/api/v1/auth/register",
        json={
            "name": "SmokeReset",
            "email": email2,
            "password": password2,
            "phone": "000",
            "birthday": "19900101",
        },
    )
    _assert(r, 200)
    r = client.post("/api/v1/auth/login", json={"email": email2, "password": password2})
    _assert(r, 200)
    with SessionLocal() as db:
        user2 = db.scalar(select(User).where(User.email == email2))
        if user2 is None:
            raise RuntimeError("Expected user2")
        old_hash = user2.password_hash
        if old_hash is None:
            raise RuntimeError("Expected password_hash")

    r = client.post("/api/v1/auth/found_psw", json={"email": email2})
    _assert(r, 200)
    with SessionLocal() as db:
        user2 = db.scalar(select(User).where(User.email == email2))
        if user2 is None:
            raise RuntimeError("Expected user2")
        if user2.must_change_password is not True:
            raise RuntimeError("Expected must_change_password true")
        if user2.password_hash == old_hash:
            raise RuntimeError("Expected password_hash changed")
        tokens2 = db.scalars(select(RefreshToken).where(RefreshToken.user_id == user2.id)).all()
        if tokens2:
            raise RuntimeError("Expected refresh tokens revoked")

    r = client.post(
        "/api/v1/auth/delete_account",
        headers=headers,
        json={"password": new_password},
    )
    _assert(r, 200)

    print("SMOKE_OK")


if __name__ == "__main__":
    main()
