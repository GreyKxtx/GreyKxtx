#!/usr/bin/env python3
"""Regenerate the README's SVG panels from one shared design system.

Edit the content lists below (INFO, SYSTEMS, ABOUT, STACK, AI, FOCUS) and run:

    python3 tools/build_ui.py

Every panel shares the same width, surface colour, border and type scale, so the
blocks read as one continuous surface in the README. The avatar is carried over
from the existing ui/hero.svg.
"""
import os, re, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ui")

def _avatar():
    src = os.path.join(OUT, "hero.svg")
    if os.path.exists(src):
        m = re.search(r'href="(data:image/[^"]+)"', open(src).read())
        if m:
            return m.group(1)
    raise SystemExit("no avatar found in ui/hero.svg - restore it before rebuilding")

AVATAR = _avatar()

W = 1020
# --- design tokens -------------------------------------------------------
BG      = "#12121B"   # panel surface (lighter than pure black)
BAR     = "#191926"   # title bar / bands
BORDER  = "#2E2846"
RAIL    = "#3A3358"   # gutter marks, leader dots
TEXT    = "#EDEAF7"
MUTED   = "#9E99B5"
ACCENT  = "#8B5CF6"
ACCENT2 = "#A78BFA"
TEAL    = "#2DD4BF"
FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,monospace"
CW = 0.6  # monospace advance / em

def w(text, size, ls=0.0):
    return len(text) * (size * CW + ls)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def txt(x, y, s, size, fill, anchor=None, weight=None, ls=None, cls=None, delay=None):
    a = f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"'
    if anchor: a += f' text-anchor="{anchor}"'
    if weight: a += f' font-weight="{weight}"'
    if ls:     a += f' letter-spacing="{ls}"'
    if cls:    a += f' class="{cls}"'
    if delay is not None: a += f' style="animation-delay:{delay}s"'
    return a + f">{esc(s)}</text>"

def section(label, meta, x0, x1, y):
    """Accent kicker + gradient rule + right-aligned meta note."""
    o = [txt(x0, y, label, 14, ACCENT, ls=2.5)]
    o.append(f'<line x1="{x0 + w(label,14,2.5) + 16:.1f}" y1="{y-4}" x2="{x1}" y2="{y-4}" stroke="url(#rule)"/>')
    if meta:
        o.append(txt(x1, y, meta, 13, MUTED, anchor="end"))
    return o

def leader(x1, x2, y):
    return (f'<line x1="{x1:.1f}" y1="{y-5}" x2="{x2:.1f}" y2="{y-5}" stroke="{RAIL}" '
            f'stroke-width="1.6" stroke-dasharray="1.6 7" stroke-linecap="round"/>')

def row(lx, rx, y, key, val, size=17, kf=MUTED, vf=TEXT):
    """key ........ value, with a dotted leader sized from the monospace metrics."""
    o = [txt(lx, y, key, size, kf), txt(rx, y, val, size, vf, anchor="end")]
    a = lx + w(key, size) + 14
    b = rx - w(val, size) - 14
    if b > a + 10:
        o.append(leader(a, b, y))
    return o

