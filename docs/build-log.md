# Build log

This is the short version of what I actually did, in order. It comes from my
own notes and command output. Private values are removed.

The lab was not built in one clean pass. The useful part is the sequence of
small changes, checks and rollbacks.

## Starting point

The host was already running Arch Linux, but the public description did not
match it. The Docker stack had been stopped since 2026-06-04, while the README
said the services were running. SSH still accepted passwords. There were no
backups. Grafana used a default admin password, SearXNG used the upstream
default secret, and SMB allowed anonymous access.

I wanted a lab I could explain end to end: what runs, why it runs, what is
exposed, what happens when it breaks, and what is still not fixed.

## 1. Baseline and scope

I started with a read-only audit. The important findings were:

- the stack was stopped;
- the README made claims that were not true;
- SSH password authentication was enabled;
- there was no backup of the host or the AD data;
- secrets were either default or handled outside a clear policy;
- SMB anonymous access was allowed;
- `/boot` had world-accessible paths;
- update and audit tooling was incomplete.

I kept the scope small. The goal was not to add more services. It was to make
the existing stack reachable, repeatable and honest.

## 2. Docker layout

I moved the services into separate Compose projects:

| Project | Purpose |
|---|---|
| `nginx` | Reverse proxy and TLS |
| `jellyfin` | Media server |
| `searxng` | Private search |
| `grafana` | Dashboards |
| `prometheus` | Metrics |
| `alertmanager` | Alert routing |
| `node-exporter` | Host metrics |

All projects join the external `homelab` network. Only nginx publishes host
ports 80 and 443. The old containers were stopped but not deleted, so I could
compare the old and new state without destroying data.

The old monolithic monitoring Compose file was left behind during the
transition. It is not part of the final repository.

## 3. Reverse proxy and TLS

nginx is the only public-facing container. It redirects HTTP to HTTPS, serves
a small `/healthz` endpoint for the container health check, and returns 404
for unknown host names.

The certificate is self-signed because the service names are private. It
covers the service names and the host. The real names are not in the public
repo. The private key is untracked and mode 600.

I used temporary high ports during the mDNS transition so I could test the
proxy without touching the final 80/443 mapping. Once the final vhosts were
verified, the temporary ports were removed.

## 4. Services

Jellyfin, SearXNG, Grafana, Prometheus, Alertmanager and node-exporter were
pinned to specific versions. Nothing uses `latest`.

The application containers do not publish host ports. They expose their
service port on the Docker network and are reached through nginx or, for the
monitoring UIs, through the private LAN.

Jellyfin was left without a documented media library. The first-run wizard
was completed later, after the rest of the stack was stable. I did not use the
media tree for experiments beyond the approved test asset.

## 5. Monitoring

Prometheus scrapes itself, node-exporter and Alertmanager every 15 seconds.
The alert rules cover a down target, low root disk, low available memory and
unsynchronised time.

Alertmanager has a `null` receiver. Alerts are visible in its UI, but no email
or webhook is configured. That is deliberate for now: a notification receiver
needs a destination and a secret, and I did not want to add a half-configured
one.

A small Python script writes SMART health, temperature and selected sector
counters into a node-exporter textfile. It deliberately exports device paths
and numbers only, not model names or serial numbers. A systemd timer runs it
every five minutes.

## 6. Samba AD

The Samba AD DC is the part that caused the most confusing failures. The
important detail is that this is an AD DC, so `smbd` and `nmbd` are not the
services to watch. `samba.service` is.

The domain uses Samba's internal DNS. `systemd-resolved` must stay disabled
because it would bind port 53 and conflict with Samba. The functional level
is Windows 2008 R2 and was not raised.

I hardened the password policy and anonymous access:

- minimum password length 12;
- lockout threshold 5;
- maximum password age 42 days;
- complexity, history and minimum age kept enabled;
- `restrict anonymous = 2`.

Anonymous SMB enumeration now fails with `NT_STATUS_ACCESS_DENIED`. That is
the intended result. The SPNs for the DC's own computer account were complete
and were not changed.

## 7. mDNS

The old `.home` names did not resolve. Instead of adding a `.home` DNS zone, I
used Avahi and `.local`.

