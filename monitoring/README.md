# Monitoring

The monitoring stack is split into separate Compose projects so that one
service can be restarted without recreating the others. All services join the
shared external `homelab` network.

| Directory | Service | Host port |
|---|---|---|
| `grafana/` | Grafana 13.2.4 | none (expose 3000) |
| `prometheus/` | Prometheus v3.15.0 | none (expose 9090) |
| `alertmanager/` | Alertmanager v0.34.1 | none (expose 9093) |
| `node-exporter/` | node-exporter v1.12.1 | none (expose 9100) |

Access is through nginx at private placeholders:

- `https://grafana.example.test/`
- `https://prometheus.example.test/` (LAN only)
- `https://alerts.example.test/` (LAN only)

## Configuration

- `prometheus/prometheus.yml` scrapes Prometheus itself, node-exporter and
  Alertmanager every 15 seconds.
- `prometheus/alerts.yml` contains alerts for a down target, low root disk,
  low available memory and unsynchronised time.
- `alertmanager/alertmanager.yml` currently has a `null` receiver. Alerts are
  visible in the UI; no email or webhook destination is configured.
- `node-exporter/homelab-node-metrics.py` exports SMART health, temperature
  and selected sector counters without model names or serial numbers. The
  timer runs it every five minutes.
- `.env.example` is the template for the Grafana admin password. The real
  `.env` is untracked and mode 600.

## Grafana secret

```bash
cp .env.example .env
chmod 600 .env
# replace the placeholder with a unique strong password
```

Do not commit `.env` and do not use a public default password. The Grafana
container reads it through `env_file`.

## Data

Prometheus and Grafana data live in external Docker volumes. Alertmanager
data and node-exporter textfile output are private directories and are
ignored by Git.

## Start

Start each project from its directory:

```bash
docker compose -f grafana/compose.yml up -d
docker compose -f prometheus/compose.yml up -d
docker compose -f alertmanager/compose.yml up -d
docker compose -f node-exporter/compose.yml up -d
```

Verify `docker compose ps`, the container health checks and the private HTTPS
endpoints. A 302 on Grafana or Prometheus is normally a redirect to the login
or UI.

## Limitations

- No notification receiver is configured.
- The host is a small Celeron machine; retention and memory limits are
  deliberately modest.
- The raw `homelab.prom` textfile and monitoring data are not repository
  content.
