# mDNS aliases

The host uses Avahi to publish private `.local` aliases for the web services.
The actual aliases are private and are not listed here.

`homelab-mdns-alias@.service` is a systemd template. Install it under
`/etc/systemd/system/` and enable one instance per alias, for example:

```bash
sudo systemctl enable --now homelab-mdns-alias@<name>.service
```

The `ExecStart` line contains the placeholder `192.0.2.10`; replace it with
the host's real LAN address in the private deployment. Do not commit the real
address.

Requirements:

- `avahi-daemon` active;
- UDP 5353 allowed on the private Wi-Fi interface;
- `nss-mdns` configured on Linux clients that need `.local` resolution.

The Arch host and an Android client were verified. The NixOS client setup is
deferred; see [`docs/troubleshooting.md`](../docs/troubleshooting.md).
