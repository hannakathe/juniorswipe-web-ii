"""Password hashing and JWT helpers + auth decorators."""
from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import current_app, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from .errors import ApiError


def hash_password(raw: str) -> str:
    return generate_password_hash(raw, method="pbkdf2:sha256")


def verify_password(raw: str, hashed: str) -> bool:
    return check_password_hash(hashed, raw)


def create_access_token(user) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.name if user.role else None,
        "iat": now,
        "exp": now + current_app.config["JWT_EXPIRES"],
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        raise ApiError("token_expired", "The access token has expired", 401)
    except jwt.InvalidTokenError:
        raise ApiError("token_invalid", "The access token is invalid", 401)


def _load_user_from_request():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise ApiError("token_missing", "Authorization Bearer token required", 401)
    token = auth.split(" ", 1)[1].strip()
    data = decode_token(token)

    # Imported here to avoid circular import at module load time.
    from .models.user import User

    user = db_get_user(User, data.get("sub"))
    if user is None:
        raise ApiError("user_not_found", "Token subject no longer exists", 401)
    g.current_user = user
    g.token_claims = data
    return user


def db_get_user(User, raw_id):
    try:
        return User.query.get(int(raw_id))
    except (TypeError, ValueError):
        return None


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _load_user_from_request()
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _load_user_from_request()
            if user.role is None or user.role.name not in roles:
                raise ApiError(
                    "forbidden",
                    f"Requires one of roles: {', '.join(roles)}",
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def current_user():
    return getattr(g, "current_user", None)
