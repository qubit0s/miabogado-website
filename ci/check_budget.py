#!/usr/bin/env python3
"""Size budgets. Numeric values are first guesses: tighten to measured + 10 % after the first green build."""
import gzip
import re
import sys
from pathlib import Path

PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
HTML_GZ, CSS_GZ, RASTER, HOME, JS = 20_000, 15_000, 70_000, 200_000, 1_000


def gz(p):
    return len(gzip.compress(p.read_bytes(), 9))


def main():
    errors = []
    for f in PUBLIC.rglob("*.html"):
        if gz(f) > HTML_GZ:
            errors.append(f"{f.relative_to(PUBLIC)}: {gz(f)} B gzipped > {HTML_GZ}")
    css = list(PUBLIC.glob("css/*.css"))
    for f in css:
        if gz(f) > CSS_GZ:
            errors.append(f"{f.name}: {gz(f)} B gzipped > {CSS_GZ}")
    for f in PUBLIC.rglob("*"):
        if f.suffix in (".avif", ".webp", ".png", ".jpg", ".jpeg") and f.stat().st_size > RASTER:
            if f.name in ("og-image.jpg", "sms-optin-form.png"):
                continue
            errors.append(f"{f.relative_to(PUBLIC)}: {f.stat().st_size} B > {RASTER}")
    js = sum(gz(f) for f in PUBLIC.glob("*.js"))
    if js > JS:
        errors.append(f"JS total {js} B gzipped > {JS}")
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    total = gz(PUBLIC / "index.html") + sum(gz(f) for f in css)
    for href in re.findall(r'rel=preload href=(\S+?) as=font', home):
        total += (PUBLIC / href.lstrip("/")).stat().st_size
    m = re.search(r'<source type=image/avif sizes="?[^>]*?srcset="?([^">]+)', home)
    if m:
        first = m.group(1).split(",")[-2 if "," in m.group(1) else 0].split()[0]
        total += (PUBLIC / first.lstrip("/")).stat().st_size
    if total > HOME:
        errors.append(f"home page weight {total} B > {HOME}")
    print(f"home weight (HTML+CSS+fonts+hero): {total} B")
    for e in errors:
        print("FAIL", e)
    print("check_budget:", "FAILED" if errors else "ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
