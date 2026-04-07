#!/usr/bin/env python3
"""
GZ-Aufgaben mit CadQuery + HLR (Hidden Line Removal).

Erzeugt SVG-Projektionszeichnungen fuer 10 GZ-Standardaufgaben
mithilfe echter 3D-Koerper und OCC Hidden Line Removal.
"""

import math
import traceback
from pathlib import Path

import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line

# ── Paths ─────────────────────────────────────────────────────────
BASE = Path(r"e:\2026_GoogleDrive\00 Arbeit\01 PH\Veranstaltungen"
            r"\2026_04_09 Graz KI im Geometrieunterricht\CAD_by_AI")
OUT = BASE / "output" / "gz_cadquery"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "run_log.txt"

log_file = open(LOG, "w", encoding="utf-8")

def log(msg):
    log_file.write(msg + "\n")
    log_file.flush()

# ── HLR helpers ───────────────────────────────────────────────────

def hlr_project(shape, direction, xdir=None):
    """Run HLR on shape with given view direction.
    Returns (visible_edges, hidden_edges) as lists of point-lists.
    Each edge is a list of (x, y) tuples. Lines have 2 points,
    curves have ~40 sampled points.
    direction: gp_Dir - view direction (normal to projection plane)
    xdir: gp_Dir - what maps to the projected X axis
    """
    BRepMesh_IncrementalMesh(shape, 0.5).Perform()

    hlr = HLRBRep_Algo()
    hlr.Add(shape)

    if xdir is not None:
        ax = gp_Ax2(gp_Pnt(0, 0, 0), direction, xdir)
    else:
        ax = gp_Ax2(gp_Pnt(0, 0, 0), direction)
    hlr.Projector(HLRAlgo_Projector(ax))
    hlr.Update()
    hlr.Hide()

    hs = HLRBRep_HLRToShape(hlr)

    def extract(shape_compound):
        edges = []
        if shape_compound is None or shape_compound.IsNull():
            return edges
        exp = TopExp_Explorer(shape_compound, TopAbs_EDGE)
        while exp.More():
            edge = TopoDS.Edge_s(exp.Current())
            curve = BRepAdaptor_Curve(edge)
            u0 = curve.FirstParameter()
            u1 = curve.LastParameter()
            ctype = curve.GetType()

            if ctype == GeomAbs_Line:
                p0 = curve.Value(u0)
                p1 = curve.Value(u1)
                edges.append([(p0.X(), p0.Y()), (p1.X(), p1.Y())])
            else:
                # Sample curve
                n = 40
                pts = []
                for i in range(n + 1):
                    u = u0 + (u1 - u0) * i / n
                    p = curve.Value(u)
                    pts.append((p.X(), p.Y()))
                edges.append(pts)
            exp.Next()
        return edges

    vis = extract(hs.VCompound()) + extract(hs.OutLineVCompound()) + extract(hs.Rg1LineVCompound())
    hid = extract(hs.HCompound()) + extract(hs.OutLineHCompound()) + extract(hs.Rg1LineHCompound())
    return vis, hid


def edges_bbox(all_edge_lists):
    """Compute bounding box of edge lists."""
    xs, ys = [], []
    for edges in all_edge_lists:
        for edge in edges:
            for x, y in edge:
                xs.append(x)
                ys.append(y)
    if not xs:
        return 0, 0, 1, 1
    return min(xs), min(ys), max(xs), max(ys)


# ── SVG generation ────────────────────────────────────────────────

def edges_to_svg_group(vis_edges, hid_edges, ox=0, oy=0, scale=1.0, flip_y=True):
    """Convert edge lists to SVG path elements, offset by (ox, oy).
    flip_y: negate Y coords (HLR Y increases up, SVG Y increases down).
    """
    lines = []

    def edge_to_path(edge, cls):
        pts = []
        for x, y in edge:
            sx = ox + x * scale
            sy = oy + (-y if flip_y else y) * scale
            pts.append((sx, sy))
        if len(pts) < 2:
            return ""
        d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
        for p in pts[1:]:
            d += f" L{p[0]:.2f},{p[1]:.2f}"
        return f'  <path d="{d}" class="{cls}"/>\n'

    for e in vis_edges:
        lines.append(edge_to_path(e, "visible"))
    for e in hid_edges:
        lines.append(edge_to_path(e, "hidden"))
    return "".join(lines)


