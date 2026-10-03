#!/usr/bin/env python3
"""WCAG contrast of the declared text/background pairs, using the tokens in assets/css/site.css."""
import re
import sys
from pathlib import Path

CSS = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/css/site.css").read_text(encoding="utf-8")
TOK = dict(re.findall(r"--([a-z-]+):(#[0-9a-fA-F]{6})", CSS))
TOK.update({"white": "#ffffff", "bannerink": TOK["ink"]})
# (foreground, background, large text?)  Large = 24 px, or 19 px bold, and above.
PAIRS = [
    ("ink", "white", 0), ("ink-soft", "white", 0), ("ink-mid", "white", 0), ("ink-soft", "paper", 0),
    ("ink-soft", "cream", 0), ("ink-mid", "paper", 0), ("gold-text", "white", 0), ("gold-text", "paper", 0),
    ("gold-text", "cream", 0), ("gold", "dark", 0), ("sand", "dark", 0),
    ("cream", "dark", 0), ("dark", "gold", 0), ("ink", "gold", 0),
]
EXTRA = [("#a89a80", "dark", 0), ("#8a6000", "#faf3e0", 0), ("#8a6000", "#f5e7c8", 0), ("#4a4238", "#faf3e0", 0),
         ("#4a4238", "#f5e7c8", 0), ("#a89a80", "#1c1712", 0)]


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def val(x):
    return TOK.get(x, x)


def main():
    bad = 0
    for fg, bg, large in PAIRS + EXTRA:
        r = ratio(val(fg), val(bg))
        need = 3.0 if large else 4.5
        if r < need:
            bad += 1
            print(f"FAIL {fg} on {bg}: {r:.2f} < {need}")
    print("check_contrast:", "FAILED" if bad else "ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
