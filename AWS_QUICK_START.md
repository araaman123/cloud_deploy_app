# AWS Deployment - Quick Start Guide

Your Cloud Deploy platform is ready to deploy to AWS. Follow these steps to get a public URL.

## Prerequisites

### 1. AWS Account (Free Tier Eligible)
- Go to: https://aws.amazon.com/free/
- Sign up with email and credit card (not charged for free tier)
- Free tier includes: 750 hours ECS Fargate + 20GB RDS + data transfer

### 2. Install AWS CLI

**Windows (Recommended):**
1. Download: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the MSI installer
3. Restart PowerShell

**Verify installation:**
```powershell
aws --version
```

### 3. Get AWS Credentials

1. Go to: https://console.aws.amazon.com/
2. Log in with your AWS account
3. Go to: IAM → Users → Your Username → Security Credentials
4. Click: "Create access key"
5. Save the Access Key ID and Secret Access Key

### 4. Configure AWS CLI

```powershell
aws configure
```

Enter:
- AWS Access Key ID: `AKIA...`
- AWS Secret Access Key: `wJal...`
- Default region: `us-east-1`
- Default output format: `json`

### 5. Verify Configuration

```powershell
aws sts get-caller-identity
```

Should return your AWS account ID.

---

## Deploy to AWS (20 minutes)

### Step 1: Set Database Password

```powershell
$env:DB_PASSWORD = "your-secure-password-123"
```

### Step 2: Initialize Terraform

```powershell
cd terraform
terraform init
```

### Step 3: Plan Infrastructure

```powershell
terraform plan -out=plan.tfplan
```

Review the output - it will show:
- VPC and subnets
- ECS cluster
- RDS database
- ALB load balancer
- ECR registry

### Step 4: Deploy Infrastructure (15 minutes)

```powershell
terraform apply plan.tfplan
```

**Wait for completion!** You'll see:
```
Apply complete! Resources: 45 added
```

### Step 5: Get Infrastructure Outputs

```powershell
# Get all outputs
terraform output

# Or specific outputs
terraform output alb_dns_name
terraform output ecr_registry_url
```

### Step 6: Build and Push Docker Image

```powershell
# Back to repo root
cd ..

# Get ECR URL
$ECR_URL = (cd terraform; terraform output -raw ecr_registry_url; cd ..)

# Login to ECR
aws ecr get-login-password --region us-east-1 | `
  docker login --username AWS --password-stdin $ECR_URL

# Build image
docker build -t cloud-deploy-app .

# Tag image
docker tag cloud-deploy-app:latest "$ECR_URL`:latest"

# Push to ECR
docker push "$ECR_URL`:latest"
```

### Step 7: Access Application

```powershell
# Get application URL
$APP_URL = (cd terraform; terraform output -raw deployment_url; cd ..)
Write-Host "Application URL: $APP_URL"

# Open in browser or curl
Start-Process $APP_URL
```

---

## End-to-End Test on AWS

### 1. Create Application

Open the URL from step 7, or use API:

```powershell
$ALB_URL = "http://<ALB-DNS-from-terraform-output>"

$body = @{
    app_name = "aws-test-app"
    repo_url = "https://github.com/verylou/test_hello_world"
    runtime = "python"
} | ConvertTo-Json

$app = Invoke-WebRequest -Uri "$ALB_URL/api/v1/apps" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body -UseBasicParsing | ConvertFrom-Json

$appId = $app.app.id
Write-Host "App created: $appId"
```

### 2. Trigger Deployment

```powershell
$dep = Invoke-WebRequest -Uri "$ALB_URL/api/v1/deployments/trigger?app_id=$appId" `
  -Method POST -UseBasicParsing | ConvertFrom-Json

$depId = $dep.deployment_id
Write-Host "Deployment: $depId"
```

### 3. Monitor Deployment

```powershell
# Check status
$status = Invoke-WebRequest -Uri "$ALB_URL/api/v1/deployments/$depId" `
  -UseBasicParsing | ConvertFrom-Json

