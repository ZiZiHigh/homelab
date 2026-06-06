# 🏠 Homelab — Self-Hosted Infrastructure on Arch Linux

Personal homelab running on a 10+ year old laptop. Fully headless, managed via SSH, with Docker-based services, monitoring, reverse proxy and security hardening.

---

## 🖥️ Hardware

| Component | Spec |
|-----------|------|
| CPU | Intel Celeron 1000M (2 cores) @ 1.80 GHz |
| GPU | Intel 3rd Gen Core Graphics |
| RAM | 3.70 GiB |
| OS | Arch Linux x86_64 — headless, TTY only |

---

## 🧩 Services

| Service | Description | Access |
|---------|-------------|--------|
| Jellyfin | Self-hosted media server | `jellyfin.home` |
| SearXNG | Privacy-focused meta search engine | `search.home` |
| Grafana | Metrics dashboard | `grafana.home` |
| Prometheus | Metrics collection | Internal |
| Node Exporter | System metrics | Internal |
| Nginx | Reverse proxy for all services | Port 80 |

---

## 🏗️ Architecture

```
Client (browser)
      │
      ▼
  Nginx :80          ← reverse proxy
  ┌────┴────┐
  │         │
Jellyfin  SearXNG   Grafana
 :8096     :8080     :3000
                       │
                  Prometheus
                       │
                 Node Exporter
                  (host metrics)
```

---

## 🔒 Security

- SSH key-based authentication (password auth disabled)
- nftables firewall — only ports 22 and 80 open
- fail2ban — auto-ban after 5 failed SSH attempts

---

## 📁 Project Structure

```
homelab/
├── README.md               ← you are here
├── jellyfin/
│   └── README.md
├── searxng/
│   └── README.md
├── monitoring/
│   ├── README.md
│   ├── docker-compose.yml
│   └── prometheus/
│       └── prometheus.yml
├── nginx/
│   └── nginx.conf
└── hardening/
    └── README.md
```

---

## 🛠️ Skills Demonstrated

- Linux system administration (Arch Linux, headless setup)
- Docker & Docker Compose
- Service deployment and management
- Reverse proxy configuration (Nginx)
- Server monitoring (Prometheus, Grafana)
- Network security (nftables, fail2ban, SSH hardening)
- Troubleshooting and problem solving

---

## 📸 Screenshots

<!-- Add screenshots here -->

