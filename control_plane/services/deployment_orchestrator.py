"""Deployment orchestration service."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import subprocess
import uuid
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from models.database import Deployment, Application, DeploymentStatus
from database.init import SessionLocal

logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates the complete deployment pipeline."""
    
    def __init__(self):
        self.deployments_in_progress = {}
    
    async def execute_deployment(self, deployment_id: str, app_id: str) -> None:
        """Execute full deployment pipeline."""
        db = SessionLocal()
        try:
            deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
            app = db.query(Application).filter(Application.id == app_id).first()
            
            if not deployment or not app:
                logger.error(f"Deployment {deployment_id} or app {app_id} not found")
                return
            
            self.deployments_in_progress[deployment_id] = True
            
            # Update deployment status
            deployment.status = "building"
            db.commit()
            
            logger.info(f"Starting deployment {deployment_id} for app {app.name}")
            
            # Step 1: Clone repository
            await self._step_clone_repository(deployment, app, db)
            
            # Step 2: Detect app type
            await self._step_detect_app_type(deployment, app, db)
            
            # Step 3: Build Docker image
            await self._step_build_docker_image(deployment, app, db)
            
            # Step 4: Push to registry
            await self._step_push_to_registry(deployment, app, db)
            
            # Step 5: Create Kubernetes namespace
            await self._step_create_namespace(deployment, app, db)
            
            # Step 6: Deploy application
            await self._step_deploy_application(deployment, app, db)
            
            # Step 7: Configure TLS
            await self._step_configure_tls(deployment, app, db)
            
            # Mark deployment as complete
            deployment.status = "running"
            deployment.completed_at = datetime.utcnow()
            app.status = "running"
            db.commit()
            
            logger.info(f"Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {str(e)}")
            if deployment:
                deployment.status = "failed"
                deployment.error_message = str(e)
                deployment.completed_at = datetime.utcnow()
                db.commit()
        finally:
            self.deployments_in_progress.pop(deployment_id, None)
            db.close()
    
    async def _step_clone_repository(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 1: Clone the GitHub repository."""
        try:
            logger.info(f"Cloning repository {app.github_repo_url}...")
            
            # Simulate cloning (in production, use GitPython or subprocess)
            clone_dir = f"/tmp/{app.id}"
            
            await asyncio.sleep(1)  # Simulate work
            
            logger.info(f"Repository cloned to {clone_dir}")
            app.image_uri = clone_dir
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    async def _step_detect_app_type(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 2: Detect application type."""
        try:
            logger.info(f"Detecting app type for {app.name}...")
            
            # App type is already set, but we could auto-detect from repo
            detected_type = app.app_type.value if app.app_type else "python"
            
            await asyncio.sleep(0.5)  # Simulate detection
            
            logger.info(f"Detected app type: {detected_type}")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to detect app type: {str(e)}")
            raise
    
    async def _step_build_docker_image(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 3: Build Docker image."""
        try:
            logger.info(f"Building Docker image for {app.name}...")
            
            # Simulate Docker build
            image_tag = f"{app.name}:{deployment.commit_hash[:8]}"
            
            await asyncio.sleep(2)  # Simulate build time
            
            deployment.image_uri = image_tag
            db.commit()
            
            logger.info(f"Docker image built: {image_tag}")
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {str(e)}")
            raise
    
    async def _step_push_to_registry(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 4: Push image to container registry."""
        try:
            logger.info(f"Pushing image to registry...")
            
            # Simulate push to ECR/Docker Hub
            registry_uri = f"registry.example.com/{app.name}:{deployment.commit_hash[:8]}"
            
            await asyncio.sleep(1.5)  # Simulate push time
            
            logger.info(f"Image pushed to registry: {registry_uri}")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to push to registry: {str(e)}")
            raise
    
    async def _step_create_namespace(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 5: Create Kubernetes namespace."""
        try:
            logger.info(f"Creating Kubernetes namespace {app.namespace}...")
            
            # Simulate kubectl create namespace
            await asyncio.sleep(0.5)
            
            logger.info(f"Namespace created: {app.namespace}")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create namespace: {str(e)}")
            raise
    
    async def _step_deploy_application(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 6: Deploy application to Kubernetes."""
        try:
            logger.info(f"Deploying {app.name} to Kubernetes...")
            
            # Simulate kubectl apply
            await asyncio.sleep(2)  # Simulate deployment time
            
            logger.info(f"Application deployed successfully")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to deploy application: {str(e)}")
            raise
    
    async def _step_configure_tls(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 7: Configure TLS certificate."""
        try:
            if not app.tls_enabled:
                logger.info("TLS disabled, skipping configuration")
                return
            
            logger.info(f"Configuring TLS for {app.domain}...")
            
            # Simulate cert provisioning (Let's Encrypt, etc.)
            await asyncio.sleep(1)
            
            logger.info(f"TLS certificate configured for {app.domain}")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to configure TLS: {str(e)}")
            raise


# Global orchestrator instance
orchestrator = DeploymentOrchestrator()


async def start_deployment(deployment_id: str, app_id: str) -> None:
    """Start a deployment asynchronously."""
    # Run in background without blocking
    asyncio.create_task(orchestrator.execute_deployment(deployment_id, app_id))
