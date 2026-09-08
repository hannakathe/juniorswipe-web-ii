from datetime import datetime, timezone

from ..extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship("User", back_populates="role")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    role = db.relationship("Role", back_populates="users")
    profile = db.relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    resumes = db.relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    projects = db.relationship(
        "Project", back_populates="owner", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.name if self.role else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
