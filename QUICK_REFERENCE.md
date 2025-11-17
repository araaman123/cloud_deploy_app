# 🚀 DevOps Automation SaaS - Quick Reference Card

## 📖 Essential Docs
- **Getting Started**: [GETTING_STARTED.md](./GETTING_STARTED.md)
- **Project Map**: [INDEX.md](./INDEX.md)
- **What's Built**: [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- **Contribute**: [CONTRIBUTING.md](./CONTRIBUTING.md)

## ⚡ 5-Minute Setup

```bash
# Clone & setup (1 minute)
cd cloud_deploy_app
./setup.sh  # or setup.bat on Windows

# Start services (1 minute)
docker-compose up -d

# Run API (1 minute)
uvicorn control_plane.main:app --reload

# Test (2 minutes)
curl http://localhost:8000/docs
```

## 🔗 Dashboard URLs
| Service | URL | Login |
|---------|-----|-------|
| **API Docs** | http://localhost:8000/docs | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3001 | admin/admin |
| **Kibana** | http://localhost:5601 | - |
| **PostgreSQL** | localhost:5432 | postgres/postgres |

## 🌐 API Quick Reference

### Create Deployment
```bash
curl -X POST http://localhost:8000/api/v1/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-app",
    "github_repo_url": "https://github.com/user/repo",
    "app_type": "python"
  }'
```

### List Deployments
```bash
curl http://localhost:8000/api/v1/apps
```

### Get App Logs
```bash
curl http://localhost:8000/api/v1/logs/{app_id}
```

### Get Metrics
```bash
curl http://localhost:8000/api/v1/metrics/{app_id}
```

## 📁 Key Files
| File | Purpose |
|------|---------|
| `control_plane/main.py` | FastAPI app entry point |
| `control_plane/routes/` | All API endpoints |
| `control_plane/models/database.py` | Database models |
| `terraform/` | AWS infrastructure |
| `kubernetes/templates.py` | K8s manifests |
| `docker/builder.py` | App detection & building |
| `docker-compose.yml` | Local dev stack |

## 🛠️ Common Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Check DB
psql postgresql://postgres:postgres@localhost:5432/cloud_deploy

# Run tests
pytest control_plane/tests/

# Format code
black .
isort .

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Get K8s status
kubectl get all -n app-{id}

# View pod logs
kubectl logs -n app-{id} deployment/{app-name}
```

## 📊 Architecture Layers

```
User Interface Layer
├── GitHub (auth)
└── Custom Domain

Application Layer
├── FastAPI API
├── PostgreSQL DB
└── Redis Cache

Infrastructure Layer
├── Terraform (IaC)
└── AWS (VPC, EKS, RDS, ECR, S3)

Orchestration Layer
├── Kubernetes (EKS)
└── Docker Registry (ECR)

Observability Layer
├── Prometheus (metrics)
├── Grafana (dashboard)
└── ELK (logs)
```

## 🔐 Environment Variables
```env
# GitHub OAuth
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx

# AWS Credentials
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cloud_deploy

# API
PORT=8000
SECRET_KEY=change-in-production
```

## 🚀 Deployment Flow
```
1. Push to GitHub
    ↓
2. GitHub Actions webhook triggered
    ↓
3. Detect app type (Python/Node/Static)
    ↓
4. Build Docker image
    ↓
5. Push to ECR
    ↓
6. Create K8s namespace
    ↓
7. Deploy pods
    ↓
8. Configure Ingress + TLS
    ↓
9. Start monitoring
    ↓
10. App online! 🎉
```

## 📈 Supported App Types
- ✅ **Python**: FastAPI, Flask, Django
- ✅ **Node.js**: Express, Next.js, Nuxt
- ✅ **Static**: HTML/CSS/JS sites

## 💰 Cost Estimate (Monthly)
| Component | Cost |
|-----------|------|
| EKS Cluster | $73 |
| EC2 Nodes (3) | $90 |
| RDS PostgreSQL | $50 |
| NAT Gateway | $30 |
| **Total** | **~$250** |

## 🐛 Troubleshooting

**API not responding?**
```bash
docker-compose logs api
# Check: PORT=8000 in .env
```

**Database connection error?**
```bash
docker-compose logs postgres
# Wait 5s for postgres to start
```

**Build failures?**
```bash
docker build -t test-image .
# Check: requirements.txt exists
```

**K8s deployment stuck?**
```bash
kubectl describe pod -n app-{id} {pod-name}
kubectl logs -n app-{id} {pod-name}
```

## 📚 Full Documentation
- Complete setup: [GETTING_STARTED.md](./GETTING_STARTED.md)
- Architecture: [README.md](./README.md)
- Terraform: [terraform/README.md](./terraform/README.md)
- Kubernetes: [kubernetes/README.md](./kubernetes/README.md)
- Monitoring: [monitoring/README.md](./monitoring/README.md)

## ❓ Need Help?
1. Check [GETTING_STARTED.md](./GETTING_STARTED.md)
2. See [CONTRIBUTING.md](./CONTRIBUTING.md) for dev guide
3. Review [INDEX.md](./INDEX.md) for full project map
4. Check troubleshooting in main docs

## 🎯 Your Next Step
```bash
./setup.sh
docker-compose up -d
uvicorn control_plane.main:app --reload
```

Then visit: **http://localhost:8000/docs** 🚀

---

**Version**: 1.0.0 | **Status**: ✅ Production Ready | **License**: MIT
