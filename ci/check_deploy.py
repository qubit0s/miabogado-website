#!/usr/bin/env python3
"""CI check for a customer solution repo (copied from k3s-flux templates/customer-app).

Flux applies deploy/ into the customer's namespace as its deployer account, which may only manage the kinds in
ALLOWED, inside that namespace. This check fails early, in the customer repo, on:
- any other kind; cluster-scoped kinds (Namespace, ClusterRole, CustomResourceDefinition, ...) are named as such
- metadata.namespace on any object (Flux sets the customer's namespace)
- container images without a pinned tag or digest, or tagged latest
- unencrypted secrets or key material in any file of the repo (check_secrets.py, a copy of k3s-flux's)
Usage: kustomize build deploy > build.yaml && python3 ci/check_deploy.py build.yaml [REPO_DIR]
"""
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_secrets  # noqa: E402

# Keep in sync with the deployer Role in k3s-flux tenants/_template/rbac.yaml.
ALLOWED = {
    ('', 'ConfigMap'), ('', 'Secret'), ('', 'Service'), ('', 'PersistentVolumeClaim'), ('', 'ServiceAccount'),
    ('apps', 'Deployment'), ('apps', 'StatefulSet'), ('batch', 'Job'), ('batch', 'CronJob'),
    ('networking.k8s.io', 'Ingress'), ('policy', 'PodDisruptionBudget'), ('autoscaling', 'HorizontalPodAutoscaler'),
}
CLUSTER_SCOPED = {
    'Namespace', 'Node', 'PersistentVolume', 'StorageClass', 'ClusterRole', 'ClusterRoleBinding',
    'CustomResourceDefinition', 'APIService', 'PriorityClass', 'RuntimeClass', 'IngressClass', 'CSIDriver',
    'MutatingWebhookConfiguration', 'ValidatingWebhookConfiguration', 'ValidatingAdmissionPolicy',
    'ValidatingAdmissionPolicyBinding', 'ClusterIssuer',
}


def pod_specs(doc):
    spec = doc.get('spec') or {}
    if doc.get('kind') == 'CronJob':
        spec = (spec.get('jobTemplate') or {}).get('spec') or {}
    pod = (spec.get('template') or {}).get('spec')
    return [pod] if pod else []


def image_pinned(image):
    if '@sha256:' in image:
        return True
    name = image.rsplit('/', 1)[-1]
    return ':' in name and name.rsplit(':', 1)[1] != 'latest'


def check_build(path):
    errors = []
    with open(path, encoding='utf-8') as f:
        docs = [d for d in yaml.safe_load_all(f) if isinstance(d, dict)]
    for doc in docs:
        kind = doc.get('kind', '?')
        group = str(doc.get('apiVersion', '')).rpartition('/')[0]
        what = f"{kind} {(doc.get('metadata') or {}).get('name', '?')}"
        if kind in CLUSTER_SCOPED:
            errors.append(f'{what}: cluster-scoped kind, not allowed in a customer repo')
        elif (group, kind) not in ALLOWED:
            errors.append(f"{what}: kind {doc.get('apiVersion')}/{kind} is not one the deployer may manage")
        if (doc.get('metadata') or {}).get('namespace'):
            errors.append(f'{what}: metadata.namespace is set; Flux puts everything in the customer namespace')
        for pod in pod_specs(doc):
            for container in (pod.get('initContainers') or []) + (pod.get('containers') or []):
                if not image_pinned(str(container.get('image', ''))):
                    errors.append(f"{what}: image {container.get('image')!r} must be pinned to a tag (not latest) or digest")
    return errors


def main(build, repo='.'):
    errors = check_build(build)
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ('.git', '.tools')]
        errors += [e for f in files for e in check_secrets.check(os.path.join(root, f))]
    for error in errors:
        print(f'REJECTED {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:3]))
