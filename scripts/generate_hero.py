#!/usr/bin/env python3
"""Generate the animated SVG fiber hero for the VersinoPsiOmega org README.

Concept: CONVERGENCE. Dozens of fiber paths (the unbounded conversation stream)
flow in from the left and converge into a single ember core (the fixed-size
semantic state vector); one steady line exits right — constant output, whatever
went in.

The SEMVEC wordmark is the ANSI-Shadow ASCII banner rendered as *vector*
geometry (block cells become rects, box-drawing chars become shadow strokes),
so it is pixel-identical on every machine instead of depending on the viewer's
monospace font. That is the same retro banner as the README code block, just
crisp.

Animation runs via CSS inside the SVG (works in GitHub's <img> embed);
prefers-reduced-motion collapses it to the settled still frame.

Deterministic: seeded RNG, no timestamps. Run: python3 scripts/generate_hero.py
"""
import random
from pathlib import Path

W, H = 1200, 420
FX, FY = 930.0, 214.0         # focal point — where every stream becomes one state
N_FIBERS = 46
CLEARING_X = 660              # the typography clearing fades out by here

BANNER = [
    "███████╗███████╗███╗   ███╗██╗   ██╗███████╗ ██████╗",
    "██╔════╝██╔════╝████╗ ████║██║   ██║██╔════╝██╔════╝",
    "███████╗█████╗  ██╔████╔██║██║   ██║█████╗  ██║",
    "╚════██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝██╔══╝  ██║",
    "███████║███████╗██║ ╚═╝ ██║ ╚████╔╝ ███████╗╚██████╗",
    "╚══════╝╚══════╝╚═╝     ╚═╝  ╚═══╝  ╚══════╝ ╚═════╝",
]
TAGLINE = "constant-cost semantic memory for LLM agents"
STATLINE = "turn 10  ·  turn 10 000  ·  same input footprint"

# box-drawing char -> which half-edges from the cell centre it draws
EDGES = {
    "═": ("L", "R"),
    "║": ("T", "B"),
    "╔": ("R", "B"),
    "╗": ("L", "B"),
    "╚": ("R", "T"),
    "╝": ("L", "T"),
}

THEMES = {
    "dark": dict(
        bg="#0A1626",
        bg_deep="#060E19",
        fibers=["#4E7BAA", "#6E9AC4", "#33587F", "#9FBBD6"],
        text="#E4EDF6",
        shadow="#5C7893",
        subtext="#93ADC6",
        ember="#E8843C",
        ember_deep="#C4571A",
        fiber_op=(0.16, 0.55),
        grain_op=0.055,
    ),
    "light": dict(
        bg="#F7F6F2",
        bg_deep="#EDEBE4",
        fibers=["#2A5480", "#3F6B9B", "#1B3E63", "#6690B8"],
        text="#12293F",
        shadow="#7B93AC",
        subtext="#46617E",
        ember="#C4571A",
        ember_deep="#9C3F0E",
        fiber_op=(0.20, 0.62),
        grain_op=0.03,
    ),
}


def bezier_len(p0, p1, p2, p3, steps=120):
    """Approximate cubic bezier length by sampling — needed for dash-offset draw-on."""
    def pt(t):
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        return x, y
    total, prev = 0.0, pt(0)
    for i in range(1, steps + 1):
        cur = pt(i / steps)
        total += ((cur[0] - prev[0]) ** 2 + (cur[1] - prev[1]) ** 2) ** 0.5
        prev = cur
    return total


def make_fibers(rng):
    """Three depth layers so the field has real z-depth, not a flat spray."""
    fibers = []
    for i in range(N_FIBERS):
        layer = "far" if i % 3 == 0 else ("mid" if i % 3 == 1 else "near")
        spread = {"far": 1.65, "mid": 1.25, "near": 0.85}[layer]
        y0 = FY + (rng.random() - 0.5) * H * spread
        y0 = max(-40.0, min(H + 40.0, y0))
        p0 = (-30.0, y0)
        c1 = (200.0 + rng.random() * 220.0, y0 + (rng.random() - 0.5) * 150.0)
        c2 = (640.0 + rng.random() * 200.0, FY + (y0 - FY) * (0.22 + rng.random() * 0.34))
        p3 = (FX, FY)
        fibers.append(dict(p0=p0, c1=c1, c2=c2, p3=p3,
                           len=bezier_len(p0, c1, c2, p3), i=i, layer=layer))
    return fibers


