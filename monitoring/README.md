# Monitoring & Observability

This directory contains configurations for monitoring and logging.

## Components

1. **Prometheus** - Metrics collection
2. **Grafana** - Metrics visualization
3. **ELK Stack** - Logs aggregation and analysis
4. **Alert Manager** - Alert routing and management

## Prometheus Configuration

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

## Grafana Dashboards

Pre-built dashboards for:
- Cluster overview
- Node metrics
- Pod performance
- Application metrics
- Network traffic

## ELK Stack

### Elasticsearch

```bash
docker run -d \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0
```

### Kibana

```bash
docker run -d \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/kibana/kibana:8.0.0
```

### Filebeat

Collects logs from pods and sends to Elasticsearch.

## Alerts

Example alerts configured:

- High CPU usage
- High memory usage
- Pod crashes
- Deployment failures
- Missing health checks

## Usage

1. **Deploy Prometheus**
   ```bash
   kubectl apply -f prometheus-config.yaml
   kubectl apply -f prometheus-deployment.yaml
   ```

2. **Deploy Grafana**
   ```bash
   kubectl apply -f grafana-deployment.yaml
   ```

3. **Deploy ELK**
   ```bash
   kubectl apply -f elasticsearch-deployment.yaml
   kubectl apply -f kibana-deployment.yaml
   kubectl apply -f filebeat-daemonset.yaml
   ```

4. **Access Dashboards**
   - Prometheus: http://prometheus.local
   - Grafana: http://grafana.local
   - Kibana: http://kibana.local
