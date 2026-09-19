#!/usr/bin/env python3
"""Verify a disposable empty Compose deployment; never print generated credentials."""
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

root = Path(sys.argv[1]).resolve()
env = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
base = 'http://127.0.0.1:' + env.get('SERVER_PORT', '8080')
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def request(path, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
    with opener.open(req, timeout=20) as response:
        value = json.load(response)
        return value.get('data', value)


request('/health')
with opener.open(base + '/', timeout=20) as response:
    assert '<html' in response.read().decode().lower(), 'Embedded frontend missing'
auth = request('/api/v1/auth/login', {'email': env['ADMIN_EMAIL'], 'password': env['ADMIN_PASSWORD']})
token = auth.get('access_token', auth.get('token'))
assert token, 'Admin login failed'
settings = request('/api/v1/admin/settings', token=token)
assert settings['openai_codex_ticket_enabled'] is False
assert not settings.get('openai_codex_ticket_harvest_proxy_configured')
query = "SELECT json_build_object('accounts',(SELECT count(*) FROM accounts),'proxies',(SELECT count(*) FROM proxies),'api_keys',(SELECT count(*) FROM api_keys));"
raw = subprocess.check_output(['docker', 'compose', 'exec', '-T', 'postgres', 'psql', '-U', 'sub2api', '-d', 'sub2api', '-At', '-c', query], cwd=root, text=True)
counts = json.loads(raw)
assert all(value == 0 for value in counts.values()), 'Distribution was not initialized empty'
result = {'health': 'passed', 'embedded_frontend': 'passed', 'generated_admin_login': 'passed', 'state_default_off': True, 'global_pool_empty': True, 'counts': counts, 'architecture': json.loads((root / 'RELEASE.json').read_text())['architecture']}
print(json.dumps(result, indent=2))
