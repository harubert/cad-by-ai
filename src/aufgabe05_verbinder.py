"""
Aufgabe 05: TPU-Verbinder fuer Alu-Profil 40x40
- 46x46mm aussen (3mm Rand rings herum)
- 40mm hoch (flexible Huelse)
- Profil-Aussenkontour als Durchbruch (ohne Bohrung, ohne Ecktaschen)
"""

import math
import numpy as np
import re
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely.validation import make_valid
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'
SVG_FILE = OUT / 'aufgabe01_path.svg'

# === Parameter ===
RAND = 3.0
HOEHE = 40.0
PROFIL_W = 40.0
KAPPE_W = PROFIL_W + 2 * RAND  # 46mm

# === SVG Parser ===

def parse_svg_path(d_string):
    tokens = re.findall(r'[MLAZmlaz]|[-+]?\d*\.?\d+', d_string)
    points = []
    i = 0
    cx, cy = 0, 0
    while i < len(tokens):
        cmd = tokens[i]; i += 1
        if cmd == 'M':
            cx, cy = float(tokens[i]), float(tokens[i+1]); i += 2
            points.append((cx, -cy))
        elif cmd == 'L':
            cx, cy = float(tokens[i]), float(tokens[i+1]); i += 2
            points.append((cx, -cy))
        elif cmd == 'A':
            rx = float(tokens[i]); i += 1
            ry = float(tokens[i]); i += 1
            rot = float(tokens[i]); i += 1
            la = int(tokens[i]); i += 1
            sw = int(tokens[i]); i += 1
            ex, ey = float(tokens[i]), float(tokens[i+1]); i += 2
            arc_pts = svg_arc_to_points(cx, -cy, ex, -ey, rx, la, 1 - sw)
            points.extend(arc_pts[1:])
            cx, cy = ex, ey
        elif cmd == 'Z':
            pass
        else:
            try:
                cx, cy = float(cmd), float(tokens[i]); i += 1
                points.append((cx, -cy))
            except: pass
    return points

def svg_arc_to_points(x1, y1, x2, y2, r, large_arc, sweep, n=24):
    dx = (x1 - x2) / 2; dy = (y1 - y2) / 2
    d_sq = dx*dx + dy*dy; r_sq = r*r
    if r_sq < d_sq: r = math.sqrt(d_sq)*1.001; r_sq = r*r
    sq = max(0, (r_sq - d_sq) / d_sq); sq = math.sqrt(sq)
    if large_arc == sweep: sq = -sq
    ccx = sq*dy + (x1+x2)/2; ccy = -sq*dx + (y1+y2)/2
    a1 = math.atan2(y1-ccy, x1-ccx); a2 = math.atan2(y2-ccy, x2-ccx)
    if sweep == 0:
        if a2 > a1: a2 -= 2*math.pi
    else:
        if a2 < a1: a2 += 2*math.pi
    angles = np.linspace(a1, a2, n)
    return [(ccx+r*math.cos(a), ccy+r*math.sin(a)) for a in angles]

# === Profil-Aussenkontur laden (nur Sub-Path 0) ===

def load_profile_outer_only():
    svg_text = SVG_FILE.read_text(encoding='utf-8')
    d_matches = re.findall(r'd="([^"]+)"', svg_text)
    full_d = max(d_matches, key=len)
    sub_paths = re.split(r'(?=M )', full_d.strip())
    sub_paths = [s.strip() for s in sub_paths if s.strip() and len(s) > 10]

    # Only use sub-path 0 (outer contour)
    pts = parse_svg_path(sub_paths[0])
    if len(pts) >= 3:
        poly = make_valid(Polygon(pts))
        print(f"  Outer contour area: {poly.area:.1f}mm^2")
        return poly
    raise ValueError("Could not parse outer contour")

print("Loading profile outer contour from SVG...")
profil_outer = load_profile_outer_only()

# === Verbinder konstruieren ===

# Aeussere Huelle: 46x46 mit abgerundeten Ecken
kappe_aussen = box(-KAPPE_W/2, -KAPPE_W/2, KAPPE_W/2, KAPPE_W/2)
kappe_aussen = kappe_aussen.buffer(-7.5, join_style=1).buffer(7.5, join_style=1)
print(f"  Outer shell area: {kappe_aussen.area:.1f}mm^2")

