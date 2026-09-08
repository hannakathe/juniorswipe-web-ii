from flask import Blueprint, g, jsonify, request

from ..extensions import db
from ..errors import ApiError
from ..models.project import PROJECT_STATUSES, Project
from ..security import current_user, jwt_required
from ..validation import get_json, one_of, pagination, require

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def _owned_or_404(project_id):
    project = Project.query.get(project_id)
    if project is None or project.owner_id != current_user().id:
        raise ApiError("not_found", "Project not found", 404)
    return project


@projects_bp.get("")
@jwt_required
def list_projects():
    page, per_page = pagination()
    query = Project.query.filter_by(owner_id=g.current_user.id)
    status = one_of(request.args.get("status"), set(PROJECT_STATUSES), "status")
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Project.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({
        "items": [p.to_dict() for p in rows],
        "page": page, "per_page": per_page, "total": total,
    }), 200


@projects_bp.get("/<int:project_id>")
@jwt_required
def get_project(project_id):
    return jsonify(_owned_or_404(project_id).to_dict(with_tasks=True)), 200


@projects_bp.post("")
@jwt_required
def create_project():
    data = get_json()
    require(data, "title")
    one_of(data.get("status"), set(PROJECT_STATUSES), "status")
    project = Project(
        owner_id=g.current_user.id,
        title=data["title"].strip(),
        description=data.get("description"),
        status=data.get("status") or "draft",
        tech_stack=data.get("tech_stack"),
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.put("/<int:project_id>")
@projects_bp.patch("/<int:project_id>")
@jwt_required
def update_project(project_id):
    project = _owned_or_404(project_id)
    data = get_json()
    one_of(data.get("status"), set(PROJECT_STATUSES), "status")
    for field in ("title", "description", "status", "tech_stack"):
        if field in data and data[field] is not None:
            setattr(project, field, data[field])
    db.session.commit()
    return jsonify(project.to_dict()), 200


@projects_bp.delete("/<int:project_id>")
@jwt_required
def delete_project(project_id):
    db.session.delete(_owned_or_404(project_id))
    db.session.commit()
    return "", 204
