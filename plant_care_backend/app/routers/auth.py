from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.deps import get_current_user
from app.models import Plant, RefreshToken, User
from app.schemas import (
    ApiMessage,
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthResponse,
    ChangePasswordRequest,
    DeleteAccountRequest,
    TokenPair,
    TokenRefreshRequest,
    UserUpdateRequest,
    UserPublic,
)
from app.utils.datetime import parse_ymd

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: AuthRegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == str(payload.email)))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    birthday = None
    if payload.birthday:
        try:
            birthday = parse_ymd(payload.birthday)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid birthday")

    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        birthday=birthday,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, access_expires_at = create_access_token(user_id=user.id)
    refresh_token, jti, refresh_expires_at = create_refresh_token(user_id=user.id)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
        )
    )
    db.commit()

    return AuthResponse(
        user=UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
            points=user.points,
            phone=user.phone,
            birthday=user.birthday,
        ),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthLoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token, access_expires_at = create_access_token(user_id=user.id)
    refresh_token, jti, refresh_expires_at = create_refresh_token(user_id=user.id)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
        )
    )
    db.commit()

    return AuthResponse(
        user=UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
            points=user.points,
            phone=user.phone,
            birthday=user.birthday,
        ),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
        ),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: TokenRefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    sub = decoded.get("sub")
    jti = decoded.get("jti")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if not isinstance(jti, str) or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_row = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.user_id == user_id))
    if token_row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if token_row.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    expires_at = token_row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(tz=UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired refresh token")
    if token_row.token_hash != hash_refresh_token(payload.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_row.revoked_at = datetime.now(tz=UTC)
    access_token, access_expires_at = create_access_token(user_id=user_id)
    refresh_token, new_jti, refresh_expires_at = create_refresh_token(user_id=user_id)
    db.add(
        RefreshToken(
            user_id=user_id,
            jti=new_jti,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
        )
    )
    db.commit()

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
    )


@router.post("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=user.id,
        name=user.name,
        email=user.email,
        points=user.points,
        phone=user.phone,
        birthday=user.birthday,
    )


@router.post("/update_profile", response_model=UserPublic)
def update_profile(
    payload: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    fields = payload.model_fields_set

    if "email" in fields and payload.email is not None:
        next_email = str(payload.email).strip()
        if next_email and next_email.lower() != user.email.lower():
            existing = db.scalar(select(User).where(User.email == next_email))
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )
            user.email = next_email

    if "name" in fields and payload.name is not None:
        user.name = payload.name.strip()

    if "phone" in fields:
        if payload.phone is None or not payload.phone.strip():
            user.phone = None
        else:
            user.phone = payload.phone.strip()

    if "birthday" in fields:
        if payload.birthday is None or not payload.birthday.strip():
            user.birthday = None
        else:
            try:
                user.birthday = parse_ymd(payload.birthday)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid birthday",
                )

    db.commit()
    db.refresh(user)
    return UserPublic(
        id=user.id,
        name=user.name,
        email=user.email,
        points=user.points,
        phone=user.phone,
        birthday=user.birthday,
    )


@router.post("/change_password", response_model=TokenPair)
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TokenPair:
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password",
        )

    user.password_hash = hash_password(payload.new_password)

    db.execute(
        delete(RefreshToken).where(
            RefreshToken.user_id == user.id,
        )
    )

    access_token, access_expires_at = create_access_token(user_id=user.id)
    refresh_token, jti, refresh_expires_at = create_refresh_token(user_id=user.id)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
        )
    )
    db.commit()

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
    )


@router.post("/delete_account", response_model=ApiMessage)
def delete_account(
    payload: DeleteAccountRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiMessage:
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )

    db.execute(delete(Plant).where(Plant.user_id == user.id))
    db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    db.execute(delete(User).where(User.id == user.id))
    db.commit()
    return ApiMessage(message="Account deleted")


@router.post("/found_psw", response_model=ApiMessage)
def found_password(_: dict, db: Session = Depends(get_db)) -> ApiMessage:
    _ = db
    return ApiMessage(message="If the account exists, a reset email will be sent.")