def wordmark(t, ox, oy, cw=9.6, ch=16.6):
    """Render the ANSI-Shadow banner as vector geometry — no font dependency."""
    blocks, strokes = [], []
    sw = 1.7  # shadow stroke width
    for r, line in enumerate(BANNER):
        for c, chx in enumerate(line):
            if chx == " ":
                continue
            x, y = ox + c * cw, oy + r * ch
            if chx == "█":
                # +0.4 overlap kills hairline seams between adjacent cells
                blocks.append(f'<rect x="{x:.1f}" y="{y:.1f}" '
                              f'width="{cw + 0.4:.1f}" height="{ch + 0.4:.1f}"/>')
            elif chx in EDGES:
                mx, my = x + cw / 2, y + ch / 2
                for edge in EDGES[chx]:
                    if edge == "L":
                        strokes.append(f'<path d="M {x:.1f} {my:.1f} H {mx:.1f}"/>')
                    elif edge == "R":
                        strokes.append(f'<path d="M {mx:.1f} {my:.1f} H {x + cw:.1f}"/>')
                    elif edge == "T":
                        strokes.append(f'<path d="M {mx:.1f} {y:.1f} V {my:.1f}"/>')
                    elif edge == "B":
                        strokes.append(f'<path d="M {mx:.1f} {my:.1f} V {y + ch:.1f}"/>')
    # shadow contour first, so the solid blocks sit cleanly on top of it
    return (f'<g stroke="{t["shadow"]}" stroke-width="{sw}" fill="none" '
            f'stroke-linecap="square">\n      ' + "\n      ".join(strokes) + '\n    </g>\n'
            f'    <g fill="{t["text"]}">\n      ' + "\n      ".join(blocks)
            + "\n    </g>"), len(BANNER[0]) * cw, len(BANNER) * ch


