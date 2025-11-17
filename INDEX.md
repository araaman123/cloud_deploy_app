# DevOps Automation SaaS - Project Index

Welcome to the **DevOps Automation SaaS** platform! This is your complete guide to the codebase.

## 📚 Documentation (Start Here!)

- **[README.md](./README.md)** - Project overview and features
- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - Local development setup & examples
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - What's been built + architecture
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to contribute

## 📁 Directory Structure

### Core Application
```
control_plane/
├── main.py           # FastAPI application entry point
├── config.py         # Configuration management
├── routes/           # API route handlers
│   ├── auth.py       # GitHub OAuth & authentication
│   ├── apps.py       # Application CRUD operations
│   ├── deployments.py # Deployment management
│   ├── logs.py       # Log retrieval
│   └── metrics.py    # Metrics endpoints
├── models/
│   └── database.py   # SQLAlchemy ORM models
├── schemas/
│   └── schemas.py    # Pydantic request/response schemas
├── database/
│   ├── init.py       # Database connection & session management
│   └── migrations.py # Database schema & migrations
├── middleware/
│   └── error_handler.py # Global error handling
└── services/
    ├── orchestrator.py   # Deployment orchestration
    └── deployment.py     # Deployment services
```

### Infrastructure
```
terraform/
├── README.md         # Infrastructure guide
├── main.tf          # Provider & module configuration
├── variables.tf     # Input variables
├── outputs.tf       # Output values
├── network.tf       # VPC, subnets, security groups
├── eks.tf           # Kubernetes cluster
├── rds.tf           # PostgreSQL database
├── ecr.tf           # Container registry
└── s3.tf            # Object storage
```

### Kubernetes & Container
```
kubernetes/
├── README.md         # Kubernetes guide
└── templates.py      # Manifest generation

docker/
├── Dockerfile.python # Python app template
├── Dockerfile.node   # Node.js app template
└── builder.py        # App detection & building
```

### CI/CD & Monitoring
```
github_actions/
├── deploy.yml        # GitHub Actions workflow
└── webhook.py        # GitHub webhook handler

monitoring/
├── README.md         # Monitoring guide
├── prometheus.yaml   # Prometheus config & deployment
├── grafana.yaml      # Grafana deployment
└── service.py        # Monitoring endpoints
```

### Database
```
database/
├── README.md         # Database documentation
└── migrations.py     # Schema & migrations
```

### Configuration & Setup
```
.github/
├── workflows/
│   └── deploy.yml    # CI/CD workflow
└── copilot-instructions.md # Project guidelines

.env.example          # Environment template
docker-compose.yml    # Local development stack
setup.sh              # Linux/macOS setup script
setup.bat             # Windows setup script
requirements.txt      # Python dependencies
```

## 🚀 Quick Reference

### Getting Started
```bash
# 1. Clone & enter directory
cd cloud_deploy_app

# 2. Run setup
./setup.sh              # macOS/Linux
# or
setup.bat              # Windows

# 3. Start services
docker-compose up -d

# 4. Run API
uvicorn control_plane.main:app --reload

# 5. Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### API Endpoints

**Authentication**
- `POST /api/v1/auth/github` - GitHub OAuth
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user

**Applications**
- `POST /api/v1/apps` - Create app
- `GET /api/v1/apps` - List apps
- `GET /api/v1/apps/{app_id}` - Get app details
- `PATCH /api/v1/apps/{app_id}` - Update app
- `DELETE /api/v1/apps/{app_id}` - Delete app

**Deployments**
- `POST /api/v1/deployments/{app_id}/trigger` - Deploy
- `GET /api/v1/deployments/{deployment_id}` - Status
- `POST /api/v1/deployments/{deployment_id}/retry` - Retry
- `POST /api/v1/deployments/{deployment_id}/cancel` - Cancel

**Monitoring**
- `GET /api/v1/logs/{app_id}` - Get logs
- `GET /api/v1/metrics/{app_id}` - Get metrics
- `GET /api/v1/metrics/{app_id}/cpu` - CPU metrics
- `GET /api/v1/metrics/{app_id}/memory` - Memory metrics
- `GET /api/v1/metrics/{app_id}/health` - Health status

**Health**
- `GET /health` - API health check

### Dashboard URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin/admin |
| Kibana | http://localhost:5601 | - |
| MinIO | http://localhost:9001 | minioadmin/minioadmin |
| PostgreSQL | localhost:5432 | postgres/postgres |
| Redis | localhost:6379 | - |

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           GitHub Repository                      │
│  (Push triggers webhook)                        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│     Control Plane (FastAPI)                     │
│  ┌──────────────────────────────────────┐       │
│  │ GitHub OAuth → User Management      │       │
│  │ App CRUD → Infrastructure Config    │       │
│  │ Deployment Orchestration            │       │
│  │ Logs & Metrics Retrieval            │       │
│  └──────────────────────────────────────┘       │
└─────┬───────────┬────────────┬──────────────────┘
      │           │            │
      ▼           ▼            ▼
┌──────────┐ ┌─────────┐ ┌────────────┐
│ Terraform│ │Kubernetes│ │Docker ECR  │
│ (AWS)    │ │ (EKS)    │ │(Images)    │
└──────────┘ └─────────┘ └────────────┘
      │           │            │
      ▼           ▼            ▼
┌──────────────────────────────────────┐
│     Application Infrastructure        │
│  ┌──────────────────────────────┐    │
│  │ VPC, EKS, RDS, ECR, S3       │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│    Monitoring & Logging              │
│  ┌──────────────────────────────┐    │
│  │ Prometheus, Grafana, ELK     │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
```

