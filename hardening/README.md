# 🔒 Server Hardening — SSH + nftables + fail2ban

Security hardening applied to a headless Arch Linux server running Docker services.

---

## 🛡️ What Was Done

| Layer | Tool | Purpose |
|-------|------|---------|
| SSH | OpenSSH config | Key-based auth, no passwords |
| Firewall | nftables | Block all traffic except SSH and HTTP |
| Brute-force protection | fail2ban | Auto-ban IPs after failed logins |

---

## ⚙️ SSH Hardening

**Generate key pair on client:**
```bash
ssh-keygen -t ed25519 -C "homelab"
```

**Copy public key to server:**
```bash
ssh-copy-id user@SERVER_IP
```

**Edit `/etc/ssh/sshd_config` on server:**
```
PasswordAuthentication no
PermitRootLogin yes
```

**Restart SSH:**
```bash
systemctl restart sshd
```

> ⚠️ In production: `PermitRootLogin no` — kept enabled here for homelab convenience.

---

## ⚙️ nftables Firewall

**`/etc/nftables.conf`:**
```nftables
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        iif "lo" accept comment "loopback"
        ct state invalid drop comment "drop invalid packets"
        ct state { established, related } accept comment "allow established"

        ip protocol icmp accept comment "allow ping"

        tcp dport 22 accept comment "SSH"
        tcp dport 80 accept comment "HTTP - Nginx"
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

**Enable:**
```bash
nft -f /etc/nftables.conf
systemctl enable --now nftables
```

> Docker manages its own forwarding rules — the forward chain is intentionally omitted to avoid conflicts.

---

## ⚙️ fail2ban

**`/etc/fail2ban/jail.local`:**
```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5
backend  = systemd

[sshd]
enabled = true
port    = ssh
```

**Enable:**
```bash
systemctl enable --now fail2ban
```

**Check status:**
```bash
fail2ban-client status sshd
```

After 5 failed SSH login attempts within 10 minutes → IP banned for 1 hour automatically.

---

## 🐛 Problems & Solutions

No issues encountered during hardening setup.

---

## 🔧 What Could Be Improved

- [ ] `PermitRootLogin no` for production
- [ ] Change default SSH port (obscurity measure)
- [ ] HTTPS with self-signed certificate (Nginx)
- [ ] Longer fail2ban bantime for repeat offenders
- [ ] Automatic security updates (pacman hooks)
