# Contributing to DevOps Automation SaaS

Thank you for your interest in contributing! This guide will help you get started.

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new features
   - Update documentation

3. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new deployment strategy"
   ```

4. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python (FastAPI, Terraform CLI)

```python
# Use type hints
def get_app(app_id: str) -> Application:
    pass

# Use descriptive names
user_applications = get_user_applications(user_id)

# Add docstrings
def deploy_application(config: dict) -> str:
    """
    Deploy an application to Kubernetes.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Deployment ID
    """
    pass

# Use async/await for I/O operations
async def fetch_deployment_status(deployment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/deployments/{deployment_id}")
    return response.json()
```

### Error Handling

```python
from fastapi import HTTPException, status

try:
    app = get_application(app_id)
except ApplicationNotFound:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Application {app_id} not found"
    )
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Application deployed successfully", extra={
    "app_id": app.id,
    "namespace": app.namespace
})

logger.error("Deployment failed", exc_info=True)
```

## Adding New Features

### API Endpoints

1. Create schema in `control_plane/schemas/`
2. Create route in `control_plane/routes/`
3. Add service logic in `control_plane/services/`
4. Include in `control_plane/main.py`
5. Document in README

### Database Models

1. Create model in `control_plane/models/database.py`
2. Add migration in `database/migrations.py`
3. Create Pydantic schema in `control_plane/schemas/`

### Infrastructure

1. Create Terraform module in `terraform/`
2. Add variables in `variables.tf`
3. Add outputs in `outputs.tf`
4. Document in `terraform/README.md`

## Testing

```bash
# Run all tests
pytest control_plane/tests/

# Run with coverage
pytest --cov=control_plane control_plane/tests/

# Run specific test
pytest control_plane/tests/test_routes.py::test_create_app
```

## Documentation

- Update README for user-facing features
- Add docstrings to all functions
- Include examples for new endpoints
- Update GETTING_STARTED.md if setup changes

## Pull Request Process

1. **Title**: Use conventional commits
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code refactoring
   - `test:` for tests

2. **Description**: Explain what and why
   - Link related issues
   - Include before/after for UI changes
   - List any breaking changes

3. **Testing**: Ensure all tests pass
   ```bash
   pytest
   black .
   isort .
   flake8 .
   ```

4. **Review**: Address reviewer comments

## Areas for Contribution

### High Priority
- [ ] Add comprehensive test suite
- [ ] Implement payment processing
- [ ] Add database transaction support
- [ ] Implement proper error recovery
- [ ] Add API rate limiting

### Medium Priority
- [ ] Multi-region deployment
- [ ] Advanced monitoring dashboards
- [ ] Backup/restore functionality
- [ ] Cost estimation tool
- [ ] Performance optimization

### Low Priority
- [ ] UI dashboard
- [ ] CLI tool
- [ ] Additional framework support
- [ ] Documentation improvements
- [ ] Community examples

## Reporting Issues

When reporting issues, include:
- **Title**: Clear, concise description
- **Environment**: OS, Python version, Docker version
- **Steps to reproduce**: Exact steps to trigger the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or logs

## Community

- 💬 Discussions: Use GitHub Discussions for questions
- 🐛 Bugs: Report via GitHub Issues
- 📧 Contact: See maintainers in repository

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- GitHub contributors page
- Release notes for major contributions
