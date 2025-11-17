"""Docker image builder and app detector."""

import os
import json
import subprocess
from typing import Tuple, Optional


class AppDetector:
    """Detect application type and configuration."""
    
    @staticmethod
    def detect_language(repo_path: str) -> Tuple[str, dict]:
        """Detect programming language and get app configuration."""
        # Check for Python
        if os.path.exists(os.path.join(repo_path, "requirements.txt")) or \
           os.path.exists(os.path.join(repo_path, "Pipfile")) or \
           os.path.exists(os.path.join(repo_path, "pyproject.toml")):
            return "python", AppDetector._get_python_config(repo_path)
        
        # Check for Node.js
        if os.path.exists(os.path.join(repo_path, "package.json")):
            return "node", AppDetector._get_node_config(repo_path)
        
        # Check for static files
        if os.path.exists(os.path.join(repo_path, "index.html")):
            return "static", AppDetector._get_static_config(repo_path)
        
        raise ValueError("Could not detect application type")
    
    @staticmethod
    def _get_python_config(repo_path: str) -> dict:
        """Get Python application configuration."""
        config = {
            "language": "python",
            "framework": "unknown",
            "port": 8000,
            "start_command": "uvicorn main:app --host 0.0.0.0 --port 8000"
        }
        
        requirements = ""
        if os.path.exists(os.path.join(repo_path, "requirements.txt")):
            with open(os.path.join(repo_path, "requirements.txt")) as f:
                requirements = f.read()
        
        if "fastapi" in requirements:
            config["framework"] = "fastapi"
        elif "flask" in requirements:
            config["framework"] = "flask"
            config["start_command"] = "python -m flask run --host 0.0.0.0 --port 8000"
        elif "django" in requirements:
            config["framework"] = "django"
            config["start_command"] = "python manage.py runserver 0.0.0.0:8000"
        
        return config
    
    @staticmethod
    def _get_node_config(repo_path: str) -> dict:
        """Get Node.js application configuration."""
        config = {
            "language": "node",
            "framework": "unknown",
            "port": 3000,
            "start_command": "npm start"
        }
        
        package_json_path = os.path.join(repo_path, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path) as f:
                package_json = json.load(f)
            
            dependencies = package_json.get("dependencies", {})
            
            if "express" in dependencies:
                config["framework"] = "express"
            elif "next" in dependencies:
                config["framework"] = "next"
            elif "nuxt" in dependencies:
                config["framework"] = "nuxt"
            
            if "scripts" in package_json and "start" in package_json["scripts"]:
                config["start_command"] = package_json["scripts"]["start"]
            
            if "port" in package_json:
                config["port"] = package_json["port"]
        
        return config
    
    @staticmethod
    def _get_static_config(repo_path: str) -> dict:
        """Get static site configuration."""
        return {
            "language": "static",
            "framework": "nginx",
            "port": 80,
            "start_command": "nginx -g 'daemon off;'"
        }


class DockerBuilder:
    """Build Docker images for applications."""
    
    @staticmethod
    def build_image(
        repo_path: str,
        image_name: str,
        image_tag: str,
        language: str,
        registry_url: Optional[str] = None
    ) -> str:
        """Build Docker image for the application."""
        dockerfile_map = {
            "python": "Dockerfile.python",
            "node": "Dockerfile.node",
            "static": "Dockerfile.static"
        }
        
        dockerfile = dockerfile_map.get(language, "Dockerfile.python")
        dockerfile_path = os.path.join(
            os.path.dirname(__file__),
            dockerfile
        )
        
        image_uri = image_name
        if registry_url:
            image_uri = f"{registry_url}/{image_name}"
        
        full_image = f"{image_uri}:{image_tag}"
        
        print(f"Building Docker image: {full_image}")
        
        build_cmd = [
            "docker", "build",
            "-t", full_image,
            "-f", dockerfile_path,
            repo_path
        ]
        
        try:
            subprocess.run(build_cmd, check=True, cwd=repo_path)
            print(f"Successfully built: {full_image}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker build failed: {e}")
        
        return full_image
    
    @staticmethod
    def push_image(image_uri: str) -> None:
        """Push image to registry."""
        print(f"Pushing image: {image_uri}")
        
        try:
            subprocess.run(["docker", "push", image_uri], check=True)
            print(f"Successfully pushed: {image_uri}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker push failed: {e}")
