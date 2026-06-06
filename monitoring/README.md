# 📊 Monitoring Stack — Prometheus + Grafana + Node Exporter

Full server monitoring stack running via Docker Compose on a headless Arch Linux server.

---

## 🧩 Stack

| Service | Purpose |
|---------|---------|
| Node Exporter | Collects system metrics (CPU, RAM, disk, network) |
| Prometheus | Scrapes and stores metrics from Node Exporter |
| Grafana | Visualizes metrics as real-time dashboards |

---

## 📋 Hardware

| Component | Spec |
|-----------|------|
| CPU | Intel Celeron 1000M (2 cores) @ 1.80 GHz |
| RAM | 3.70 GiB |
| OS | Arch Linux x86_64 (headless, TTY only) |

---

## ⚙️ Installation

**Directory structure**
```
~/homelab/monitoring/
├── docker-compose.yml
└── prometheus/
    └── prometheus.yml
```

**prometheus.yml**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

**docker-compose.yml**
```yaml
networks:
  monitoring:
    driver: bridge

services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
    networks:
      - monitoring
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter
    container_name: node-exporter
    ports:
      - "9100:9100"
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
```

**Deploy**
```bash
docker compose up -d
```

**Grafana setup**
1. Open `http://SERVER_IP:3000` (admin / changeme)
2. Connections → Data Sources → Add → Prometheus → URL: `http://prometheus:9090`
3. Dashboards → Import → ID `1860` (Node Exporter Full)

---

## 🐛 Problems & Solutions

No issues encountered. Stack deployed and connected without errors.

---

## 🔧 What Could Be Improved

- [ ] Change default Grafana password via env variable properly
- [ ] Alert rules in Prometheus (notify when CPU/RAM too high)
- [ ] Persistent Grafana dashboard config
- [ ] Restrict Prometheus and Node Exporter ports — expose only to local network

---

## 📸 Demo

<!-- Add Grafana dashboard screenshot here -->
![Grafana Dashboard](demo.png)
