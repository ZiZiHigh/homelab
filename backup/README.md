# Backup units

These are sanitized copies of the systemd units. The private backup script,
repository URL, repository ID, snapshot IDs and password are not published.

Install the units under `/etc/systemd/system/`, create the real
`/usr/local/sbin/homelab-backup.sh` with root-only permissions, and keep
`/root/.restic-password` mode 600.

```bash
sudo install -m 0644 homelab-backup.service homelab-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now homelab-backup.timer
```

See [`docs/backup.md`](../docs/backup.md) for limitations and checks.