def make_svg(content, title, nr, w=297, h=210):
    """Wrap content in A4 landscape SVG."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{w}mm" height="{h}mm"
     viewBox="0 0 {w} {h}">
  <defs>
    <style>
      .visible {{ stroke: black; stroke-width: 0.3; fill: none; stroke-linecap: round; }}
      .hidden  {{ stroke: black; stroke-width: 0.15; fill: none;
                  stroke-dasharray: 2,1; stroke-linecap: round; }}
      .axis    {{ stroke: red; stroke-width: 0.15; fill: none; }}
      .section {{ fill: #dde; stroke: black; stroke-width: 0.3; }}
      text {{ font-family: Arial, sans-serif; }}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="white"/>
  <rect x="20" y="10" width="{w-30}" height="{h-20}"
        stroke="black" stroke-width="0.5" fill="none"/>
  <rect x="{w-100}" y="{h-25}" width="90" height="15"
        stroke="black" stroke-width="0.35" fill="white"/>
  <text x="{w-97}" y="{h-18}" font-size="3.5" fill="black">Aufgabe {nr}: {title}</text>
  <text x="{w-97}" y="{h-13}" font-size="2.5" fill="black">GZ Sek I | CadQuery + HLR</text>
{content}</svg>
"""


def draw_axes(cx, cy, length=15):
    """Draw red coordinate axes at (cx, cy)."""
    return (
        f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+length:.1f}" y2="{cy:.1f}" class="axis" marker-end="none"/>\n'
        f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy-length:.1f}" class="axis"/>\n'
        f'  <text x="{cx+length+1:.1f}" y="{cy+1:.1f}" font-size="2.5" fill="red">x</text>\n'
        f'  <text x="{cx+1:.1f}" y="{cy-length-1:.1f}" font-size="2.5" fill="red">z</text>\n'
    )


def write_svg(name, svg_text):
    path = OUT / name
    path.write_text(svg_text, encoding="utf-8")
    log(f"  -> {path.name}")


# ── Task results collector ────────────────────────────────────────
results = []  # list of (nr, title, svg_name_or_None, error_or_None)


# ══════════════════════════════════════════════════════════════════
# TASK 1: Dreitafelprojektion Quader 80x50x30
# ══════════════════════════════════════════════════════════════════
def task01():
    log("Task 1: Dreitafelprojektion Quader 80x50x30")
    box = cq.Workplane("XY").box(80, 50, 30).val().wrapped

    # Front view (Aufriss): looking along -Y, X->proj_X, Z->proj_Y
    v_front, h_front = hlr_project(box, gp_Dir(0, -1, 0), xdir=gp_Dir(1, 0, 0))
    # Top view (Grundriss): looking along -Z, X->proj_X, -Y->proj_Y
    v_top, h_top = hlr_project(box, gp_Dir(0, 0, -1), xdir=gp_Dir(1, 0, 0))
    # Side view (Kreuzriss): looking along +X, -Y->proj_X, Z->proj_Y
    v_side, h_side = hlr_project(box, gp_Dir(1, 0, 0), xdir=gp_Dir(0, -1, 0))

    s = 0.8  # scale
    # Layout: Aufriss top-left, Grundriss bottom-left, Kreuzriss top-right
    # Aufriss center at (100, 65)
    au_cx, au_cy = 100, 65
    # Grundriss below: center at (100, 145)
    gr_cx, gr_cy = 100, 145
    # Kreuzriss right: center at (200, 65)
    kr_cx, kr_cy = 200, 65

    content = ""
    # Labels
    content += f'  <text x="{au_cx}" y="30" font-size="3.5" text-anchor="middle" fill="black">Aufriss (Vorderansicht)</text>\n'
    content += f'  <text x="{gr_cx}" y="115" font-size="3.5" text-anchor="middle" fill="black">Grundriss (Draufsicht)</text>\n'
    content += f'  <text x="{kr_cx}" y="30" font-size="3.5" text-anchor="middle" fill="black">Kreuzriss (Seitenansicht)</text>\n'

    content += edges_to_svg_group(v_front, h_front, au_cx, au_cy, s)
    content += edges_to_svg_group(v_top, h_top, gr_cx, gr_cy, s)
    content += edges_to_svg_group(v_side, h_side, kr_cx, kr_cy, s)

    # Axes
    content += draw_axes(35, 100)
    # Fold lines (Risslinien) as thin gray
    content += f'  <line x1="30" y1="108" x2="260" y2="108" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'
    content += f'  <line x1="155" y1="20" x2="155" y2="200" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'

    svg = make_svg(content, "Dreitafelprojektion Quader 80x50x30", 1)
    write_svg("aufgabe_01_dreitafelprojektion.svg", svg)
    return "aufgabe_01_dreitafelprojektion.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 2: Schraegriss Quader
