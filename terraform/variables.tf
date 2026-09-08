variable "docker_host" {
  description = "Docker daemon endpoint"
  type        = string
  default     = "npipe:////./pipe/docker_engine" # Windows; use unix:///var/run/docker.sock on Linux/macOS
}

variable "project_name" {
  description = "Prefix for all created resources"
  type        = string
  default     = "juniorswipe"
}

variable "postgres_user" {
  type    = string
  default = "juniorswipe"
}

variable "postgres_password" {
  type      = string
  default   = "juniorswipe"
  sensitive = true
}

variable "postgres_db" {
  type    = string
  default = "juniorswipe"
}

variable "jwt_secret" {
  type      = string
  default   = "terraform-dev-jwt-secret"
  sensitive = true
}

variable "backend_port" {
  type    = number
  default = 5000
}

variable "frontend_port" {
  type    = number
  default = 8080
}

variable "seed_on_startup" {
  type    = bool
  default = true
}
