# Cloud Deploy App - AWS Deployment Guide

Complete production deployment guide for deploying to AWS using Terraform.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** (v1.0+)
3. **AWS CLI** configured with credentials
4. **Docker** (for building and pushing images)

### Install Terraform

**Windows (PowerShell):**
```powershell
# Using Chocolatey
choco install terraform

# Or download from https://www.terraform.io/downloads
```

**Mac/Linux:**
```bash
# Using Homebrew
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Or download from https://www.terraform.io/downloads
```

## Deployment Steps

### Step 1: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter your AWS Access Key ID, Secret Access Key, and default region
```

### Step 2: Prepare Terraform Variables

Create `terraform/terraform.tfvars`:

```hcl
aws_region          = "us-east-1"
environment         = "production"
cluster_name        = "cloud-deploy"
db_username         = "postgres"
db_password         = "your-secure-password-here"  # Change this!
node_count          = 2
instance_type       = "t3.medium"
```

**Important:** Use a strong password! Consider using AWS Secrets Manager in production.

### Step 3: Initialize Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# This downloads required providers and sets up the backend
```

### Step 4: Review Infrastructure Plan

```bash
# See what will be created
terraform plan -out=plan.tfplan

# Review the output - it should show:
# - VPC with subnets
# - ECS Cluster
# - RDS PostgreSQL Database
# - ECR Container Registry
# - Application Load Balancer
# - Security Groups
# - IAM Roles
```

### Step 5: Deploy Infrastructure

```bash
# Apply the terraform plan
terraform apply plan.tfplan

# This takes ~15-20 minutes to complete
# Terraform will output the Application URL when done
```

### Step 6: Build and Push Docker Image

After infrastructure is created:

```bash
# Get ECR repository URL from terraform output
ECR_URL=$(terraform output -raw ecr_registry_url)

# Log in to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Build Docker image
docker build -t cloud-deploy-app .

# Tag image
docker tag cloud-deploy-app:latest $ECR_URL:latest

# Push to ECR
docker push $ECR_URL:latest
```

### Step 7: Update ECS Service

The ECS service will pull the latest image within a few minutes. Monitor the deployment:

```bash
# Get cluster and service names
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)

# Check service status
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --region us-east-1

# View task logs
aws logs tail /ecs/cloud-deploy --follow --region us-east-1
```

### Step 8: Access the Application

Once deployment completes:

```bash
# Get the application URL
APP_URL=$(terraform output -raw deployment_url)

# Open in browser or curl
curl $APP_URL
```

The platform is now running at: **`http://<ALB-DNS>/ui`**

## Verify Deployment

### Check ECS Cluster Health

```bash
aws ecs describe-clusters \
  --clusters cloud-deploy-ecs \
  --region us-east-1
```

### Check Running Tasks

```bash
aws ecs list-tasks \
  --cluster cloud-deploy-ecs \
  --region us-east-1

aws ecs describe-tasks \
  --cluster cloud-deploy-ecs \
  --tasks <task-arn> \
  --region us-east-1
```

### Check Database Connectivity

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Test connection from your machine (requires psql)
psql -h $RDS_ENDPOINT -U postgres -d clouddeploy
```

### View Application Logs

```bash
aws logs tail /ecs/cloud-deploy --follow --region us-east-1
```

## End-to-End Testing

Once deployed, test the full workflow:

### 1. Create Application

```bash
APP_URL=$(terraform output -raw api_endpoint)

curl -X POST $APP_URL/apps \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "test-app",
    "repo_url": "https://github.com/YOUR-REPO/YOUR-APP",
    "runtime": "python"
  }'
```

### 2. List Applications

```bash
curl $APP_URL/apps
```

### 3. Trigger Deployment

```bash
# Use the app ID from step 1
APP_ID="<app-id-from-step-1>"

