# Jellyfin

Jellyfin runs as a pinned container behind nginx.

```text
jellyfin/jellyfin:10.11.11
```

The private hostname is replaced with `https://jellyfin.example.test/` in
this public copy.

## Layout

- `compose.yml`: pinned image, resource limits and `no-new-privileges`.
- `config/`: private Jellyfin state; ignored by Git.
- `cache/`: private transcode cache; ignored by Git.
- `media/`: read-only media mount; ignored by Git. In this deployment it is a
  CIFS mount of a share on another machine, described in
  [`../docs/media-share.md`](../docs/media-share.md).

The container runs with UID/GID `1000:1000` and exposes port 8096 only on the
shared `homelab` network. nginx is the only host-facing proxy.

## Start

```bash
docker compose up -d
```

Verify through nginx, not by publishing port 8096 to the host.

## Current state

- The first-run wizard is complete.
- The web UI at `/web/` returns HTTP 200.
- The public info endpoint reports `StartupWizardCompleted=true`.
- Media library setup is not documented in this repository. The media tree
  was not changed beyond the approved test asset.

Do not add a library or modify the media directory without a separate
approval. Hardware transcoding is not configured; the host's Celeron GPU is a
known limitation.

## Secrets

Jellyfin has no repository secret in this Compose file. Its state under
`config/` is private and must not be committed. Backups of the config are
part of the private backup scope.
