from datetime import datetime, timezone

from ..extensions import db

PROJECT_STATUSES = ("draft", "open", "active", "closed")


def _utcnow():
    return datetime.now(timezone.utc)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft", nullable=False)
    tech_stack = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    owner = db.relationship("User", back_populates="projects")
    tasks = db.relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    def to_dict(self, with_tasks=False):
        data = {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "tech_stack": self.tech_stack,
            "task_count": len(self.tasks),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if with_tasks:
            data["tasks"] = [t.to_dict() for t in self.tasks]
        return data