HEAD = ('<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        'font-family="{f}">')

DEFS = f'''<defs>
<linearGradient id="rule" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{ACCENT}"/><stop offset="100%" stop-color="{TEAL}" stop-opacity="0.10"/></linearGradient>
<linearGradient id="spine" x1="0%" y1="0%" x2="0%" y2="100%">
<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.85"/><stop offset="100%" stop-color="{TEAL}" stop-opacity="0.25"/></linearGradient>
</defs>
<style>
.fi{{animation:fi .5s ease backwards}}
@keyframes fi{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
.cur{{animation:bl 1.05s step-end infinite}}@keyframes bl{{50%{{opacity:0}}}}
.pu{{animation:pu 1.8s ease-in-out infinite}}@keyframes pu{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{.fi{{opacity:1;animation:none}}.cur,.pu{{animation:none}}}}
</style>'''

def panel(h, top_round=True, bottom_round=True):
    """Surface + 1px frame. Square corners where a panel continues into the next."""
    rt, rb = (14 if top_round else 0), (14 if bottom_round else 0)
    d = (f"M0 {rt} A{rt} {rt} 0 0 1 {rt} 0 L{W-rt} 0 A{rt} {rt} 0 0 1 {W} {rt} "
         f"L{W} {h-rb} A{rb} {rb} 0 0 1 {W-rb} {h} L{rb} {h} A{rb} {rb} 0 0 1 0 {h-rb} Z")
    if not top_round and not bottom_round:
        d = f"M0 0 L{W} 0 L{W} {h} L0 {h} Z"
    return (f'<path d="{d}" fill="{BG}"/>'
            f'<path d="{d}" fill="none" stroke="{BORDER}"/>'
            f'<rect x="0" y="{rt}" width="3" height="{h-rt-rb}" fill="url(#spine)" opacity="0.7"/>')

def write(name, h, body, top_round=True, bottom_round=True):
    svg = HEAD.format(w=W, h=h, f=FONT) + DEFS + panel(h, top_round, bottom_round) + "\n" + "\n".join(body) + "\n</svg>\n"
    open(os.path.join(OUT, name), "w").write(svg)
    print(f"  {name:22} {W}x{h}  {len(svg)/1024:.1f}K")


# =========================================================================
# hero.svg — terminal header + system info + ABOUT, one continuous surface
# =========================================================================
INFO = [("Subject", "GreyKxtx"), ("Role", "Full-stack Developer / AI Engineer"),
        ("Focus", "Applied AI - Agents - Distributed Systems"),
        ("Experience", "5+ years"), ("Status", "Building the Acro ecosystem")]
INFO2 = [("Lang.Primary", "Python, TypeScript, Go"),
         ("Lang.Also", "JavaScript, Java, C++, Ruby, SQL"),
         ("Domain", "Backend - AI/ML - Frontend - Infra"),
         ("Runtime", "Local-first inference on own hardware")]
SYSTEMS = [("Orchestra Code", "local-first AI coding agent"),
           ("Orchestra Studio", "content generation pipeline"),
           ("Orchestra Augur", "information aggregation"),
           ("Acro EdTech", "course platform + AI tutor"),
           ("Acro ERP", "business operations suite")]

ABOUT = [
    "I build production systems where AI is the product, not a feature — "
    "from agent orchestration and model serving to the interfaces people use.",
    "",
    "Most of my work goes into Acro: an ecosystem of tools for businesses and "
    "teams — coding and content agents, an information aggregator, an education "
    "platform with a realtime AI tutor, and the infrastructure underneath them. "
    "I design the architecture, write the backends, serve the models, ship the UI.",
    "",
    "I care about systems that run locally and cheaply as much as ones that "
    "scale. Much of my stack is built around local-first inference — vLLM, "
    "quantized models on consumer GPUs — rather than renting someone else's API.",
]

def build_hero():
    o, d = [], 0.0
    LX, RX = 380, 980       # right column
    # --- title bar
    o.append(f'<path d="M0 14 A14 14 0 0 1 14 0 L{W-14} 0 A14 14 0 0 1 {W} 14 L{W} 48 L0 48 Z" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{BORDER}"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        o.append(f'<circle cx="{28+i*20}" cy="24" r="6" fill="{c}"/>')
    o.append(txt(510, 30, "greykxtx@acro ~ % ./profile.sh --live", 16, MUTED, anchor="middle"))
    o.append(f'<circle class="pu" cx="{980 - w("ONLINE",13,1.5) - 14:.1f}" cy="20" r="4" fill="{TEAL}"/>')
    o.append(txt(980, 25, "ONLINE", 13, TEAL, anchor="end", ls=1.5))

    # --- left column: avatar
    o += section("IDENTITY", None, 40, 340, 88)
    o.append(f'<circle cx="190" cy="268" r="180" fill="url(#halo)"/>')
    o.append('<clipPath id="av"><rect x="40" y="110" width="300" height="316" rx="12"/></clipPath>')
    o.append(f'<image href="{AVATAR}" x="40" y="110" width="300" height="316" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#av)" class="fi"/>')
    o.append(f'<rect x="40.5" y="110.5" width="299" height="315" rx="12" fill="none" stroke="{BORDER}"/>')
    o.append(txt(190, 462, "GreyKxtx", 23, TEXT, anchor="middle", weight="600", ls=1))
    o.append(txt(190, 488, "ACRO // SYSTEMS", 14, MUTED, anchor="middle", ls=2.5))

    # --- right column: system info
    o += section("SYSTEM.INFO", None, LX, RX, 88)
    o.append(txt(LX, 124, "greykxtx@acro", 20, ACCENT2, weight="600"))
    o.append(f'<rect class="cur" x="{LX + w("greykxtx@acro",20) + 6:.1f}" y="110" width="10" height="18" fill="{ACCENT}"/>')
    y = 162
    for k, v in INFO:
        d += .06; o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">' + "".join(row(LX, RX, y, k, v)) + '</g>'); y += 27
    y += 10
    for k, v in INFO2:
        d += .06; o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">' + "".join(row(LX, RX, y, k, v)) + '</g>'); y += 27
    y += 18
    o.append(txt(LX, y, "-", 17, ACCENT))
    o.append(txt(LX + 22, y, "ACTIVE.SYSTEMS", 17, ACCENT2, ls=1)); y += 28
    for k, v in SYSTEMS:
        d += .06; o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">' + "".join(row(LX, RX, y, k, v, kf=TEXT, vf=MUTED)) + '</g>'); y += 27

    # --- ABOUT, same surface, divider instead of a gap
    y = max(y + 20, 540)
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
    o += section("ABOUT", "whoami", 40, W-40, y)
    y += 40
    for para in ABOUT:
        if not para:
            o.append(txt(40, y, "|", 19, RAIL)); y += 29; continue
        for line in textwrap.wrap(para, 70):
            d += .06
            o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">'
                     + txt(40, y, "|", 19, RAIL) + txt(62, y, line, 19, TEXT) + '</g>')
            y += 29
    y += 16
    o.append(txt(40, y, ">", 18, ACCENT))
    o.append(txt(62, y, "Open to:", 18, ACCENT2))
    o.append(txt(62 + w("Open to:", 18) + 16, y, "AI / backend collaborations - open source - hard engineering problems", 18, MUTED))

    o.insert(0, f'<radialGradient id="halo" cx="50%" cy="50%" r="50%">'
                f'<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.28"/>'
                f'<stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>')
    write("hero.svg", y + 34, o)


# =========================================================================
# ecosystem.svg — section header for the Acro Ecosystem block
# =========================================================================
def build_ecosystem():
    o = section("ACRO.ECOSYSTEM", "5 systems", 40, W-40, 46)
    o.append(txt(40, 88, "An umbrella of platforms for business needs — built as independent", 19, TEXT))
    o.append(txt(40, 117, "systems that share infrastructure.", 19, TEXT))
    chips = [("Orchestra Code", TEAL), ("Orchestra Studio", ACCENT2), ("Orchestra Augur", ACCENT2),
             ("Acro EdTech", ACCENT2), ("Acro ERP", MUTED)]
    x = 40
    for label, col in chips:
        cw = w(label, 15) + 30
        o.append(f'<rect x="{x:.1f}" y="146" width="{cw:.1f}" height="32" rx="8" fill="{BAR}" stroke="{BORDER}"/>')
        o.append(f'<circle cx="{x+15:.1f}" cy="162" r="3.5" fill="{col}"/>')
        o.append(txt(x + 26, 167, label, 15, TEXT if col != MUTED else MUTED))
        x += cw + 10
    write("ecosystem.svg", 208, o)


# =========================================================================
# stack.svg — TECH.STACK + AI.DIRECTIONS on one continuous surface
# =========================================================================
STACK = [("BACKEND",    ["Django", "FastAPI", "Flask", "AIOHTTP", "REST", "WebSockets", "gRPC"]),
         ("FRONTEND",   ["React", "Next.js", "Tailwind", "shadcn/ui", "SASS", "Vite"]),
         ("AI TOOLING", ["PyTorch", "TensorFlow", "LangGraph", "vLLM", "LM Studio", "OpenCV",
                         "HuggingFace", "scikit-learn"]),
         ("DATA",       ["PostgreSQL", "Redis", "MongoDB", "MySQL", "SQLite"]),
         ("INFRA",      ["Docker", "Kubernetes", "Nginx", "Linux", "CI/CD", "GitHub Actions"])]

AI = [("LLM", "local inference, quantization, fine-tuning, function calling"),
      ("Agents / Orchestration", "LangGraph, planner-worker loops, tool use, multi-agent"),
      ("RAG & Knowledge Graphs", "retrieval pipelines, embeddings, code knowledge graphs"),
      ("VLM", "vision-language models — documents, UI & screen reasoning"),
      ("Segmentation / SAM", "Segment Anything, promptable segmentation, mask pipelines"),
      ("Computer Vision", "OpenCV — detection, tracking, image pipelines"),
      ("Classic ML", "scikit-learn, clustering, scoring & ranking"),
      ("MLOps / Serving", "vLLM, Docker GPU serving, local-first deployment")]

def build_stack():
    o, d = [], 0.0
    y = 46
    o += section("TECH.STACK", "frameworks & tooling", 40, W-40, y)
    y += 36
    CX, CMAX, CH = 212, W - 40, 32
    for label, items in STACK:
        o.append(txt(40, y + 22, label, 14, ACCENT, ls=2))
        x, ry = CX, y
        for it in items:
            cw = w(it, 15.5) + 26
            if x + cw > CMAX:
                x, ry = CX, ry + CH + 9
            d += .04
            o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">'
                     f'<rect x="{x:.1f}" y="{ry}" width="{cw:.1f}" height="{CH}" rx="8" fill="{BAR}" stroke="{BORDER}"/>'
                     + txt(x + 13, ry + 21, it, 15.5, TEXT) + '</g>')
            x += cw + 9
        y = ry + CH + 16
    y += 26
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
    o += section("AI.DIRECTIONS", "applied focus areas", 40, W-40, y)
    y += 40
    for title, desc in AI:
        d += .05
        o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">'
                 + f'<circle cx="46" cy="{y-6}" r="3.5" fill="{ACCENT}"/>'
                 + txt(62, y, title, 17, TEXT)
                 + txt(380, y, desc, 15.5, MUTED) + '</g>')
        y += 30
    write("stack.svg", y + 26, o)


