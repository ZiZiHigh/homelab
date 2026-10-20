# Samba AD

The host runs a Samba Active Directory domain controller for the private LAN.
The real realm, NetBIOS name, DNS names, IP addresses, accounts and DNS
forwarder are omitted from this public copy.

## Service model

The AD DC runs as `samba.service`. `smbd`, `nmbd`, `winbind` and
`samba-ad-dc` may be inactive while `samba.service` is active; that is normal
for an AD DC in this deployment.

```bash
systemctl is-active samba
ss -tulpn | grep -E ':(53|88|389|445|636)\b'
```

`systemd-resolved` must remain disabled. Samba needs TCP/UDP port 53 for its
internal DNS, and the resolved stub listener would conflict.

## Key settings

The sanitized example is in [`samba/smb.conf.example`](../samba/smb.conf.example).

| Setting | Value |
|---|---|
| Server role | `active directory domain controller` |
| DNS backend | `SAMBA_INTERNAL` |
| Functional level | Windows 2008 R2 |
| Anonymous access | `restrict anonymous = 2` |
| Password minimum length | 12 characters |
| Account lockout threshold | 5 attempts |
| Maximum password age | 42 days |
| Complexity, history and minimum age | Kept enabled |
| RPC dynamic ports | Restricted to a small range |

The functional level is legacy but was not raised in this work. The DC's SPNs
for its own computer account are complete; no SPN changes were made.

## DNS

Samba provides the AD DNS zone and SRV records. The DNS forwarder is a
private value and is replaced with a placeholder in the example. Do not
enable `systemd-resolved` or add a second stub listener on port 53.

## Ports

The AD DC uses TCP 53, 88, 135, 139, 389, 445, 464, 636, 3268 and 3269, and
UDP 53, 88, 123, 137, 138, 389 and 464. The nftables policy allows these
ports only from the private LAN. Do not expose them to the internet.

## Common checks

```bash
# Domain and forest level
sudo samba-tool domain level show

# Domain information
sudo samba-tool domain info 127.0.0.1

# Password policy
sudo samba-tool domain passwordsettings show

# DNS zones (replace the realm placeholder)
sudo samba-tool dns zonelist 127.0.0.1 -U <admin-account>
```

Anonymous SMB enumeration is expected to be denied. A test can print
`Anonymous login successful` followed by
`tree connect failed: NT_STATUS_ACCESS_DENIED`; the denial is the expected
result.

## Security notes

- Never put the domain administrator password or any user password in this
  repository, a report, a commit or shell history.
- Do not reuse the test accounts from the setup in production.
- The private TLS certificate for the DC is self-signed. It is not published.
- GPO management needs a separate administrative workstation; this repository
  does not provide a GUI.
- Back up the AD data and configuration as described in
  [`docs/backup.md`](backup.md).

## Client notes

A Linux client needs DNS pointed at the AD DC, correct time and an FQDN. Use
`realm discover` and `realm join` only after confirming that the client can
reach the AD ports and that NTP is stable. The NixOS client mDNS work is
deferred, so do not assume `.local` AD discovery from that client yet.