curl -X POST "$APP_URL/deployments/trigger?app_id=$APP_ID&commit_hash=main"
```

### 4. Check Deployment Status

```bash
# Use deployment ID from step 3
DEPLOYMENT_ID="<deployment-id-from-step-3>"

curl $APP_URL/deployments/$DEPLOYMENT_ID
```

### 5. View Logs

All deployment logs are stored in CloudWatch:

```bash
aws logs tail /ecs/cloud-deploy --follow
```

## Scaling

### Auto-Scaling Configuration

The infrastructure includes auto-scaling:

- **Min Instances:** 2 (for high availability)
- **Max Instances:** 10 (configurable)
- **Scale Trigger:** CPU > 70% or Memory > 80%

To adjust:

```hcl
# In terraform/terraform.tfvars
min_node_count = 2
max_node_count = 10
```

Then reapply:

```bash
terraform apply
```

## Monitoring & Logs

### CloudWatch Logs

```bash
# View recent logs
aws logs tail /ecs/cloud-deploy --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/cloud-deploy \
  --filter-pattern "ERROR"
```

### CloudWatch Metrics

View in AWS Console:
1. Go to CloudWatch → Dashboards
2. Search for "cloud-deploy"
3. Monitor CPU, Memory, Network usage

## Cost Optimization

Current setup costs:
- **ECS Fargate:** ~$50-70/month (2-3 tasks)
- **RDS PostgreSQL:** ~$15-20/month (t3.micro)
- **ALB:** ~$15/month
- **Data Transfer:** ~$5-10/month

**Total:** ~$85-115/month

To reduce costs:

```hcl
# Use spot instances for non-production
instance_type = "t3.small"  # Smaller instance type

# Reduce task count
desired_count = 1  # Not recommended for production
```

## Cleanup

To destroy all infrastructure and stop billing:

```bash
cd terraform

# Review what will be deleted
terraform plan -destroy

# Delete all resources
terraform destroy

# Confirm when prompted
```

## Troubleshooting

### Issue: "Credentials not found"

```bash
# Check AWS credentials
aws sts get-caller-identity

# If not set, configure:
aws configure
```

### Issue: ECS Task fails to start

```bash
# Check CloudWatch logs
aws logs tail /ecs/cloud-deploy --follow

# Look for DATABASE_URL or image pull errors
```

### Issue: Database connection refused

```bash
# Verify RDS security group allows ECS access
# Check that RDS is running
aws rds describe-db-instances --query 'DBInstances[0].DBInstanceStatus'

# Should return: "available"
```

### Issue: ECR image not found

```bash
# Verify image was pushed
aws ecr describe-images --repository-name cloud-deploy

# If empty, rebuild and push:
docker build -t cloud-deploy-app .
docker tag cloud-deploy-app:latest <ECR_URL>:latest
docker push <ECR_URL>:latest
```

## Production Checklist

- [ ] AWS credentials configured
- [ ] Terraform variables set with strong DB password
- [ ] Infrastructure deployed (terraform apply)
- [ ] Docker image built and pushed to ECR
- [ ] Application accessible at ALB URL
- [ ] Health check returning 200 OK
- [ ] End-to-end deployment test completed
- [ ] CloudWatch logs being collected
- [ ] Monitoring and alerts configured
- [ ] Backup strategy for RDS defined

## Next Steps

1. **Configure HTTPS/SSL:** Add ACM certificate and HTTPS listener
2. **Set up CI/CD:** Automated image builds with GitHub Actions
3. **Add Custom Domain:** Route 53 or your DNS provider
4. **Configure Backups:** RDS automated backups (already enabled)
5. **Set up Alerts:** CloudWatch alarms for CPU, memory, errors

## Support

For issues, check:
1. CloudWatch logs: `/ecs/cloud-deploy`
2. AWS Console → ECS → Clusters → cloud-deploy-ecs
3. GitHub Issues: https://github.com/araaman123/cloud_deploy_app/issues

---

**Congratulations!** Your DevOps platform is now running in production on AWS! 🚀
