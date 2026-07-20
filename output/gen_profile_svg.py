#!/usr/bin/env python3
"""Generate the neofetch-style profile card SVG.

Re-run after editing SECTIONS:  python3 output/gen_profile_svg.py output/profile.svg
"""
import os
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import theme as T  # noqa: E402

CW = T.FS * 0.6      # monospace advance
COLS = 62            # leader-line width in characters
WLH = 19             # wordmark line height

# --- block wordmark: AYAAN -------------------------------------------------
GLYPHS = {
    "A": [" ████ ", "██  ██", "██████", "██  ██", "██  ██"],
    "Y": ["██  ██", " ████ ", "  ██  ", "  ██  ", "  ██  "],
    "N": ["██  ██", "███ ██", "██████", "██ ███", "██  ██"],
}


def wordmark(word):
    return ["  ".join(GLYPHS[c][r] for c in word) for r in range(5)]


SECTIONS = [
    ("system", [
        ("name",     "Ayaan Rustagi"),
        ("role",     "Research Assistant · Builder · Student"),
        ("school",   "Rouse HS, Leander / Austin, TX"),
        ("labs",     "Boston University · University of Alabama"),
    ]),
    ("dev", [
        ("langs",    "Python · TypeScript · JavaScript · Swift"),
        ("frontend", "React · Next.js · Vite · Tailwind · GSAP"),
        ("backend",  "Node · MongoDB · Supabase · Firebase"),
        ("hardware", "micro:bit · ESP32 · Arduino · MicroPython"),
        ("research", "Brian2 · NumPy · SciPy · Matplotlib"),
        ("shipping", "Chrome Extensions · Vercel"),
    ]),
    ("research", [
        ("lab",      "Boston University · University of Alabama"),
        ("focus",    "computational neuroscience · neurodegeneration"),
        ("status",   "in progress, details on request"),
    ]),
    ("contact", [
        ("mail",     "ayaan.rustagi2010@gmail.com"),
        ("web",      "https://ayaanrustagi.vercel.app"),
        ("linkedin", "in/ayaan-rustagi-66026b35a"),
    ]),
]


def tspan(txt, fill, bold=False):
    w = ' font-weight="700"' if bold else ""
    return f'<tspan fill="{fill}"{w}>{escape(txt)}</tspan>'


out, y = [], T.PAD + T.FS

# prompt
out.append(f'<text x="{T.PAD}" y="{y}" xml:space="preserve">'
           + tspan("┌[ ", T.DOTS) + tspan("ayaan", T.USER, True) + tspan("@", T.AT)
           + tspan("github", T.HOST, True) + tspan(" ]─[ ", T.DOTS)
           + tspan("~/dev", T.PATH) + tspan(" ]", T.DOTS) + "</text>")
y += T.LH
out.append(f'<text x="{T.PAD}" y="{y}" xml:space="preserve">'
           + tspan("└> ", T.ARROW) + tspan("./profile.sh", T.CMD, True) + "</text>")
y += T.LH - 4

# rule
inner = COLS * CW
out.append(f'<line x1="{T.PAD}" y1="{y}" x2="{T.PAD+inner:.0f}" y2="{y}" '
           f'stroke="{T.BORDER}" stroke-width="1"/>')
y += T.LH + 6

# wordmark
for row in wordmark("AYAAN"):
    out.append(f'<text x="{T.PAD}" y="{y}" xml:space="preserve" font-size="{T.FS}">'
               + tspan(row, T.WORDMARK) + "</text>")
    y += WLH
y += T.LH - 2

# sections
for name, rows in SECTIONS:
    out.append(f'<text x="{T.PAD}" y="{y}" xml:space="preserve">'
               + tspan("[ ", T.BRACKET) + tspan(name, T.SECTION, True)
               + tspan(" ]", T.BRACKET) + "</text>")
    y += T.LH
    for label, value in rows:
        dots = COLS - len(label) - len(value) - 2
        if dots < 2:
            raise SystemExit(f"line too long: {label} / {value} (dots={dots})")
        out.append(f'<text x="{T.PAD}" y="{y}" xml:space="preserve">'
                   + tspan(label, T.LABEL)
                   + tspan(" " + "." * dots + " ", T.DOTS)
                   + tspan(value, T.TEXT) + "</text>")
        y += T.LH
    y += 10

H = int(y - 10 + T.PAD - T.LH + T.FS)
W = int(T.PAD * 2 + inner)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{T.FONT}" font-size="{T.FS}">
  <rect width="{W}" height="{H}" rx="12" fill="{T.BG}" stroke="{T.BORDER}" stroke-width="1"/>
  {chr(10).join("  " + l for l in out)}
</svg>
'''

dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "profile.svg")
open(dest, "w").write(svg)
print(f"wrote {dest}  {W}x{H}")
