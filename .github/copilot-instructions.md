# DevOps Automation SaaS - Project Instructions

This is a mini-Vercel platform for automatic backend deployment. Users push code to GitHub, and the platform auto-provisions AWS infrastructure, Kubernetes namespaces, CI/CD pipelines, and deploys apps with TLS.

## Project Status

- [x] Project structure scaffolded
- [x] Control plane API (FastAPI) - Core endpoints implemented
- [x] Terraform AWS automation - Full infrastructure as code
- [x] Kubernetes deployment logic - Manifest generation
- [x] GitHub Actions integration - CI/CD workflows
- [x] Docker image builder - App detection & image building
- [x] Monitoring & logging - Prometheus, Grafana, ELK stack
- [x] Database schema - PostgreSQL migrations
- [ ] End-to-end testing
- [ ] Payment integration (Stripe)
- [ ] Multi-region deployment

## Project Structure

```
cloud_deploy_app/
├── control_plane/          # FastAPI control plane
│   ├── main.py            # Main application
│   ├── config.py          # Configuration
│   ├── routes/            # API endpoints
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── database/          # DB initialization
│   ├── middleware/        # Error handling
│   └── services/          # Business logic
├── terraform/             # AWS infrastructure
│   ├── main.tf           # Root configuration
│   ├── network.tf        # VPC setup
│   ├── eks.tf            # EKS cluster
│   ├── rds.tf            # PostgreSQL
│   ├── ecr.tf            # Docker registry
│   └── s3.tf             # Object storage
├── kubernetes/           # K8s deployment
│   └── templates.py      # Manifest generation
├── docker/              # Docker builders
│   ├── Dockerfile.python
│   ├── Dockerfile.node
│   └── builder.py       # App detection
├── monitoring/          # Observability
│   ├── prometheus.yaml
│   ├── grafana.yaml
│   └── service.py
├── database/           # DB schemas
│   └── migrations.py
├── github_actions/    # CI/CD workflows
│   ├── deploy.yml
│   └── webhook.py
├── docker-compose.yml # Local development
├── requirements.txt   # Python dependencies
└── GETTING_STARTED.md # Setup guide
```

## Key Components

1. **Control Plane** (FastAPI) - Main SaaS backend with:
   - GitHub OAuth authentication
   - Application CRUD operations
   - Deployment management
   - Logs & metrics API

2. **Terraform Modules** - AWS infrastructure:
   - VPC with public/private subnets
   - EKS cluster with auto-scaling
   - RDS PostgreSQL database
   - ECR container registry
   - S3 for app data

3. **Kubernetes Orchestration**:
   - Auto-generated manifests
   - TLS via cert-manager
   - Horizontal Pod Autoscaling
   - ServiceMonitor for Prometheus

4. **Docker Builder**:
   - Python/Node/Static app detection
   - Automatic Dockerfile selection
   - ECR image push

5. **GitHub Integration**:
   - OAuth for authentication
   - Webhook for push events
   - CI/CD workflow automation

6. **Monitoring Stack**:
   - Prometheus for metrics
   - Grafana for dashboards
   - ELK for log aggregation

## Development Guidelines

- Use FastAPI for all API endpoints
- Use async/await for I/O operations
- Implement error handling with HTTPException
- Use SQLAlchemy ORM for database
- Use Kubernetes Python client for orchestration
- Each app gets isolated namespace
- Support Python/Node app auto-detection
- Implement proper logging throughout

## Quick Start

1. **Setup**: `./setup.sh` (macOS/Linux) or `setup.bat` (Windows)
2. **Environment**: Update `.env` with credentials
3. **Services**: `docker-compose up -d`
4. **Run**: `uvicorn control_plane.main:app --reload`
5. **Access**: http://localhost:8000/docs

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/auth/github` - GitHub OAuth
- `POST /api/v1/apps` - Create deployment
- `GET /api/v1/apps` - List deployments
- `GET /api/v1/logs/{app_id}` - Get logs
- `GET /api/v1/metrics/{app_id}` - Get metrics
- `POST /api/v1/deployments/{app_id}/trigger` - Manual deploy

## Infrastructure Deployment

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Next Steps for Development

1. Implement database models properly with async SQLAlchemy
2. Add GitHub OAuth callback handler
3. Integrate with Kubernetes Python client for deployments
4. Add Terraform dynamic configuration generation
5. Implement end-to-end tests
6. Add payment integration with Stripe
7. Deploy to production AWS infrastructure
