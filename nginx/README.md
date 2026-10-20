# nginx

nginx is the only container that publishes host ports. It terminates TLS,
redirects HTTP to HTTPS, serves `/healthz` and proxies the private services on
the shared `homelab` network.

- `compose.yml`: pinned `nginx:1.30.6-alpine3.24`, ports 80/443, read-only
  config and certificate mounts, resource limits and health check.
- `nginx.conf`: sanitized reverse-proxy configuration. Private names and the
  real LAN CIDR are replaced with placeholders.
- `certs/README.md`: certificate handling; real certificate and key are
  untracked.

Only nginx publishes ports. Do not add host port mappings for the application
containers. See [`docs/https.md`](../docs/https.md) for TLS details.
