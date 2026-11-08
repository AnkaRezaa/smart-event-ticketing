import secrets
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, status
from app.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="session-salt")

def create_session_token(data: Dict[str, Any]) -> str:
    """Creates a cryptographically signed session token."""
    return serializer.dumps(data)

def decode_session_token(token: str, max_age: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Decodes and validates a session token."""
    if not token:
        return None
    if max_age is None:
        max_age = settings.SESSION_MAX_AGE_SECONDS
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None

def generate_csrf_token() -> str:
    """Generates a secure random CSRF token."""
    return secrets.token_hex(32)

def get_current_user_from_session(request: Request) -> Optional[Dict[str, Any]]:
    """Extracts authenticated user payload from session cookie."""
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        return None
    return decode_session_token(token)

def require_auth(request: Request) -> Dict[str, Any]:
    """Dependency for routes requiring authentication."""
    user = get_current_user_from_session(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

def require_role(allowed_roles: list[str]):
    """Dependency generator for role-based authorization."""
    def role_checker(request: Request) -> Dict[str, Any]:
        user = require_auth(request)
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: insufficient role permissions"
            )
        return user
    return role_checker

