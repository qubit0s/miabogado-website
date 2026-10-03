# miabogado-website

Static site for www.mi-abogado.us (Spanish and English). Hugo 0.167.0 builds it, nginx serves it, Flux deploys it to the
Hostinger k3s cluster, Cloudflare Tunnel brings traffic in. Design and rationale: `docs` in the Cibernex - Mi Abogado
project (Mi-Abogado-Hugo-k3s-Flux-Spec).

| Where | What |
|---|---|
| `content/` | One Markdown file per page and language (`name.es.md`, `name.en.md`). Legal pages are full Markdown. |
| `data/content/{es,en}.yaml` | Design copy for the home, defense, pricing, attorney and services pages. Edit text here. |
| `data/site.yaml` | Phone, email, legal name, address, flat fee, social links, resource links. |
| `data/images.yaml` | Image widths, alt text (both languages), `sizes`. |
| `i18n/` | Small UI strings and the SMS opt-in form labels (consent text is verbatim: carrier requirement). |
| `layouts/` | Templates. Partials in `_partials`, shortcodes in `_shortcodes`. |
| `assets/` | CSS, fonts, source images, `sms-optin.js`. All output files are content-hashed. |
| `static/` | Favicons, `og-image.jpg`, `sms-optin-form.png` (kept at their old paths). |
| `nginx/default.conf`, `Dockerfile` | Image (nginx-unprivileged, read-only root, UID 10001). |
| `deploy/` | Kustomize manifests Flux applies to `tenant-miabogado`. CI rewrites the image digest on every release. |
| `ci/` | Checks run by `make check` and CI. |

## Local

```
make check
```

`make serve` runs the dev server. Needs Hugo 0.167.0 (extended not required), Python 3.

## Release

Push to `main`. `.github/workflows/site.yml` builds, runs every check, pushes `ghcr.io/qubit0s/miabogado-website`,
scans it and commits the new digest to `deploy/kustomization.yaml`; Flux rolls it out.

First time only: after the first successful push, set the GHCR package to Public (profile > Packages >
miabogado-website > Package settings > Change visibility). Cannot be undone.

## Rules

- No inline `style=` or `<script>` (the CSP blocks them), no third-party hosts, no tracking.
- Zero JavaScript except `sms-optin.js` on the two opt-in pages.
- `mi-abogado.us` DNS is not touched until Phase 5 of the spec; the test host is `mi-abogado.poly.one`.
