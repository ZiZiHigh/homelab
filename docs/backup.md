# Backup

The host uses restic to write a backup to a separate private machine over
SFTP. The real repository URL, password, repository ID, snapshot IDs and the
full include/exclude list are not in this public repository.

```mermaid
flowchart LR
    host["Host configuration and AD data"] --> restic["restic"]
    restic --> backupHost["Backup host"]
    backupHost -.-> gap["Open gap: same site, no offsite copy"]
```

## Schedule

A systemd timer starts the job daily:

```ini
[Timer]
OnCalendar=*-*-* 20:00:00
Persistent=true
RandomizedDelaySec=15m
Unit=homelab-backup.service
```

`Persistent=true` starts a missed run after the next boot. The service is a
oneshot job with a two-hour timeout and a low I/O priority. It is conditioned
on the root-only restic password file, so a missing secret skips the run rather
than failing with a readable error.

The sanitized units are in [`backup/`](../backup/). The private backup script
is not published.

## What is covered

The private script defines the exact paths. It covers the host configuration
and the Samba AD data. The repository is on a separate backup host, not on the
machine being backed up.

## What is still missing

- There is no offsite second copy. The backup host is a separate machine on
  the same private site.
- Old AD dumps are not automatically deleted. A retention policy still needs
  to be approved and tested.
- A full restore drill is not recorded. Until a restore has been tested, the
  backup should be treated as unproven.
- The repository password and identifier are secrets. They never belong in a
  report, commit, issue or chat.

## Checks

```bash
systemctl list-timers --all | grep homelab-backup
systemctl status homelab-backup.service
journalctl -u homelab-backup.service --since today
```

Run restic checks from the private root shell. Do not put the real repository
path or password in a command that will be copied into the repository.

## Restore

Restore to a temporary path first, verify the contents, then decide whether to
replace live data. A restore is an approval-required operation and must not be
tested against the only production copy.

A useful restore test would cover:

1. the host configuration;
2. the Samba AD database;
3. the Jellyfin configuration, if media is added later;
4. file permissions and ownership after restore.

## Next steps

1. Add an offsite copy.
2. Define and test retention for old AD dumps.
3. Perform and document a full restore drill.
