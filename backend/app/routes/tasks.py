from flask import Blueprint, g, jsonify, request

from ..extensions import db
from ..errors import ApiError
from ..models.project import Project
from ..models.task import TASK_STATUSES, Task
from ..security import current_user, jwt_required
from ..validation import get_json, one_of, pagination, parse_date, require

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api")


def _owned_project_or_404(project_id):
    project = Project.query.get(project_id)
    if project is None or project.owner_id != current_user().id:
        raise ApiError("not_found", "Project not found", 404)
    return project


def _owned_task_or_404(task_id):
    task = Task.query.get(task_id)
    if task is None or task.project.owner_id != current_user().id:
        raise ApiError("not_found", "Task not found", 404)
    return task


@tasks_bp.get("/tasks")
@jwt_required
def list_tasks():
    """List every task across the caller's projects. Optional ?project_id= & ?status=."""
    page, per_page = pagination()
    query = Task.query.join(Project).filter(Project.owner_id == g.current_user.id)

    pid = request.args.get("project_id", type=int)
    if pid:
        query = query.filter(Task.project_id == pid)
    status = one_of(request.args.get("status"), set(TASK_STATUSES), "status")
    if status:
        query = query.filter(Task.status == status)

    query = query.order_by(Task.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({
        "items": [t.to_dict() for t in rows],
        "page": page, "per_page": per_page, "total": total,
    }), 200


@tasks_bp.get("/projects/<int:project_id>/tasks")
@jwt_required
def list_project_tasks(project_id):
    project = _owned_project_or_404(project_id)
    return jsonify({"items": [t.to_dict() for t in project.tasks],
                    "total": len(project.tasks)}), 200


@tasks_bp.get("/tasks/<int:task_id>")
@jwt_required
def get_task(task_id):
    return jsonify(_owned_task_or_404(task_id).to_dict()), 200


@tasks_bp.post("/tasks")
@jwt_required
def create_task():
    data = get_json()
    require(data, "title", "project_id")
    _owned_project_or_404(data["project_id"])
    one_of(data.get("status"), set(TASK_STATUSES), "status")
    task = Task(
        project_id=data["project_id"],
        title=data["title"].strip(),
        description=data.get("description"),
        status=data.get("status") or "todo",
        priority=data.get("priority") or "medium",
        due_date=parse_date(data.get("due_date")),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.post("/projects/<int:project_id>/tasks")
@jwt_required
def create_project_task(project_id):
    _owned_project_or_404(project_id)
    data = get_json()
    require(data, "title")
    one_of(data.get("status"), set(TASK_STATUSES), "status")
    task = Task(
        project_id=project_id,
        title=data["title"].strip(),
        description=data.get("description"),
        status=data.get("status") or "todo",
        priority=data.get("priority") or "medium",
        due_date=parse_date(data.get("due_date")),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.put("/tasks/<int:task_id>")
@tasks_bp.patch("/tasks/<int:task_id>")
@jwt_required
def update_task(task_id):
    task = _owned_task_or_404(task_id)
    data = get_json()
    one_of(data.get("status"), set(TASK_STATUSES), "status")
    for field in ("title", "description", "status", "priority"):
        if field in data and data[field] is not None:
            setattr(task, field, data[field])
    if "due_date" in data:
        task.due_date = parse_date(data.get("due_date"))
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/tasks/<int:task_id>")
@jwt_required
def delete_task(task_id):
    db.session.delete(_owned_task_or_404(task_id))
    db.session.commit()
    return "", 204