# ══════════════════════════════════════════════════════════════════
def task02():
    log("Task 2: Schraegriss Quader 80x50x30")
    box = cq.Workplane("XY").box(80, 50, 30).val().wrapped

    # Oblique view: cavalier projection from front-right-above
    # Direction: combination that gives typical "Schraegriss" look
    a = math.radians(30)
    direction = gp_Dir(math.sin(a), -math.cos(a), 0.3)
    vis, hid = hlr_project(box, direction)

    s = 1.0
    cx, cy = 148, 105
    content = edges_to_svg_group(vis, hid, cx, cy, s)
    content += draw_axes(40, 180)

    svg = make_svg(content, "Schraegriss Quader 80x50x30", 2)
    write_svg("aufgabe_02_schraegriss_quader.svg", svg)
    return "aufgabe_02_schraegriss_quader.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 3: Normalriss Pyramide 60x60 h=80
# ══════════════════════════════════════════════════════════════════
def task03():
    log("Task 3: Normalriss Pyramide 60x60 h=80")
    # Build pyramid: base 60x60 at Z=0, apex at (0,0,80)
    base_half = 30
    apex_h = 80
    # Use CadQuery loft from square base to point
    base_pts = [(-base_half, -base_half), (base_half, -base_half),
                (base_half, base_half), (-base_half, base_half)]
    # Create base wire
    base = (cq.Workplane("XY")
            .moveTo(*base_pts[0])
            .lineTo(*base_pts[1])
            .lineTo(*base_pts[2])
            .lineTo(*base_pts[3])
            .close()
            .wire())
    # Create apex as tiny square for loft
    tiny = 0.01
    apex = (cq.Workplane("XY").workplane(offset=apex_h)
            .moveTo(-tiny, -tiny)
            .lineTo(tiny, -tiny)
            .lineTo(tiny, tiny)
            .lineTo(-tiny, tiny)
            .close()
            .wire())
    pyramid = cq.Solid.makeLoft([base.val(), apex.val()])
    shape = pyramid.wrapped

    # Three views
    v_front, h_front = hlr_project(shape, gp_Dir(0, -1, 0), xdir=gp_Dir(1, 0, 0))
    v_top, h_top = hlr_project(shape, gp_Dir(0, 0, -1), xdir=gp_Dir(1, 0, 0))
    v_side, h_side = hlr_project(shape, gp_Dir(1, 0, 0), xdir=gp_Dir(0, -1, 0))

    s = 0.65
    au_cx, au_cy = 90, 85
    gr_cx, gr_cy = 90, 160
    kr_cx, kr_cy = 200, 85

    content = ""
    content += f'  <text x="{au_cx}" y="25" font-size="3.5" text-anchor="middle" fill="black">Aufriss</text>\n'
    content += f'  <text x="{gr_cx}" y="125" font-size="3.5" text-anchor="middle" fill="black">Grundriss</text>\n'
    content += f'  <text x="{kr_cx}" y="25" font-size="3.5" text-anchor="middle" fill="black">Kreuzriss</text>\n'

    content += edges_to_svg_group(v_front, h_front, au_cx, au_cy, s)
    content += edges_to_svg_group(v_top, h_top, gr_cx, gr_cy, s)
    content += edges_to_svg_group(v_side, h_side, kr_cx, kr_cy, s)

    content += f'  <line x1="30" y1="118" x2="260" y2="118" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'
    content += f'  <line x1="148" y1="20" x2="148" y2="200" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'
    content += draw_axes(35, 110)

    svg = make_svg(content, "Normalriss Pyramide 60x60 h=80", 3)
    write_svg("aufgabe_03_normalriss_pyramide.svg", svg)
    return "aufgabe_03_normalriss_pyramide.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 4: Abwicklung Wuerfel 40mm (2D only - CadQuery skip)
