import json
from datetime import datetime, timezone

from ..extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    headline = db.Column(db.String(150))
    bio = db.Column(db.Text)
    location = db.Column(db.String(120))
    website = db.Column(db.String(255))
    company_name = db.Column(db.String(150))
    skills = db.Column(db.Text, default="[]")  # JSON-encoded list of strings
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    user = db.relationship("User", back_populates="profile")

    @property
    def skills_list(self):
        try:
            return json.loads(self.skills or "[]")
        except ValueError:
            return []

    @skills_list.setter
    def skills_list(self, value):
        self.skills = json.dumps(list(value or []))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "headline": self.headline,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
            "company_name": self.company_name,
            "skills": self.skills_list,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
