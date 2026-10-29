#!/usr/bin/env bash
# Rebuild every sheet and copy the PDFs to the shared Google Drive.
#   scripts/republish-all.sh                 build all, then publish all
#   scripts/republish-all.sh --build-only    build all, no publish (preview)
# Each sheet builds in its own process: the builder keeps per-sheet state. Failures stop the run,
# so a broken sheet never leaves a half-published Drive.
set -euo pipefail

PUBLISH_TRIES=3  # publish-sheets sometimes sees an empty Nextcloud glob on its first run

build_all() {
    local sheet
    for sheet in sheets/*.md; do
        echo "== build ${sheet}"
        uv run build-sheet "${sheet}"
    done
}

publish_all() {
    local try
    for try in $(seq 1 "${PUBLISH_TRIES}"); do
        uv run publish-sheets && return 0
        echo "publish try ${try} failed, retrying" >&2
        sleep 2
    done
    return 1
}

main() {
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    build_all
    [[ "${1:-}" == "--build-only" ]] || publish_all
}

main "$@"