# =========================================================================
# focus.svg — roadmap
# =========================================================================
FOCUS = [("shipping",  [("Orchestra Studio — content pipeline", TEAL),
                        ("Acro EdTech — course platform", TEAL)]),
         ("building",  [("Orchestra Augur — React rewrite", ACCENT2),
                        ("Orchestra Code — CKG & planner loop", ACCENT2)]),
         ("learning",  [("agent architectures at scale", ACCENT),
                        ("distributed systems design", ACCENT)]),
         ("exploring", [("VLM for document & UI understanding", ACCENT),
                        ("local-first model serving", ACCENT)]),
         ("open_to",   [("collaboration", MUTED), ("open source", MUTED),
                        ("hard engineering problems", MUTED)])]

def build_focus():
    o, d = [], 0.0
    y = 46
    o += section("CURRENT.FOCUS", "~/roadmap.yaml", 40, W-40, y)
    y += 42
    for group, items in FOCUS:
        o.append(txt(40, y, group + ":", 18, ACCENT2))
        y += 28
        for label, col in items:
            d += .06
            o.append(f'<g class="fi" style="animation-delay:{d:.2f}s">'
                     + txt(62, y, "-", 18, col)
                     + txt(84, y, label, 18, TEXT) + '</g>')
            y += 27
        y += 14
    write("focus.svg", y + 18, o)