I installed `nss-mdns`, published five private aliases, and allowed UDP 5353
on the Wi-Fi interface. The Arch host and an Android client were verified. The
temporary proxy ports were removed after that.

The NixOS client is still deferred. That system uses `doas`, has no Avahi and
does not have the `mdns` NSS entry. A setup script exists, but I have not run
it. I did not change router or DHCP settings to work around the client.

## 8. Backup

restic writes to a separate backup host over SFTP. The password file is
root-only. A systemd timer runs daily at 20:00, with `Persistent=true` and up
to 15 minutes of random delay.

The first snapshot was created. There is still no offsite copy, old AD dumps
are not automatically deleted, and I have not completed a full restore drill.
Those are the three backup tasks I would not mark as done.

## 9. Security pass

I disabled SSH password authentication and kept key-based access. fail2ban is
active. nftables is enabled and allows only the required LAN ports: SSH, HTTP,
HTTPS, mDNS and the Samba AD ports. The AD ports are not exposed to the
internet.

The Grafana admin password and the SearXNG secret were regenerated and moved
into untracked files with mode 600. The repository only contains examples with
placeholders.

The audit also found seven vulnerable packages. `libxml2` and `pam` are High.
`arch-audit -u` offered no fixed versions at the time. I did not install a
partial update or claim the packages were patched.

Lynis reported a hardening index of 66, 251 tests, one warning and 29
suggestions. The warning repeated the vulnerable-package finding. The raw
output stays private because it contains host-specific information.

I installed the missing audit tools and `fakeroot`, which `checkupdates`
needs. `paccache --keep 2` found no candidates because no package had more than
two cached versions. I left the cache alone.

Two routine updates were pending, `opencode` and `python-markdown`. I did not
install them during the audit and did not run a full system upgrade.

## 10. Boot permissions

`/boot` used masks that left files world-accessible. I changed the mount to
`fmask=0077,dmask=0077`.

The first remount did not apply the vfat masks. The second attempt used a
fresh mount and was rolled back because the check expected 600. On vfat,
`fmask=0077` produces 700 for files, not 600. I settled on 700 with no group
or other access and documented why. Exact 600 would require `fmask=0177`,
which is a different policy.

`bootctl` reported no world-accessible paths. I did not reboot after the
change, so a reboot test is still open.

## 11. Jellyfin

The first-run wizard is complete. The web UI returns HTTP 200 and the public
info endpoint reports `StartupWizardCompleted=true`.

No media library is documented in this repository. If one is added later, it
needs its own scope decision, a read-only mount, and a backup decision.

## 12. Documentation

The final pass moved the documentation into a fresh clone at
`~/homelab-repo`. The live source tree was not overwritten. Private values
were replaced with placeholders, and the raw audit evidence stayed outside the
repository.

The repository now contains the Compose files, nginx config, monitoring
config, sanitized Samba example, systemd units, and the notes for backup,
HTTPS, troubleshooting, the audit and the update policy.

## What I got wrong

The vfat permission assumption was the clearest mistake. I expected 600 from
`fmask=0077` and wrote a check around that expectation. The mount was correct
for security, but the check was wrong. I rolled it back and fixed the
documentation instead of forcing the system to match a bad assumption.

The NTP target was another wrong assumption. I treated a Wi-Fi link as if it
could hold wired-clock precision. It could not. The useful outcome was not a
green check; it was an honest measurement and a note not to claim the target.

The original README was the third mistake. It described the intended state,
not the actual state. A README that is aspirational is worse than no README,
because it hides outages.

## What I would do differently

- Write the runbook while making the change, not after it.
- Test mount options on a disposable mount before changing the real one.
- Use a wired link if NTP precision matters. If not, write down the real
  precision and move on.
- Separate Compose projects from the first deployment.
- Add the offsite backup and restore test before calling the backup done.
- Verify service names before documenting them. `smbd` is not the AD DC.

## What is still open

- Seven vulnerable packages; recheck for fixed versions.
- Offsite backup, AD dump retention and a real restore drill.
- NixOS mDNS client.
- Reboot test for the `/boot` change.
- Decision on the Samba functional level.
- Decision on the legacy `.home` names.
- Jellyfin media library, if it is ever added.
- NTP precision over Wi-Fi.
