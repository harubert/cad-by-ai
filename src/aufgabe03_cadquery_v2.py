"""
CadQuery Schraegriss - Versuch 2b.
Laedt das Profil aus aufgabe01_path.svg, extrudiert in CadQuery, HLR-Projektion.
"""

import math
import re
import numpy as np
from pathlib import Path

import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt, gp_Vec, gp_Circ, gp_Ax2, gp_Dir
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds

OUT = Path(__file__).resolve().parent.parent / 'output'
SVG_FILE = OUT / 'aufgabe01_path.svg'

# ================================================================
# 1) SVG-Pfad parsen (gleicher Parser wie aufgabe01_stl.py)
# ================================================================

def parse_svg_path(d_string):
    tokens = re.findall(r'[MLAZmlaz]|[-+]?\d*\.?\d+', d_string)
    points = []
    arcs = []  # (start_idx, cx, cy, r, start_angle, end_angle)
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
            # Arc zu Punktliste (mit Y-Inversion)
            arc_pts = svg_arc_to_points(cx, -cy, ex, -ey, rx, la, 1 - sw)
            points.extend(arc_pts[1:])
            cx, cy = ex, ey
        elif cmd == 'Z':
            pass
    return points

def svg_arc_to_points(x1, y1, x2, y2, r, large_arc, sweep, n=6):
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

# Lade SVG
print("SVG laden...")
svg_text = SVG_FILE.read_text(encoding='utf-8')
d_matches = re.findall(r'd="([^"]+)"', svg_text)
full_d = max(d_matches, key=len)
sub_paths = re.split(r'(?=M )', full_d.strip())
sub_paths = [s.strip() for s in sub_paths if s.strip() and len(s) > 10]

print(f"  {len(sub_paths)} Sub-Pfade gefunden")

