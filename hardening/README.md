# Hardening

This is the sanitized description of the host hardening. The real addresses,
interface names and service names are private.

## SSH

The deployed SSH configuration disables password authentication and
keyboard-interactive password prompts:

```text
PasswordAuthentication no
KbdInteractiveAuthentication no
```

Use an SSH key. Do not re-enable password authentication to make a client
work; fix the key or client configuration instead.

The login user is intentionally not in the `docker` group. Docker
administration is performed through the root-managed service or a root shell.

## nftables

The host firewall is enabled and applies an input policy of `drop`. It allows:

- loopback and established/related traffic;
- IPv4 and IPv6 ICMP;
- SSH (22), HTTP (80) and HTTPS (443);
- mDNS UDP 5353 on the Wi-Fi interface;
- Samba AD DNS, Kerberos, LDAP, SMB, kpasswd, LDAPS, global catalog and the
  small RPC range only from the private LAN.

The real LAN CIDR and interface names are replaced with documentation values
in examples:

```nft
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        iif "lo" accept
        ct state invalid drop
        ct state { established, related } accept
        ip protocol icmp accept
        ip6 nexthdr icmpv6 accept

        tcp dport 22 accept
        tcp dport { 80, 443 } accept
        iifname "<wifi-if>" udp dport 5353 accept

        iifname "<lan-if>" ip saddr 192.0.2.0/24 \
            tcp dport { 53, 88, 135, 139, 389, 445, 464, 636, 3268, 3269 } accept
        iifname "<lan-if>" ip saddr 192.0.2.0/24 \
            udp dport { 53, 88, 123, 137, 138, 389, 464 } accept
        iifname "<lan-if>" ip saddr 192.0.2.0/24 \
            tcp dport 49152-49160 accept
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

`nftables.service` is a oneshot unit. It may show `inactive (dead)` after
successfully loading the rules. Verify with `sudo nft list ruleset`; do not
assume the firewall is off from the unit state alone.

Do not add an internet-facing port-forward for the AD ports or the Docker
application ports.

## fail2ban

fail2ban is enabled and active. It reads systemd journals. Check the jail:

```bash
sudo fail2ban-client status sshd
```

Do not claim a specific ban threshold unless the private `jail.local` is
checked; the threshold is intentionally not published.

## Container boundary

- Only nginx publishes host ports 80 and 443.
- Application containers use the shared external `homelab` network and
  `expose` only.
- Compose files set `no-new-privileges`, memory/CPU/PID limits and health
  checks where supported.
- Do not run `docker system prune` or remove containers/volumes without
  approval.

## Known gaps

See [`docs/audit-2026-10.md`](../docs/audit-2026-10.md) for the current list.
The important gaps are the seven unresolved vulnerable packages (including
High-risk `libxml2` and `pam`), the missing offsite backup, the unstable NTP
target and the deferred NixOS mDNS client.