def svg(theme_name):
    t = THEMES[theme_name]
    rng = random.Random(19269195)  # seed: the US patent application number
    fibers = make_fibers(rng)

    paths, rules, pulses = [], [], []
    op_lo, op_hi = t["fiber_op"]
    for f in fibers:
        i, layer = f["i"], f["layer"]
        width = {"far": 0.5, "mid": 0.9, "near": 1.5}[layer] + rng.random() * 0.4
        op_scale = {"far": 0.55, "mid": 0.8, "near": 1.0}[layer]
        op = (op_lo + rng.random() * (op_hi - op_lo)) * op_scale
        col = t["fibers"][i % len(t["fibers"])]
        # Staggered *durations*, not delays: every fiber starts at t=0, so the
        # settled state is also the pre-animation state. A viewer whose client
        # never runs the animation still sees the finished frame, not an empty
        # canvas. Varying draw time also reads as varying path length.
        dur = 0.9 + rng.random() * 1.3
        L = f["len"] + 4
        d = (f"M {f['p0'][0]:.1f} {f['p0'][1]:.1f} "
             f"C {f['c1'][0]:.1f} {f['c1'][1]:.1f} {f['c2'][0]:.1f} {f['c2'][1]:.1f} "
             f"{f['p3'][0]:.1f} {f['p3'][1]:.1f}")
        paths.append(f'<path class="fb f{i}" d="{d}" stroke="{col}" '
                     f'stroke-width="{width:.2f}" stroke-opacity="{op:.2f}"/>')
        rules.append(f'.f{i}{{stroke-dasharray:{L:.0f};--plen:{L:.0f}px;'
                     f'animation:draw {dur:.2f}s cubic-bezier(.16,1,.3,1) forwards}}')
        # a handful of ember pulses travelling into the core, after the entrance settles
        if i % 9 == 0:
            pd = 2.6 + rng.random() * 1.8
            pulses.append(f'<path class="pulse p{i}" d="{d}" stroke="{t["ember"]}" '
                          f'stroke-width="1.7" stroke-opacity=".6" '
                          f'stroke-dasharray="16 {f["len"]:.0f}"/>')
            rules.append(f'.p{i}{{animation:flow {pd:.2f}s linear 2.5s infinite;'
                         f'--flen:-{f["len"] + 16:.0f}px}}')

    wm, wm_w, wm_h = wordmark(t, 64, 92)
    base_y = 92 + wm_h

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Menlo, Consolas, 'DejaVu Sans Mono', ui-monospace, monospace" role="img" aria-label="SEMVEC — constant-cost semantic memory for LLM agents. Many conversation streams converge into one fixed-size state vector, and a single steady line leaves it.">
  <style>
    /* Every animated element's CSS base state IS its settled state, and no rule
       uses animation-delay with a hidden start. If the animation never runs the
       page still shows the finished composition. */
    .fb, .pulse {{ fill:none; stroke-linecap:round }}
    .pulse {{ opacity:0 }}
    .tag {{ font-size:15.5px; letter-spacing:.17em; fill:{t["subtext"]} }}
    .stat {{ font-size:12px; letter-spacing:.13em; fill:{t["subtext"]}; opacity:.72 }}
    .olabel {{ font-size:11.5px; letter-spacing:.22em; fill:{t["ember"]}; opacity:.9 }}
    .cursor {{ fill:{t["ember"]}; animation:blink 1.15s step-end infinite }}
    .core-glow {{ animation:breathe 4.6s cubic-bezier(.45,0,.55,1) infinite }}
    .core-ring {{ animation:ring 4.6s cubic-bezier(.45,0,.55,1) infinite }}
    /* the "wait then appear" beats are baked into keyframe percentages rather
       than animation-delay, for the same reason */
    .exit {{ animation:settle-late 2.8s cubic-bezier(.16,1,.3,1) }}
    .veil {{ animation:settle 1.8s cubic-bezier(.16,1,.3,1) }}
    .veil-late {{ animation:settle-late 3.1s cubic-bezier(.16,1,.3,1) }}
    @keyframes draw {{ from {{ stroke-dashoffset:var(--plen,1600px) }} to {{ stroke-dashoffset:0 }} }}
    @keyframes flow {{ from {{ stroke-dashoffset:0; opacity:1 }}
                       to {{ stroke-dashoffset:var(--flen); opacity:1 }} }}
    @keyframes blink {{ 50% {{ opacity:0 }} }}
    @keyframes breathe {{ 0%,100% {{ opacity:.8 }} 50% {{ opacity:1 }} }}
    @keyframes ring {{ 0%,100% {{ r:14; opacity:.55 }} 50% {{ r:17; opacity:.28 }} }}
    @keyframes settle {{ from {{ opacity:0 }} to {{ opacity:1 }} }}
    @keyframes settle-late {{ 0%,52% {{ opacity:0 }} 100% {{ opacity:1 }} }}
    {chr(10).join("    " + r for r in rules).strip()}
    @media (prefers-reduced-motion: reduce) {{
      .fb, .exit {{ animation:none; stroke-dashoffset:0 }}
      .pulse, .cursor {{ animation:none; opacity:0 }}
      .core-glow, .core-ring, .veil, .veil-late {{ animation:none; opacity:1 }}
    }}
  </style>
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t["bg"]}"/>
      <stop offset="100%" stop-color="{t["bg_deep"]}"/>
    </linearGradient>
    <linearGradient id="clearing" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t["bg"]}" stop-opacity=".97"/>
      <stop offset="55%" stop-color="{t["bg"]}" stop-opacity=".82"/>
      <stop offset="100%" stop-color="{t["bg"]}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{t["ember"]}" stop-opacity=".85"/>
      <stop offset="35%" stop-color="{t["ember_deep"]}" stop-opacity=".34"/>
      <stop offset="100%" stop-color="{t["ember_deep"]}" stop-opacity="0"/>
    </radialGradient>
    <!-- userSpaceOnUse: a horizontal line has a zero-height bbox, which would
         degenerate an objectBoundingBox gradient and drop the stroke entirely -->
    <linearGradient id="exitGrad" gradientUnits="userSpaceOnUse"
                    x1="{FX + 22:.0f}" y1="0" x2="{W - 40}" y2="0">
      <stop offset="0%" stop-color="{t["ember"]}"/>
      <stop offset="70%" stop-color="{t["ember"]}" stop-opacity=".85"/>
      <stop offset="100%" stop-color="{t["ember"]}" stop-opacity=".3"/>
    </linearGradient>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bgGrad)"/>

  <g>
    {chr(10).join("    " + p for p in paths).strip()}
  </g>
  <g>
    {chr(10).join("    " + p for p in pulses).strip()}
  </g>

  <!-- the clearing: fibers dissolve behind the typography, resurface to the right -->
  <rect width="{CLEARING_X}" height="{H}" fill="url(#clearing)"/>

  <circle class="core-glow" cx="{FX:.0f}" cy="{FY:.0f}" r="92" fill="url(#coreGlow)"/>
  <circle cx="{FX:.0f}" cy="{FY:.0f}" r="6.5" fill="{t["ember"]}"/>
  <circle class="core-ring" cx="{FX:.0f}" cy="{FY:.0f}" r="14" fill="none"
          stroke="{t["ember"]}" stroke-opacity=".55" stroke-width="1.3"/>
  <!-- constant output: an even, metronomic dash — same tick, forever -->
  <path class="exit" d="M {FX + 22:.0f} {FY:.0f} H {W - 40}" stroke="url(#exitGrad)"
        stroke-width="3.2" fill="none" stroke-linecap="round" stroke-dasharray="4 11"/>
  <g class="veil-late">
    <text class="olabel" x="{FX - 17:.0f}" y="{FY + 46:.0f}" text-anchor="middle">O(1)</text>
  </g>

  <g class="veil">
    {wm}
    <text class="tag" x="66" y="{base_y + 34:.0f}" xml:space="preserve">{TAGLINE}</text>
    <text class="stat" x="67" y="{base_y + 60:.0f}" xml:space="preserve">{STATLINE}</text>
  </g>

  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="{t["grain_op"]}"/>
</svg>
'''


def main():
    out = Path(__file__).resolve().parent.parent / "profile" / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for name in ("dark", "light"):
        p = out / f"hero-{name}.svg"
        p.write_text(svg(name), encoding="utf-8")
        print(f"wrote {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
