# Kubernetes Deployment Configuration

This directory contains Kubernetes manifests for deploying applications automatically.

## Overview

Each deployed application gets:

1. **Namespace** - Isolated environment per app
2. **Deployment** - Replicated pod configuration
3. **Service** - Internal and external networking
4. **Ingress** - HTTP/HTTPS routing with TLS
5. **ConfigMap** - Environment variables
6. **Secret** - Sensitive data
7. **HPA** - Auto-scaling policies
8. **PVC** - Persistent storage (if needed)

## Directory Structure

```
kubernetes/
├── base/              # Base configurations
├── overlays/          # Environment-specific overrides
├── templates/         # Jinja2 templates for dynamic generation
├── cert-manager/      # Certificate management
├── ingress/           # Ingress controller setup
└── monitoring/        # Prometheus ServiceMonitor configs
```

## Templates

### Application Deployment Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image_uri }}:{{ image_tag }}
        ports:
        - containerPort: {{ port }}
        resources:
          limits:
            cpu: {{ cpu_limit }}
            memory: {{ memory_limit }}
          requests:
            cpu: {{ cpu_request }}
            memory: {{ memory_request }}
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ app_name }}-secrets
              key: database-url
```

### Service & Ingress Template

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ app_name }}-service
  namespace: {{ namespace }}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: {{ port }}
  selector:
    app: {{ app_name }}
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ app_name }}-ingress
  namespace: {{ namespace }}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - {{ domain }}
    secretName: {{ app_name }}-tls
  rules:
  - host: {{ domain }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ app_name }}-service
            port:
              number: 80
```

## Deployment Process

1. **Namespace Creation**
   ```bash
   kubectl create namespace app-{id}
   ```

2. **Secrets & ConfigMaps**
   ```bash
   kubectl create secret generic app-secrets -n app-{id}
   kubectl create configmap app-config -n app-{id}
   ```

3. **Apply Deployment**
   ```bash
   kubectl apply -f deployment.yaml -n app-{id}
   ```

4. **Setup Ingress**
   ```bash
   kubectl apply -f ingress.yaml -n app-{id}
   ```

5. **Verify Deployment**
   ```bash
   kubectl get pods -n app-{id}
   kubectl get ingress -n app-{id}
   ```

## Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ app_name }}-hpa
  namespace: {{ namespace }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ app_name }}
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring

Each app gets a ServiceMonitor for Prometheus:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
spec:
  selector:
    matchLabels:
      app: {{ app_name }}
  endpoints:
  - port: metrics
```

## Usage

Apply a deployment:

```bash
python -c "
from templates import generate_deployment
config = {
    'app_name': 'my-api',
    'namespace': 'app-123',
    'image_uri': '123456789.dkr.ecr.us-east-1.amazonaws.com/app',
    'image_tag': 'v1.0.0',
    'port': 8000,
    'replicas': 3,
}
manifests = generate_deployment(config)
"
```
