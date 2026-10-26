import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except Exception:
        pass
    return None

def admin_key_matches(candidate: Optional[str]) -> bool:
    """X-Admin-Key check in constant time. An unset ADMIN_API_KEY disables key access entirely."""
    configured = settings.ADMIN_API_KEY
    if not configured or not candidate:
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), configured.encode("utf-8"))

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires administrator privileges."
        )
    return current_user

def verify_admin_key_or_user(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> bool:
    """Verifies either valid X-Admin-Key header or valid admin JWT token."""
    if admin_key_matches(x_admin_key):
        return True
    if token:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.is_admin:
                    return True
        except Exception:
            pass
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized: Admin access required."
    )
