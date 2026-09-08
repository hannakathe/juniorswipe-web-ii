from flask import Blueprint, g, jsonify

from ..extensions import db
from ..models.profile import Profile
from ..security import jwt_required
from ..validation import get_json

profiles_bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")

_EDITABLE = ("headline", "bio", "location", "website", "company_name")


def _get_or_create(user):
    if user.profile is None:
        user.profile = Profile(user_id=user.id)
        db.session.add(user.profile)
        db.session.commit()
    return user.profile


@profiles_bp.get("/me")
@jwt_required
def get_profile():
    return jsonify(_get_or_create(g.current_user).to_dict()), 200


@profiles_bp.put("/me")
@profiles_bp.patch("/me")
@jwt_required
def update_profile():
    data = get_json()
    profile = _get_or_create(g.current_user)
    for field in _EDITABLE:
        if field in data:
            setattr(profile, field, data[field])
    if "skills" in data and isinstance(data["skills"], list):
        profile.skills_list = [str(s).strip() for s in data["skills"] if str(s).strip()]
    db.session.commit()
    return jsonify(profile.to_dict()), 200
