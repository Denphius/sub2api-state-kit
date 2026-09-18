#!/usr/bin/env python3
"""Assemble the pinned upstream source and verified STATE overlay into a new directory."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='New, non-existing output directory')
    parser.add_argument('--upstream-source', help='Optional upstream Git mirror (including a local repository)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / 'UPSTREAM.json').read_text())
    upstream = args.upstream_source or manifest['repository']
    if args.upstream_source and Path(upstream).expanduser().exists():
        upstream = str(Path(upstream).expanduser().resolve())
    destination = args.destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        parser.error('Destination must not exist; existing checkouts are never overwritten.')
    if not destination.parent.is_dir():
        parser.error('Destination parent must already exist.')
    payload = {}
    for name, entry in manifest['files'].items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
            raise ValueError('Unsafe manifest path')
        data = (root / 'overlay' / name).read_bytes()
        if sha(data) != entry['overlay_sha256']:
            raise ValueError(f'Overlay checksum mismatch: {name}')
        payload[name] = data
    with tempfile.TemporaryDirectory(prefix='.state-kit-', dir=destination.parent) as temporary:
        tree = Path(temporary) / 'source'
        tree.mkdir()
        def git(*arguments):
            return subprocess.check_output(['git', '-C', str(tree), *arguments], text=True).strip()
        git('init', '--quiet')
        git('fetch', '--quiet', '--depth=1', '--no-tags', upstream, manifest['commit'])
        git('checkout', '--quiet', '--detach', 'FETCH_HEAD')
        if git('rev-parse', 'HEAD') != manifest['commit']:
            raise ValueError('Unexpected upstream revision')
        for name, entry in manifest['files'].items():
            target = tree / name
            expected = entry['base_sha256']
            if target.is_symlink():
                raise ValueError(f'Unexpected symlink: {name}')
            if expected is None:
                if target.exists():
                    raise ValueError(f'New file already exists upstream: {name}')
            elif not target.is_file() or sha(target.read_bytes()) != expected:
                raise ValueError(f'Upstream checksum mismatch: {name}')
        for name, data in payload.items():
            target = tree / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        shutil.copytree(root / 'docs', tree / 'docs' / 'state-kit')
        shutil.copyfile(root / 'NOTICE.md', tree / 'STATE-KIT-NOTICE.md')
        shutil.copyfile(root / 'COPYING.GPL3', tree / 'COPYING.GPL3')
        shutil.rmtree(tree / '.git')
        tree.rename(destination)
    print(f'Prepared source: {destination}')
    print(f'Upstream: {manifest["commit"]}; overlay files: {len(payload)}')


if __name__ == '__main__':
    main()
