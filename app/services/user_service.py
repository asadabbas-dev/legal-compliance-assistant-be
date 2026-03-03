"""User CRUD and auth helper service."""

from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.core.config import settings
from app.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def create_user(db: Session, email: str, password: str) -> User:
    user = User(email=email.lower().strip(), password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    # Block authentication for guest accounts (they use unique emails now)
    if email.lower().strip().startswith("guest-") and email.lower().strip().endswith("@anonymous.local"):
        return None
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_or_create_anonymous_user(db: Session) -> User:
    """Create a unique anonymous user for each guest session."""
    import uuid
    unique_email = f"guest-{uuid.uuid4().hex}@anonymous.local"
    anon = User(
        email=unique_email,
        password_hash=hash_password("guest-no-login"),
    )
    db.add(anon)
    db.commit()
    db.refresh(anon)
    return anon
