#!/usr/bin/env python3
"""URL parity: the 16 indexable URLs, the two noindex thank-you pages, the static files; nothing else."""
import re
import sys
from pathlib import Path

PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
INDEXABLE = [
    "", "defensa", "precios", "abogada", "servicios", "privacidad", "sms", "sms-optin",
    "en", "en/defense", "en/pricing", "en/attorney", "en/services", "en/privacy", "en/sms", "en/sms-optin",
]
NOINDEX = ["sms-optin/gracias", "en/sms-optin/thanks"]
STATIC = ["404.html", "en/404.html", "robots.txt", "sitemap.xml", "favicon.svg", "favicon-32.png",
          "apple-touch-icon.png", "og-image.jpg", "sms-optin-form.png"]


def main():
    errors = []
    pages = {str(p.parent.relative_to(PUBLIC)).replace(".", ""): p for p in PUBLIC.rglob("index.html")}
    expected = set(INDEXABLE + NOINDEX)
    for url in sorted(expected - set(pages)):
        errors.append(f"missing page /{url}/")
    for url in sorted(set(pages) - expected):
        errors.append(f"unexpected page /{url}/ (a stub such as /es/ must not exist)")
    for f in STATIC:
        if not (PUBLIC / f).is_file():
            errors.append(f"missing file /{f}")
    sm = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    locs = sorted(re.findall(r"<loc>([^<]+)</loc>", sm))
    want = sorted("https://www.mi-abogado.us/" + (u + "/" if u else "") for u in INDEXABLE)
    if locs != want:
        errors.append(f"sitemap.xml lists {len(locs)} URLs, expected exactly the {len(want)} indexable ones")
    for u in NOINDEX:
        if u in pages and not re.search(r'name="?robots"? content="?noindex', pages[u].read_text(encoding="utf-8")):
            errors.append(f"/{u}/ lacks noindex")
    for e in errors:
        print("FAIL", e)
    print("check_urls:", "FAILED" if errors else "ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
