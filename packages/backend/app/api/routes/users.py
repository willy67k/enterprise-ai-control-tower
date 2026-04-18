from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.middleware.auth import get_current_user
from app.models.rbac import User
from app.schemas.user import UserListResponse, UserRead
from app.services.db import get_db

router = APIRouter(tags=["users"])


@router.get("/users", response_model=UserListResponse)
def list_users(
    db: Session = Depends(get_db),
    viewer: User = Depends(get_current_user),
) -> UserListResponse:
    """List all users; `viewer` is the authenticated dev user (Depends practice)."""
    stmt = select(User).order_by(User.created_at.asc())
    rows = list(db.execute(stmt).scalars().all())
    return UserListResponse(
        users=[UserRead.model_validate(u) for u in rows],
        viewer=UserRead.model_validate(viewer),
    )


@router.get("/users/me", response_model=UserRead)
def read_me(current: User = Depends(get_current_user)) -> UserRead:
    """Return the resolved current user (same logic as list's viewer)."""
    return UserRead.model_validate(current)
