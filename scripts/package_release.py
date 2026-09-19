#!/usr/bin/env python3
"""Build clean complete-source and Linux distribution archives from the verified overlay."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(version):
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?', version):
        raise ValueError('Expected a release version such as v0.2.0')
    upstream = json.loads((ROOT / 'UPSTREAM.json').read_text())
    return {
        'project': 'Sub2API STATE Kit',
        'version': version,
        'application_version': '0.2.6-state-kit.' + version.removeprefix('v'),
        'repository': 'https://github.com/wangyunjeff/sub2api-state-kit',
        'commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'upstream_version': upstream['tag'],
        'upstream_commit': upstream['commit'],
        'overlay_manifest_sha256': digest(ROOT / 'UPSTREAM.json'),
        'includes_user_data': False,
    }


def write_manifest(tree, info):
    (tree / 'RELEASE.json').write_text(json.dumps(info, indent=2) + '\n')
    files = sorted(p for p in tree.rglob('*') if p.is_file() and p.name != 'SHA256SUMS')
    for p in files:
        if p.is_symlink() or '.git' in p.relative_to(tree).parts or p.name == '.env':
            raise ValueError('Unexpected runtime data or symlink in package')
    (tree / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(tree).as_posix()}\n' for p in files))


def archive(tree, output, make_zip=False):
    output.mkdir(parents=True, exist_ok=True)
    target = output / (tree.name + '.tar.gz')
    if target.exists():
        raise ValueError(f'Archive already exists: {target.name}')
    with tarfile.open(target, 'w:gz') as tf:
        tf.add(tree, arcname=tree.name, filter=lambda entry: clean_owner(entry))
    result = [target]
    if make_zip:
        target = output / (tree.name + '.zip')
        with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(tree.rglob('*')):
                if path.is_file():
                    zf.write(path, f'{tree.name}/{path.relative_to(tree).as_posix()}')
        result.append(target)
    return result


def clean_owner(entry):
    entry.uid = entry.gid = 0
    entry.uname = entry.gname = ''
    return entry


def deploy_files(tree, source=False):
    for path in (ROOT / 'release' / 'deploy').iterdir():
        name = 'DEPLOY-STATE-KIT.md' if source and path.name == 'README.md' else path.name
        if source and path.name == '.dockerignore':
            continue
        shutil.copyfile(path, tree / name)
    (tree / 'init.sh').chmod(0o755)
    if source:
        path = tree / 'DEPLOY-STATE-KIT.md'
        path.write_text(path.read_text().replace('docs/usage.md', 'docs/state-kit/usage.md') + '\n完整源码包需要编译：在本目录运行 `sh init.sh`、配置 `.env` 后执行 `docker compose up -d --build`，会编译完整前端和后端。无需编译的使用者请选择 Linux 部署包。\n')


def source_package(args):
    tree = args.work / f'sub2api-state-kit_{args.version}_full-source'
    command = ['python3', str(ROOT / 'scripts' / 'prepare.py'), str(tree)]
    if args.upstream_source:
        command += ['--upstream-source', args.upstream_source]
    subprocess.run(command, check=True)
    deploy_files(tree, source=True)
    for name in ('README.md', 'README_CN.md', 'README_JA.md'):
        path = tree / name
        banner = ('> **Sub2API STATE Kit 完整源码版 / Unofficial complete source.**\n'
                  '> This tree contains upstream Sub2API v0.2.6 plus the STATE extension.\n'
                  '> 部署本扩展请先阅读 [完整部署说明](DEPLOY-STATE-KIT.md)，使用本目录的 `compose.yaml`。下方保留上游原文；官方安装脚本/镜像不包含本扩展。\n\n')
        path.write_text(banner + path.read_text())
    shutil.copyfile(ROOT / 'UPSTREAM.json', tree / 'STATE-KIT-UPSTREAM.json')
    info = metadata(args.version)
    info['kind'] = 'complete-source'
    write_manifest(tree, info)
    return archive(tree, args.output, make_zip=True)


def runtime_package(args):
    tree = args.work / f'sub2api-state-kit_{args.version}_linux_{args.arch}'
    tree.mkdir()
    deploy_files(tree)
    shutil.copyfile(args.binary, tree / 'sub2api')
    (tree / 'sub2api').chmod(0o755)
    shutil.copytree(args.source / 'backend' / 'resources', tree / 'resources')
    (tree / 'deploy').mkdir()
    shutil.copyfile(args.source / 'deploy' / 'docker-entrypoint.sh', tree / 'deploy' / 'docker-entrypoint.sh')
    dockerfile = (args.source / 'Dockerfile.goreleaser').read_text()
    dockerfile = dockerfile.replace('backend/resources /app/resources', 'resources /app/resources')
    dockerfile = dockerfile.replace('https://github.com/Wei-Shaw/sub2api"', 'https://github.com/wangyunjeff/sub2api-state-kit"')
    dockerfile += f'\nLABEL org.opencontainers.image.version="{args.version}"\n'
    (tree / 'Dockerfile').write_text(dockerfile)
    for name in ('LICENSE', 'COPYING.GPL3', 'STATE-KIT-NOTICE.md'):
        shutil.copyfile(args.source / name, tree / name)
    shutil.copytree(ROOT / 'docs', tree / 'docs')
    info = metadata(args.version)
    info.update(kind='linux-deployment', architecture=args.arch, binary_sha256=digest(tree / 'sub2api'))
    write_manifest(tree, info)
    return archive(tree, args.output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['source', 'runtime'])
    parser.add_argument('--version', default='v0.2.0')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--upstream-source')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--arch', choices=['amd64', 'arm64'])
    args = parser.parse_args()
    metadata(args.version)
    args.work.mkdir(parents=True, exist_ok=True)
    if args.kind == 'runtime' and not all((args.source, args.binary, args.arch)):
        parser.error('runtime requires --source, --binary and --arch')
    paths = source_package(args) if args.kind == 'source' else runtime_package(args)
    for path in paths:
        print(f'{digest(path)}  {path.name}')


if __name__ == '__main__':
    main()
