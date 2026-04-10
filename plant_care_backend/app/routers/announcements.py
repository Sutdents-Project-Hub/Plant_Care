from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Announcement
from app.schemas import AnnouncementItem, AnnouncementListResponse

router = APIRouter()


@router.post("/search_announcements", response_model=AnnouncementListResponse)
def search_announcements(_: dict, db: Session = Depends(get_db)) -> AnnouncementListResponse:
    rows = db.scalars(select(Announcement).order_by(Announcement.date.desc())).all()
    return AnnouncementListResponse(
        results=[
            AnnouncementItem(title=a.title, date=a.date.strftime("%Y-%m-%d"), content=a.content) for a in rows
        ]
    )
