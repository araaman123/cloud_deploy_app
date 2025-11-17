# DevOps Automation SaaS Platform

A mini-Vercel for backend applications. Automatically deploy Python/Node apps to Kubernetes with one GitHub push.

## Features

✨ **One-Click Deployments**
- Connect GitHub repo
- Auto-detect app type (Python/Node)
- Generate Docker image
- Deploy to Kubernetes

🚀 **Automatic Infrastructure**
- AWS provisioning via Terraform
- EKS cluster management
- Auto-scaling configuration
- TLS certificates via cert-manager

📊 **Monitoring & Logs**
- Prometheus metrics
- ELK stack for logs
- Real-time dashboards
- Application performance monitoring

🔐 **Security & DevOps**
- GitHub OAuth authentication
- CI/CD pipeline automation
- Namespace isolation
- API key management

## Tech Stack

- **Control Plane**: Python FastAPI
- **Infrastructure**: Terraform (AWS)
- **Orchestration**: Kubernetes (EKS)
- **Container Registry**: AWS ECR
- **Monitoring**: Prometheus, Grafana, ELK
- **CI/CD**: GitHub Actions
- **Database**: PostgreSQL

## Project Structure

```
cloud_deploy_app/
├── control_plane/        # FastAPI application & business logic
├── terraform/            # AWS infrastructure as code
├── kubernetes/           # K8s manifests & deployment logic
├── docker/              # Docker image builders
├── github_actions/      # CI/CD workflows
├── monitoring/          # Prometheus, Grafana, ELK configs
├── database/            # PostgreSQL schemas & migrations
└── .github/             # GitHub configuration
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r control_plane/requirements.txt
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

3. **Start the Control Plane**
   ```bash
   uvicorn control_plane.main:app --reload
   ```

4. **Deploy an App**
   - Connect GitHub repo via OAuth
   - Select backend type (Python/Node)
   - Platform auto-deploys with custom domain & TLS

## Monetization

- **Pricing Tiers**:
  - Starter: $15/mo (1 app, 1 GB RAM, 1 CPU)
  - Pro: $49/mo (5 apps, 4 GB RAM, 2 CPUs)
  - Enterprise: $99/mo (unlimited apps, custom resources)

- **Revenue Model**: SaaS subscriptions with metered usage

## Development Roadmap

- [ ] Core API & user authentication
- [ ] Terraform AWS provisioning
- [ ] Kubernetes deployment engine
- [ ] GitHub Actions integration
- [ ] Docker image builder
- [ ] Monitoring dashboard
- [ ] Payment processing (Stripe)
- [ ] Custom domain management
- [ ] Scaling & multi-region support

## API Endpoints

### Authentication
- `POST /auth/github` - GitHub OAuth callback
- `POST /auth/logout` - Logout

### Applications
- `POST /apps` - Create new deployment
- `GET /apps` - List user's deployments
- `GET /apps/{app_id}` - Get deployment details
- `DELETE /apps/{app_id}` - Delete deployment

### Deployment Management
- `POST /apps/{app_id}/deploy` - Trigger deployment
- `GET /apps/{app_id}/logs` - Get application logs
- `GET /apps/{app_id}/metrics` - Get metrics
- `PATCH /apps/{app_id}/scale` - Scale resources

## Documentation

- See `control_plane/README.md` for API documentation
- See `terraform/README.md` for infrastructure setup
- See `kubernetes/README.md` for deployment configs

## License

MIT License - see LICENSE file for details