Write-Host "Status: $($status.status)"
```

### 4. View Logs

```powershell
# Stream CloudWatch logs
aws logs tail /ecs/cloud-deploy --follow --region us-east-1
```

Look for:
```
Cloning repository https://github.com/...
Building Docker image...
Deployment completed successfully
```

---

## Verify Everything Works

### Check ECS Cluster

```powershell
aws ecs list-clusters --region us-east-1
aws ecs list-tasks --cluster cloud-deploy-ecs --region us-east-1
```

### Check RDS Database

```powershell
aws rds describe-db-instances `
  --query 'DBInstances[0].{Endpoint:Endpoint.Address,Status:DBInstanceStatus}' `
  --region us-east-1
```

### Check Load Balancer

```powershell
aws elbv2 describe-load-balancers `
  --query 'LoadBalancers[0].DNSName' `
  --region us-east-1
```

### Test Health Endpoint

```powershell
curl "http://<ALB-DNS>/health"
# Should return: {"status":"healthy",...}
```

---

## Troubleshooting

### Issue: Terraform fails to initialize
```
Error: Error loading modules: module not found
```
Solution:
```powershell
cd terraform
rm -r .terraform .terraform.lock.hcl
terraform init
```

### Issue: ECR login fails
```
Error: error getting credentials
```
Solution:
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Re-configure if needed
aws configure
```

### Issue: ECS tasks not starting
```powershell
# Check logs
aws logs tail /ecs/cloud-deploy --follow

# Check task status
aws ecs describe-tasks --cluster cloud-deploy-ecs --tasks <task-arn> --region us-east-1
```

### Issue: Database connection error
```
ERROR: could not connect to server
```
Check security group:
```powershell
aws ec2 describe-security-groups `
  --filters "Name=group-name,Values=cloud-deploy-db-sg" `
  --region us-east-1
```

---

## Costs During Deployment

**Free Tier (12 months):**
- ECS Fargate: 750 hours/month = FREE ✅
- RDS PostgreSQL: 20GB = FREE ✅
- Data transfer: 100GB/month = FREE ✅
- **Total during test: $0**

**After Free Tier:**
- ECS: $30-50/month
- RDS: $15-20/month
- ALB: $15/month
- **Total: $85-115/month**

---

## Success Criteria

When everything works, you'll see:

✅ Platform URL responds with status 200
✅ App created and stored in RDS
✅ Deployment triggered successfully
✅ CloudWatch logs show orchestration steps
✅ Deployment status changes to "running"
✅ All resources visible in AWS console

---

## Next Steps

1. **Test with multiple repos**
   - Try different GitHub repos
   - Test Python, Node.js, Static sites

2. **Monitor costs**
   ```powershell
   # Check spending
   aws ce get-cost-and-usage --time-period Start=2025-11-01,End=2025-11-30 `
     --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE
   ```

3. **Set up alerts**
   - CloudWatch alarms for high CPU/memory
   - SNS notifications for errors

4. **Enable HTTPS**
   - Use AWS Certificate Manager
   - Update load balancer listener

5. **Scale up**
   - Increase task count for higher availability
   - Add more database storage

---

## Demo to Investors

With this deployed, you can show:

1. **Infrastructure Dashboard**
   - AWS Console → ECS → Clusters
   - Show running tasks, logs, metrics

2. **Live Deployment**
   - Open your platform URL
   - Enter GitHub repo
   - Show deployment pipeline execute
   - Show logs in real-time

3. **Production Metrics**
   - CloudWatch dashboard
   - CPU, memory, network usage
   - Deployment history

4. **Database**
   - Show PostgreSQL with stored apps
   - Explain persistence and reliability

---

## Cleanup (Stop Costs)

When you're done testing:

```powershell
cd terraform

# Delete all resources
terraform destroy

# Confirm deletion
# This removes: ECS, RDS, ALB, VPC, etc.
```

---

## Support

- **AWS Documentation:** https://docs.aws.amazon.com
- **Terraform AWS Provider:** https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Platform Docs:** ../README.md
- **GitHub Issues:** https://github.com/araaman123/cloud_deploy_app/issues

---

**Your platform is ready for production! 🚀**

See you on the AWS side!