# Parse alle Sub-Pfade, vereinfache Kreise
all_contours = []
for i, sp in enumerate(sub_paths):
    pts = parse_svg_path(sp)
    if len(pts) >= 3:
        # Vereinfache: wenn > 100 Punkte und fast kreisfoermig, reduziere
        if len(pts) > 50:
            # Jeden n-ten Punkt nehmen
            step = max(1, len(pts) // 20)
            pts = pts[::step]
        all_contours.append(pts)
        print(f"  Sub-Pfad {i}: {len(pts)} Punkte")

# ================================================================
# 2) CadQuery Wire aus Punktlisten bauen
# ================================================================
print("\nCadQuery Solid aufbauen...")

def points_to_wire(pts):
    """Konvertiert eine Punktliste zu einem CadQuery Wire."""
    builder = BRepBuilderAPI_MakeWire()
    for i in range(len(pts) - 1):
        p1 = gp_Pnt(pts[i][0], pts[i][1], 0)
        p2 = gp_Pnt(pts[i+1][0], pts[i+1][1], 0)
        if p1.Distance(p2) > 0.001:
            edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
            builder.Add(edge)
    # Schliessen
    p1 = gp_Pnt(pts[-1][0], pts[-1][1], 0)
    p2 = gp_Pnt(pts[0][0], pts[0][1], 0)
    if p1.Distance(p2) > 0.001:
        edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
        builder.Add(edge)
    return builder.Wire()

# Aeussere Kontur = Sub-Pfad 0
outer_wire = points_to_wire(all_contours[0])
outer_face = BRepBuilderAPI_MakeFace(outer_wire).Face()

# Loecher (Bohrung + Pockets) abziehen
for contour in all_contours[1:]:
    hole_wire = points_to_wire(contour)
    outer_face = BRepAlgoAPI_Cut(outer_face, BRepBuilderAPI_MakeFace(hole_wire).Face()).Shape()

# Extrudieren auf 100mm
prism_vec = gp_Vec(0, 0, 100)
solid = BRepPrimAPI_MakePrism(outer_face, prism_vec).Shape()

print("  Solid erstellt!")

# ================================================================
# 3) HLR Projektion
# ================================================================
print("HLR Projektion...")

BRepMesh_IncrementalMesh(solid, 0.3, True)

# Blickrichtung: Schraegriss 30° von rechts-oben-vorn
angle = math.radians(30)
view_dir = gp_Dir(-math.cos(angle) * 0.5, math.sin(angle) * 0.5, -1)
up_dir = gp_Dir(0, 0, 1)

ax = gp_Ax2(gp_Pnt(0, 0, 0), view_dir, up_dir)
projector = HLRAlgo_Projector(ax)

hlr = HLRBRep_Algo()
hlr.Add(solid)
hlr.Projector(projector)
hlr.Update()
hlr.Hide()

hlr_shapes = HLRBRep_HLRToShape(hlr)

# Kanten extrahieren
def edges_to_paths(compound):
    paths = []
    explorer = TopExp_Explorer(compound, TopAbs_EDGE)
    while explorer.More():
        edge = TopoDS.Edge_s(explorer.Current())
        try:
            adaptor = BRepAdaptor_Curve(edge)
            first = adaptor.FirstParameter()
            last = adaptor.LastParameter()
            # Nur Start- und Endpunkt (gerade Linien brauchen nicht mehr)
            p1 = adaptor.Value(first)
            p2 = adaptor.Value(last)
            d = f"M {p1.X():.2f},{-p1.Y():.2f} L {p2.X():.2f},{-p2.Y():.2f}"
            paths.append(d)
        except:
            pass
        explorer.Next()
    return paths

vis_paths = []
hid_paths = []
for method in ['VCompound', 'OutLineVCompound', 'Rg1LineVCompound']:
    try:
        comp = getattr(hlr_shapes, method)()
        if comp and not comp.IsNull():
            vis_paths.extend(edges_to_paths(comp))
    except: pass

for method in ['HCompound', 'OutLineHCompound', 'Rg1LineHCompound']:
    try:
        comp = getattr(hlr_shapes, method)()
        if comp and not comp.IsNull():
            hid_paths.extend(edges_to_paths(comp))
    except: pass

print(f"  Sichtbar: {len(vis_paths)}, Verdeckt: {len(hid_paths)}")

# ================================================================
# 4) SVG erzeugen (zentriert auf A4)
# ================================================================
print("SVG erzeugen...")

# BBox
all_nums = []
for d in vis_paths + hid_paths:
    nums = re.findall(r'[-+]?\d*\.?\d+', d)
    for j in range(0, len(nums) - 1, 2):
        all_nums.append((float(nums[j]), float(nums[j+1])))

if all_nums:
    min_x = min(p[0] for p in all_nums)
    max_x = max(p[0] for p in all_nums)
    min_y = min(p[1] for p in all_nums)
    max_y = max(p[1] for p in all_nums)
else:
    min_x, max_x, min_y, max_y = -50, 50, -60, 60

w = max_x - min_x
h = max_y - min_y

A4_W, A4_H = 297, 210
margin_x, margin_y = 30, 25
scale = min((A4_W - 2*margin_x) / w, (A4_H - 2*margin_y) / h) if w > 0 and h > 0 else 1
cx_offset = A4_W/2 - (min_x + w/2) * scale
cy_offset = A4_H/2 - (min_y + h/2) * scale

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">')
lines.append(f'<rect x="0" y="0" width="{A4_W}" height="{A4_H}" fill="white"/>')
lines.append(f'<rect x="20" y="10" width="{A4_W-30}" height="{A4_H-20}" fill="none" stroke="black" stroke-width="0.5"/>')

lw_vis = 0.4 / scale
lw_hid = 0.2 / scale
dash = f"{1.5/scale:.2f},{0.8/scale:.2f}"

lines.append(f'<g transform="translate({cx_offset:.1f},{cy_offset:.1f}) scale({scale:.4f},{scale:.4f})">')

for d in vis_paths:
    lines.append(f'  <path d="{d}" fill="none" stroke="black" stroke-width="{lw_vis:.3f}"/>')

for d in hid_paths:
    lines.append(f'  <path d="{d}" fill="none" stroke="black" stroke-width="{lw_hid:.3f}" stroke-dasharray="{dash}"/>')

lines.append('</g>')

# Schriftfeld
SF_X = A4_W - 10 - 130
SF_Y = A4_H - 10 - 12
lines.append(f'<rect x="{SF_X}" y="{SF_Y}" width="130" height="12" fill="white" stroke="black" stroke-width="0.3"/>')
lines.append(f'<text x="{SF_X+65}" y="{SF_Y+5}" font-size="3.5" font-family="sans-serif" text-anchor="middle" font-weight="bold">Alu-Profil 40 x 40 &mdash; Schrägriss (CadQuery HLR)</text>')
lines.append(f'<text x="{SF_X+65}" y="{SF_Y+9}" font-size="2.5" font-family="sans-serif" text-anchor="middle" fill="#555">Kavalierprojektion 30° | Verkürzung 0.5 | CAD-AI-003</text>')

lines.append('</svg>')

svg_path = OUT / 'aufgabe03_schraegriss_cadquery_v2.svg'
svg_path.write_text('\n'.join(lines), encoding='utf-8')
print(f"\nOK: {svg_path}")
