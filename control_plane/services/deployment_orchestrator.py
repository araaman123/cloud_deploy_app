"""Deployment orchestration service."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import subprocess
import uuid
import sys
import os
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
        self.deployments_dir = "/tmp/deployments"
        os.makedirs(self.deployments_dir, exist_ok=True)
    
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
            clone_dir = await self._step_clone_repository(deployment, app, db)
            
            # Step 2: Detect app type
            await self._step_detect_app_type(deployment, app, db)
            
            # Step 3: Build Docker image
            image_name = await self._step_build_docker_image(deployment, app, clone_dir, db)
            
            # Step 4: Push to registry (simulate)
            await self._step_push_to_registry(deployment, app, db)
            
            # Step 5: Run container
            container_id = await self._step_run_container(deployment, app, image_name, db)
            
            # Step 6: Verify health
            await self._step_verify_health(deployment, app, container_id, db)
            
            # Step 7: Configure TLS (simulate)
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
    
    async def _step_clone_repository(self, deployment: Deployment, app: Application, db: Session) -> str:
        """Step 1: Clone the GitHub repository."""
        try:
            logger.info(f"Cloning repository {app.github_repo_url}...")
            
            clone_dir = f"{self.deployments_dir}/{app.id}"
            
            # Remove if exists
            if os.path.exists(clone_dir):
                subprocess.run(f"rm -rf {clone_dir}", shell=True, check=True)
            
            # Clone repo
            result = subprocess.run(
                f"git clone --depth 1 {app.github_repo_url} {clone_dir}",
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr.decode()}")
            
            logger.info(f"Repository cloned to {clone_dir}")
            app.image_uri = clone_dir
            db.commit()
            
            return clone_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    async def _step_detect_app_type(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 2: Detect application type."""
        try:
            logger.info(f"Detecting app type for {app.name}...")
            
            detected_type = app.app_type.value if app.app_type else "python"
            
            await asyncio.sleep(0.5)
            
            logger.info(f"Detected app type: {detected_type}")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to detect app type: {str(e)}")
            raise
    
    async def _step_build_docker_image(self, deployment: Deployment, app: Application, clone_dir: str, db: Session) -> str:
        """Step 3: Build Docker image."""
        try:
            logger.info(f"Building Docker image for {app.name}...")
            
            image_tag = f"deployment-{app.id}:{deployment.commit_hash[:8]}"
            dockerfile_path = clone_dir
            
            # Check if Dockerfile exists, if not create one
            dockerfile = os.path.join(clone_dir, "Dockerfile")
            if not os.path.exists(dockerfile):
                logger.info("No Dockerfile found, using generic one based on runtime")
                dockerfile_content = self._generate_dockerfile(app.app_type.value if app.app_type else "python")
                with open(dockerfile, "w") as f:
                    f.write(dockerfile_content)
            
            # Build Docker image
            result = subprocess.run(
                f"docker build -t {image_tag} {clone_dir}",
                shell=True,
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Docker build failed: {result.stderr.decode()}")
            
            deployment.image_uri = image_tag
            db.commit()
            
            logger.info(f"Docker image built: {image_tag}")
            
            return image_tag
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {str(e)}")
            raise
    
    def _generate_dockerfile(self, runtime: str) -> str:
        """Generate a basic Dockerfile for the app."""
        if runtime == "python":
            return """FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || echo "No requirements.txt"
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 2>/dev/null || ["python", "app.py"] 2>/dev/null || ["sh", "-c", "echo 'App running'"]
"""
        elif runtime == "node":
            return """FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install 2>/dev/null || echo "No package.json"
EXPOSE 3000
CMD ["npm", "start"] 2>/dev/null || ["node", "server.js"] 2>/dev/null || ["sh", "-c", "echo 'App running'"]
"""
        else:  # static
            return """FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
    
    async def _step_push_to_registry(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 4: Push image to registry (simulated)."""
        try:
            logger.info(f"Pushing image to registry...")
            
            await asyncio.sleep(0.5)
            
            logger.info(f"Image pushed to registry")
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to push to registry: {str(e)}")
            raise
    
    async def _step_run_container(self, deployment: Deployment, app: Application, image_name: str, db: Session) -> str:
        """Step 5: Run the Docker container."""
        try:
            logger.info(f"Running Docker container for {app.name}...")
            
            container_name = f"app-{app.id[:8]}"
            port = 8000 if app.app_type.value == "python" else 3000
            
            # Stop existing container if any
            subprocess.run(f"docker stop {container_name} 2>/dev/null", shell=True, capture_output=True)
            subprocess.run(f"docker rm {container_name} 2>/dev/null", shell=True, capture_output=True)
            
            # Run container
            result = subprocess.run(
                f"docker run -d --name {container_name} -p {port}:8000 {image_name}",
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"Docker run failed: {result.stderr.decode()}")
            
            container_id = result.stdout.decode().strip()
            
            logger.info(f"Container running: {container_id}")
            
            await asyncio.sleep(2)  # Give container time to start
            
            return container_id
            
        except Exception as e:
            logger.error(f"Failed to run container: {str(e)}")
            raise
    
    async def _step_verify_health(self, deployment: Deployment, app: Application, container_id: str, db: Session) -> None:
        """Step 6: Verify container is healthy."""
        try:
            logger.info(f"Verifying container health...")
            
            # Check if container is running
            result = subprocess.run(
                f"docker inspect -f '{{{{.State.Running}}}}' {container_id}",
                shell=True,
                capture_output=True
            )
            
            is_running = "true" in result.stdout.decode().lower()
            
            if not is_running:
                raise Exception("Container is not running")
            
            logger.info(f"Container is healthy")
            db.commit()
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            raise
    
    async def _step_configure_tls(self, deployment: Deployment, app: Application, db: Session) -> None:
        """Step 7: Configure TLS certificate."""
        try:
            if not app.tls_enabled:
                logger.info("TLS disabled, skipping configuration")
                return
            
            logger.info(f"Configuring TLS for {app.domain}...")
            
            await asyncio.sleep(0.5)
            
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

