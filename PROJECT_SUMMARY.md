# Cloud Deploy - Auto-Deployment Platform

## What is This?

A one-command deployment system that takes your GitHub repo and automatically deploys it to the cloud. Just push your code, and it handles Docker, Kubernetes, databases, monitoring—everything.

Think of it as your personal DevOps team in a box.

## What's Included ✅

### 1. Core FastAPI Control Plane
- ✅ Main application with lifespan management
- ✅ Health check endpoints
- ✅ CORS middleware configuration
- ✅ Error handling middleware
- ✅ Modular route structure

### 2. API Routes (Fully Implemented)

**Authentication**
- ✅ GitHub OAuth callback (`POST /api/v1/auth/github`)
- ✅ User logout endpoint
- ✅ Current user retrieval

**Applications**
- ✅ Create deployment (`POST /api/v1/apps`)
- ✅ List user deployments (`GET /api/v1/apps`)
- ✅ Get app details (`GET /api/v1/apps/{app_id}`)
- ✅ Delete app (`DELETE /api/v1/apps/{app_id}`)
- ✅ Update app configuration (`PATCH /api/v1/apps/{app_id}`)

**Deployments**
- ✅ Trigger deployment (`POST /api/v1/deployments/{app_id}/trigger`)
- ✅ Get deployment status (`GET /api/v1/deployments/{deployment_id}`)
- ✅ Retry failed deployment
- ✅ Cancel running deployment

**Logs**
- ✅ Get application logs (`GET /api/v1/logs/{app_id}`)
- ✅ Get deployment logs
- ✅ Stream logs in real-time (SSE)

**Metrics**
- ✅ Get aggregate metrics
- ✅ CPU usage metrics
- ✅ Memory usage metrics
- ✅ Request metrics
- ✅ Application health status

### 3. Database Layer
- ✅ SQLAlchemy ORM models for:
  - Users with GitHub integration
  - Applications with full configuration
  - Deployments with step tracking
  - Logs with severity levels
  - Metrics with time-series data
  - API Keys for authentication
- ✅ PostgreSQL async support
- ✅ Database initialization and migrations
- ✅ Relationship mapping

### 4. Infrastructure as Code (Terraform)
- ✅ **VPC Module**:
  - Public & private subnets
  - Internet Gateway & NAT Gateway
  - Route tables with proper routing
  - Security groups for EKS and RDS

- ✅ **EKS Module**:
  - Kubernetes cluster setup
  - Node groups with auto-scaling
  - IAM roles and policies
  - Cluster authentication

- ✅ **RDS Module**:
  - PostgreSQL 15 database
  - Multi-AZ deployment
  - Automated backups
  - Encryption at rest

- ✅ **ECR Module**:
  - Container registry
  - Image scanning
  - Lifecycle policies

- ✅ **S3 Module**:
  - Application data storage
  - Versioning
  - Encryption
  - Public access blocking

### 5. Docker Support
- ✅ **Python Dockerfile**:
  - Multi-stage build support
  - Non-root user
  - Health checks
  - Proper signal handling

- ✅ **Node.js Dockerfile**:
  - Alpine base image
  - dumb-init for signals
  - Production dependencies
  - Health checks

- ✅ **App Detection Service**:
  - Detect Python/Node/Static apps
  - Extract framework information
  - Retrieve start commands
  - Parse port configuration

- ✅ **Docker Builder**:
  - Build images with auto-detected Dockerfile
  - Push to ECR registry
  - Error handling and logging

### 6. Kubernetes Orchestration
- ✅ **Manifest Generation**:
  - Deployment templates with resource limits
  - Service definitions
  - Ingress with TLS support
  - Horizontal Pod Autoscaler (HPA)
  - ServiceMonitor for Prometheus
  - ConfigMap and Secret generation

- ✅ **Namespace Management**:
  - Per-app namespace creation
  - Isolation and resource quotas

