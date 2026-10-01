#!/usr/bin/env python3
"""Validate same-run artifacts, then publish test-only prereleases. No PAT required."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import zipfile
from upstream import patch_hash, TEST_REPO, VERSION

ROOT = Path(__file__).resolve().parent.parent

def validate(folder):
    info = json.loads((folder / 'build-info.json').read_text())
    from patchsets import verify
    verify(info['patchset'])
    if info['patchset'] != os.environ.get('PATCHSET', 'v1'):
        raise ValueError('Artifact selected patchset mismatch')
    if info['variant'] not in ('standard', 'sos') or info['platform'] != 'windows-x86_64':
        raise ValueError('Unexpected variant/platform')
    if info.get('signed') is not False or info.get('configuration') != 'TEST ONLY':
        raise ValueError('Unexpected signing/configuration policy')
    for field in ('upstream_sha', 'custom_repository_sha'):
        if not re.fullmatch('[0-9a-f]{40}', info[field]):
            raise ValueError('Invalid source SHA')
    for field, env in [('upstream_sha', 'UPSTREAM_EXPECTED_SHA'), ('upstream_tag', 'UPSTREAM_TAG'),
                       ('workflow_run', 'GITHUB_RUN_ID'), ('custom_repository_sha', 'GITHUB_SHA')]:
        if os.environ.get(env) and str(info.get(field)) != os.environ[env]:
            raise ValueError('Artifact/source mismatch: ' + field)
    if info['common_patch_hash'] != patch_hash('common'):
        raise ValueError('Common patch hash mismatch')
    expected_sos = patch_hash('sos') if info['variant'] == 'sos' else None
    if info['sos_patch_hash'] != expected_sos:
        raise ValueError('SOS patch hash mismatch')
    if info['runtime_ui_validation'] != 'SKIPPED BY USER' or info['real_remote_session_validation'] != 'NOT TESTED':
        raise ValueError('Runtime status must not imply validation')
    entries = set()
    for line in (folder / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        if not re.fullmatch('[0-9a-f]{64}', digest) or name in entries:
            raise ValueError('Invalid/duplicate checksum entry')
        file = folder / name
        if not file.resolve().is_relative_to(folder.resolve()) or not file.is_file():
            raise ValueError('Unsafe/missing checksum path')
        if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            raise ValueError('Checksum mismatch: ' + name)
        entries.add(name)
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'}
    if entries != actual:
        raise ValueError('Checksum manifest does not cover exactly all payload files')
    binaries = list((folder / 'rustdesk').glob('*.dll')) + [folder / 'rustdesk/rustdesk.exe']
    for file in binaries:
        data = file.read_bytes()
        if len(data) < 64 or data[:2] != b'MZ':
            raise ValueError('Missing PE header: ' + file.name)
        offset = struct.unpack_from('<I', data, 0x3c)[0]
        if offset + 6 > len(data) or data[offset:offset+4] != b'PE\0\0' or struct.unpack_from('<H', data, offset+4)[0] != 0x8664:
            raise ValueError('Not Windows AMD64: ' + file.name)
    print(f'{info["variant"]}: metadata, checksums, Windows AMD64: PASS')
    return info

def collect(root):
    infos, folders = {}, {}
    for variant in ('standard', 'sos'):
        matches = [p.parent for p in root.rglob('build-info.json') if json.loads(p.read_text()).get('variant') == variant]
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one {variant} same-run artifact')
        folders[variant] = matches[0]
        infos[variant] = validate(matches[0])
    for key in ('patchset', 'upstream_sha', 'upstream_tag', 'custom_repository_sha', 'common_patch_hash', 'workflow_run', 'patch_revision'):
        if infos['standard'][key] != infos['sos'][key]:
            raise ValueError('Standard/SOS provenance mismatch: ' + key)
    return infos, folders

def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)

def request(method, path, data):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as file:
        json.dump(data, file)
        filename = file.name
    try:
        return json.loads(gh('api', '--method', method, path, '--input', filename))
    finally:
        Path(filename).unlink()

def publish(root):
    if os.environ.get('GITHUB_REPOSITORY') != TEST_REPO:
        raise ValueError('Release writes allowed only in the named test repository')
    infos, folders = collect(root)
    prepared = []
    for variant in ('standard', 'sos'):
        info, folder = infos[variant], folders[variant]
        tag = info['upstream_tag']
        if not VERSION.fullmatch(tag):
            raise ValueError('Release requires official numeric stable tag')
        revision = (ROOT / 'patch-revision.txt').read_text().strip()
        if info['patch_revision'] != revision:
            raise ValueError('Patch revision mismatch')
        release_tag = f'v{tag.lstrip("v")}-{"custom" if variant == "standard" else "sos"}-test.{revision}'
        # GitHub creates the test tag at our immutable maintenance commit, never at upstream.
        asset_dir = ROOT / '.work/release-assets' / variant
        asset_dir.mkdir(parents=True, exist_ok=False)
        archive = asset_dir / (folder.name + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
            for file in sorted(folder.rglob('*')):
                if file.is_file():
                    output.write(file, file.relative_to(folder).as_posix())
        (asset_dir / 'build-info.json').write_bytes((folder / 'build-info.json').read_bytes())
        (asset_dir / 'SHA256SUMS').write_text((folder / 'SHA256SUMS').read_text() +
            hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
        notes = f'''TEST / DEVELOPMENT — unsigned Windows x86_64 unpacked client; fictional configuration only.

Variant: {variant}
Upstream: rustdesk/rustdesk
Upstream Tag: {tag}
Upstream SHA: {info['upstream_sha']}
Custom Repository SHA: {info['custom_repository_sha']}
Patch Set: {info['patchset']}
Common Patch Hash: {info['common_patch_hash']}
SOS Patch Hash: {info['sos_patch_hash'] or 'N/A'}
Workflow: https://github.com/{TEST_REPO}/actions/runs/{info['workflow_run']}

Build reproduction: PASS
Static/build validation: PASS
Checksum: PASS
Architecture: PASS (Windows AMD64)
Runtime/UI validation: NOT TESTED (SKIPPED BY USER)
Real remote session validation: NOT TESTED
Code signing: NOT ENABLED
Configuration: TEST ONLY

SOS retains the historical UI hiding; it does not disable controller functionality at the native level.
Source: exact upstream SHA above + the maintenance commit and included AGPL patch sources.
'''
        prepared.append((release_tag, info, asset_dir, notes))
    # Validate both before any write. Stage both drafts and upload all assets before exposure.
    drafts = []
    for release_tag, info, directory, notes in prepared:
        release = request('POST', f'repos/{TEST_REPO}/releases', {
            'tag_name': release_tag, 'target_commitish': info['custom_repository_sha'],
            'name': release_tag + ' — TEST ONLY', 'body': notes, 'draft': True, 'prerelease': True})
        gh('release', 'upload', release_tag, *map(str, sorted(directory.iterdir())), '--repo', TEST_REPO)
        assets = json.loads(gh('api', f'repos/{TEST_REPO}/releases/{release["id"]}/assets'))
        if {a['name'] for a in assets} != {f.name for f in directory.iterdir()} or any(a['state'] != 'uploaded' for a in assets):
            raise ValueError('Draft asset upload incomplete; do not expose release')
        drafts.append((release, notes))
    for release, notes in drafts:
        result = request('PATCH', f'repos/{TEST_REPO}/releases/{release["id"]}', {
            'draft': False, 'prerelease': True, 'body': notes + '\nAutomation-State: complete\n'})
        print(result['html_url'])
    # GitHub cannot atomically publish two releases. Partial API failure fails the job and dedup
    # blocks further writes until manually reviewed. Never overwrite/delete existing tags/assets.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['validate', 'collect', 'publish'])
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    {'validate': validate, 'collect': collect, 'publish': publish}[args.mode](args.path)
