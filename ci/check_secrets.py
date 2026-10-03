#!/usr/bin/env python3
"""Fails on unencrypted secrets or key material. Nothing in this repo may hold a secret in plain text.

Rejected, in any text file: PEM private keys and age secret keys. In YAML: a Secret without SOPS metadata or with a
data/stringData value that is not ENC[...], a *.sops.yaml file without SOPS metadata, and kustomize
secretGenerator (it builds Secrets from plain-text literals or files).
Usage: check_secrets.py [FILE...]   (no arguments: every file git tracks or would track)
"""
import os
import re
import subprocess
import sys

import yaml

KEY_MATERIAL = [
    (re.compile(r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----'), 'private key (PEM block)'),
    (re.compile(r'AGE-SECRET-KEY-1[0-9A-Z]{58}'), 'age secret key'),
]


def check(path):
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
        return []
    errors = [f'{path}: {what}' for pattern, what in KEY_MATERIAL if pattern.search(text)]
    if not re.search(r'\.ya?ml$', path) or os.path.basename(path) == '.sops.yaml':
        return errors
    try:
        docs = [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]
    except yaml.YAMLError:
        return errors  # yamllint reports it
    sops_file = re.search(r'\.sops\.ya?ml$', path)
    for doc in docs:
        encrypted = isinstance(doc.get('sops'), dict)
        if sops_file and not encrypted:
            errors.append(f'{path}: named *.sops.yaml but not SOPS-encrypted')
        if doc.get('kind') == 'Secret':
            name = (doc.get('metadata') or {}).get('name', '?')
            if not encrypted:
                errors.append(f'{path}: Secret {name} is not SOPS-encrypted (use a *.sops.yaml file)')
            for field in ('data', 'stringData'):
                for key, value in (doc.get(field) or {}).items():
                    if not str(value).startswith('ENC['):
                        errors.append(f'{path}: Secret {name} {field}.{key} is not encrypted')
        if 'secretGenerator' in doc:
            errors.append(f'{path}: secretGenerator builds Secrets from plain text; use a SOPS-encrypted Secret')
    return errors


def main(paths):
    if not paths:
        listing = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                                 capture_output=True, text=True, check=True)
        paths = listing.stdout.split()
    errors = [e for p in paths for e in check(p)]
    for error in errors:
        print(f'REJECTED {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
