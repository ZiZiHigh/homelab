# TLS certificate directory

The real certificate and private key are **not** in this repository:

```text
nginx/certs/homelab.crt   ignored
nginx/certs/homelab.key   ignored
```

The nginx Compose file mounts this directory read-only into the container.
Create the files privately, keep the key mode 600, and never commit or print
them.

The deployed certificate is self-signed and covers the private service names.
Those names are omitted from the public copy. See
[`docs/https.md`](../../docs/https.md) for the trust model, a placeholder
generation command and the renewal checklist.

Do not replace the certificate with a public one unless the service names are
actually public and the DNS/ACME path has been approved.