## 🔑 Key Features

✅ **One-Click Deployment** - Connect GitHub, deploy instantly
✅ **Auto Infrastructure** - AWS provision via Terraform
✅ **Container Management** - Docker building & ECR registry
✅ **Kubernetes Orchestration** - Automatic K8s deployment
✅ **TLS Certificates** - Automatic HTTPS via cert-manager
✅ **Real-time Monitoring** - Prometheus & Grafana dashboards
✅ **Log Aggregation** - Elasticsearch & Kibana
✅ **Auto-Scaling** - Horizontal pod autoscaling
✅ **CI/CD Integration** - GitHub Actions workflows
✅ **Multi-Language** - Python, Node.js, Static sites

## 📖 Documentation by Topic

### Getting Started
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Setup & first deployment
- [README.md](./README.md) - Feature overview

### Development
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guide
- `.github/copilot-instructions.md` - Development guidelines

### Infrastructure
- [terraform/README.md](./terraform/README.md) - Terraform setup
- [kubernetes/README.md](./kubernetes/README.md) - K8s deployment
- [monitoring/README.md](./monitoring/README.md) - Monitoring setup

### Configuration
- [.env.example](./.env.example) - Environment variables
- [docker-compose.yml](./docker-compose.yml) - Local development

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **API Framework** | FastAPI |
| **Web Server** | Uvicorn |
| **Database** | PostgreSQL + SQLAlchemy |
| **Infrastructure** | Terraform + AWS |
| **Container Orchestration** | Kubernetes (EKS) |
| **Container Registry** | AWS ECR |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus + Grafana |
| **Logging** | Elasticsearch + Kibana |
| **Authentication** | GitHub OAuth |

## 🎯 Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes & commit**
   ```bash
   git commit -m "feat: add feature"
   ```

3. **Test locally**
   ```bash
   docker-compose up -d
   uvicorn control_plane.main:app --reload
   pytest control_plane/tests/
   ```

4. **Push & create PR**
   ```bash
   git push origin feature/my-feature
   ```

## 📝 Common Tasks

### Add New API Endpoint
1. Create schema in `control_plane/schemas/`
2. Create route in `control_plane/routes/`
3. Add service in `control_plane/services/`
4. Include router in `control_plane/main.py`

### Deploy to AWS
1. Configure AWS credentials
2. Run `cd terraform && terraform init`
3. Run `terraform plan` to review
4. Run `terraform apply` to provision

### Add Monitoring
1. Update `monitoring/prometheus.yaml` for metrics
2. Create Grafana dashboard
3. Add ServiceMonitor in K8s templates

### Debug Issues
- Check API logs: `docker-compose logs -f`
- Check K8s: `kubectl get all -n app-{id}`
- Check database: `psql postgresql://postgres:postgres@localhost:5432/cloud_deploy`

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Coding standards
- PR process
- Feature areas
- Issue reporting

## 📧 Support

- 📖 Documentation: See links above
- 🐛 Report bugs: GitHub Issues
- 💬 Discussions: GitHub Discussions

## 📄 License

MIT License - See LICENSE file

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