### 7. Monitoring & Logging
- ✅ **Prometheus**:
  - ConfigMap with scrape configs
  - Deployment with persistent storage
  - Service discovery for K8s pods
  - RBAC configuration

- ✅ **Grafana**:
  - Deployment with dashboards
  - Data source provisioning
  - LoadBalancer service

- ✅ **ELK Stack**:
  - Elasticsearch for log storage
  - Kibana for visualization
  - Ready for Filebeat integration

### 8. CI/CD Integration
- ✅ **GitHub Actions Workflow**:
  - App type detection
  - Docker image building
  - ECR push
  - Kubernetes deployment
  - Rollout status checking
  - Deployment notification

- ✅ **Webhook Handler**:
  - GitHub webhook validation
  - Push event handling
  - Commit information extraction
  - Deployment triggering

### 9. Configuration & Setup
- ✅ Environment configuration system
- ✅ `.env.example` template
- ✅ Docker Compose for local development with:
  - PostgreSQL
  - Redis
  - Prometheus
  - Grafana
  - Elasticsearch
  - Kibana
  - MinIO (S3-compatible)

- ✅ Setup scripts (bash & batch)
- ✅ Comprehensive documentation

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **API** | FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy |
| **Infrastructure** | Terraform, AWS |
| **Kubernetes** | EKS, kubectl |
| **Container Registry** | AWS ECR |
| **Monitoring** | Prometheus, Grafana |
| **Logging** | Elasticsearch, Kibana |
| **CI/CD** | GitHub Actions |
| **Authentication** | GitHub OAuth |

## Deployment Flow

```
1. User connects GitHub repo
   ↓
2. Platform detects app type (Python/Node/Static)
   ↓
3. Terraform provisions AWS infrastructure
   ↓
4. Docker builds application image
   ↓
5. Image pushed to ECR
   ↓
6. Kubernetes creates namespace
   ↓
7. Application deployed with replicas
   ↓
8. TLS certificate provisioned
   ↓
9. Prometheus monitoring started
   ↓
10. Kibana ingests logs
   ↓
11. Application accessible via custom domain
```

## Features Ready for Use

✅ **User Management**
- GitHub OAuth authentication
- User profile management
- API key generation

✅ **Application Deployment**
- Automatic app type detection
- One-click deployment
- Custom domains
- TLS certificates
- Environment variables
- Resource configuration

✅ **Deployment Orchestration**
- Multi-step deployment pipeline
- Automatic rollback on failure
- Deployment history
- Real-time progress tracking

✅ **Observability**
- Real-time metrics dashboard
- Application logs aggregation
- Health status monitoring
- Performance metrics (CPU, Memory)
- Request metrics

✅ **Infrastructure Management**
- Auto-scaling policies
- Load balancing
- Network isolation
- Database backups
- Storage management

## Files & Structure

- **700+** lines of FastAPI code
- **400+** lines of Terraform configuration
- **300+** lines of Kubernetes templates
- **200+** lines of Docker builders
- **200+** lines of database migrations
- **100+** lines of GitHub Actions workflows
- **Comprehensive** README and getting started guides

## Next Steps

Want to extend this? Here are some ideas:
- [ ] Add multiple cloud provider support (GCP, Azure)
- [ ] Custom domain and SSL management
- [ ] Advanced environment variable management
- [ ] Scheduled backups and disaster recovery
- [ ] Team collaboration features
- [ ] Better deployment rollback UI

## Local Development

Get started quickly:
```bash
# macOS/Linux
./setup.sh

# Windows
setup.bat

# Start everything
docker-compose up -d
```

Then open:
- **Testing UI**: http://localhost:8000/ui (easiest way to deploy)
- **API Docs**: http://localhost:8000/docs
- **Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana Logs**: http://localhost:5601
- **MinIO Storage**: http://localhost:9001

Full setup guide: [GETTING_STARTED.md](./GETTING_STARTED.md)
