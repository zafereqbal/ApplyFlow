from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.cache import invalidate_user_dashboard
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, User
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationPage, ApplicationUpdate, Status

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    application = Application(owner_id=user.id, **payload.model_dump(mode="json"))
    db.add(application)
    db.commit()
    db.refresh(application)
    invalidate_user_dashboard(user.id)
    return application


@router.get("", response_model=ApplicationPage)
def list_applications(
    q: str | None = Query(default=None, max_length=160),
    application_status: Status | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="updated_at", pattern="^(updated_at|created_at|company|role)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Application).where(Application.owner_id == user.id)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Application.company.ilike(pattern), Application.role.ilike(pattern)))
    if application_status:
        query = query.where(Application.status == application_status)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    order_column = getattr(Application, sort)
    rows = db.scalars(query.order_by(order_column.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return ApplicationPage(items=rows, total=total, page=page, page_size=page_size)


def owned_application(application_id: int, user_id: int, db: Session) -> Application:
    item = db.scalar(select(Application).where(
        Application.id == application_id, Application.owner_id == user_id
    ))
    if item is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return item


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return owned_application(application_id, user.id, db)


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_application(application_id, user.id, db)
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    invalidate_user_dashboard(user.id)
    return item


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_application(application_id, user.id, db)
    db.delete(item)
    db.commit()
    invalidate_user_dashboard(user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
