#!/usr/bin/env python3
"""Hygiene of the built site (public/): no inline styles or scripts, hashed assets, no third-party loads."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
OWN = {"www.mi-abogado.us", "mi-abogado.us"}
OUTBOUND_A = {"www.facebook.com", "www.instagram.com", "www.tiktok.com", "www.miasistente.us", "www.mireembolso.com",
              "acis.eoir.justice.gov", "locator.ice.gov", "myaccount.uscis.gov", "client.docketwise.com"}
FORM_HOSTS = {"auto.mi-abogado.us"}
HASHED = re.compile(r"\.[0-9a-f]{16,}\.(css|woff2|js|avif|webp)$|_hu_[0-9a-f]+\.(avif|webp)$|\.min\.[0-9a-f]{16,}\.js$")


class P(HTMLParser):
    def __init__(self, name):
        super().__init__()
        self.name, self.errors, self.in_script, self.script_type = name, [], False, None

    def err(self, msg):
        self.errors.append(f"{self.name}: {msg}")

    def handle_data(self, data):
        if self.in_script and self.script_type == "application/ld+json":
            try:
                doc = json.loads(data)
            except ValueError:
                self.err("JSON-LD is not valid JSON")
                return
            if not isinstance(doc, list) or not all(isinstance(x, dict) and "@type" in x for x in doc):
                self.err("JSON-LD must be a list of objects with @type (a quoted string means html/template escaped it)")

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a:
            self.err(f"style= attribute on <{tag}>")
        if tag == "script":
            if "src" in a:
                if not re.search(r"sms-optin[^/]*\.js$", a["src"]):
                    self.err(f"<script src={a['src']}> not allowed")
            else:
                self.in_script, self.script_type = True, a.get("type")
                if a.get("type") != "application/ld+json":
                    self.err("inline <script> other than JSON-LD")
        for key in ("src", "href", "action"):
            v = a.get(key)
            if not v or v.startswith(("/", "#", "tel:", "mailto:", "data:")):
                continue
            host = urlparse(v).hostname
            if host in OWN:
                continue
            if tag == "a" and key == "href" and host in OUTBOUND_A:
                continue
            if tag == "form" and key == "action" and host in FORM_HOSTS:
                continue
            self.err(f"third-party {key}={v} on <{tag}>")
        if tag in ("link", "source", "img", "script"):
            for key in ("href", "src", "srcset"):
                v = a.get(key)
                if v and key != "srcset" and tag == "link" and a.get("rel") in ("canonical", "alternate", "icon", "apple-touch-icon"):
                    continue
                if v and re.search(r"\.(css|woff2|avif|webp)(\?|$)", v) and not HASHED.search(v.split("?")[0].split(" ")[0]):
                    self.err(f"asset without content hash: {v}")


def main():
    errors = []
    for f in sorted(PUBLIC.rglob("*.html")):
        p = P(str(f.relative_to(PUBLIC)))
        p.feed(f.read_text(encoding="utf-8"))
        errors += p.errors
    for f in PUBLIC.rglob("*"):
        if f.suffix in (".css", ".woff2", ".avif", ".webp", ".js") and not HASHED.search(f.name):
            errors.append(f"{f.relative_to(PUBLIC)}: file name has no content hash")
    for e in errors:
        print("FAIL", e)
    print("check_output:", "FAILED" if errors else "ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
