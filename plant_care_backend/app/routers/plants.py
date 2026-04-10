from __future__ import annotations

import json
import uuid as uuidlib
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models import Plant, User
from app.schemas import (
    ApiMessage,
    PlantCreateRequest,
    PlantInitializeRequest,
    PlantListResponse,
    PlantPublic,
    PlantUpdateTaskRequest,
)
from app.utils.datetime import parse_ymd, parse_ymdhms

router = APIRouter()


def _fmt_ymd(d: date) -> str:
    return d.strftime("%Y%m%d")


def _decode_task(value: Any) -> dict | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        s = value.strip()
        try:
            decoded = json.loads(s)
        except json.JSONDecodeError:
            return None
        if isinstance(decoded, str):
            try:
                decoded = json.loads(decoded)
            except json.JSONDecodeError:
                return None
        return decoded if isinstance(decoded, dict) else None
    return None


def _enforce_email(user: User, email: str | None) -> None:
    if email is not None and email.strip() and email.strip().lower() != user.email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("/get_plant_info", response_model=PlantListResponse)
def get_plant_info(
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlantListResponse:
    _enforce_email(user, payload.get("email"))
    plants = db.scalars(select(Plant).where(Plant.user_id == user.id).order_by(Plant.created_at.desc())).all()
    results = [
        PlantPublic(
            uuid=p.uuid,
            plant_variety=p.plant_variety,
            plant_name=p.plant_name,
            plant_state=p.plant_state,
            setup_time=_fmt_ymd(p.setup_time),
            initialization=_fmt_ymd(p.initialization) if p.initialization else None,
            task=p.task,
        )
        for p in plants
    ]
    return PlantListResponse(results=results)


@router.post("/create_plant", response_model=ApiMessage)
def create_plant(
    payload: PlantCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiMessage:
    _enforce_email(user, str(payload.email) if payload.email else None)
    try:
        setup_time = parse_ymd(payload.setup_time)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid setup_time")

    plant = Plant(
        uuid=str(uuidlib.uuid4()),
        user_id=user.id,
        plant_variety=payload.plant_variety,
        plant_name=payload.plant_name,
        plant_state=payload.plant_state,
        setup_time=setup_time,
    )
    db.add(plant)
    db.commit()
    return ApiMessage(message="Plant created")


@router.post("/initialize_plant", response_model=ApiMessage)
def initialize_plant(
    payload: PlantInitializeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiMessage:
    _enforce_email(user, str(payload.email) if payload.email else None)
    plant = db.scalar(select(Plant).where(Plant.uuid == payload.uuid, Plant.user_id == user.id))
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    plant.initialization = date.today()
    plant.today_state = payload.today_state
    if payload.last_watering_time:
        try:
            plant.last_watering_time = parse_ymdhms(payload.last_watering_time)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid last_watering_time")

    db.commit()
    return ApiMessage(message="Plant initialized")


@router.post("/update_plant_task", response_model=ApiMessage)
def update_plant_task(
    payload: PlantUpdateTaskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiMessage:
    _enforce_email(user, str(payload.email) if payload.email else None)
    plant = db.scalar(select(Plant).where(Plant.uuid == payload.uuid, Plant.user_id == user.id))
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    plant.task = _decode_task(payload.task)
    db.commit()
    return ApiMessage(message="Task updated")
