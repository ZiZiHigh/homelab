# Media over the LAN

The lab runs on two machines. The small Docker host has almost no free disk, so
the video files live on a desktop PC and are shared over SMB. Jellyfin runs on
the Docker host and reads them through a CIFS mount. Nothing is copied; the
mount is read-only.

Real host names, addresses and paths are replaced with placeholders here.

## Why SMB and not NFS

The Docker host is a minimal Arch install. It already ships `cifs-utils` and has
no `nfs-utils`, so SMB needs no new packages. SMB also survives the media host
rebooting and gives per-share access control with one config block.

## Media host: export one folder

Only the folder with finished series is exported. The rest of the disk holds
downloads, ISOs and game files that Jellyfin has no business indexing.

```nix
services.samba = {
  enable = true;
  openFirewall = true;
  settings = {
    global = {
      workgroup = "WORKGROUP";
      serverString = "media host";
      security = "user";
      "map to guest" = "Bad User";
      # Only the Docker host may connect.
      "hosts allow" = "192.0.2.10 127.0.0.1";
      "hosts deny" = "0.0.0.0/0";
    };
    media = {
      path = "/run/media/user/disk/filmy";
      browseable = "yes";
      "read only" = "yes";
      "guest ok" = "yes";
      "force user" = "user";
    };
  };
};
```

The share is read-only and restricted to a single source address, so a mistake
in Jellyfin cannot delete or rename the library.

## Docker host: mount it where Jellyfin expects it

Jellyfin's compose file mounts `./media:/media:ro`, so the share is mounted
inside that directory:

```bash
sudo mkdir -p /opt/jellyfin/media/filmy
sudo mount -t cifs //192.0.2.20/media /opt/jellyfin/media/filmy \
  -o guest,ro,uid=1000,gid=1000,iocharset=utf8,vers=3.0
```

`/etc/fstab` makes it permanent and lazy:

```fstab
//192.0.2.20/media /opt/jellyfin/media/filmy cifs guest,ro,uid=1000,gid=1000,iocharset=utf8,vers=3.0,x-systemd.automount,x-systemd.mount-timeout=10,_netdev 0 0
```

`x-systemd.automount` means the mount is created on first access instead of at
boot. If the media host is off, the Docker host still boots and Jellyfin starts;
it just has no media until the share comes back.

## The gotcha: mount propagation

A bind mount that is added **after** the container started is invisible inside
it. Docker uses `rprivate` propagation by default, so the container keeps the
view of `/media` from the moment it was created:

```bash
docker exec jellyfin ls /media        # empty, even though the host sees files
docker inspect jellyfin --format '{{range .Mounts}}{{.Source}} {{.Propagation}}{{"\n"}}{{end}}'
```

The fix is to mount the share before the container starts, or to restart the
container after mounting. Adding a `:rshared` bind mount would also work, but
restarting is simpler and needs no compose change.

## Library layout

Jellyfin matches episodes from the file name, not from the folder name, so the
release folder name does not matter as long as the episode tag is there:

```text
media/
├── Money Heist S01 ... - Telly/
│   ├── Money Heist S01E01 ... .mkv
│   └── Money Heist S01E02 ... .mkv
└── Mr. Robot (2015)(CZ)[BBRip]/
    ├── mr.robot.s01e01..mkv
    └── mr.robot.s01e02..mkv
```

The library is created with collection type `tvshows` and one path, `/media`:

```bash
curl -X POST -H "X-Emby-Token: $TOKEN" \
  "$JELLYFIN/Library/VirtualFolders?name=Shows&collectionType=tvshows&paths=%2Fmedia%2Ffilmy&refreshLibrary=true"
```

After the scan, both series were matched to TMDb (posters, logos and overviews
downloaded) and all 23 episodes were indexed. A release name with dots and a
year, such as `Mr. Robot (2015)(CZ)[BBRip]`, is recognised fine once the episode
tag follows the `SxxEyy` pattern.

## Limits worth knowing

- The media host is a desktop, so the export exists only while its disk is
  mounted. An export of a removable, user-mounted disk is not a NAS.
- Playback is fine over Wi-Fi for 720p. Copying tens of gigabytes over the same
  link is slow, so the share is meant for streaming, not for backups.
- Read-only plus a single allowed client address is the whole hardening story
  here. A real deployment would use authenticated SMB and a separate VLAN.