# ══════════════════════════════════════════════════════════════════
def task04():
    log("Task 4: Abwicklung Wuerfel 40mm (2D - Shapely-Aufgabe)")
    # CadQuery is 3D; net unfolding is purely 2D geometry.
    # Generate a simple SVG cross-net manually.
    s = 40  # side length in mm
    content = ""
    # Cross-shaped net: 4 squares in a column, 1 left, 1 right of the 2nd
    positions = [
        (1, 0), (1, 1), (1, 2), (1, 3),  # vertical column
        (0, 1), (2, 1)  # left and right
    ]
    labels = ["Oben", "Vorne", "Unten", "Hinten", "Links", "Rechts"]
    ox, oy = 100, 25
    for i, (col, row) in enumerate(positions):
        x = ox + col * s
        y = oy + row * s
        content += f'  <rect x="{x}" y="{y}" width="{s}" height="{s}" class="visible"/>\n'
        content += f'  <text x="{x + s/2}" y="{y + s/2 + 1.5}" font-size="3" text-anchor="middle" fill="#666">{labels[i]}</text>\n'

    content += f'  <text x="148" y="195" font-size="3" text-anchor="middle" fill="black">Abwicklung Wuerfel a = {s} mm (2D, kein HLR noetig)</text>\n'

    svg = make_svg(content, "Abwicklung Wuerfel 40mm", 4)
    write_svg("aufgabe_04_abwicklung_wuerfel.svg", svg)
    return "aufgabe_04_abwicklung_wuerfel.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 5: Abwicklung Zylinder (2D only)
# ══════════════════════════════════════════════════════════════════
def task05():
    log("Task 5: Abwicklung Zylinder (2D)")
    r = 20
    h_cyl = 60
    circumf = 2 * math.pi * r  # ~125.66

    content = ""
    # Rectangle = mantle
    ox, oy = 50, 40
    scale = 0.9
    rw = circumf * scale
    rh = h_cyl * scale
    content += f'  <rect x="{ox}" y="{oy}" width="{rw:.1f}" height="{rh:.1f}" class="visible"/>\n'
    content += f'  <text x="{ox + rw/2}" y="{oy - 3}" font-size="3" text-anchor="middle">Mantelflaeche {circumf:.1f} x {h_cyl} mm</text>\n'

    # Two circles (top and bottom)
    ccx1 = ox + rw + 30 + r * scale
    ccy1 = oy + rh / 2 - r * scale - 5
    ccy2 = oy + rh / 2 + r * scale + 5
    content += f'  <circle cx="{ccx1:.1f}" cy="{ccy1:.1f}" r="{r*scale:.1f}" class="visible"/>\n'
    content += f'  <circle cx="{ccx1:.1f}" cy="{ccy2:.1f}" r="{r*scale:.1f}" class="visible"/>\n'
    content += f'  <text x="{ccx1:.1f}" y="{ccy1 - r*scale - 3:.1f}" font-size="2.5" text-anchor="middle">Deckel</text>\n'
    content += f'  <text x="{ccx1:.1f}" y="{ccy2 + r*scale + 5:.1f}" font-size="2.5" text-anchor="middle">Boden</text>\n'

    content += f'  <text x="148" y="185" font-size="3" text-anchor="middle" fill="black">Abwicklung Zylinder r={r}, h={h_cyl} (2D, kein HLR)</text>\n'

    svg = make_svg(content, f"Abwicklung Zylinder r={r} h={h_cyl}", 5)
    write_svg("aufgabe_05_abwicklung_zylinder.svg", svg)
    return "aufgabe_05_abwicklung_zylinder.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 6: Parallelprojektion Prisma (dreieckiges Prisma)
# ══════════════════════════════════════════════════════════════════
def task06():
    log("Task 6: Parallelprojektion Prisma")
    # Triangular prism: equilateral triangle base, side=50, height=70
    s = 50
    h_prism = 70
    h_tri = s * math.sqrt(3) / 2

    prism = (cq.Workplane("XY")
             .moveTo(-s/2, -h_tri/3)
             .lineTo(s/2, -h_tri/3)
             .lineTo(0, 2*h_tri/3)
             .close()
             .extrude(h_prism))
    shape = prism.val().wrapped

    # Oblique view
    a = math.radians(30)
    direction = gp_Dir(math.sin(a), -math.cos(a), 0.3)
    vis, hid = hlr_project(shape, direction)

    cx, cy = 148, 105
    content = edges_to_svg_group(vis, hid, cx, cy, 0.9)
    content += draw_axes(40, 180)

    svg = make_svg(content, "Parallelprojektion Dreiecksprisma", 6)
    write_svg("aufgabe_06_parallelprojektion_prisma.svg", svg)
    return "aufgabe_06_parallelprojektion_prisma.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 7: Durchdringung Quader-Quader
