# Getting Started Guide

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Terraform >= 1.0
- kubectl CLI
- AWS CLI configured

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cloud-deploy-app.git
cd cloud-deploy-app
```

### 2. Run Setup Script

**On macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```batch
setup.bat
```

### 3. Configure Environment

Copy and update `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

### 4. Start Development Services

```bash
docker-compose up -d
```

### 5. Run the Control Plane

```bash
uvicorn control_plane.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

### Control Plane (FastAPI)

The main API server that manages:
- User authentication (GitHub OAuth)
- Application deployments
- Infrastructure provisioning
- Logs & metrics retrieval

**Key Endpoints:**
- `POST /api/v1/auth/github` - GitHub authentication
- `POST /api/v1/apps` - Create new deployment
- `GET /api/v1/apps` - List deployments
- `GET /api/v1/logs/{app_id}` - Get application logs
- `GET /api/v1/metrics/{app_id}` - Get metrics

### Terraform Modules

Infrastructure as Code for AWS:
- **VPC** - Virtual Private Cloud with public/private subnets
- **EKS** - Kubernetes cluster with auto-scaling
- **RDS** - PostgreSQL database
- **ECR** - Container registry
- **S3** - Object storage

### Kubernetes Orchestration

Automated deployment of applications with:
- Auto-generated namespaces per app
- Deployment manifests
- Service exposure
- Ingress with TLS
- Horizontal Pod Autoscaling
- ServiceMonitor for Prometheus

### Docker Builder

Auto-detection and building of:
- **Python** apps (FastAPI, Flask, Django)
- **Node.js** apps (Express, Next.js)
- **Static** sites

### Monitoring Stack

- **Prometheus** - Metrics collection
- **Grafana** - Visualization dashboards
- **ELK Stack** - Log aggregation
- **AlertManager** - Alert routing

## Deployment Flow

1. **User** connects GitHub repository
2. **Platform** detects app type (Python/Node/Static)
3. **Terraform** provisions AWS infrastructure
4. **Docker** builds application image
5. **Image** is pushed to ECR
6. **Kubernetes** creates namespace and deploys app
7. **cert-manager** provisions TLS certificate
8. **Prometheus** begins collecting metrics
9. **Kibana** indexes application logs

## Example: Deploy a Python Flask App

### 1. Create a Simple Flask App

```bash
mkdir my-flask-app
cd my-flask-app
```

Create `requirements.txt`:
```
Flask==2.3.0
gunicorn==21.0.0
```

Create `main.py`:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

@app.route('/')
def hello():
    return {'message': 'Hello from Flask!'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 2. Push to GitHub

```bash
git add .
git commit -m "Initial Flask app"
git push origin main
```

### 3. Deploy via Platform

```bash
curl -X POST http://localhost:8000/api/v1/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-flask-app",
    "github_repo_url": "https://github.com/yourusername/my-flask-app",
    "app_type": "python"
  }'
```

### 4. Monitor Deployment

```bash
curl http://localhost:8000/api/v1/apps/my-flask-app
```

## Viewing Logs & Metrics

### Logs
```bash
curl http://localhost:8000/api/v1/logs/{app_id}
```

### Metrics
```bash
curl http://localhost:8000/api/v1/metrics/{app_id}
```

### Real-time Dashboard
- **Grafana**: http://localhost:3001
- **Kibana**: http://localhost:5601
- **Prometheus**: http://localhost:9090

## Database

### PostgreSQL

Database is automatically initialized with tables for:
- Users
- Applications
- Deployments
- Logs
- Metrics
- API Keys

Access PostgreSQL:
```bash
psql postgresql://postgres:postgres@localhost:5432/cloud_deploy
```

## Testing

Run unit tests:
```bash
pytest control_plane/tests/
```

Run integration tests:
```bash
pytest control_plane/tests/integration/
```

## Production Deployment

### 1. Provision AWS Infrastructure

```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 2. Deploy Control Plane to Kubernetes

```bash
# Build and push Docker image
docker build -t your-registry/control-plane:v1.0.0 .
docker push your-registry/control-plane:v1.0.0

# Deploy via Helm or kubectl
kubectl apply -f control_plane/k8s/deployment.yaml
```

### 3. Configure GitHub OAuth

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL
4. Update `.env` with credentials

### 4. Setup TLS Certificates

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.crds.yaml
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f monitoring/cert-issuer.yaml
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/cloud_deploy -c "SELECT version();"
```

### Kubernetes Errors

```bash
# Check deployment status
kubectl get deployments -n app-{id}

# View pod logs
kubectl logs -n app-{id} deployment/{app-name}

# Debug pod
kubectl describe pod -n app-{id} {pod-name}
```

### Build Failures

```bash
# Check Docker build logs
docker build -t test-image .

# Verify Dockerfile syntax
docker build -f Dockerfile.python --dry-run .
```

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit pull request

## Support

- 📖 Documentation: `docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## License

MIT License
