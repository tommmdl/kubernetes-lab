#!/usr/bin/env python3
"""Exercise only devops-notes/notes-lab; preserve the cluster and other notes."""
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / '.local'
BASE = 'http://127.0.0.1:8005'
checks = []
observations = {}


def k(*args, label='kubectl'):
    result = subprocess.run(['bash', 'scripts/k.sh', *args], cwd=ROOT, capture_output=True, text=True)
    (LOCAL / (label + '.log')).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(label + ': ' + (result.stdout + result.stderr)[-3000:])
    return result.stdout


def get(*args):
    return json.loads(k('get', *args, '-o', 'json'))


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print('PASS: ' + name, flush=True)


def call(path, method='GET', body=None):
    request = urllib.request.Request(BASE + path, method=method,
                                    data=None if body is None else json.dumps(body).encode(),
                                    headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(request, timeout=8)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read()
        return response.status, json.loads(raw) if raw else None


def ready():
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        try:
            if call('/readyz')[0] == 200:
                return
        except OSError:
            pass
        time.sleep(1)
    raise RuntimeError('API readiness timeout')


def rollout(kind, name):
    k('rollout', 'status', kind + '/' + name, '--timeout=180s', label='rollout-' + name)


if not (LOCAL / 'cluster-owned').exists():
    raise SystemExit('Start the dedicated cluster with scripts/lab.sh up first.')
context = k('config', 'current-context').strip()
check('Dedicated kind context selected', context == 'kind-devops-notes')
nodes = get('nodes')['items']
check('Both kind nodes Ready', len(nodes) == 2 and all(any(c['type'] == 'Ready' and c['status'] == 'True' for c in n['status']['conditions']) for n in nodes))
rollout('deployment', 'notes-api')
check('Two API replicas available', get('deployment', 'notes-api')['status'].get('availableReplicas') == 2)
check('Schema Job completed before application startup', get('job', 'notes-schema')['status'].get('succeeded') == 1)
pvc = get('pvc', 'data-postgres-alpine-0')
check('PostgreSQL claim Bound', pvc['status']['phase'] == 'Bound')
ready()
check('Liveness returns 200', call('/healthz')[0] == 200)
check('Readiness verifies application database', call('/readyz')[0] == 200)
with urllib.request.urlopen(BASE + '/', timeout=8) as response:
    html = response.read().decode()
    check('Web page served through the NodePort mapping', response.status == 200 and 'Persistent notes.' in html)
check('Invalid note rejected', call('/notes', 'POST', {'title': ''})[0] == 400)
marker = 'kubernetes-' + uuid.uuid4().hex
status, note = call('/notes', 'POST', {'title': marker})
check('Create note returns 201', status == 201)
note_id = note['id']
original_image = get('deployment', 'notes-api')['spec']['template']['spec']['containers'][0]['image']
try:
    check('Created note readable through Service', any(n['id'] == note_id and n['title'] == marker for n in call('/notes')[1]['notes']))
    pod = get('pods', '-l', 'app=notes-api')['items'][0]
    old_uid = pod['metadata']['uid']
    k('delete', 'pod', pod['metadata']['name'], '--wait=true', label='delete-api-pod')
    rollout('deployment', 'notes-api')
    ready()
    pods = get('pods', '-l', 'app=notes-api')['items']
    check('Deployment replaces a deleted API Pod', all(p['metadata']['uid'] != old_uid for p in pods) and get('deployment', 'notes-api')['status'].get('availableReplicas') == 2)
    check('Note remains after API Pod replacement', any(n['id'] == note_id for n in call('/notes')[1]['notes']))
    k('scale', 'deployment/notes-api', '--replicas=3', label='scale-three')
    rollout('deployment', 'notes-api')
    check('Application scales to three ready replicas', get('deployment', 'notes-api')['status'].get('availableReplicas') == 3)
    k('apply', '-f', 'manifests/api.yaml', label='restore-declared-replicas')
    rollout('deployment', 'notes-api')
    check('Applying manifest restores two replicas', get('deployment', 'notes-api')['spec']['replicas'] == 2)
    db_uid = get('pod', 'postgres-alpine-0')['metadata']['uid']
    k('delete', 'pod', 'postgres-alpine-0', '--wait=true', label='replace-database-pod')
    rollout('statefulset', 'postgres-alpine')
    ready()
    # HTTP can recover before Kubernetes has sampled both readiness probes.
    # Finish database recovery before starting the independent bad-image test.
    rollout('deployment', 'notes-api')
    check('StatefulSet replaces PostgreSQL Pod', get('pod', 'postgres-alpine-0')['metadata']['uid'] != db_uid)
    check('PersistentVolumeClaim identity preserved', get('pvc', 'data-postgres-alpine-0')['metadata']['uid'] == pvc['metadata']['uid'])
    check('Note survives PostgreSQL Pod replacement', any(n['id'] == note_id and n['title'] == marker for n in call('/notes')[1]['notes']))
    broken = 'ghcr.io/tommmdl/docker-lab:missing-' + uuid.uuid4().hex
    k('set', 'image', 'deployment/notes-api', 'api=' + broken, label='broken-update')
    try:
        deadline = time.monotonic() + 90
        observed = None
        while time.monotonic() < deadline:
            for pod in get('pods', '-l', 'app=notes-api')['items']:
                for container in pod['status'].get('containerStatuses', []):
                    reason = container.get('state', {}).get('waiting', {}).get('reason')
                    if reason in ['ErrImagePull', 'ImagePullBackOff']:
                        observed = reason
            if observed:
                break
            time.sleep(2)
        observations['failed_update_reason'] = observed
        check('Invalid image produces an observable pull error', observed is not None)
        check('Previous replicas remain available during failed rollout', get('deployment', 'notes-api')['status'].get('availableReplicas', 0) >= 2 and call('/readyz')[0] == 200)
        k('rollout', 'undo', 'deployment/notes-api', label='rollback')
        rollout('deployment', 'notes-api')
        ready()
        check('Rollback restores the pinned working image', get('deployment', 'notes-api')['spec']['template']['spec']['containers'][0]['image'] == original_image)
    finally:
        if get('deployment', 'notes-api')['spec']['template']['spec']['containers'][0]['image'] != original_image:
            k('set', 'image', 'deployment/notes-api', 'api=' + original_image, label='repair-after-failed-test')
            rollout('deployment', 'notes-api')
    check('Note remains readable after rollback', any(n['id'] == note_id for n in call('/notes')[1]['notes']))
finally:
    k('scale', 'deployment/notes-api', '--replicas=2', label='final-scale-two')
    rollout('deployment', 'notes-api')
    ready()
    check('Remove only the test note', call('/notes/' + str(note_id), 'DELETE')[0] == 204)
check('Deleted test note returns 404', call('/notes/' + str(note_id), 'DELETE')[0] == 404)
observations.update(api_replicas=get('deployment', 'notes-api')['status'].get('availableReplicas'),
                    database_claim=get('pvc', 'data-postgres-alpine-0')['status']['phase'],
                    api_image=original_image, node_count=len(nodes))
result = {'executed_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'checks_passed': len(checks), 'checks': checks, 'observations': observations,
          'final_state': 'Dedicated cluster running; API has two replicas; test note removed'}
(LOCAL / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