# ══════════════════════════════════════════════════════════════════
def task07():
    log("Task 7: Durchdringung Quader-Quader")
    # Two crossing boxes
    box1 = cq.Workplane("XY").box(40, 40, 60)  # vertical
    box2 = cq.Workplane("XZ").box(30, 30, 80)  # horizontal through

    # Union for combined shape
    combined = box1.union(box2)
    shape = combined.val().wrapped

    # Three views
    v_front, h_front = hlr_project(shape, gp_Dir(0, -1, 0), xdir=gp_Dir(1, 0, 0))
    v_top, h_top = hlr_project(shape, gp_Dir(0, 0, -1), xdir=gp_Dir(1, 0, 0))
    v_side, h_side = hlr_project(shape, gp_Dir(1, 0, 0), xdir=gp_Dir(0, -1, 0))

    s = 0.7
    au_cx, au_cy = 90, 75
    gr_cx, gr_cy = 90, 155
    kr_cx, kr_cy = 210, 75

    content = ""
    content += f'  <text x="{au_cx}" y="25" font-size="3.5" text-anchor="middle">Aufriss</text>\n'
    content += f'  <text x="{gr_cx}" y="120" font-size="3.5" text-anchor="middle">Grundriss</text>\n'
    content += f'  <text x="{kr_cx}" y="25" font-size="3.5" text-anchor="middle">Kreuzriss</text>\n'

    content += edges_to_svg_group(v_front, h_front, au_cx, au_cy, s)
    content += edges_to_svg_group(v_top, h_top, gr_cx, gr_cy, s)
    content += edges_to_svg_group(v_side, h_side, kr_cx, kr_cy, s)

    content += f'  <line x1="30" y1="113" x2="260" y2="113" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'
    content += f'  <line x1="155" y1="20" x2="155" y2="200" stroke="#ccc" stroke-width="0.15" stroke-dasharray="4,2"/>\n'
    content += draw_axes(35, 105)

    svg = make_svg(content, "Durchdringung Quader-Quader", 7)
    write_svg("aufgabe_07_durchdringung.svg", svg)
    return "aufgabe_07_durchdringung.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 8: Ebenenschnitt Wuerfel
# ══════════════════════════════════════════════════════════════════
def task08():
    log("Task 8: Ebenenschnitt Wuerfel 40mm")
    a = 40
    cube = cq.Workplane("XY").box(a, a, a)

    # Cut with diagonal plane: from edge (x=-20,z=20) to (x=20,z=-20)
    # i.e. the plane x - z = 0
    # Use a large cutting box rotated 45 degrees
    cut_tool = (cq.Workplane("XZ")
                .transformed(rotate=(0, 45, 0))
                .rect(200, 200)
                .extrude(100))
    cut_result = cube.cut(cut_tool)
    shape = cut_result.val().wrapped

    # Also compute the section = intersection
    section = cube.intersect(cut_tool)
    section_shape = section.val().wrapped

    # Oblique view of cut cube
    a_angle = math.radians(30)
    direction = gp_Dir(math.sin(a_angle), -math.cos(a_angle), 0.35)
    vis, hid = hlr_project(shape, direction)

    cx, cy = 120, 100
    content = edges_to_svg_group(vis, hid, cx, cy, 1.0)

    # Also show section shape slightly offset
    vis_s, hid_s = hlr_project(section_shape, direction)
    # Draw section with fill
    for e in vis_s:
        pts = [(cx + x, cy - y) for x, y in e]
        if len(pts) >= 2:
            d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
            for p in pts[1:]:
                d += f" L{p[0]:.2f},{p[1]:.2f}"
            content += f'  <path d="{d}" stroke="blue" stroke-width="0.4" fill="none"/>\n'

    content += draw_axes(40, 180)
    content += f'  <text x="148" y="190" font-size="3" text-anchor="middle" fill="blue">Blau = Schnittflaeche</text>\n'

    svg = make_svg(content, "Ebenenschnitt Wuerfel 40mm", 8)
    write_svg("aufgabe_08_ebenenschnitt.svg", svg)
    return "aufgabe_08_ebenenschnitt.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 9: Kreis im Schraegriss (Zylinder → Ellipse)
