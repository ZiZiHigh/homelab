#!/usr/bin/env bash
#
# restore-drill.sh - prove that a restic repository can be turned back
# into working files, not just that a backup job exits with success.
#
# Usage:
#   ./restore-drill.sh <directory>
#
# The script never touches a production repository or production data.
# It creates a throwaway repository, backs up <directory>, moves the
# original aside (simulating loss), restores it and compares SHA-256
# manifests and file modes. Everything happens in a temporary directory
# that is removed on exit, so it is safe to run on a live host.
#
# Exit status is 0 only when the restored copy is byte-identical to the
# source and the repository passes a full data check.

set -Eeuo pipefail

SOURCE_ARG=${1:-}
if [ -z "$SOURCE_ARG" ] || [ ! -d "$SOURCE_ARG" ]; then
    echo "usage: $0 <directory>" >&2
    exit 2
fi

command -v restic >/dev/null || { echo "restic is not installed" >&2; exit 2; }

SOURCE=$(realpath "$SOURCE_ARG")
WORK=$(mktemp -d "${TMPDIR:-/tmp}/restic-drill.XXXXXX")
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

export RESTIC_REPOSITORY="$WORK/repo"
export RESTIC_PASSWORD_FILE="$WORK/password"
umask 077
head -c 32 /dev/urandom | base64 -w0 > "$RESTIC_PASSWORD_FILE"

step() { printf '\n==> %s\n' "$*"; }
now_ms() { date +%s%3N; }
elapsed() { awk -v a="$1" -v b="$2" 'BEGIN { printf "%.2f", (b - a) / 1000 }'; }

FILE_COUNT=$(find "$SOURCE" -type f | wc -l)
BYTES=$(du -sb "$SOURCE" | cut -f1)

# Manifest and metadata of the source, taken before anything is moved.
(cd "$SOURCE" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$WORK/source.sha256"
(cd "$SOURCE" && find . -type f -printf '%m %u:%g %P\n' | sort -k3) > "$WORK/source.meta"
SAMPLE_REL=$(cd "$SOURCE" && find . -type f -printf '%P\n' | sort | sed -n '1p')
SAMPLE_HASH=$(cd "$SOURCE" && sha256sum "$SAMPLE_REL" | cut -d' ' -f1)

step "1/7 init throwaway repository"
restic init --quiet

step "2/7 back up $FILE_COUNT files ($BYTES bytes)"
t0=$(now_ms)
restic backup "$SOURCE" --tag drill --quiet
t1=$(now_ms)
BACKUP_SECONDS=$(elapsed "$t0" "$t1")
REPO_SIZE=$(du -sh "$WORK/repo" | cut -f1)

step "3/7 snapshot list"
restic snapshots --compact

step "4/7 simulate total loss of the source"
mv "$SOURCE" "$WORK/lost"
test ! -e "$SOURCE" && echo "source is gone: $SOURCE"

step "5/7 full restore"
t2=$(now_ms)
restic restore latest --target "$WORK/restore" --quiet
t3=$(now_ms)
RESTORE_SECONDS=$(elapsed "$t2" "$t3")

RESTORED="$WORK/restore$SOURCE"
(cd "$RESTORED" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$WORK/restored.sha256"
(cd "$RESTORED" && find . -type f -printf '%m %u:%g %P\n' | sort -k3) > "$WORK/restored.meta"

HASH_DIFFS=0
if diff -q "$WORK/source.sha256" "$WORK/restored.sha256" >/dev/null; then
    echo "content: identical ($(wc -l < "$WORK/source.sha256") files compared)"
else
    echo "content: MISMATCH"
    diff "$WORK/source.sha256" "$WORK/restored.sha256" | sed -n '1,20p'
    HASH_DIFFS=1
fi

META_DIFFS=0
if diff -q "$WORK/source.meta" "$WORK/restored.meta" >/dev/null; then
    echo "modes and ownership: identical"
else
    echo "modes and ownership: DIFFERENT"
    diff "$WORK/source.meta" "$WORK/restored.meta" | sed -n '1,20p'
    META_DIFFS=1
fi

step "6/7 selective restore of one file"
echo "file: $SAMPLE_REL"
restic restore latest --target "$WORK/single" --include "$SOURCE/$SAMPLE_REL" --quiet
SINGLE_HASH=$(sha256sum "$WORK/single$SOURCE/$SAMPLE_REL" | cut -d' ' -f1)
if [ "$SINGLE_HASH" = "$SAMPLE_HASH" ]; then
    echo "single-file restore: hash matches"
else
    echo "single-file restore: HASH MISMATCH"
    HASH_DIFFS=1
fi

step "7/7 repository integrity"
restic check --quiet && echo "structure: OK"
restic check --read-data --quiet && echo "data read-back: OK"

printf '\n== summary ==\n'
printf 'source            : %s\n' "$SOURCE"
printf 'files             : %s\n' "$FILE_COUNT"
printf 'source bytes      : %s\n' "$BYTES"
printf 'repository size   : %s\n' "$REPO_SIZE"
printf 'backup seconds    : %s\n' "$BACKUP_SECONDS"
printf 'restore seconds   : %s\n' "$RESTORE_SECONDS"
printf 'hash mismatches   : %s\n' "$HASH_DIFFS"
printf 'metadata mismatch : %s\n' "$META_DIFFS"

if [ "$HASH_DIFFS" -ne 0 ] || [ "$META_DIFFS" -ne 0 ]; then
    printf '\nRESULT: FAIL\n'
    exit 1
fi
printf '\nRESULT: PASS\n'
