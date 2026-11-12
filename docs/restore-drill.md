# Restore drill

A backup that has never been restored is a hypothesis, not a backup. This is
the record of turning one back into files.

| | |
|---|---|
| Date | 2026-11-12 |
| Tool | restic 0.19.1 |
| Host | Arch Linux, 2 cores, about 3.7 GiB RAM |
| Result | PASS, twice |

## Scope, and what was deliberately left out

The drill ran against a **scratch repository**, not the production one. The
production repository password is a root-only file, and
[`backup.md`](backup.md) says a restore against the only production copy is an
approval-required operation. Neither rule was bent for a demonstration.

What the drill does have in common with production is the tool, the command
sequence, and the data: the dataset is a copy of the same configuration the
nightly job covers.

| Part of the dataset | Why it is there |
|---|---|
| `nftables.conf`, `sshd_config` | host configuration, small text files with strict modes |
| backup unit files | the job definition itself must survive the host |
| nginx and monitoring configuration | real service configuration with nested directories |
| Jellyfin configuration | 40 MB of config, metadata and a 1.4 MB SQLite database |

Private keys were removed from the dataset before the run. A restore drill does
not need key material, and a scratch repository in `/tmp` is not the place for
it.

## The sequence

```text
1. init a throwaway repository with a generated password
2. back up the dataset
3. list snapshots
4. move the source directory away      <- the "loss"
5. restore the whole snapshot
6. restore one single file
7. verify the repository: structure and full data read-back
```

Step 4 moves the source instead of deleting it, so nothing outside the
temporary directory can be lost even if a path is wrong. Functionally the
source path is gone, which is what a restore has to recover from.

## Reproducing it

The script is committed as [`backup/restore-drill.sh`](../backup/restore-drill.sh):

```bash
./backup/restore-drill.sh /path/to/a/directory
```

It works only in a `mktemp` directory, removes it on exit, and returns non-zero
if anything differs. The full output of one run:

```text
==> 1/7 init throwaway repository

==> 2/7 back up 265 files (39810546 bytes)

==> 3/7 snapshot list
ID        Time                 Host       Tags    Size
------------------------------------------------------------
bf243b4c  2026-11-12 17:19:44  archlinux  drill   37.966 MiB
------------------------------------------------------------
1 snapshots

==> 4/7 simulate total loss of the source
source is gone: /srv/drill/source

==> 5/7 full restore
Summary: Restored 568 files/dirs (37.966 MiB) in 0:00
content: identical (265 files compared)
modes and ownership: identical

==> 6/7 selective restore of one file
file: etc/nftables.conf
single-file restore: hash matches

==> 7/7 repository integrity
structure: OK
data read-back: OK

== summary ==
files             : 265
source bytes      : 39810546
repository size   : 37M
backup seconds    : 2.54
restore seconds   : 1.49
hash mismatches   : 0
metadata mismatch : 0

RESULT: PASS
```

## Results

Two consecutive runs on the same dataset:

| Run | Files | Source size | Repository | Backup | Restore | Hash mismatches | Mode/owner mismatches |
|---|---|---|---|---|---|---|---|
| 1 | 265 | 38.0 MiB | 37 MiB | 2.54 s | 1.49 s | 0 | 0 |
| 2 | 265 | 38.0 MiB | 37 MiB | 2.44 s | 1.65 s | 0 | 0 |

That is roughly 16 MB/s in and 27 MB/s out, but the numbers are only a sanity
check: the repository sat on `tmpfs`, not on the SFTP backup host. Do not quote
them as production throughput.

## What the drill proves

- The repository opens with the password and lists snapshots.
- A full restore reproduces every file byte for byte: 265 SHA-256 hashes
  compared, zero differences.
- Ownership and permission bits survive the round trip, which matters for
  `sshd_config`, `nftables.conf` and the unit files.
- A single file can be restored without pulling the whole snapshot, which is
  the normal case when someone deletes a config.
- `restic check` finds no structural damage and `restic check --read-data`
  re-reads the pack files without a checksum error.

## What it does not prove

- **The production repository itself.** It is root-only, so this drill used the
  same tooling on a copy of the data instead. A production restore still has to
  be run from a root shell.
- **Network throughput and SFTP latency.** Real restores read from another
  machine over the LAN, so expect slower and less predictable times.
- **A disaster on the backup host.** Both copies live on the same site. Losing
  that machine loses the backup too.
- **The whole host.** This is file-level recovery. Rebuilding the machine means
  reinstalling Arch, Docker, then restoring configuration, and that
  end-to-end time has not been measured.
- **Retention.** `forget` and `prune` were not exercised, so the policy is still
  only a plan.

## Follow-up

1. Run the same sequence against the production repository from a root shell,
   quarterly, and append the result here.
2. Measure a full host rebuild, not just a file restore, and record it as the
   real recovery time.
3. Add an offsite copy. Until then the drill proves the files are recoverable,
   not that the data survives losing the site.
