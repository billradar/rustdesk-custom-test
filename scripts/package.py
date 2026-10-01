#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SHA = '005a8b4a04fd906c707eefd69c4898aa2c696202'
BRIDGE_FILES = [
    'src/bridge_generated.rs', 'src/bridge_generated.io.rs',
    'flutter/lib/generated_bridge.dart', 'flutter/lib/generated_bridge.freezed.dart',
    'flutter/macos/Runner/bridge_generated.h', 'flutter/ios/Runner/bridge_generated.h',
]

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def patch_hash(root, folder):
    digest = hashlib.sha256()
    for file in sorted((root / 'patches' / folder).glob('*.patch')):
        digest.update(file.name.encode() + b'\0' + file.read_bytes())
    return digest.hexdigest()

command, tree, *args = sys.argv[1:]
tree = Path(tree)
if command == 'restore-bridge':
    bridge = Path(args[0])
    info = json.loads((bridge / 'bridge-info.json').read_text())
    if info['upstream_sha'] != git(tree, 'rev-parse', 'HEAD') or info['upstream_sha'] != SHA:
        raise SystemExit('Bridge/source upstream SHA mismatch')
    for name in BRIDGE_FILES:
        src = bridge / name
        if hashlib.sha256(src.read_bytes()).hexdigest() != info['files'][name]:
            raise SystemExit(f'Bridge hash mismatch: {name}')
        (tree / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, tree / name)
elif command == 'bridge-info':
    info = {'upstream_sha': git(tree, 'rev-parse', 'HEAD'), 'files': {}}
    if info['upstream_sha'] != SHA:
        raise SystemExit('Unsupported bridge upstream SHA')
    for name in BRIDGE_FILES:
        info['files'][name] = hashlib.sha256((tree / name).read_bytes()).hexdigest()
    (tree / 'bridge-info.json').write_text(json.dumps(info, indent=2) + '\n')
elif command == 'package':
    variant, ref, output, root = args
    if variant not in ('standard', 'sos'):
        raise SystemExit('Invalid variant')
    output, root = Path(output), Path(root)
    release = tree / 'flutter/build/windows/x64/runner/Release'
    for name in ['rustdesk.exe', 'librustdesk.dll', 'flutter_windows.dll', 'dylib_virtual_display.dll']:
        if not (release / name).is_file() or (release / name).stat().st_size == 0:
            raise SystemExit(f'Missing compiled output: {name}')
    if not (release / 'data/flutter_assets').is_dir():
        raise SystemExit('Missing Flutter assets')
    library = (release / 'librustdesk.dll').read_bytes()
    # Test binaries must carry the compile-time inputs, rather than merely having env vars.
    # Never print the values, password digest, or any part of the executable.
    for name in ['RUSTDESK_ID_SERVER', 'RUSTDESK_API_SERVER', 'RUSTDESK_KEY', 'RUSTDESK_PASSWORD']:
        value = os.environ.get(name, '').encode()
        if not value or value not in library:
            raise SystemExit(f'Compiled configuration not found: {name} (value withheld)')
    relay = os.environ.get('RUSTDESK_RELAY_SERVER', '').encode()
    if relay and relay not in library:
        raise SystemExit('Compiled relay configuration not found (value withheld)')
    print('Compiled test configuration presence: PASS (values withheld)')
    topmost = Path(os.environ['RUSTDESK_TOPMOST_DLL'])
    if not topmost.is_file():
        raise SystemExit('Missing WindowInjection.dll')
    shutil.copy2(topmost, release / 'WindowInjection.dll')
    folder = output / f'rustdesk-1.4.9-upstream2-{variant}-test-windows-x86_64'
    if folder.exists():
        raise SystemExit('Artifact destination already exists; never overwrite it')
    sha = git(tree, 'rev-parse', 'HEAD')
    if sha != SHA:
        raise SystemExit('Unexpected artifact upstream SHA')
    folder.mkdir(parents=True)
    shutil.copytree(release, folder / 'rustdesk')
    # This is an unsigned unpacked Flutter test bundle, not a production MSI/installer.
    info = {
        'variant': variant,
        'upstream_repository': 'rustdesk/rustdesk',
        'upstream_ref': ref,
        'upstream_sha': sha,
        'upstream_version': '1.4.9+2',
        'hbb_common_sha': git(tree / 'libs/hbb_common', 'rev-parse', 'HEAD'),
        'custom_repository_sha': git(root, 'rev-parse', 'HEAD'),
        'common_patch_hash': patch_hash(root, 'common'),
        'sos_patch_hash': patch_hash(root, 'sos') if variant == 'sos' else None,
        'build_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'workflow_run': os.environ.get('GITHUB_RUN_ID'),
        'platform': 'windows-x86_64',
        'signed': False,
    }
    (folder / 'build-info.json').write_text(json.dumps(info, indent=2) + '\n')
    # Preserve corresponding patch source and the AGPL licence with the test bundle.
    shutil.copy2(tree / 'LICENCE', folder / 'LICENCE')
    shutil.copy2(root / 'README.md', folder / 'SOURCE-README.md')
    shutil.copytree(root / 'patches/common', folder / 'patches/common')
    if variant == 'sos':
        shutil.copytree(root / 'patches/sos', folder / 'patches/sos')
    entries = []
    for file in sorted(folder.rglob('*')):
        if file.is_file():
            entries.append(hashlib.sha256(file.read_bytes()).hexdigest() + '  ' + file.relative_to(folder).as_posix())
    (folder / 'SHA256SUMS').write_text('\n'.join(entries) + '\n')
    print(f'Test artifact ready: {folder.name}')
else:
    raise SystemExit('Unknown command')
