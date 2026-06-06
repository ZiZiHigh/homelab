# 🎬 Jellyfin Media Server — Self-Hosted on Arch Linux

A self-hosted media server running on a 10+ year old laptop, deployed via Docker on a minimal headless Arch Linux installation.

> Jellyfin is an open-source alternative to Netflix/Plex — fully local, no subscriptions, no tracking.

---

## 📋 Hardware

| Component | Spec |
|-----------|------|
| CPU | Intel Celeron 1000M (2 cores) @ 1.80 GHz |
| GPU | Intel 3rd Gen Core Graphics @ 1.00 GHz |
| RAM | 3.70 GiB (792 MB available) |
| OS | Arch Linux x86_64 (headless, TTY only) |

---

## ⚙️ Installation

**Prerequisites**
- Docker
- Docker Compose
- Docker service running (`systemctl enable --now docker`)

**Steps**

1. Enable Docker service
```bash
systemctl enable --now docker
```

2. Create `docker-compose.yml` using the official Jellyfin template from [jellyfin.org](https://jellyfin.org/docs/general/installation/container)

3. Configure UID/GID in the compose file to match your user
```bash
id $USER  # get your uid and gid
```

4. Start the container
```bash
docker compose up -d
```

5. Access via browser at `http://SERVER_IP:8096`

---

## 🐛 Problems & Solutions

**Error: `unable to find user uid: no matching entries in passwd file`**
- **Cause:** UID/GID in `docker-compose.yml` was not set correctly
- **Fix:** Set `PUID` and `PGID` to match the current user's values (`id $USER`)

**Docker daemon not starting**
- **Cause:** Docker service was not enabled/started
- **Fix:** `systemctl enable --now docker`

---

## 🔧 What Could Be Improved

- [ ] Reverse proxy (Nginx/Caddy) for cleaner URL access
- [ ] HTTPS with self-signed certificate
- [ ] Tailscale VPN for remote access outside local network
- [ ] Hardware transcoding (limited by Intel Celeron iGPU)
- [ ] Automatic backups of Jellyfin config

---

## 📸 Demo

<!-- Add screenshot or GIF here -->
![Jellyfin Demo](demo.gif)