# =========================================================================
# buttons
# =========================================================================
def build_buttons():
    for slug, label in [("acro", "ACRO"), ("linkedin", "LINKEDIN"), ("email", "EMAIL"),
                        ("telegram", "TELEGRAM"), ("codewars", "CODEWARS"),
                        ("tryhackme", "TRYHACKME"), ("github", "GITHUB")]:
        fs, ls = 13.5, 1.2
        tw = w(label, fs, ls)
        bw = int(round(22 + 12 + tw + 12 + 20))
        h = 46
        svg = (HEAD.format(w=bw, h=h, f=FONT)
               + f'<style>.g{{animation:g 3s ease-in-out infinite}}@keyframes g{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}</style>'
               + f'<rect x="1" y="1" width="{bw-2}" height="{h-2}" rx="8" fill="{BG}" stroke="{BORDER}"/>'
               + f'<rect class="g" x="1" y="1" width="3" height="{h-2}" rx="1.5" fill="{ACCENT}"/>'
               + txt(20, 29.5, "[", fs, ACCENT)
               + txt(32, 29.5, label, fs, TEXT, ls=ls)
               + txt(32 + tw + 2, 29.5, "]", fs, ACCENT)
               + "</svg>\n")
        open(os.path.join(OUT, f"btn-{slug}.svg"), "w").write(svg)
        print(f"  btn-{slug}.svg {bw}x{h}")


# =========================================================================
# banner-footer.svg — recoloured to sit on the new surface
# =========================================================================
def build_footer():
    svg = f'''<svg width="1100" height="90" viewBox="0 0 1100 90" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="bgf" x1="0%" y1="100%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{BG}"/><stop offset="50%" stop-color="#2E1065"/><stop offset="100%" stop-color="{ACCENT}"/>
</linearGradient></defs>
<path d="M0 45 C200 15 420 70 640 40 C830 16 980 58 1100 32 L1100 90 L0 90 Z" fill="url(#bgf)"/>
<path d="M0 65 C240 35 460 85 700 58 C880 38 1000 74 1100 52 L1100 90 L0 90 Z" fill="{ACCENT}" fill-opacity="0.3"/>
</svg>
'''
    open(os.path.join(OUT, "banner-footer.svg"), "w").write(svg)
    print("  banner-footer.svg")


if __name__ == "__main__":
    build_hero(); build_ecosystem(); build_stack(); build_focus(); build_buttons(); build_footer()