# Verbinder-Querschnitt = Aussen minus Profil-Aussenkontur (als Durchbruch)
verbinder_quer = kappe_aussen.difference(profil_outer)
verbinder_quer = make_valid(verbinder_quer)
print(f"  Connector cross-section area: {verbinder_quer.area:.1f}mm^2")

# === SVG Export (Grundriss) ===

DC = '#333'
FS = 1.4
LW = 0.06

def _l(x1,y1,x2,y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{DC}" stroke-width="{LW}"/>\n'
def _al(x1,y1,x2,y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{DC}" stroke-width="{LW}" marker-start="url(#arr)" marker-end="url(#arr)"/>\n'
def _t(x,y,txt,anchor='middle',size=None):
    fs = size or FS
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{fs}" font-family="sans-serif" fill="{DC}" text-anchor="{anchor}">{txt}</text>\n'

def geom_to_svg(geom):
    """Shapely geometry to SVG path d-string."""
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    paths = []
    for poly in polys:
        coords = list(poly.exterior.coords)
        d = f'M {coords[0][0]:.3f},{-coords[0][1]:.3f}'
        for p in coords[1:]:
            d += f' L {p[0]:.3f},{-p[1]:.3f}'
        d += ' Z'
        for interior in poly.interiors:
            ic = list(interior.coords)
            d += f' M {ic[0][0]:.3f},{-ic[0][1]:.3f}'
            for p in ic[1:]:
                d += f' L {p[0]:.3f},{-p[1]:.3f}'
            d += ' Z'
        paths.append(d)
    return ' '.join(paths)

# Profil-SVG (original path for reference drawing)
svg_text = SVG_FILE.read_text(encoding='utf-8')
d_matches = re.findall(r'd="([^"]+)"', svg_text)
profil_svg_d = max(d_matches, key=len)

# Only outer contour sub-path for the through-hole display
sub_paths_raw = re.split(r'(?=M )', profil_svg_d.strip())
sub_paths_raw = [s.strip() for s in sub_paths_raw if s.strip() and len(s) > 10]
profil_outer_svg_d = sub_paths_raw[0]  # just the outer contour

# A4 frame
A4_W, A4_H = 297, 210
RAND_L, RAND_R, RAND_T, RAND_B = 20, 10, 10, 10
ZF_W = A4_W - RAND_L - RAND_R
ZF_H = A4_H - RAND_T - RAND_B
SF_W, SF_H = 180, 32
SF_X = A4_W - RAND_R - SF_W
SF_Y = A4_H - RAND_B - SF_H

VIEW_C_X = RAND_L + ZF_W * 0.5
VIEW_Y = RAND_T + (ZF_H - SF_H) / 2
SCALE = 2.0

# Dimensions
dim = ''
# Overall width 46 (top)
dim += _l(-23, -23-0.5, -23, -23-4)
dim += _l(23, -23-0.5, 23, -23-4)
dim += _al(-23, -23-3, 23, -23-3)
dim += _t(0, -23-3.6, '46')

# Wall thickness 3 (top left)
dim += _l(-20, -20-0.5, -20, -20-6)
dim += _al(-23, -20-5, -20, -20-5)
dim += _t(-21.5, -20-5.6, '3', size=1.1)

# Height annotation
dim += _t(28, 0, 'H=40', size=1.2)
dim += _t(28, 2, '(Durchbruch)', size=1.0)

# Centerlines
cl = ''
cl += f'<line x1="-28" y1="0" x2="28" y2="0" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n'
cl += f'<line x1="0" y1="-28" x2="0" y2="28" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n'

# Connector cross-section SVG
verbinder_d = geom_to_svg(verbinder_quer)

# View: Grundriss (top view) with hatched cross-section
view_c = f'''
  {cl}
  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="0.75" height="0.75"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="0.75" stroke="#66a" stroke-width="0.12"/>
    </pattern>
  </defs>
  <path d="{verbinder_d}" fill="url(#hatch)" stroke="blue" stroke-width="0.2" fill-rule="evenodd"/>
  <path d="{profil_outer_svg_d}" fill="none" stroke="red" stroke-width="0.15" stroke-dasharray="0.5,0.3"/>
  {dim}
'''

def mm_to_svg(content, cx, cy, scale):
    return f'<g transform="translate({cx:.1f},{cy:.1f}) scale({scale},{scale})">\n{content}</g>\n'

# Title block
schriftfeld = f'''
<rect x="{SF_X}" y="{SF_Y}" width="{SF_W}" height="{SF_H}" fill="white" stroke="black" stroke-width="0.35"/>
<line x1="{SF_X}" y1="{SF_Y+10}" x2="{SF_X+SF_W}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X}" y1="{SF_Y+20}" x2="{SF_X+SF_W}" y2="{SF_Y+20}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+50}" y1="{SF_Y}" x2="{SF_X+50}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+100}" y1="{SF_Y}" x2="{SF_X+100}" y2="{SF_Y+SF_H}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+140}" y1="{SF_Y}" x2="{SF_X+140}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<text x="{SF_X+2}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Erstellt</text>
<text x="{SF_X+52}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Geprueft</text>
<text x="{SF_X+102}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Werkstoff</text>
<text x="{SF_X+142}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Datum</text>
<text x="{SF_X+2}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Claude Code (KI)</text>
<text x="{SF_X+52}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Mensch</text>
<text x="{SF_X+102}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">TPU 95A</text>
<text x="{SF_X+142}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">2026-04-01</text>
<text x="{SF_X+2}" y="{SF_Y+13.5}" font-size="2.5" font-family="sans-serif" fill="#666">Benennung</text>
<text x="{SF_X+2}" y="{SF_Y+18}" font-size="4.5" font-family="sans-serif" fill="black" font-weight="bold">TPU-Verbinder 40x40</text>
<text x="{SF_X+102}" y="{SF_Y+13.5}" font-size="2.5" font-family="sans-serif" fill="#666">Massstab</text>
<text x="{SF_X+102}" y="{SF_Y+18}" font-size="3.5" font-family="sans-serif" fill="black" font-weight="bold">2:1</text>
<text x="{SF_X+2}" y="{SF_Y+23.5}" font-size="2.5" font-family="sans-serif" fill="#666">Zeichnungs-Nr.</text>
<text x="{SF_X+2}" y="{SF_Y+29}" font-size="5" font-family="sans-serif" fill="black" font-weight="bold">CAD-AI-005</text>
<text x="{SF_X+102}" y="{SF_Y+23.5}" font-size="2.5" font-family="sans-serif" fill="#666">passend zu</text>
<text x="{SF_X+102}" y="{SF_Y+29}" font-size="3.5" font-family="sans-serif" fill="black">Profil 40x40 (CAD-AI-001)</text>
'''

labels = f'''
<text x="{VIEW_C_X}" y="{VIEW_Y + 30*SCALE}" font-size="4" font-family="sans-serif" fill="{DC}" text-anchor="middle" font-style="italic">Grundriss / Draufsicht (M 2:1)</text>
<text x="{VIEW_C_X}" y="{VIEW_Y + 30*SCALE + 5}" font-size="3" font-family="sans-serif" fill="#666" text-anchor="middle">schraffiert = TPU-Material, rot gestrichelt = Profil-Aussenkontur (Durchbruch)</text>
'''

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  <defs>
    <marker id="arr" markerWidth="2.5" markerHeight="2" refX="1.25" refY="1"
            orient="auto" markerUnits="strokeWidth">
      <path d="M 0,0 L 2.5,1 L 0,2 Z" fill="{DC}"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="{A4_W}" height="{A4_H}" fill="white"/>
  <rect x="{RAND_L}" y="{RAND_T}" width="{ZF_W}" height="{ZF_H}" fill="none" stroke="black" stroke-width="0.5"/>
  {schriftfeld}
  {mm_to_svg(view_c, VIEW_C_X, VIEW_Y, SCALE)}
  {labels}
</svg>'''

svg_out = OUT / 'aufgabe05_verbinder_grundriss.svg'
svg_out.write_text(svg, encoding='utf-8')
print(f"\nOK: {svg_out}")

# === STL Export ===
import trimesh
from trimesh.creation import extrude_polygon

print("\nSTL Export...")

if isinstance(verbinder_quer, MultiPolygon):
    meshes = [extrude_polygon(p, height=HOEHE) for p in verbinder_quer.geoms if p.area > 0.5]
    verbinder_mesh = trimesh.util.concatenate(meshes)
else:
    verbinder_mesh = extrude_polygon(verbinder_quer, height=HOEHE)

stl_path = OUT / 'aufgabe05_verbinder_40mm.stl'
verbinder_mesh.export(str(stl_path))
print(f"OK: {stl_path}")
print(f"  File size: {stl_path.stat().st_size / 1024:.0f} KB")
print(f"  Mesh bounds: {verbinder_mesh.bounds}")
print(f"  Volume: {verbinder_mesh.volume:.1f}mm^3")
