from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import User, UserRole
from app.security.password import hash_password, verify_password

def register_user(db: Session, name: str, email: str, password: str, role_str: str = "participant") -> User:
    role = UserRole.PARTICIPANT
    if role_str == "operator":
        role = UserRole.OPERATOR
    elif role_str == "admin":
        role = UserRole.ADMIN

    existing = db.query(User).filter(User.email == email.lower().strip()).first()
    if existing:
        raise ValueError("An account with this email already exists")

    hashed = hash_password(password)
    user = User(
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=hashed,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

