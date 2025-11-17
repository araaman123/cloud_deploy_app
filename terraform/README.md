# DevOps Automation SaaS - AWS Infrastructure

Production-ready Terraform configuration for deploying the Cloud Deploy platform to AWS ECS with managed PostgreSQL database.

## Architecture Overview

```
Internet → ALB (Port 80) → ECS Fargate Tasks → RDS PostgreSQL
```

### Components
- **ECS Fargate:** Serverless container orchestration (2-10 tasks)
- **ALB:** Application Load Balancer with automatic health checks
- **RDS PostgreSQL:** Managed database with automated backups
- **ECR:** Private Docker container registry
- **VPC:** Isolated network with public/private subnets
- **Auto-Scaling:** CPU and memory-based scaling policies

## Prerequisites

- **Terraform** >= 1.0
- **AWS CLI** configured with credentials  
- **Docker** (for building images)
- **AWS Account** with appropriate IAM permissions

## Quick Start

### 1. Create terraform.tfvars

```bash
cd terraform

cat > terraform.tfvars << 'EOF'
aws_region          = "us-east-1"
environment         = "production"
cluster_name        = "cloud-deploy"
db_username         = "postgres"
db_password         = "YOUR-SECURE-PASSWORD-HERE"
node_count          = 2
instance_type       = "t3.medium"
EOF
```

### 2. Initialize & Deploy

```bash
# Initialize Terraform
terraform init

# Review infrastructure plan
terraform plan

# Deploy infrastructure (15-20 minutes)
terraform apply
```

### 3. Build & Push Docker Image

```bash
# Get ECR URL
ECR_URL=$(terraform output -raw ecr_registry_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URL

# Build image
docker build -t cloud-deploy-app ..

# Tag and push
docker tag cloud-deploy-app:latest $ECR_URL:latest
docker push $ECR_URL:latest
```

### 4. Access Application

```bash
# Get application URL
terraform output deployment_url

# Open in browser: http://<ALB-DNS>/ui
```

## Configuration Files

- **main.tf** - AWS provider and Terraform configuration
- **variables.tf** - All input variables with defaults
- **outputs.tf** - ECS cluster, ALB, database endpoints
- **ecs.tf** - ECS cluster, service, task definitions, auto-scaling
- **iam.tf** - IAM roles and permissions
- **alb.tf** - Application Load Balancer and security groups
- **rds.tf** - PostgreSQL database with backups
- **ecr.tf** - Docker container registry
- **vpc.tf** - VPC, subnets, and networking
- **network.tf** - Network configuration

## Key Variables

```hcl
aws_region          = "us-east-1"      # AWS region
environment         = "production"     # Environment name
cluster_name        = "cloud-deploy"   # Resource prefix
db_username         = "postgres"       # Database user
db_password         = "..."            # Database password (REQUIRED)
node_count          = 2                # Desired ECS tasks
min_node_count      = 2                # Minimum tasks (auto-scaling)
max_node_count      = 10               # Maximum tasks (auto-scaling)
instance_type       = "t3.medium"      # EC2 instance type
db_instance_class   = "db.t3.micro"    # RDS instance type
db_storage_size     = 20               # RDS storage (GB)
```

## Outputs

After deployment:

```bash
# Get outputs
terraform output

# Key outputs:
terraform output deployment_url       # App UI
terraform output api_endpoint         # API base URL
terraform output alb_dns_name         # Load balancer DNS
terraform output rds_endpoint         # Database endpoint
terraform output ecr_registry_url     # Docker registry
```

## Cost Analysis

| Component | Cost/Month |
|-----------|-----------|
| ECS Fargate (2-3 tasks) | $50-70 |
| RDS PostgreSQL | $15-20 |
| ALB | $15 |
| Data Transfer | $5-10 |
| **Total** | **$85-115** |

To optimize costs, reduce `node_count` or use `t3.small` instance type (not recommended for production).

## Monitoring & Logs

### CloudWatch Logs

```bash
# View application logs
aws logs tail /ecs/cloud-deploy --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/cloud-deploy \
  --filter-pattern "ERROR"
```

### ECS Cluster Status

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)

# List tasks
aws ecs list-tasks --cluster $CLUSTER

# Describe tasks
aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks <task-arn>
```

### Database Status

```bash
# Check RDS instance
aws rds describe-db-instances \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address}'
```

## Auto-Scaling

ECS service automatically scales based on:
- **CPU > 70%** → Scale up
- **Memory > 80%** → Scale up
- **CPU < 30%** → Scale down

To adjust limits:

```hcl
# In terraform.tfvars
min_node_count = 2
max_node_count = 20

# Then reapply
terraform apply
```

## Security

### Implemented
✅ VPC isolation (private subnets for RDS/ECS)
✅ Security group rules (least privilege)
✅ Database encryption at rest
✅ IAM role-based access
✅ Automated backups

### Recommended
🔒 Enable HTTPS with ACM certificate
🔒 Add AWS WAF for DDoS protection
🔒 Enable CloudTrail for auditing
🔒 Use AWS Secrets Manager for credentials
🔒 Regular security assessments

## Cleanup

⚠️ Delete all resources:

```bash
terraform destroy

# Confirm deletion when prompted
```

This will delete ECS, RDS, ALB, VPC, and all other resources.

## Troubleshooting

### Issue: Credentials not found

```bash
aws sts get-caller-identity
aws configure  # If needed
```

### Issue: ECS task fails to start

```bash
# Check logs
aws logs tail /ecs/cloud-deploy --follow

# Common causes:
# - IMAGE_PULL_BACK_OFF → Image not in ECR yet
# - DATABASE_CONNECTION_ERROR → RDS security group
```

### Issue: ALB shows unhealthy targets

```bash
# Verify security group allows ALB → ECS
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=cloud-deploy-ecs-tasks-sg"

# Check health check path
curl http://<ALB-DNS>/health
```

## Advanced: HTTPS with Custom Domain

### 1. Request ACM Certificate

```bash
aws acm request-certificate \
  --domain-name example.com \
  --validation-method DNS
```

### 2. Update ALB Listener

```hcl
# Add to alb.tf
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = "arn:aws:acm:..."
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

## Further Documentation

- **Deployment Guide:** See `../DEPLOYMENT_GUIDE.md`
- **AWS ECS:** https://docs.aws.amazon.com/ecs/
- **Terraform AWS Provider:** https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Platform Guide:** See `../README.md`

---

**Updated:** November 2025
**Terraform:** >= 1.0
**AWS Provider:** >= 5.0
