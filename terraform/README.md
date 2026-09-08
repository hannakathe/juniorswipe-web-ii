# Terraform — local infrastructure

Manages the JuniorSwipe stack (network, Postgres volume + container, backend
image + container, frontend image + container) with the
[`kreuzwerker/docker`](https://registry.terraform.io/providers/kreuzwerker/docker/latest)
provider. **No cloud, no cost.**

| File | Purpose |
|------|---------|
| `versions.tf` | `required_version`, `required_providers`, provider config |
| `variables.tf` | ports, DB credentials, secrets, `docker_host` |
| `main.tf` | resources: `docker_network`, `docker_volume`, `docker_image`, `docker_container` |
| `outputs.tf` | URLs (frontend, backend, health, metrics) + container names |
| `terraform.tfvars.example` | copy to `terraform.tfvars` |

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit docker_host for your OS

terraform init      # downloads the docker provider
terraform validate  # static check
terraform plan      # preview
terraform apply     # build images + start containers
terraform output    # frontend_url, backend_url, ...
terraform destroy   # remove everything
```

Prerequisite: a running Docker daemon. On Windows keep the default
`npipe:////./pipe/docker_engine`; on Linux/macOS set
`docker_host = "unix:///var/run/docker.sock"`.

> This intentionally mirrors `docker-compose.yml`. Use whichever you prefer —
> Compose for quick dev, Terraform to demonstrate IaC with plan/apply/state.
> Prometheus/Grafana are covered by Compose and the k8s manifests; add them here
> as extra `docker_container` blocks if required.
