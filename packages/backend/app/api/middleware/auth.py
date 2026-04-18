"""Dev-only fake auth: shared secret via Bearer or X-API-Token.

Production should replace this with real JWT/OIDC and RBAC checks.
"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.rbac import User
from app.services.db import get_db


def verify_dev_token(
    authorization: str | None = Header(None),
    x_api_token: str | None = Header(None, alias="X-API-Token"),
) -> None:
    """Require `Authorization: Bearer <token>` or `X-API-Token` matching settings."""
    settings = get_settings()
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_token:
        token = x_api_token.strip()
    if not token or token != settings.dev_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


def get_current_user(
    db: Session = Depends(get_db),
    _: None = Depends(verify_dev_token),
    x_dev_user_email: str | None = Header(None, alias="X-Dev-User-Email"),
) -> User:
    """Resolve the acting user after token check.

    If `X-Dev-User-Email` is set, load that user; otherwise use the oldest user row.
    """
    if x_dev_user_email:
        stmt = select(User).where(User.email == x_dev_user_email.strip())
        user = db.execute(stmt).scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user matches X-Dev-User-Email",
            )
        return user

    stmt = select(User).order_by(User.created_at.asc())
    user = db.execute(stmt).scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No users in database; add a row or pass X-Dev-User-Email",
        )
    return user
