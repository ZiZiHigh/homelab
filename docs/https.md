# HTTPS and certificates

nginx terminates TLS for the private services. Port 80 answers a health
endpoint and redirects ordinary HTTP requests to HTTPS. Port 443 has a
default server that returns 404 for unknown names, plus the private service
vhosts.

## Why a self-signed certificate

The service names are private and are not issued by a public certificate
authority. The deployment therefore uses a self-signed certificate whose SAN
list covers the private service names and the host. Those names are omitted
from this public repository.

The certificate and key are not in Git:

```text
nginx/certs/README.md   (this note)
nginx/certs/*.crt       ignored
nginx/certs/*.key       ignored
```

The private key must be mode 600 and owned by the account that manages the
nginx deployment. Never print it or commit it.

## Creating a replacement certificate

Use placeholder names only in public examples:

```bash
openssl req -x509 -nodes -newkey rsa:4096 -days 1095 \
  -keyout nginx/certs/homelab.key \
  -out nginx/certs/homelab.crt \
  -subj "/CN=homelab.example.test" \
  -addext "subjectAltName=DNS:jellyfin.example.test,DNS:search.example.test,DNS:grafana.example.test,DNS:prometheus.example.test,DNS:alerts.example.test"
```

Set the real SANs in the private deployment. Keep the certificate valid for
a known period and replace it before expiry through a planned nginx restart.

## Trusting it on clients

A browser will show a warning for a self-signed certificate. Trust the
certificate on private clients instead of disabling TLS verification.
Do not add a permanent browser exception and do not use `curl -k` as a
substitute for checking a production endpoint.

## Behaviour

- HTTP on port 80 redirects to HTTPS except for `/healthz`.
- HTTPS unknown-host requests return 404.
- `/healthz` is available without a vhost and is used by the container health
  check.
- TLS 1.2 and TLS 1.3 are enabled; older protocols are disabled.
- Security headers are set by the service vhosts.

## Legacy names

The private configuration may still contain legacy `.home` names in nginx and
the certificate. They do not resolve through DNS. `.local` mDNS is the primary
path; the actual private names are not published here. Do not add a `.home`
DNS zone just to make legacy names work.
