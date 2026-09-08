###############################################################################
# Local, reproducible infrastructure for JuniorSwipe using the Docker provider.
# No cloud resources, no cost. `terraform apply` brings up the same stack as
# docker-compose, but managed as Terraform state.
###############################################################################

locals {
  root = abspath("${path.module}/..")
}

# --- Network -----------------------------------------------------------------
resource "docker_network" "app" {
  name = "${var.project_name}-net"
}

# --- Database --------------------------------------------------------------- -
resource "docker_volume" "pgdata" {
  name = "${var.project_name}-pgdata"
}

resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_container" "db" {
  name  = "${var.project_name}-db"
  image = docker_image.postgres.image_id

  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}",
  ]

  networks_advanced {
    name    = docker_network.app.name
    aliases = ["db"]
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  volumes {
    host_path      = "${local.root}/database/schema.sql"
    container_path = "/docker-entrypoint-initdb.d/01-schema.sql"
    read_only      = true
  }
  volumes {
    host_path      = "${local.root}/database/seed.sql"
    container_path = "/docker-entrypoint-initdb.d/02-seed.sql"
    read_only      = true
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.postgres_user} -d ${var.postgres_db}"]
    interval = "5s"
    retries  = 10
    timeout  = "3s"
  }
}

# --- Backend ---------------------------------------------------------------- -
resource "docker_image" "backend" {
  name = "${var.project_name}-backend:tf"

  build {
    context = "${local.root}/backend"
    tag     = ["${var.project_name}-backend:tf"]
  }
}

resource "docker_container" "backend" {
  name  = "${var.project_name}-backend"
  image = docker_image.backend.image_id

  env = [
    "DATABASE_URL=postgresql://${var.postgres_user}:${var.postgres_password}@db:5432/${var.postgres_db}",
    "JWT_SECRET=${var.jwt_secret}",
    "SECRET_KEY=${var.jwt_secret}",
    "SEED_ON_STARTUP=${var.seed_on_startup}",
    "CORS_ORIGINS=http://localhost:${var.frontend_port},http://localhost",
    "STORAGE_DIR=/app/storage",
  ]

  networks_advanced {
    name    = docker_network.app.name
    aliases = ["backend"]
  }

  ports {
    internal = 5000
    external = var.backend_port
  }

  depends_on = [docker_container.db]
}

# --- Frontend ------------------------------------------------------------- ---
resource "docker_image" "frontend" {
  name = "${var.project_name}-frontend:tf"

  build {
    context    = local.root
    dockerfile = "frontend/Dockerfile"
    tag        = ["${var.project_name}-frontend:tf"]
  }
}

resource "docker_container" "frontend" {
  name  = "${var.project_name}-frontend"
  image = docker_image.frontend.image_id

  networks_advanced {
    name    = docker_network.app.name
    aliases = ["frontend"]
  }

  ports {
    internal = 80
    external = var.frontend_port
  }

  depends_on = [docker_container.backend]
}
