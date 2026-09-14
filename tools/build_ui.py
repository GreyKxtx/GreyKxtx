#!/usr/bin/env python3
"""Regenerate the README's artwork from one shared design system.

Edit the content lists below (INFO, SYSTEMS, ABOUT, PROJECTS, STACK, AI) and run:

    python3 tools/build_ui.py

The whole body of the profile is emitted as a SINGLE file, ui/profile.svg.
That is deliberate: GitHub renders README images as inline elements and strips
any style that would collapse the line box, so separate images always sit a few
pixels apart. One image is the only way to get a genuinely continuous surface.

The avatar is carried over from the existing ui/profile.svg.
"""
import os, re, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ui")

def _avatar():
    for name in ("profile.svg", "hero.svg"):
        src = os.path.join(OUT, name)
        if os.path.exists(src):
            m = re.search(r'href="(data:image/[^"]+)"', open(src).read())
            if m:
                return m.group(1)
    raise SystemExit("no avatar found in ui/profile.svg - restore it before rebuilding")

AVATAR = _avatar()

W = 1020
# --- design tokens -------------------------------------------------------
BG      = "#12121B"   # panel surface (lighter than pure black)
BAR     = "#191926"   # title bar, cards, chips
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

def txt(x, y, s, size, fill, anchor=None, weight=None, ls=None, cls=None):
    a = f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"'
    if anchor: a += f' text-anchor="{anchor}"'
    if weight: a += f' font-weight="{weight}"'
    if ls:     a += f' letter-spacing="{ls}"'
    if cls:    a += f' class="{cls}"'
    return a + f">{esc(s)}</text>"

def section(label, meta, x0, x1, y):
    """Accent kicker + gradient rule + right-aligned meta note."""
    o = [txt(x0, y, label, 14, ACCENT, ls=2.5),
         f'<line x1="{x0 + w(label,14,2.5) + 16:.1f}" y1="{y-4}" x2="{x1}" y2="{y-4}" stroke="url(#rule)"/>']
    if meta:
        o.append(txt(x1, y, meta, 13, MUTED, anchor="end"))
    return o

def leader(x1, x2, y):
    return (f'<line x1="{x1:.1f}" y1="{y-5:.1f}" x2="{x2:.1f}" y2="{y-5:.1f}" stroke="{RAIL}" '
            f'stroke-width="1.6" stroke-dasharray="1.6 7" stroke-linecap="round"/>')

