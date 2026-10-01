#!/usr/bin/env bash
set -euo pipefail
ref=${1:-005a8b4a04fd906c707eefd69c4898aa2c696202}
destination=${2:?Usage: prepare.sh [upstream-ref] empty-workspace}
expected=005a8b4a04fd906c707eefd69c4898aa2c696202
[[ "$ref" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]{0,100}$ ]] || { echo 'Invalid upstream ref' >&2; exit 1; }
mkdir -p "$destination"
[[ -z "$(ls -A "$destination")" ]] || { echo 'Workspace must be empty; no existing files are reset or deleted.' >&2; exit 1; }
git -C "$destination" init --quiet
git -C "$destination" remote add origin https://github.com/rustdesk/rustdesk.git
git -C "$destination" fetch --depth=1 origin "$ref"
sha=$(git -C "$destination" rev-parse 'FETCH_HEAD^{commit}')
[[ "$sha" == "$expected" ]] || { echo "Unsupported SHA: $sha; this phase supports only $expected" >&2; exit 1; }
git -C "$destination" checkout --quiet --detach "$sha"
git -C "$destination" submodule update --init --recursive
[[ "$(git -C "$destination/libs/hbb_common" rev-parse HEAD)" == 7e1c392c62d39c364127307cd408421dd5f8cfb0 ]]
[[ -z "$(git -C "$destination" status --porcelain --untracked-files=all)" ]]
git -C "$destination" submodule foreach --recursive 'test -z "$(git status --porcelain --untracked-files=all)"'
printf 'Official version: 1.4.9 + 2 upstream commits\nUpstream ref: %s\nUpstream SHA: %s\n' "$ref" "$sha"
