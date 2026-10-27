from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.cache import get_json, set_json
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, User
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    key = f"dashboard:{user.id}"
    cached = get_json(key)
    if cached is not None:
        return cached

    rows = db.scalars(select(Application.status).where(Application.owner_id == user.id)).all()
    counts = Counter(rows)
    total = len(rows)
    interview_stages = counts["screening"] + counts["interview"] + counts["offer"]
    result = {
        "total": total,
        "by_status": dict(counts),
        "interview_rate_percent": round((interview_stages / total) * 100, 1) if total else 0.0,
        "offer_count": counts["offer"],
    }
    set_json(key, result, ttl_seconds=60)
    return result
