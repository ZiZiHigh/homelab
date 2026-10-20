# Update policy

Status: adopted 2026-10-20

## Principles

- Use only the official Arch repositories for host packages.
- Never use the `latest` tag for container images. Every image is pinned to
  a reviewed version in its Compose file.
- Do not run partial upgrades. Perform a full `pacman -Syu` in a planned
  maintenance window, then reboot only when the update requires it.
- Review updates before installing them. They are not installed
  automatically.
- Keep secrets out of Git, reports, logs and shell history.
- Record changes and verify the services afterwards.

## Routine checks

Run these checks weekly, or before a maintenance window.

```bash
# Pending repository updates; does not install anything
checkupdates

# Known vulnerabilities in installed packages
arch-audit

# Vulnerabilities that already have a fixed version
arch-audit -u
```

If a relevant update exists, schedule a window and run a full upgrade:

```bash
sudo pacman -Syu
```

Do not use `pacman -Sy` followed by a partial install.

## Monthly review

```bash
# Host hardening audit; run as root
sudo lynis audit system

# Preview the cache cleanup first
paccache -d --keep 2

# Remove old cached versions, keeping the two newest per package
paccache -r --keep 2
```

Keep two cached versions. Do not use a more aggressive cleanup unless a
documented disk-space emergency has been approved.

## Reboot policy

A reboot is never automatic. Confirm that the boot entry, the backup and the
running workload are healthy before rebooting. A reboot is normally needed
after a kernel, systemd, initramfs, microcode or bootloader change.

## Container updates

- Change one image tag at a time in the relevant Compose file.
- Pin a specific version; never use `latest`.
- Recreate only the affected project and verify its health.
- Keep the shared external `homelab` network and the published ports
  unchanged unless the change is approved.
- Do not run `docker system prune`.

## Emergency security work

If a high-risk issue has a fixed version, treat it as a maintenance priority
even outside the routine window. If no fixed version exists, record the CVE
and the mitigation decision, and check again at the next review. Do not claim
that a package is patched while the installed version is still affected.

## Verification after an update

```bash
systemctl --failed
docker ps
findmnt /boot
```

Also verify the private HTTPS endpoints and the Samba AD health when the
update touches those components. For a kernel or boot change, verify that the
boot entry and the random seed are still present.

## Baseline

The 2026-10-20 review recorded:

- Two routine updates pending (opencode and python-markdown), not installed.
- Seven vulnerable installed packages. `arch-audit -u` offered no fixed
  versions. `libxml2` and `pam` were High; `coreutils`, `linux`, `openssl`,
  `perl` and `systemd` were Medium. They are not marked as resolved.
- Lynis hardening index 66, 251 tests, 1 warning and 29 suggestions.
- `paccache --keep 2` found no candidates; the cache was unchanged.
- `/boot` mounted with `fmask=0077,dmask=0077`; directories were 700 and the
  random-seed file was 700 on vfat. There was no group/other access.

The detailed raw audit output stays outside this repository. It can contain
host-specific information and must not be committed.
