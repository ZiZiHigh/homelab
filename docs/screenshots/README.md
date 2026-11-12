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
| [searxng-home.png](searxng-home.png) | SearXNG: the private search instance. |
| [searxng-results.png](searxng-results.png) | SearXNG: a results page served through the nginx proxy. |

## What is not here

Jellyfin and Alertmanager screenshots were left out on purpose. The Jellyfin
admin page shows the private user name and internal container addresses, which
do not belong in a sanitized public repository. The Alertmanager page was empty
because no alerts were firing at the time, so it would not show anything useful.
