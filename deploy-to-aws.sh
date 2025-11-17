#!/bin/bash
# Cloud Deploy Platform - AWS Deployment Script
# Usage: ./deploy-to-aws.sh

set -e

AWS_REGION=${1:-us-east-1}
ENVIRONMENT=${2:-production}

echo "========================================"
echo "Cloud Deploy Platform - AWS Deployment"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

for tool in terraform aws docker; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool not found - please install"
        exit 1
    fi
    echo "✅ $tool installed"
done

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured - run: aws configure"
    exit 1
fi
echo "✅ AWS credentials configured"

# Get database password
echo ""
read -s -p "Enter secure database password (or press Enter for auto-generated): " DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32 | head -c 32)
    echo "Auto-generated password: $DB_PASSWORD"
fi

# Create terraform.tfvars
echo ""
echo "Creating Terraform configuration..."

cat > terraform/terraform.tfvars << EOF
aws_region          = "$AWS_REGION"
environment         = "$ENVIRONMENT"
cluster_name        = "cloud-deploy"
db_username         = "postgres"
db_password         = "$DB_PASSWORD"
node_count          = 2
instance_type       = "t3.medium"
max_node_count      = 10
min_node_count      = 2
db_instance_class   = "db.t3.micro"
db_storage_size     = 20
EOF

echo "✅ terraform.tfvars created"

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
cd terraform
terraform init
cd ..

# Plan infrastructure
echo ""
echo "Planning infrastructure..."
cd terraform
terraform plan -out=plan.tfplan
cd ..

# Confirm deployment
echo ""
echo "Infrastructure Details:"
echo "  AWS Region: $AWS_REGION"
echo "  Environment: $ENVIRONMENT"
echo "  ECS Tasks: 2 (auto-scaling to 10)"
echo "  Database: PostgreSQL"
echo "  Estimated Cost: ~\$85-115/month"
echo ""

read -p "Deploy infrastructure? (yes/no): " CONTINUE
if [ "$CONTINUE" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Apply Terraform
echo ""
echo "Deploying infrastructure (this takes ~15-20 minutes)..."
cd terraform
terraform apply plan.tfplan
cd ..

# Get outputs
echo ""
echo "Deployment complete! Getting endpoints..."
cd terraform
ECR_URL=$(terraform output -raw ecr_registry_url)
ALB_URL=$(terraform output -raw alb_url)
APP_URL=$(terraform output -raw deployment_url)
cd ..

# Build and push Docker image
echo ""
echo "Building Docker image..."
docker build -t cloud-deploy-app .

# Login to ECR
echo ""
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL

# Tag and push image
echo ""
echo "Pushing image to ECR..."
docker tag cloud-deploy-app:latest "$ECR_URL:latest"
docker push "$ECR_URL:latest"

# Success
echo ""
echo "========================================"
echo "✅ Deployment successful!"
echo "========================================"
echo ""
echo "Your application is ready at:"
echo "  Platform UI: $APP_URL"
echo "  API Endpoint: $ALB_URL/api/v1"
echo "  Health Check: $ALB_URL/health"
echo ""
echo "Next steps:"
echo "  1. Open $APP_URL in your browser"
echo "  2. Create an app with a GitHub repo URL"
echo "  3. Trigger a deployment"
echo "  4. Watch it deploy in real-time"
echo ""
echo "View logs:"
echo "  aws logs tail /ecs/cloud-deploy --follow --region $AWS_REGION"
echo ""
echo "Cleanup (delete all resources):"
echo "  cd terraform && terraform destroy"
echo ""
echo "Documentation:"
echo "  Deployment: ./DEPLOYMENT_GUIDE.md"
echo "  Infrastructure: ./terraform/README.md"
echo "  Platform: ./README.md"
echo ""
