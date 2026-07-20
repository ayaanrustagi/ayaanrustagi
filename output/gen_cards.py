#!/usr/bin/env python3
"""Generate self-hosted stats + language cards from the GitHub API.

Re-run any time to refresh:  python3 output/gen_cards.py
Requires: gh CLI, authenticated.
"""
import collections
import json
import os
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

USER = "ayaanrustagi"

import theme as T

BG, BORDER, TEXT, DOTS = T.BG, T.BORDER, T.TEXT, T.DOTS

FS, PAD, LH = 13, 24, 20
CW = FS * 0.6
COLS = 44
FONT = T.FONT

QUERY = """
{
  user(login: "%s") {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalRepositoriesWithContributedCommits
    }
  }
}
""" % USER


def fetch():
    raw = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(raw)["data"]["user"]


def tspan(txt, fill, bold=False):
    w = ' font-weight="700"' if bold else ""
    return f'<tspan fill="{fill}"{w}>{escape(txt)}</tspan>'


def leader(label, value, cols=COLS):
    dots = cols - len(label) - len(value) - 2
    return (tspan(label, T.LABEL)
            + tspan(" " + "." * max(dots, 2) + " ", DOTS)
            + tspan(value, TEXT))


def wrap(body, width, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FS}">\n'
            f'  <rect width="{width}" height="{height}" rx="10" fill="{BG}" '
            f'stroke="{BORDER}" stroke-width="1"/>\n'
            + "\n".join("  " + l for l in body) + "\n</svg>\n")


def header(out, y, path, cmd):
    out.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">'
               + tspan("┌[ ", DOTS) + tspan("ayaan", T.USER, True)
               + tspan("@", T.AT) + tspan("github", T.HOST, True)
               + tspan(" ]─[ ", DOTS) + tspan(path, T.PATH) + tspan(" ]", DOTS) + "</text>")
    y += LH
    out.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">'
               + tspan("└> ", T.ARROW) + tspan(cmd, T.CMD, True) + "</text>")
    y += LH - 4
    inner = COLS * CW
    out.append(f'<line x1="{PAD}" y1="{y}" x2="{PAD+inner:.0f}" y2="{y}" '
               f'stroke="{BORDER}" stroke-width="1"/>')
    return y + LH


def build_stats(u):
    c = u["contributionsCollection"]
    commits = c["totalCommitContributions"] + c["restrictedContributionsCount"]
    repos = u["repositories"]["totalCount"]
    rows = [
        ("commits", f"{commits:,}"),
        ("repositories", f"{repos}"),
        ("active in", f"{c['totalRepositoriesWithContributedCommits']} repos"),
        ("followers", f"{u['followers']['totalCount']}"),
    ]
    out, y = [], PAD + FS
    y = header(out, y, "~/stats", "./stats.sh")
    for label, value in rows:
        out.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">'
                   + leader(label, value) + "</text>")
        y += LH
    w = int(PAD * 2 + COLS * CW)
    return wrap(out, w, int(y - LH + PAD + 4))


def build_langs(u):
    tally, colors = collections.Counter(), {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            tally[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or DOTS
    total = sum(tally.values()) or 1
    top = [(n, s) for n, s in tally.most_common(6) if 100 * s / total >= 0.1]

    out, y = [], PAD + FS
    y = header(out, y, "~/langs", "./langs.sh")

    # stacked bar
    bar_w, bar_h, x = COLS * CW, 9, float(PAD)
    for n, s in top:
        seg = bar_w * s / total
        out.append(f'<rect x="{x:.1f}" y="{y-FS+2}" width="{max(seg,1):.1f}" height="{bar_h}" '
                   f'fill="{colors[n]}"/>')
        x += seg
    y += LH + 2

    for n, s in top:
        pct = f"{100*s/total:.1f}%"
        out.append(f'<circle cx="{PAD+4}" cy="{y-4}" r="4" fill="{colors[n]}"/>')
        out.append(f'<text x="{PAD+16}" y="{y}" xml:space="preserve">'
                   + leader(n, pct, COLS - 2) + "</text>")
        y += LH
    w = int(PAD * 2 + COLS * CW)
    return wrap(out, w, int(y - LH + PAD + 4))


if __name__ == "__main__":
    user = fetch()
    for name, svg in (("stats", build_stats(user)), ("langs", build_langs(user))):
        path = os.path.join(HERE, f"{name}.svg")
        open(path, "w").write(svg)
        print(f"wrote {path}")
