# DevOps Automation SaaS - AWS Infrastructure

This directory contains Terraform modules for automatically provisioning cloud infrastructure.

## Overview

The platform uses Terraform to provision:

1. **VPC & Networking**
   - Custom VPC with public/private subnets
   - Security groups for EKS, RDS, etc.
   - Internet Gateway and NAT Gateway

2. **EKS Cluster**
   - Amazon Elastic Kubernetes Service
   - Managed node groups
   - Auto-scaling configuration

3. **Database**
   - Amazon RDS for PostgreSQL
   - Automated backups
   - Multi-AZ deployment

4. **Container Registry**
   - Amazon ECR for Docker images
   - Lifecycle policies for image cleanup

5. **Storage**
   - S3 buckets for application data
   - CloudFront CDN for static assets

## Directory Structure

```
terraform/
├── main.tf              # Root configuration
├── variables.tf         # Input variables
├── outputs.tf          # Output values
├── vpc/                # VPC and networking
├── eks/                # Kubernetes cluster
├── rds/                # Database
├── ecr/                # Container registry
└── s3/                 # Storage
```

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with credentials
- kubectl CLI
- helm CLI (optional)

## Usage

1. **Initialize Terraform**
   ```bash
   cd terraform
   terraform init
   ```

2. **Plan Infrastructure**
   ```bash
   terraform plan -out=tfplan
   ```

3. **Apply Configuration**
   ```bash
   terraform apply tfplan
   ```

4. **Get Outputs**
   ```bash
   terraform output
   ```

## Configuration Variables

Key variables in `terraform.tfvars`:

```hcl
aws_region           = "us-east-1"
cluster_name         = "cloud-deploy-eks"
node_count           = 3
instance_type        = "t3.medium"
db_username          = "postgres"
db_password          = "secure-password"  # Change this!
```

## Cost Estimation

Approximate monthly costs:

- EKS Cluster: $73
- EC2 Nodes (3x t3.medium): $90
- RDS PostgreSQL: $50
- NAT Gateway: $30
- **Total: ~$250/month**

## Cleanup

To remove all infrastructure:

```bash
terraform destroy
```

## Notes

- All resources are tagged with `Environment` and `ManagedBy` labels
- State file is stored locally (configure S3 backend for production)
- Enable versioning on S3 buckets for state file protection
