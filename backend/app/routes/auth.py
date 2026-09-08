from flask import Blueprint, g, jsonify

from ..extensions import db
from ..errors import ApiError
from ..models.user import Role, User
from ..models.profile import Profile
from ..security import create_access_token, hash_password, jwt_required, verify_password
from ..validation import get_json, require, valid_email, valid_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

DEFAULT_ROLE = "developer"
SELF_SIGNUP_ROLES = {"developer", "company"}


@auth_bp.post("/register")
def register():
    data = get_json()
    require(data, "email", "password", "full_name")
    email = valid_email(data["email"])
    valid_password(data["password"])

    role_name = (data.get("role") or DEFAULT_ROLE).lower()
    if role_name not in SELF_SIGNUP_ROLES:
        raise ApiError("validation_error", "role must be 'developer' or 'company'", 422)

    if User.query.filter_by(email=email).first():
        raise ApiError("email_taken", "Email already registered", 409)

    role = Role.query.filter_by(name=role_name).first()
    if role is None:
        role = Role(name=role_name, description=f"{role_name} account")
        db.session.add(role)
        db.session.flush()

    user = User(
        email=email,
        password_hash=hash_password(data["password"]),
        full_name=data["full_name"].strip(),
        role_id=role.id,
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(Profile(user_id=user.id,
                           company_name=data["full_name"].strip()
                           if role_name == "company" else None))
    db.session.commit()

    token = create_access_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = get_json()
    require(data, "email", "password")
    email = valid_email(data["email"])
    user = User.query.filter_by(email=email).first()
    if user is None or not verify_password(data["password"], user.password_hash):
        raise ApiError("invalid_credentials", "Email or password is incorrect", 401)
    token = create_access_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required
def me():
    user = g.current_user
    body = user.to_dict()
    body["profile"] = user.profile.to_dict() if user.profile else None
    return jsonify(body), 200
