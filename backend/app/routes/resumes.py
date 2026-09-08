import os
import uuid

from flask import Blueprint, current_app, g, jsonify, request, send_file
from werkzeug.utils import secure_filename

from ..extensions import db
from ..errors import ApiError
from ..models.resume import Resume
from ..security import current_user, jwt_required, roles_required

resumes_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")

ALLOWED_TYPES = {"application/pdf", "application/msword",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "text/plain", "text/markdown"}


def _owned_or_404(resume_id):
    resume = Resume.query.get(resume_id)
    if resume is None or resume.user_id != current_user().id:
        raise ApiError("not_found", "Resume not found", 404)
    return resume


def _storage_dir():
    path = current_app.config["STORAGE_DIR"]
    os.makedirs(path, exist_ok=True)
    return path


@resumes_bp.get("")
@jwt_required
def list_resumes():
    items = (Resume.query.filter_by(user_id=g.current_user.id)
             .order_by(Resume.is_primary.desc(), Resume.created_at.desc()).all())
    return jsonify({"items": [r.to_dict() for r in items], "total": len(items)}), 200


@resumes_bp.get("/<int:resume_id>")
@jwt_required
def get_resume(resume_id):
    return jsonify(_owned_or_404(resume_id).to_dict()), 200


@resumes_bp.post("")
@roles_required("developer")
def create_resume():
    """Accepts JSON metadata or multipart/form-data with an optional 'file'."""
    if request.content_type and request.content_type.startswith("multipart/"):
        form = request.form
        title = (form.get("title") or "").strip()
        summary = form.get("summary")
    else:
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        summary = data.get("summary")

    if not title:
        raise ApiError("validation_error", "title is required", 422)

    resume = Resume(user_id=g.current_user.id, title=title, summary=summary)

    upload = request.files.get("file")
    if upload and upload.filename:
        if upload.mimetype not in ALLOWED_TYPES:
            raise ApiError("unsupported_type",
                           f"Unsupported file type: {upload.mimetype}", 415)
        safe = secure_filename(upload.filename) or "cv"
        key = f"{g.current_user.id}/{uuid.uuid4().hex}_{safe}"
        dest = os.path.join(_storage_dir(), key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        upload.save(dest)
        resume.storage_key = key
        resume.original_filename = safe
        resume.content_type = upload.mimetype
        resume.size_bytes = os.path.getsize(dest)

    if not Resume.query.filter_by(user_id=g.current_user.id, is_primary=True).first():
        resume.is_primary = True

    db.session.add(resume)
    db.session.commit()
    return jsonify(resume.to_dict()), 201


@resumes_bp.put("/<int:resume_id>")
@resumes_bp.patch("/<int:resume_id>")
@jwt_required
def update_resume(resume_id):
    resume = _owned_or_404(resume_id)
    data = request.get_json(silent=True) or {}
    for field in ("title", "summary"):
        if field in data:
            setattr(resume, field, data[field])
    if data.get("is_primary") is True:
        Resume.query.filter_by(user_id=g.current_user.id).update({"is_primary": False})
        resume.is_primary = True
    db.session.commit()
    return jsonify(resume.to_dict()), 200


@resumes_bp.delete("/<int:resume_id>")
@jwt_required
def delete_resume(resume_id):
    resume = _owned_or_404(resume_id)
    if resume.storage_key:
        try:
            os.remove(os.path.join(current_app.config["STORAGE_DIR"], resume.storage_key))
        except OSError:
            pass
    db.session.delete(resume)
    db.session.commit()
    return "", 204


@resumes_bp.get("/<int:resume_id>/file")
@jwt_required
def download_resume(resume_id):
    resume = _owned_or_404(resume_id)
    if not resume.storage_key:
        raise ApiError("no_file", "This resume has no attached file", 404)
    full = os.path.join(current_app.config["STORAGE_DIR"], resume.storage_key)
    if not os.path.exists(full):
        raise ApiError("no_file", "Stored file is missing", 404)
    return send_file(full, mimetype=resume.content_type or "application/octet-stream",
                     as_attachment=True, download_name=resume.original_filename or "cv")
