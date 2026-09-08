"""Idempotent seed data: roles + two demo users (developer & company)."""
from .extensions import db
from .models.profile import Profile
from .models.project import Project
from .models.task import Task
from .models.user import Role, User
from .security import hash_password

ROLES = [
    ("developer", "Junior developer looking for opportunities"),
    ("company", "Company hiring junior developers"),
]

DEMO_USERS = [
    {
        "email": "dev@local.test",
        "password": "Password123!",
        "full_name": "Dana Developer",
        "role": "developer",
    },
    {
        "email": "company@local.test",
        "password": "Password123!",
        "full_name": "Acme Corp",
        "role": "company",
    },
]


def seed(app):
    with app.app_context():
        for name, desc in ROLES:
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        db.session.commit()

        roles = {r.name: r for r in Role.query.all()}
        created = []
        for spec in DEMO_USERS:
            if User.query.filter_by(email=spec["email"]).first():
                continue
            user = User(
                email=spec["email"],
                password_hash=hash_password(spec["password"]),
                full_name=spec["full_name"],
                role_id=roles[spec["role"]].id,
            )
            db.session.add(user)
            db.session.flush()
            db.session.add(Profile(
                user_id=user.id,
                headline="Full-stack in training" if spec["role"] == "developer"
                else "We hire junior talent",
                company_name=spec["full_name"] if spec["role"] == "company" else None,
            ))
            created.append(user)
        db.session.commit()

        # A sample project + tasks for the demo developer so lists aren't empty.
        dev = User.query.filter_by(email="dev@local.test").first()
        if dev and not Project.query.filter_by(owner_id=dev.id).first():
            proj = Project(owner_id=dev.id, title="Portfolio API",
                           description="REST API showcase for JuniorSwipe",
                           status="active", tech_stack="Flask, PostgreSQL")
            db.session.add(proj)
            db.session.flush()
            db.session.add_all([
                Task(project_id=proj.id, title="Design schema", status="done"),
                Task(project_id=proj.id, title="Implement auth", status="in_progress"),
                Task(project_id=proj.id, title="Write tests", status="todo"),
            ])
            db.session.commit()

        app.logger.info("Seed complete (%d new users)", len(created))
