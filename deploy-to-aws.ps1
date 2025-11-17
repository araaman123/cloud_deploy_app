#!/usr/bin/env powershell
# Cloud Deploy Platform - AWS Deployment Script
# Usage: .\deploy-to-aws.ps1

param(
    [string]$AwsRegion = "us-east-1",
    [string]$Environment = "production",
    [string]$DbPassword = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cloud Deploy Platform - AWS Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$checks = @{
    "Terraform" = { terraform version | Select-String "Terraform v" }
    "AWS CLI" = { aws --version }
    "Docker" = { docker --version }
}

foreach ($tool in $checks.Keys) {
    try {
        & $checks[$tool] | Out-Null
        Write-Host "✅ $tool installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $tool not found - please install" -ForegroundColor Red
        exit 1
    }
}

# Check AWS credentials
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS credentials configured" -ForegroundColor Green
}
catch {
    Write-Host "❌ AWS credentials not configured - run: aws configure" -ForegroundColor Red
    exit 1
}

# Get database password if not provided
if (-not $DbPassword) {
    $DbPassword = Read-Host "Enter secure database password (or press Enter for auto-generated)" -AsSecureString
    if ($DbPassword.Length -eq 0) {
        $DbPassword = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString())) | Select-Object -First 32
        Write-Host "Auto-generated password: $DbPassword" -ForegroundColor Yellow
    }
    else {
        $DbPassword = [System.Net.NetworkCredential]::new("", $DbPassword).Password
    }
}

# Create terraform.tfvars
Write-Host ""
Write-Host "Creating Terraform configuration..." -ForegroundColor Yellow

$tfvars = @"
aws_region          = "$AwsRegion"
environment         = "$Environment"
cluster_name        = "cloud-deploy"
db_username         = "postgres"
db_password         = "$DbPassword"
node_count          = 2
instance_type       = "t3.medium"
max_node_count      = 10
min_node_count      = 2
db_instance_class   = "db.t3.micro"
db_storage_size     = 20
"@

Set-Content -Path "terraform/terraform.tfvars" -Value $tfvars
Write-Host "✅ terraform.tfvars created" -ForegroundColor Green

# Initialize Terraform
Write-Host ""
Write-Host "Initializing Terraform..." -ForegroundColor Yellow
Push-Location terraform
terraform init
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform initialization failed" -ForegroundColor Red
    exit 1
}

# Plan infrastructure
Write-Host ""
Write-Host "Planning infrastructure..." -ForegroundColor Yellow
Push-Location terraform
terraform plan -out=plan.tfplan
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform plan failed" -ForegroundColor Red
    exit 1
}

# Confirm deployment
Write-Host ""
Write-Host "Infrastructure Details:" -ForegroundColor Cyan
Write-Host "  AWS Region: $AwsRegion" -ForegroundColor Green
Write-Host "  Environment: $Environment" -ForegroundColor Green
Write-Host "  ECS Tasks: 2 (auto-scaling to 10)" -ForegroundColor Green
Write-Host "  Database: PostgreSQL" -ForegroundColor Green
Write-Host "  Estimated Cost: ~\$85-115/month" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Deploy infrastructure? (yes/no)"
if ($continue -ne "yes") {
    Write-Host "Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

# Apply Terraform
Write-Host ""
Write-Host "Deploying infrastructure (this takes ~15-20 minutes)..." -ForegroundColor Yellow
Push-Location terraform
terraform apply plan.tfplan
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform deployment failed" -ForegroundColor Red
    exit 1
}

# Get outputs
Write-Host ""
Write-Host "Deployment complete! Getting endpoints..." -ForegroundColor Green
Push-Location terraform

$ecr_url = terraform output -raw ecr_registry_url
$alb_url = terraform output -raw alb_url
$app_url = terraform output -raw deployment_url

Pop-Location

# Build and push Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow

docker build -t cloud-deploy-app .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Login to ECR
Write-Host ""
Write-Host "Logging in to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin $ecr_url

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR login failed" -ForegroundColor Red
    exit 1
}

# Tag and push image
Write-Host ""
Write-Host "Pushing image to ECR..." -ForegroundColor Yellow

docker tag cloud-deploy-app:latest "$ecr_url`:latest"
docker push "$ecr_url`:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Image push failed" -ForegroundColor Red
    exit 1
}

# Success
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your application is ready at:" -ForegroundColor Cyan
Write-Host "  Platform UI: $app_url" -ForegroundColor Green
Write-Host "  API Endpoint: $alb_url/api/v1" -ForegroundColor Green
Write-Host "  Health Check: $alb_url/health" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open $app_url in your browser" -ForegroundColor White
Write-Host "  2. Create an app with a GitHub repo URL" -ForegroundColor White
Write-Host "  3. Trigger a deployment" -ForegroundColor White
Write-Host "  4. Watch it deploy in real-time" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  aws logs tail /ecs/cloud-deploy --follow --region $AwsRegion" -ForegroundColor Gray
Write-Host ""
Write-Host "Cleanup (delete all resources):" -ForegroundColor Yellow
Write-Host "  cd terraform && terraform destroy" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  Deployment: ./DEPLOYMENT_GUIDE.md" -ForegroundColor Gray
Write-Host "  Infrastructure: ./terraform/README.md" -ForegroundColor Gray
Write-Host "  Platform: ./README.md" -ForegroundColor Gray
Write-Host ""
