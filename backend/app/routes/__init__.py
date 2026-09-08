from .auth import auth_bp
from .health import health_bp
from .profiles import profiles_bp
from .projects import projects_bp
from .resumes import resumes_bp
from .tasks import tasks_bp
from .users import users_bp

ALL_BLUEPRINTS = (
    health_bp,
    auth_bp,
    users_bp,
    profiles_bp,
    resumes_bp,
    projects_bp,
    tasks_bp,
)
