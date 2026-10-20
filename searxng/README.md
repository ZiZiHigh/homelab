# SearXNG

SearXNG runs as a pinned private instance behind nginx.

```text
searxng/searxng:2026.10.19-81371861f
```

The private hostname is replaced with `https://search.example.test/` in this
public copy.

## Layout

- `compose.yml`: pinned image, resource limits and `no-new-privileges`.
- `settings.yml.example`: sanitized configuration template.
- `config/settings.yml`: real private settings; ignored by Git.
- `cache/`: private cache; ignored by Git.

The container exposes port 8080 only on the shared `homelab` network.

## Configure

```bash
mkdir -p config
cp settings.yml.example config/settings.yml
secret=$(openssl rand -hex 32)
sed -i "s|__GENERATE_WITH_OPENSSL_RAND_HEX_32__|$secret|" config/settings.yml
chmod 600 config/settings.yml
```

Keep the real `settings.yml` untracked. The secret key is unique to this
instance and must not be reused.

The instance is private: `limiter: false`, `public_instance: false` and
`image_proxy: false`. Do not expose it to the internet. If the limiter is
enabled later, add Redis and update the configuration deliberately.

## Start and verify

```bash
docker compose up -d
curl -k https://search.example.test/healthz
```

The health endpoint should return a successful response. Searches are
performed by the container; no API key is stored in this repository.