# ══════════════════════════════════════════════════════════════════
def task09():
    log("Task 9: Kreis im Schraegriss")
    cyl = cq.Workplane("XY").circle(25).extrude(50)
    shape = cyl.val().wrapped

    # Oblique view that turns circles into ellipses
    a = math.radians(30)
    direction = gp_Dir(math.sin(a), -math.cos(a), 0.4)
    vis, hid = hlr_project(shape, direction)

    cx, cy = 148, 105
    content = edges_to_svg_group(vis, hid, cx, cy, 1.0)
    content += draw_axes(40, 180)

    svg = make_svg(content, "Kreis im Schraegriss (Zylinder)", 9)
    write_svg("aufgabe_09_kreis_schraegriss.svg", svg)
    return "aufgabe_09_kreis_schraegriss.svg"


# ══════════════════════════════════════════════════════════════════
# TASK 10: Zusammengesetzter Koerper (Box + Pyramide)
# ══════════════════════════════════════════════════════════════════
def task10():
    log("Task 10: Zusammengesetzter Koerper")
    # Box 60x60x40
    box = cq.Workplane("XY").box(60, 60, 40)

    # Pyramid on top: base 60x60 at z=20 (top of box), apex at z=20+50=70
    base_half = 30
    apex_z = 70  # box top = 20, pyramid height = 50
    box_top_z = 20
    tiny = 0.01
    base_wire = (cq.Workplane("XY").workplane(offset=box_top_z)
                 .moveTo(-base_half, -base_half)
                 .lineTo(base_half, -base_half)
                 .lineTo(base_half, base_half)
                 .lineTo(-base_half, base_half)
                 .close()
                 .wire())
    apex_wire = (cq.Workplane("XY").workplane(offset=apex_z)
                 .moveTo(-tiny, -tiny)
                 .lineTo(tiny, -tiny)
                 .lineTo(tiny, tiny)
                 .lineTo(-tiny, tiny)
                 .close()
                 .wire())
    pyramid = cq.Solid.makeLoft([base_wire.val(), apex_wire.val()])

    combined = box.union(cq.Workplane("XY").add(pyramid))
    shape = combined.val().wrapped

    # Oblique view
    a = math.radians(30)
    direction = gp_Dir(math.sin(a), -math.cos(a), 0.35)
    vis, hid = hlr_project(shape, direction)

    cx, cy = 148, 115
    content = edges_to_svg_group(vis, hid, cx, cy, 0.85)
    content += draw_axes(40, 185)

    svg = make_svg(content, "Zusammengesetzter Koerper (Quader + Pyramide)", 10)
    write_svg("aufgabe_10_zusammengesetzter_koerper.svg", svg)
    return "aufgabe_10_zusammengesetzter_koerper.svg"


# ── Run all tasks ─────────────────────────────────────────────────
tasks = [
    (1, "Dreitafelprojektion Quader 80x50x30", task01),
    (2, "Schraegriss Quader 80x50x30", task02),
    (3, "Normalriss Pyramide 60x60 h=80", task03),
    (4, "Abwicklung Wuerfel 40mm", task04),
    (5, "Abwicklung Zylinder", task05),
    (6, "Parallelprojektion Prisma", task06),
    (7, "Durchdringung Quader-Quader", task07),
    (8, "Ebenenschnitt Wuerfel 40mm", task08),
    (9, "Kreis im Schraegriss", task09),
    (10, "Zusammengesetzter Koerper", task10),
]

log("=" * 60)
log("GZ CadQuery HLR - Starting all tasks")
log("=" * 60)

for nr, title, func in tasks:
    try:
        svg_name = func()
        results.append((nr, title, svg_name, None))
        log(f"  OK: {svg_name}")
    except Exception as e:
        tb = traceback.format_exc()
        log(f"  FAIL: {e}\n{tb}")
        results.append((nr, title, None, str(e)))

log("\n" + "=" * 60)
log("Generating comparison HTML")
log("=" * 60)

# ── Comparison HTML ───────────────────────────────────────────────
GZ_ORIG = BASE / "output" / "gz"
orig_names = [
    "aufgabe_01_dreitafelprojektion.svg",
    "aufgabe_02_schraegriss_quader.svg",
    "aufgabe_03_normalriss_pyramide.svg",
    "aufgabe_04_abwicklung_wuerfel.svg",
    "aufgabe_05_abwicklung_zylinder.svg",
    "aufgabe_06_parallelprojektion_prisma.svg",
    "aufgabe_07_durchdringung.svg",
    "aufgabe_08_ebenenschnitt.svg",
    "aufgabe_09_kreis_schraegriss.svg",
    "aufgabe_10_zusammengesetzter_koerper.svg",
]