def row(lx, rx, y, key, val, size=17, kf=MUTED, vf=TEXT):
    """key ........ value, with a dotted leader sized from the monospace metrics."""
    o = [txt(lx, y, key, size, kf), txt(rx, y, val, size, vf, anchor="end")]
    a, b = lx + w(key, size) + 14, rx - w(val, size) - 14
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
<radialGradient id="halo" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.28"/><stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
<clipPath id="av"><rect x="40" y="110" width="300" height="316" rx="12"/></clipPath>
</defs>
<style>
.fi{{animation:fi .5s ease backwards}}
@keyframes fi{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
.cur{{animation:bl 1.05s step-end infinite}}@keyframes bl{{50%{{opacity:0}}}}
.pu{{animation:pu 1.8s ease-in-out infinite}}@keyframes pu{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{.fi{{opacity:1;animation:none}}.cur,.pu{{animation:none}}}}
</style>'''

def panel(h):
    d = (f"M0 14 A14 14 0 0 1 14 0 L{W-14} 0 A14 14 0 0 1 {W} 14 "
         f"L{W} {h-14} A14 14 0 0 1 {W-14} {h} L14 {h} A14 14 0 0 1 0 {h-14} Z")
    return (f'<path d="{d}" fill="{BG}"/><path d="{d}" fill="none" stroke="{BORDER}"/>'
            f'<rect x="0" y="14" width="3" height="{h-28}" fill="url(#spine)" opacity="0.7"/>')

def write(name, h, body):
    svg = HEAD.format(w=W, h=h, f=FONT) + DEFS + panel(h) + "\n" + "\n".join(body) + "\n</svg>\n"
    open(os.path.join(OUT, name), "w").write(svg)
    print(f"  {name:16} {W}x{h}  {len(svg)/1024:.1f}K")


# =========================================================================
# content
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
           ("Mentorium", "AI tutor + skill graph"),
           ("Lunacy", "E2E messenger + calls"),
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

# name, tagline, status text, status colour, [(key, value)], description
PROJECTS = [
    ("Orchestra Code", "local-first AI coding agent", "test & polish", TEAL, [
        ("Stack", "Go - local LLMs - planner-worker orchestration"),
        ("Architecture", "Planner-worker agent loop over a Code Knowledge Graph (CKG)"),
        ("Why", "Optimized for local models - no API costs, no data leaves the machine")],
     "Coding agent designed around the constraint that the model runs on your own hardware. "
     "A planner decomposes tasks, workers execute them, and a code knowledge graph gives the "
     "model structural context instead of raw file dumps."),

    ("Orchestra Studio", "prompt-driven video generation pipeline", "in development - ships first", ACCENT2, [
        ("Stack", "Python - LLM / VLM pipelines"),
        ("Input", "A prompt - no templates, no preset scenes to fill in"),
        ("Output", "Finished video, planned, generated and assembled end to end")],
     "A prompt goes in and a finished video comes out. The pipeline plans the piece, generates "
     "its parts and assembles them - nothing is stamped out of a template, so every video is "
     "built from the prompt itself rather than fitted into a preset."),

    ("Orchestra Augur", "information aggregation & signal detection", "in development", ACCENT2, [
        ("API", "Go 1.26 - chi - pgx - goose - gofeed"),
        ("Console", "Next.js 16 - React 19 - TypeScript - Tailwind 4 - shadcn/ui - Recharts"),
        ("Data", "PostgreSQL + pgvector - RSSHub"),
        ("Markup", "LM Studio - nomic embeddings, Qwen3 for clustering and headlines"),
        ("Repository", "github.com/GreyKxtx/Orchestra-Augur")],
     "A source is added by link - site, feed, Telegram, YouTube, GitHub, Reddit, arXiv - and the "
     "service works out the feed itself. A catalogue of 806 verified sources feeds a pipeline that "
     "embeds publications, folds related ones into single story events and scores how much each "
     "matters, so the output is a ranked picture of what happened, not a feed."),

    ("Mentorium", "education platform with a realtime AI tutor", "near complete", ACCENT2, [
        ("Backend", "FastAPI (async) - SQLAlchemy - Celery - PostgreSQL - Redis - MinIO"),
        ("Frontend", "React 19 - TypeScript - Vite - React Router v7 - Tailwind - shadcn/ui"),
        ("AI", "Agent core: model routing, tools, context budget, three-tier memory"),
        ("Voice", "Local faster-whisper STT + Piper TTS, F5-TTS voice cloning"),
        ("Repository", "github.com/GreyKxtx/Mentorium")],
     "Courses, a skill-graph roadmap scoring mastery 0-5 from evidence, generated exams whose "
     "code tasks run in a locked-down Docker sandbox, verifiable certificates, and a tutor that "
     "teaches by voice on a live whiteboard."),

    ("Lunacy", "messenger for personal and corporate communication", "core stable", ACCENT2, [
        ("Backend", "Java 21 - Spring Boot 3 - Spring Cloud microservices - gRPC/Protobuf"),
        ("Data", "PostgreSQL - Redis - RabbitMQ - Elasticsearch - Prometheus/Grafana"),
        ("Frontend", "React 18 - TypeScript - Zustand - Vite - Tailwind - Electron"),
        ("Crypto", "End-to-end encryption: X3DH + Double Ratchet, device keys, JWT/RBAC"),
        ("Repository", "github.com/GreyKxtx/Lunacy")],
     "Eight Spring Boot services behind a gateway with service discovery: direct and group chats, "
     "broadcast channels, WebRTC audio/video calls with screen share, and end-to-end encrypted "
     "direct messages. Web and Electron desktop ship from one React monorepo."),

    ("TRONIX", "anti-detect browser with local-only profiles", "in development", ACCENT2, [
        ("Storage", "Profiles and configs live on your machine, not on a vendor server"),
        ("Security", "Nothing about an identity is uploaded or synced anywhere"),
        ("Automation", "Built-in scripting drives repetitive events instead of hand-clicking")],
     "An anti-detect browser built the other way round from the hosted ones: the profiles and "
     "their configuration stay local, so the data that identifies a session never leaves the "
     "machine it runs on. Routine work is handed to a script rather than repeated by hand."),

    ("Acro ERP", "business operations suite", "parked - resumes after Studio", MUTED, [
        ("Role", "One system over every module connected to the business"),
        ("Does", "Run and analyse all directions, their statistics and the problems in them"),
        ("Approach", "A modern alternative to legacy suites, with AI built in, not bolted on")],
     "A single place to run the whole business: connected modules report into it, so every "
     "direction, its statistics and the problems surfacing in it are managed and analysed "
     "together instead of module by module."),
]

STACK = [("BACKEND",    ["FastAPI", "Django", "Flask", "AIOHTTP", "Spring Boot", "Spring Cloud",
                         "REST", "WebSockets", "gRPC"]),
         ("FRONTEND",   ["React", "Next.js", "Vite", "Zustand", "Tailwind", "shadcn/ui", "SASS",
                         "Electron"]),
         ("AI TOOLING", ["PyTorch", "TensorFlow", "LangGraph", "vLLM", "LM Studio", "OpenCV",
                         "HuggingFace", "scikit-learn", "faster-whisper", "Piper"]),
         ("DATA",       ["PostgreSQL", "Redis", "MongoDB", "MySQL", "SQLite", "Elasticsearch",
                         "pgvector", "SQLAlchemy", "Alembic"]),
         ("INFRA",      ["Docker", "Kubernetes", "Nginx", "Linux", "CI/CD", "GitHub Actions",
                         "RabbitMQ", "Celery", "MinIO", "Prometheus", "Grafana", "Gradle"])]

AI = [("LLM", "local inference, quantization, fine-tuning, function calling"),
      ("Agents / Orchestration", "LangGraph, planner-worker loops, tool use, multi-agent"),
      ("RAG & Knowledge Graphs", "retrieval pipelines, embeddings, code knowledge graphs"),
      ("VLM", "vision-language models — documents, UI & screen reasoning"),
      ("Segmentation / SAM", "Segment Anything, promptable segmentation, mask pipelines"),
      ("Computer Vision", "OpenCV — detection, tracking, image pipelines"),
      ("Classic ML", "scikit-learn, clustering, scoring & ranking"),
      ("MLOps / Serving", "vLLM, Docker GPU serving, local-first deployment")]


# =========================================================================
# profile.svg — the entire body as one continuous surface
# =========================================================================
def build():
    o, d = [], 0.0
    def fade(inner):
        nonlocal d
        d += .05
        return f'<g class="fi" style="animation-delay:{d:.2f}s">{inner}</g>'

    LX, RX = 380, 980

    # --- terminal title bar ------------------------------------------------
    o.append(f'<path d="M0 14 A14 14 0 0 1 14 0 L{W-14} 0 A14 14 0 0 1 {W} 14 L{W} 48 L0 48 Z" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="48" x2="{W}" y2="48" stroke="{BORDER}"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        o.append(f'<circle cx="{28+i*20}" cy="24" r="6" fill="{c}"/>')
    o.append(txt(510, 30, "greykxtx@acro ~ % ./profile.sh --live", 16, MUTED, anchor="middle"))
    o.append(f'<circle class="pu" cx="{980 - w("ONLINE",13,1.5) - 14:.1f}" cy="20" r="4" fill="{TEAL}"/>')
    o.append(txt(980, 25, "ONLINE", 13, TEAL, anchor="end", ls=1.5))

    # --- identity ----------------------------------------------------------
    o += section("IDENTITY", None, 40, 340, 88)
    o.append('<circle cx="190" cy="268" r="180" fill="url(#halo)"/>')
    o.append(f'<image href="{AVATAR}" x="40" y="110" width="300" height="316" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#av)" class="fi"/>')
    o.append(f'<rect x="40.5" y="110.5" width="299" height="315" rx="12" fill="none" stroke="{BORDER}"/>')
    o.append(txt(190, 462, "GreyKxtx", 23, TEXT, anchor="middle", weight="600", ls=1))
    o.append(txt(190, 488, "ACRO // SYSTEMS", 14, MUTED, anchor="middle", ls=2.5))

    # --- system info -------------------------------------------------------
    o += section("SYSTEM.INFO", None, LX, RX, 88)
    o.append(txt(LX, 124, "greykxtx@acro", 20, ACCENT2, weight="600"))
    o.append(f'<rect class="cur" x="{LX + w("greykxtx@acro",20) + 6:.1f}" y="110" width="10" height="18" fill="{ACCENT}"/>')
    y = 162
    for group in (INFO, INFO2):
        for k, v in group:
            o.append(fade("".join(row(LX, RX, y, k, v)))); y += 27
        y += 10
    y += 8
    o.append(txt(LX, y, "-", 17, ACCENT))
    o.append(txt(LX + 22, y, "ACTIVE.SYSTEMS", 17, ACCENT2, ls=1)); y += 28
    for k, v in SYSTEMS:
        o.append(fade("".join(row(LX, RX, y, k, v, kf=TEXT, vf=MUTED)))); y += 27

    # --- about -------------------------------------------------------------
    y = max(y + 20, 540)
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
    o += section("ABOUT", "whoami", 40, W-40, y)
    y += 40
    for para in ABOUT:
        if not para:
            o.append(txt(40, y, "|", 19, RAIL)); y += 29; continue
        for line in textwrap.wrap(para, 70):
            o.append(fade(txt(40, y, "|", 19, RAIL) + txt(62, y, line, 19, TEXT))); y += 29
    y += 16
    o.append(txt(40, y, ">", 18, ACCENT))
    o.append(txt(62, y, "Open to:", 18, ACCENT2))
    o.append(txt(62 + w("Open to:", 18) + 16, y, "AI / backend collaborations - open source - hard engineering problems", 18, MUTED))

    # --- ecosystem + project cards ----------------------------------------
    y += 40
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
    o += section("ACRO.ECOSYSTEM", f"{len(PROJECTS)} systems", 40, W-40, y)
    y += 38
    for line in ("An umbrella of platforms for business needs — built as independent",
                 "systems that share infrastructure."):
        o.append(txt(40, y, line, 19, TEXT)); y += 29
    y += 16

    CX0, CX1 = 40, W - 40
    for name, tag, status, scol, rows, desc in PROJECTS:
        inner = []
        cy = 36                                   # cursor inside the card
        inner.append(f'<circle cx="{CX0+22}" cy="{cy-6}" r="4" fill="{scol}"/>')
        inner.append(txt(CX0 + 38, cy, name, 19, TEXT, weight="600"))
        inner.append(txt(CX0 + 38 + w(name, 19) + 18, cy, "· " + tag, 15, MUTED))
        sw = w(status, 13) + 24
        inner.append(f'<rect x="{CX1-22-sw:.1f}" y="{cy-19}" width="{sw:.1f}" height="26" rx="7" '
                     f'fill="{BG}" stroke="{BORDER}"/>')
        inner.append(txt(CX1 - 22 - sw/2, cy - 1, status, 13, scol, anchor="middle"))
        cy += 30
        for k, v in rows:
            inner.append(txt(CX0 + 38, cy, k, 14.5, ACCENT2))
            inner.append(txt(CX0 + 178, cy, v, 14.5, MUTED))
            cy += 23
        cy += 6
        for line in textwrap.wrap(desc, 92):
            inner.append(txt(CX0 + 38, cy, line, 15, TEXT))
            cy += 22
        ch = cy + 6
        o.append(fade(f'<rect x="{CX0}" y="{y}" width="{CX1-CX0}" height="{ch}" rx="10" '
                      f'fill="{BAR}" stroke="{BORDER}"/>'
                      f'<rect x="{CX0}" y="{y+10}" width="3" height="{ch-20}" fill="{scol}" opacity="0.55"/>'
                      + f'<g transform="translate(0,{y})">' + "".join(inner) + '</g>'))
        y += ch + 14

    # --- tech stack --------------------------------------------------------
    y += 18
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
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
            o.append(fade(f'<rect x="{x:.1f}" y="{ry}" width="{cw:.1f}" height="{CH}" rx="8" '
                          f'fill="{BAR}" stroke="{BORDER}"/>' + txt(x + 13, ry + 21, it, 15.5, TEXT)))
            x += cw + 9
        y = ry + CH + 16

    # --- ai directions -----------------------------------------------------
    y += 26
    o.append(f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="{BORDER}"/>')
    y += 46
    o += section("AI.DIRECTIONS", "applied focus areas", 40, W-40, y)
    y += 40
    for title, desc in AI:
        o.append(fade(f'<circle cx="46" cy="{y-6}" r="3.5" fill="{ACCENT}"/>'
                      + txt(62, y, title, 17, TEXT) + txt(380, y, desc, 15.5, MUTED)))
        y += 30

    write("profile.svg", y + 22, o)


# =========================================================================
# buttons + footer banner
# =========================================================================
def build_buttons():
    labels = ["ACRO", "LINKEDIN", "EMAIL", "TELEGRAM", "CODEWARS", "TRYHACKME",
              "MENTORIUM", "LUNACY", "AUGUR"]
    # One width for every button: ragged rows were the reason the footer looked scattered.
    BTN_W = int(round(max(w(l, 13.5, 1.2) for l in labels))) + 66
    for slug, label in [("acro", "ACRO"), ("linkedin", "LINKEDIN"), ("email", "EMAIL"),
                        ("telegram", "TELEGRAM"), ("codewars", "CODEWARS"),
                        ("tryhackme", "TRYHACKME"),
                        ("mentorium", "MENTORIUM"), ("lunacy", "LUNACY"), ("augur", "AUGUR")]:
        fs, ls = 13.5, 1.2
        tw = w(label, fs, ls)
        bw, h = BTN_W, 46
        svg = (HEAD.format(w=bw, h=h, f=FONT)
               + '<style>.g{animation:g 3s ease-in-out infinite}@keyframes g{0%,100%{opacity:.55}50%{opacity:1}}</style>'
               + f'<rect x="1" y="1" width="{bw-2}" height="{h-2}" rx="8" fill="{BG}" stroke="{BORDER}"/>'
               + f'<rect class="g" x="1" y="1" width="3" height="{h-2}" rx="1.5" fill="{ACCENT}"/>'
               + txt(bw/2 - tw/2 - 12, 29.5, "[", fs, ACCENT)
               + txt(bw/2 - tw/2, 29.5, label, fs, TEXT, ls=ls)
               + txt(bw/2 + tw/2 + 2, 29.5, "]", fs, ACCENT) + "</svg>\n")
        open(os.path.join(OUT, f"btn-{slug}.svg"), "w").write(svg)
        print(f"  btn-{slug}.svg {bw}x{h}")

def build_footer(name="banner-footer.svg", cw=1020, h=130, fs=15, rx=14, amps=(14, 10)):
    """Closing bar on the panel surface: two waves drift behind a terminal prompt.

    Each wave path is twice the canvas wide and its period divides the canvas,
    so translating by exactly one canvas width loops without a visible seam.
    Rendered at two widths - the wide canvas shrinks to a ~46px sliver on a
    phone, so the README swaps in the narrow one below 700px.
    """
    import math

    def wave(amp, periods, y0):
        period = cw / periods
        step = max(6, cw // 51)
        pts = [f"{x},{y0 + amp * math.sin(2 * math.pi * x / period):.1f}"
               for x in range(0, 2 * cw + step, step)]
        return "M" + " L".join(pts) + f" L{2*cw},{h + 40} L0,{h + 40} Z"

    rr = (f"M0 {rx} A{rx} {rx} 0 0 1 {rx} 0 L{cw-rx} 0 A{rx} {rx} 0 0 1 {cw} {rx} "
          f"L{cw} {h-rx} A{rx} {rx} 0 0 1 {cw-rx} {h} L{rx} {h} A{rx} {rx} 0 0 1 0 {h-rx} Z")
    prompt = "greykxtx@acro ~ % exit"
    curx = cw / 2 + w(prompt, fs) / 2 + 7
    ty = h * 0.37 + fs / 2

    svg = HEAD.format(w=cw, h=h, f=FONT) + f'''<defs>
<linearGradient id="fw" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{ACCENT}"/><stop offset="55%" stop-color="#6D3BF5"/><stop offset="100%" stop-color="{TEAL}"/></linearGradient>
<linearGradient id="fr" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="50%" stop-color="{ACCENT}"/><stop offset="100%" stop-color="{TEAL}" stop-opacity="0"/></linearGradient>
<clipPath id="fc"><path d="{rr}"/></clipPath></defs>
<style>
.dr{{animation:dr 18s linear infinite}}@keyframes dr{{to{{transform:translateX(-{cw}px)}}}}
.dr2{{animation:dr 27s linear infinite reverse}}
.cur{{animation:bl 1.05s step-end infinite}}@keyframes bl{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.dr,.dr2,.cur{{animation:none}}}}
</style>
<path d="{rr}" fill="{BG}"/>
<g clip-path="url(#fc)">
<path class="dr2" d="{wave(amps[1], 2, h * 0.72)}" fill="url(#fw)" fill-opacity="0.15"/>
<path class="dr" d="{wave(amps[0], 3, h * 0.60)}" fill="url(#fw)" fill-opacity="0.30"/>
</g>
<rect x="{rx}" y="0" width="{cw - 2*rx}" height="1.6" fill="url(#fr)"/>
<text x="{cw/2}" y="{ty:.0f}" font-size="{fs}" fill="{MUTED}" text-anchor="middle">{prompt}</text>
<rect class="cur" x="{curx:.1f}" y="{ty - fs + 2:.0f}" width="{fs*0.6:.0f}" height="{fs*1.15:.0f}" fill="{ACCENT}"/>
<path d="{rr}" fill="none" stroke="{BORDER}"/>
</svg>
'''
    open(os.path.join(OUT, name), "w").write(svg)
    print(f"  {name:24} {cw}x{h}")


# =========================================================================
# profile-mobile.svg — same content, one narrow column
#
# A phone shrinks the 1020px canvas to ~390px (scale 0.38), which drops the
# 19px body type to about 7px - unreadable. This canvas is narrow enough that
# a phone barely scales it (~0.9), so the type lands near its nominal size.
# README picks it via <picture media="(max-width:700px)">.
# =========================================================================
MW = 400          # canvas width
MI, MR = 20, 380  # inner left / right edge

def mpanel(h):
    d = (f"M0 12 A12 12 0 0 1 12 0 L{MW-12} 0 A12 12 0 0 1 {MW} 12 "
         f"L{MW} {h-12} A12 12 0 0 1 {MW-12} {h} L12 {h} A12 12 0 0 1 0 {h-12} Z")
    return (f'<path d="{d}" fill="{BG}"/><path d="{d}" fill="none" stroke="{BORDER}"/>'
            f'<rect x="0" y="12" width="3" height="{h-24}" fill="url(#spine)" opacity="0.7"/>')

def build_mobile():
    o = []
    def sec(label, y, meta=None):
        out = [txt(MI, y, label, 12.5, ACCENT, ls=2.2),
               f'<line x1="{MI + w(label,12.5,2.2) + 12:.1f}" y1="{y-4}" x2="{MR}" y2="{y-4}" stroke="url(#rule)"/>']
        if meta:
            out.append(txt(MR, y, meta, 11, MUTED, anchor="end"))
        return out

    def field(key, val, y, kf=ACCENT2, vf=TEXT, ks=12, vs=14.5, wrap_at=41):
        out = [txt(MI, y, key, ks, kf, ls=1.2)]
        y += 19
        for line in textwrap.wrap(val, wrap_at):
            out.append(txt(MI, y, line, vs, vf)); y += 20
        return out, y + 9

    # title bar
    o.append(f'<path d="M0 12 A12 12 0 0 1 12 0 L{MW-12} 0 A12 12 0 0 1 {MW} 12 L{MW} 38 L0 38 Z" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="38" x2="{MW}" y2="38" stroke="{BORDER}"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        o.append(f'<circle cx="{20+i*16}" cy="19" r="5" fill="{c}"/>')
    o.append(f'<circle class="pu" cx="{MR - w("ONLINE",11,1.2) - 11:.1f}" cy="16" r="3.5" fill="{TEAL}"/>')
    o.append(txt(MR, 20, "ONLINE", 11, TEAL, anchor="end", ls=1.2))

    # identity
    y = 68
    o += sec("IDENTITY", y)
    y += 16
    o.append(f'<circle cx="{MW/2}" cy="{y+95}" r="130" fill="url(#halo)"/>')
    o.append(f'<clipPath id="avm"><rect x="{MW/2-85:.0f}" y="{y}" width="170" height="190" rx="10"/></clipPath>')
    o.append(f'<image href="{AVATAR}" x="{MW/2-85:.0f}" y="{y}" width="170" height="190" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#avm)"/>')
    o.append(f'<rect x="{MW/2-84.5:.0f}" y="{y+0.5}" width="169" height="189" rx="10" fill="none" stroke="{BORDER}"/>')
    y += 190 + 32
    o.append(txt(MW/2, y, "GreyKxtx", 20, TEXT, anchor="middle", weight="600", ls=1)); y += 22
    o.append(txt(MW/2, y, "ACRO // SYSTEMS", 11.5, MUTED, anchor="middle", ls=2.2)); y += 40

    # system info
    o += sec("SYSTEM.INFO", y); y += 30
    for k, v in INFO + INFO2:
        block, y = field(k, v, y)
        o += block
    y += 6

    o += sec("ACTIVE.SYSTEMS", y, f"{len(SYSTEMS)} systems"); y += 28
    for name, desc in SYSTEMS:
        o.append(f'<circle cx="{MI+4}" cy="{y-5}" r="3" fill="{ACCENT}"/>')
        o.append(txt(MI + 16, y, name, 14.5, TEXT)); y += 19
        for line in textwrap.wrap(desc, 40):
            o.append(txt(MI + 16, y, line, 12.5, MUTED)); y += 17
        y += 10
    y += 8

    # about
    o += sec("ABOUT", y, "whoami"); y += 30
    for para in ABOUT:
        if not para:
            y += 12; continue
        for line in textwrap.wrap(para, 37):
            o.append(txt(MI, y, "|", 15, RAIL))
            o.append(txt(MI + 16, y, line, 15, TEXT)); y += 22
    y += 18
    o.append(txt(MI, y, ">", 14, ACCENT))
    o.append(txt(MI + 16, y, "Open to:", 14, ACCENT2)); y += 20
    for line in textwrap.wrap("AI / backend collaborations - open source - hard engineering problems", 41):
        o.append(txt(MI + 16, y, line, 13, MUTED)); y += 18
    y += 26

    # ecosystem + cards
    o += sec("ACRO.ECOSYSTEM", y, f"{len(PROJECTS)} systems"); y += 28
    for line in textwrap.wrap("An umbrella of platforms for business needs — built as "
                              "independent systems that share infrastructure.", 40):
        o.append(txt(MI, y, line, 14.5, TEXT)); y += 21
    y += 14

    for name, tag, status, scol, rows, desc in PROJECTS:
        inner, cy = [], 26
        inner.append(f'<circle cx="{MI+16}" cy="{cy-5}" r="3.5" fill="{scol}"/>')
        inner.append(txt(MI + 28, cy, name, 15.5, TEXT, weight="600")); cy += 19
        for line in textwrap.wrap(tag, 38):
            inner.append(txt(MI + 28, cy, line, 12.5, MUTED)); cy += 17
        cy += 4
        sw = w(status, 11) + 18
        inner.append(f'<rect x="{MI+28}" y="{cy-13}" width="{sw:.1f}" height="21" rx="6" fill="{BG}" stroke="{BORDER}"/>')
        inner.append(txt(MI + 28 + sw/2, cy + 2, status, 11, scol, anchor="middle"))
        cy += 26
        for k, v in rows:
            inner.append(txt(MI + 28, cy, k, 11.5, ACCENT2, ls=1)); cy += 16
            for line in textwrap.wrap(v, 38):
                inner.append(txt(MI + 28, cy, line, 12.5, MUTED)); cy += 16
            cy += 6
        cy += 2
        for line in textwrap.wrap(desc, 37):
            inner.append(txt(MI + 28, cy, line, 13, TEXT)); cy += 18
        ch = cy + 6
        o.append(f'<rect x="{MI}" y="{y}" width="{MR-MI}" height="{ch}" rx="9" fill="{BAR}" stroke="{BORDER}"/>'
                 f'<rect x="{MI}" y="{y+9}" width="3" height="{ch-18}" fill="{scol}" opacity="0.55"/>'
                 f'<g transform="translate(0,{y})">' + "".join(inner) + '</g>')
        y += ch + 12
    y += 16

    # tech stack
    o += sec("TECH.STACK", y, "frameworks & tooling"); y += 26
    for label, items in STACK:
        o.append(txt(MI, y, label, 12, ACCENT, ls=1.8)); y += 18
        x, ry, CH = MI, y, 26
        for it in items:
            cw = w(it, 12.5) + 20
            if x + cw > MR:
                x, ry = MI, ry + CH + 7
            o.append(f'<rect x="{x:.1f}" y="{ry}" width="{cw:.1f}" height="{CH}" rx="7" '
                     f'fill="{BAR}" stroke="{BORDER}"/>' + txt(x + 10, ry + 17, it, 12.5, TEXT))
            x += cw + 7
        y = ry + CH + 18
    y += 10

    # ai directions
    o += sec("AI.DIRECTIONS", y, "applied focus areas"); y += 28
    for title, desc in AI:
        o.append(f'<circle cx="{MI+4}" cy="{y-5}" r="3" fill="{ACCENT}"/>')
        o.append(txt(MI + 16, y, title, 14, TEXT)); y += 18
        for line in textwrap.wrap(desc, 40):
            o.append(txt(MI + 16, y, line, 12.5, MUTED)); y += 17
        y += 10

    h = y + 14
    defs = DEFS.replace('<clipPath id="av"><rect x="40" y="110" width="300" height="316" rx="12"/></clipPath>', '')
    svg = HEAD.format(w=MW, h=h, f=FONT) + defs + mpanel(h) + "\n" + "\n".join(o) + "\n</svg>\n"
    open(os.path.join(OUT, "profile-mobile.svg"), "w").write(svg)
    print(f"  profile-mobile.svg {MW}x{h}  {len(svg)/1024:.1f}K")



def check(name, right):
    """Fail loudly if any text runs past the panel's inner edge."""
    import html as _html
    s = open(os.path.join(OUT, name)).read()
    bad = []
    for m in re.finditer(r'<text x="([-0-9.]+)" y="[0-9.]+"([^>]*)>(.*?)</text>', s):
        x, attrs = float(m.group(1)), m.group(2)
        text = _html.unescape(re.sub(r"<[^>]+>", "", m.group(3)))
        fs = float(re.search(r'font-size="([0-9.]+)"', attrs).group(1))
        ls = re.search(r'letter-spacing="([0-9.]+)"', attrs)
        wid = len(text) * (fs * 0.6021 + (float(ls.group(1)) if ls else 0))
        if 'text-anchor="end"' in attrs:      x0, x1 = x - wid, x
        elif 'text-anchor="middle"' in attrs: x0, x1 = x - wid / 2, x + wid / 2
        else:                                 x0, x1 = x, x + wid
        if x1 > right + 0.5 or x0 < 0:
            bad.append(f"{text[:60]!r} ends at {x1:.0f}")
    if bad:
        raise SystemExit(f"{name}: {len(bad)} line(s) overflow past x={right}:\n  " + "\n  ".join(bad))
    print(f"  {name:18} no overflow past x={right}")


if __name__ == "__main__":
    build(); build_mobile(); build_buttons()
    build_footer()
    build_footer('banner-footer-mobile.svg', cw=400, h=104, fs=13, rx=12, amps=(9, 7))
    check("profile.svg", 980); check("profile-mobile.svg", 380)
