# Screenshots

Taken from the running host on 2026-11-12, over HTTPS with the private
self-signed certificate. The interfaces are in Czech because that is the
language the host runs in. No credentials, tokens or private keys are visible.

| File | What it shows |
|---|---|
| [grafana-node-exporter-overview.png](grafana-node-exporter-overview.png) | Grafana, Node Exporter Full: pressure, CPU, memory, swap, filesystem and uptime at a glance. |
| [grafana-cpu-memory-network.png](grafana-cpu-memory-network.png) | Grafana: CPU, memory and network panels with the min, mean and max tables. |
| [grafana-memory-detail.png](grafana-memory-detail.png) | Grafana: meminfo, slab, shared and mapped memory panels. |
| [prometheus-target-health.png](prometheus-target-health.png) | Prometheus target health: alertmanager, node-exporter and prometheus all up. |
| [prometheus-alert-rules.png](prometheus-alert-rules.png) | Prometheus alert rules: five rules loaded, four inactive and the Watchdog rule firing. |
| [prometheus-cpu-usage-1d.png](prometheus-cpu-usage-1d.png) | Prometheus: CPU usage over 24 hours. The flat stretch is the host being powered off overnight, not a rendering bug. |
| [prometheus-memory-usage-1d.png](prometheus-memory-usage-1d.png) | Prometheus: memory usage over 24 hours, with the same night gap. |
| [alertmanager-watchdog-alert.png](alertmanager-watchdog-alert.png) | Alertmanager: the Watchdog alert delivered from Prometheus, grouped, with silence controls. |
| [jellyfin-shows-library.png](jellyfin-shows-library.png) | Jellyfin: the Shows library, two series with TMDb posters, served from a read-only SMB share. |
| [jellyfin-mr-robot-series.png](jellyfin-mr-robot-series.png) | Jellyfin: series page with the TMDb overview, rating and cast. |
| [searxng-home.png](searxng-home.png) | SearXNG: the private search instance. |
| [searxng-results.png](searxng-results.png) | SearXNG: a results page served through the nginx proxy. |

## What is not here

The Jellyfin **admin dashboard** is left out on purpose: it shows the private user
name and internal container addresses, which do not belong in a sanitized public
repository. The library view above is what a normal user sees. How the media gets
there is documented in [`../media-share.md`](../media-share.md).

The Watchdog alert is deliberately always firing. It is a dead man's switch: if
it disappears from Alertmanager, the alerting pipeline is broken.
