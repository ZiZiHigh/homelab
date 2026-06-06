# 🔍 SearXNG — Self-Hosted Search Engine

A privacy-focused meta search engine running locally via Docker on a headless Arch Linux server.

> SearXNG aggregates results from 70+ search engines (Google, Bing, DuckDuckGo...) with no tracking, no ads, and no search history stored anywhere.

---

## 📋 Hardware

| Component | Spec |
|-----------|------|
| CPU | Intel Celeron 1000M (2 cores) @ 1.80 GHz |
| GPU | Intel 3rd Gen Core Graphics @ 1.00 GHz |
| RAM | 3.70 GiB |
| OS | Arch Linux x86_64 (headless, TTY only) |

---

## ⚙️ Installation

**Prerequisites**
- Docker installed and service running
- User added to `docker` group (no root needed)

**Steps**

1. Pull the image
```bash
docker pull searxng/searxng
```

2. Run the container
```bash
docker run -d \
  --name searxng \
  -p 8080:8080 \
  searxng/searxng
```

3. Access via browser at `http://SERVER_IP:8080`

That's it — no config file needed for basic setup.

---

## 🐛 Problems & Solutions

No issues encountered during setup. Straightforward single-command deployment.

---

## 🔧 What Could Be Improved

- [ ] Persistent config volume (`-v`) to survive container restarts
- [ ] Custom `settings.yml` to enable/disable specific search engines
- [ ] Reverse proxy (Nginx/Caddy) for cleaner URL
- [ ] HTTPS with self-signed certificate
- [ ] Tailscale for remote access outside local network

---

## 📸 Demo

<!-- Add screenshot or GIF here -->
![SearXNG Demo](demo.gif)
