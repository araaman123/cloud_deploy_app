"""Generate Kubernetes manifests for application deployments."""

from jinja2 import Template
import yaml
from typing import Dict, Any


# Deployment template
DEPLOYMENT_TEMPLATE = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
  labels:
    app: {{ app_name }}
    managed-by: cloud-deploy
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{{ metrics_port }}"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image_uri }}:{{ image_tag }}
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: {{ port }}
        - name: metrics
          containerPort: {{ metrics_port }}
        resources:
          limits:
            cpu: {{ cpu_limit }}
            memory: {{ memory_limit }}
          requests:
            cpu: {{ cpu_request }}
            memory: {{ memory_request }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
        envFrom:
        - configMapRef:
            name: {{ app_name }}-config
        - secretRef:
            name: {{ app_name }}-secrets
"""

# Service template
SERVICE_TEMPLATE = """
apiVersion: v1
kind: Service
metadata:
  name: {{ app_name }}-service
  namespace: {{ namespace }}
  labels:
    app: {{ app_name }}
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: http
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: metrics
    protocol: TCP
  selector:
    app: {{ app_name }}
"""

# Ingress template
INGRESS_TEMPLATE = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ app_name }}-ingress
  namespace: {{ namespace }}
  annotations:
    cert-manager.io/cluster-issuer: {{ issuer }}
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
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
"""

# HPA template
HPA_TEMPLATE = """
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
  minReplicas: {{ min_replicas }}
  maxReplicas: {{ max_replicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ cpu_threshold }}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {{ memory_threshold }}
"""

# ServiceMonitor template (for Prometheus)
SERVICE_MONITOR_TEMPLATE = """
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
  labels:
    app: {{ app_name }}
spec:
  selector:
    matchLabels:
      app: {{ app_name }}
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
"""


def generate_deployment(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate all Kubernetes manifests for an application.
    
    Args:
        config: Dictionary with application configuration
        
    Returns:
        Dictionary with manifest names and YAML content
    """
    
    # Set defaults
    config.setdefault('metrics_port', 9090)
    config.setdefault('cpu_request', '100m')
    config.setdefault('memory_request', '128Mi')
    config.setdefault('min_replicas', 2)
    config.setdefault('max_replicas', 10)
    config.setdefault('cpu_threshold', 70)
    config.setdefault('memory_threshold', 80)
    config.setdefault('issuer', 'letsencrypt-prod')
    
    manifests = {}
    
    # Generate Deployment
    template = Template(DEPLOYMENT_TEMPLATE)
    manifests['deployment.yaml'] = template.render(**config)
    
    # Generate Service
    template = Template(SERVICE_TEMPLATE)
    manifests['service.yaml'] = template.render(**config)
    
    # Generate Ingress
    template = Template(INGRESS_TEMPLATE)
    manifests['ingress.yaml'] = template.render(**config)
    
    # Generate HPA
    template = Template(HPA_TEMPLATE)
    manifests['hpa.yaml'] = template.render(**config)
    
    # Generate ServiceMonitor
    template = Template(SERVICE_MONITOR_TEMPLATE)
    manifests['servicemonitor.yaml'] = template.render(**config)
    
    return manifests


def generate_namespace(namespace: str) -> str:
    """Generate namespace manifest."""
    return f"""
apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
  labels:
    managed-by: cloud-deploy
"""


def generate_configmap(app_name: str, namespace: str, env_vars: Dict[str, str]) -> str:
    """Generate ConfigMap manifest."""
    config = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {app_name}-config
  namespace: {namespace}
data:
"""
    for key, value in env_vars.items():
        config += f"  {key}: \"{value}\"\n"
    
    return config


def generate_secret(app_name: str, namespace: str, secrets: Dict[str, str]) -> str:
    """Generate Secret manifest."""
    import base64
    
    config = f"""
apiVersion: v1
kind: Secret
metadata:
  name: {app_name}-secrets
  namespace: {namespace}
type: Opaque
data:
"""
    for key, value in secrets.items():
        encoded = base64.b64encode(value.encode()).decode()
        config += f"  {key}: {encoded}\n"
    
    return config
