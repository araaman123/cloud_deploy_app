output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "alb_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.app.dns_name}"
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "ecr_registry_url" {
  description = "ECR registry URL"
  value       = aws_ecr_repository.app.repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "deployment_url" {
  description = "Complete URL to access deployed platform"
  value       = "http://${aws_lb.app.dns_name}/ui"
}

output "api_endpoint" {
  description = "API endpoint"
  value       = "http://${aws_lb.app.dns_name}/api/v1"
}

