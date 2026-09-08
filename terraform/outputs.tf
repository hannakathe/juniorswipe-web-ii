output "frontend_url" {
  description = "JuniorSwipe web app (React SPA + landing under /landing/)"
  value       = "http://localhost:${var.frontend_port}"
}

output "backend_url" {
  description = "REST API base URL"
  value       = "http://localhost:${var.backend_port}"
}

output "api_health_url" {
  value = "http://localhost:${var.backend_port}/api/health"
}

output "metrics_url" {
  value = "http://localhost:${var.backend_port}/metrics"
}

output "database_dsn" {
  description = "Postgres DSN (host port not published; reachable inside the docker network)"
  value       = "postgresql://${var.postgres_user}:***@db:5432/${var.postgres_db}"
  sensitive   = false
}

output "containers" {
  value = [
    docker_container.db.name,
    docker_container.backend.name,
    docker_container.frontend.name,
  ]
}
