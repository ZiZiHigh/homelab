# Design decisions

Short notes on the choices that shaped the lab. These are not rules for a
production environment. They are the trade-offs I made on one small host.

## ADR-001: one host, Docker Compose, no orchestration

**Context:** the hardware is a single old laptop with limited memory. I wanted
repeatable service management without adding a cluster.

**Decision:** run each service as a separate Compose project on the same host.

**Consequences:** simple recovery and a small resource footprint. There is no
high availability. A host failure takes everything down, and the backup and
restore path matters more than in a clustered setup.

## ADR-002: shared external network, one published proxy

**Context:** application containers need to reach each other, but I did not
want every service to bind a host port.

**Decision:** put the projects on the external `homelab` network. Only nginx
publishes host ports 80 and 443.

**Consequences:** smaller attack surface and less port confusion. The proxy is
now a single dependency: if nginx is down, the web services are down even when
their containers are healthy.

## ADR-003: pinned container versions

**Context:** `latest` makes a deployment hard to reproduce and easy to break
without a visible change.

**Decision:** pin every image to a reviewed version in its Compose file.

**Consequences:** updates are deliberate and reviewable. I have to check
versions manually and cannot rely on an automatic updater.

## ADR-004: self-signed TLS for private names

**Context:** the service names are private and do not have public DNS or a
public ACME path. A browser still needs HTTPS for cookies and for anything
that touches credentials.

**Decision:** use a self-signed certificate with the private names in the SAN
list, and document how to trust it on a client.

**Consequences:** no public CA dependency, but clients need a trust step. I do
not disable TLS verification as a workaround.

## ADR-005: `.local` mDNS, no `.home` DNS zone

**Context:** the old names used `.home`, but they did not resolve. I could add
a DNS zone or switch to mDNS.

**Decision:** make `.local` the primary path through Avahi and `nss-mdns`.
Keep the old `.home` names as legacy only and do not add a `.home` zone.

**Consequences:** works on the home LAN without router changes. mDNS does not
cross every network boundary, and the NixOS client is not finished. The
legacy names remain a loose end.

## ADR-006: Samba AD with its own DNS

**Context:** the lab needs a domain controller, and the AD services depend on
SRV records and Kerberos.

**Decision:** use Samba's internal DNS and keep `systemd-resolved` disabled.

**Consequences:** the AD DC is self-contained, but the host cannot use the
resolved stub resolver on port 53. Re-enabling `systemd-resolved` would break
AD DNS. The functional level stays at Windows 2008 R2 until there is a reason
and a tested plan to raise it.

## ADR-007: local restic backup now, offsite later

**Context:** the starting point had no backup at all. A separate host was
available, but an offsite target was not.

**Decision:** add a daily restic backup to the separate host first, with a
root-only password file and a systemd timer.

**Consequences:** there is a recoverable copy on another machine, but it is
still on the same site. The backup is not complete until there is an offsite
copy and a restore drill. Old AD dumps also need a retention decision.

## ADR-008: untracked secrets and a sanitized public repo

**Context:** the repository is public. The real environment contains private
names, addresses, account details and secret files.

**Decision:** keep real `.env`, SearXNG settings, TLS keys and restic password
outside Git. Publish examples with placeholders. Sanitize the audit and the
Samba configuration.

**Consequences:** the public repo is useful as a design and troubleshooting
record, not as a deployable copy of the private environment. Some commands
need private values that are intentionally absent.

## ADR-009: manual updates, full upgrades

**Context:** partial upgrades on Arch are risky, and automatic container
updates would make a small lab harder to reason about.

**Decision:** check updates manually, run a full `pacman -Syu` in a planned
window, and move container versions one at a time.

**Consequences:** no surprise upgrades, but updates depend on me remembering
to run the check. The audit found seven vulnerable packages with no fixed
version, which is a reason to keep checking rather than a reason to claim the
host is clean.