ratings = [
    "CadQuery liefert exakte Kantenprojektion via HLR; Shapely-Version ist handkodiert.",
    "HLR berechnet sichtbare/verdeckte Kanten automatisch; Shapely muss dies manuell loesen.",
    "Pyramide als Loft: HLR liefert korrekte Dreiecksprojektion; Shapely berechnet manuell.",
    "Beide 2D: CadQuery hat hier keinen Vorteil (reine Abwicklung).",
    "Beide 2D: CadQuery hat hier keinen Vorteil (reine Abwicklung).",
    "HLR berechnet verdeckte Kanten des Prismas automatisch korrekt.",
    "CadQuery-Boolean + HLR zeigt exakte Durchdringungskurve; Shapely approximiert.",
    "CadQuery-Cut + HLR zeigt exakten Schnitt; Shapely berechnet manuell.",
    "HLR projiziert Kreis automatisch als Ellipse (BSpline); Shapely approximiert.",
    "CadQuery-Union + HLR: automatische Sichtbarkeitsberechnung.",
]

html_rows = ""
for i, (nr, title, svg_name, error) in enumerate(results):
    orig_svg = f"../gz/{orig_names[i]}"
    orig_exists = (GZ_ORIG / orig_names[i]).exists()

    if svg_name:
        cq_img = f'<img src="{svg_name}" alt="CadQuery {nr}" style="max-width:100%;cursor:pointer" onclick="openLB(this.src)"/>'
    else:
        cq_img = f'<div style="color:red;padding:20px">FEHLER: {error}</div>'

    if orig_exists:
        orig_img = f'<img src="{orig_svg}" alt="Shapely {nr}" style="max-width:100%;cursor:pointer" onclick="openLB(this.src)"/>'
    else:
        orig_img = '<div style="color:#888;padding:20px">Shapely-SVG nicht vorhanden</div>'

    rating = ratings[i] if i < len(ratings) else ""
    if error:
        rating = f'<span style="color:red">Fehler bei CadQuery: {error}</span><br/>' + rating

    html_rows += f"""
    <tr>
      <td style="vertical-align:top;padding:8px;text-align:center;background:#f9f9f9">
        <strong>Aufgabe {nr}</strong><br/><small>{title}</small>
      </td>
      <td style="padding:4px">{orig_img}</td>
      <td style="padding:4px">{cq_img}</td>
      <td style="padding:8px;font-size:13px;vertical-align:top">{rating}</td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8"/>
<title>GZ Vergleich: Shapely vs CadQuery+HLR</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; background: #fafafa; }}
  h1 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th {{ background: #2c3e50; color: white; padding: 10px; text-align: center; }}
  td {{ border: 1px solid #ddd; }}
  tr:nth-child(even) td {{ background: #f5f5f5; }}
  #lightbox {{
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.85); z-index: 1000; cursor: pointer;
    justify-content: center; align-items: center;
  }}
  #lightbox img {{ max-width: 95%; max-height: 95%; }}
</style>
</head>
<body>
<h1>GZ Aufgaben &ndash; Vergleich Shapely vs CadQuery + HLR</h1>
<p>Generiert am 2026-04-01. Links: manuell kodierte Shapely-Loesung. Rechts: CadQuery 3D + OCC Hidden Line Removal.</p>

<div id="lightbox" onclick="this.style.display='none'">
  <img id="lb-img" src=""/>
</div>
<script>
function openLB(src) {{
  document.getElementById('lb-img').src = src;
  document.getElementById('lightbox').style.display = 'flex';
}}
</script>

<table>
<tr>
  <th style="width:12%">Aufgabe</th>
  <th style="width:33%">Shapely (manuell)</th>
  <th style="width:33%">CadQuery + HLR</th>
  <th style="width:22%">Bewertung</th>
</tr>
{html_rows}
</table>

<p style="color:#888;margin-top:30px;font-size:12px">
  Erzeugt mit gz_cadquery.py &ndash; CadQuery {cq.__version__} + OCC HLR
</p>
</body>
</html>
"""

html_path = OUT / "gz_cadquery_vergleich.html"
html_path.write_text(html, encoding="utf-8")
log(f"HTML: {html_path}")

log("\nDONE.")
log_file.close()
