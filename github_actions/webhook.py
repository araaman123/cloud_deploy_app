"""GitHub webhook handler for deployment triggers."""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
import hmac
import hashlib
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    expected_signature = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/webhook/github")
async def github_webhook(
    payload: dict,
    x_hub_signature_256: str = None,
    x_github_event: str = None
):
    """
    GitHub webhook endpoint for deployment triggers.
    
    Receives push events and triggers app deployments.
    """
    
    # Verify signature
    if not x_hub_signature_256:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing GitHub signature"
        )
    
    # TODO: Verify signature with secret
    # if not verify_github_signature(payload_bytes, x_hub_signature_256, GITHUB_SECRET):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    
    if x_github_event == "ping":
        return {"message": "pong"}
    
    if x_github_event == "push":
        return await handle_push_event(payload)
    
    return {"message": "Event received"}


async def handle_push_event(payload: dict):
    """Handle GitHub push event."""
    
    repo_name = payload.get("repository", {}).get("name", "unknown")
    branch = payload.get("ref", "").split("/")[-1]
    commits = payload.get("commits", [])
    head_commit = payload.get("head_commit", {})
    
    logger.info(f"Push to {repo_name}/{branch}")
    logger.info(f"Commits: {len(commits)}")
    
    if not head_commit:
        return {"message": "No commits to deploy"}
    
    commit_hash = head_commit.get("id")
    commit_message = head_commit.get("message")
    
    # TODO: Trigger deployment
    # 1. Look up app by repo URL
    # 2. Create deployment record
    # 3. Trigger build pipeline
    # 4. Deploy to Kubernetes
    
    deployment_info = {
        "repo": repo_name,
        "branch": branch,
        "commit": commit_hash,
        "message": commit_message,
        "status": "queued"
    }
    
    logger.info(f"Deployment queued: {deployment_info}")
    
    return {
        "message": "Deployment triggered",
        "deployment": deployment_info
    }
