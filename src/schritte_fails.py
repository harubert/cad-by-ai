"""Erzeugt FAIL-SVGs: gescheiterte Konstruktionsversuche.

Aufruf: "D:/Programme/python/scripts/python.bat" src/schritte_fails.py
"""

import math
import numpy as np
from shapely.geometry import Polygon, Point, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
from shapely.validation import make_valid
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output' / 'schritte'
OUT.mkdir(exist_ok=True, parents=True)

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------
SLOT_W = 8
SLOT_DEPTH = 12.5
CD_DEPTH = 4.5
E_EXT = 3

sw = SLOT_W / 2          # 4
sb = 20 - SLOT_DEPTH     # 7.5
cd_y = 20 - CD_DEPTH     # 15.5
e_x = sw + E_EXT         # 7

A_x, A_y = sw, sb        # (4, 7.5)
B_x, B_y = sw, 20        # (4, 20)
C_x, C_y = sw, cd_y      # (4, 15.5)
E_x, E_y = e_x, cd_y     # (7, 15.5)
F_x, F_y = E_x, E_y + 2.5   # (7, 18)
G_x, G_y = E_x + 2.5, E_y   # (9.5, 15.5)
D_x = G_x                    # 9.5
D_y = A_y + math.sqrt(8**2 - (D_x - A_x)**2)  # ~13.31

P_x, P_y = 4, 16.5
Q_x, Q_y = 5, 15.5

# Arc center M
S_xm = (A_x + D_x) / 2
S_ym = (A_y + D_y) / 2
ad_dir = math.atan2(D_y - A_y, D_x - A_x)
nx = math.cos(ad_dir + math.pi / 2)
ny = math.sin(ad_dir + math.pi / 2)
half_chord = math.sqrt((D_x - A_x)**2 + (D_y - A_y)**2) / 2
sagitta = math.sqrt(8**2 - half_chord**2)
M_x = S_xm + sagitta * nx
M_y = S_ym + sagitta * ny

r_arc = 8.0
r_ef = 2.5

# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def geom_to_svg_path(geom):
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    paths = []
    for poly in polys:
        pts = list(poly.exterior.coords)
        d = f'M {pts[0][0]:.4f},{-pts[0][1]:.4f}'
        for p in pts[1:]:
            d += f' L {p[0]:.4f},{-p[1]:.4f}'
        d += ' Z'
        for interior in poly.interiors:
            pts = list(interior.coords)
            d += f' M {pts[0][0]:.4f},{-pts[0][1]:.4f}'
            for p in pts[1:]:
                d += f' L {p[0]:.4f},{-p[1]:.4f}'
            d += ' Z'
        paths.append(d)
    return ' '.join(paths)


def save_svg(filename, profile, extra_svg='', points=None, description=''):
    vb = '-25 -25 50 50'
    d = geom_to_svg_path(profile)

    labels = ''
    if points:
        for name, px, py in points:
            labels += f'  <circle cx="{px:.3f}" cy="{-py:.3f}" r="0.3" fill="blue"/>\n'
            labels += (f'  <text x="{px + 0.5:.3f}" y="{-(py + 0.5):.3f}" '
                       f'font-size="1.1" font-family="sans-serif" fill="blue">{name}</text>\n')

    desc_text = ''
    if description:
        desc_text = (f'  <text x="0" y="23" text-anchor="middle" fill="#666" '
                     f'font-size="1.4" font-family="sans-serif">{description}</text>\n')

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">
  <rect x="-25" y="-25" width="50" height="50" fill="white"/>
  <path d="{d}" fill="none" stroke="red" stroke-width="0.3" fill-rule="evenodd"/>
{extra_svg}{labels}  <text x="15" y="-18" fill="red" font-size="3.5" font-weight="bold"
        font-family="sans-serif">FAIL</text>
{desc_text}</svg>'''
    (OUT / filename).write_text(svg, encoding='utf-8')
    print(f"  OK: {filename}")


# ---------------------------------------------------------------------------
# Rotation helpers
# ---------------------------------------------------------------------------

def four_rotations(geom):
    parts = [geom]
    for a in [90, 180, 270]:
        r = affinity.rotate(geom, a, origin=(0, 0))
        r = make_valid(r)
        parts.append(r)
    return unary_union(parts)


def rot_xy(x, y, angle_deg):
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    return (x * c - y * s, x * s + y * c)


# ---------------------------------------------------------------------------
# Base profile (with straight A-E lines, used by most FAIL diagrams)
# ---------------------------------------------------------------------------

square = box(-20, -20, 20, 20)
rounded = square.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)
bore = Point(0, 0).buffer(6.8 / 2, resolution=64)
slot_deep = box(-sw, sb, sw, 20.1)
all_slots = four_rotations(slot_deep)
with_slots = rounded.difference(all_slots).difference(bore)
with_r2 = with_slots.buffer(-2, join_style=1).buffer(2, join_style=1)

hinterschnitt_top = Polygon([
    (-sw, cd_y + 0.01), (-e_x, cd_y), (-sw, sb),
    (sw, sb), (e_x, cd_y), (sw, cd_y + 0.01),
])
all_h = four_rotations(hinterschnitt_top)
base_profile = with_r2.difference(all_h)

# Arc overlay (correct arcs as red lines for reference)
def build_arc_overlay(color='red', width='0.2'):
    arcs = ''
    for angle in [0, 90, 180, 270]:
        for sx_val in [1, -1]:
            ax, ay = rot_xy(sx_val * A_x, A_y, angle)
            dx, dy = rot_xy(sx_val * D_x, D_y, angle)
            gx, gy = rot_xy(sx_val * G_x, G_y, angle)
            fx, fy = rot_xy(sx_val * F_x, F_y, angle)
            ex, ey = rot_xy(sx_val * E_x, E_y, angle)
            sweep_ad = 0 if sx_val == 1 else 1
            sweep_gf = 0 if sx_val == 1 else 1
            arcs += (f'  <path d="M {ax:.4f},{-ay:.4f} '
                     f'A {r_arc:.4f},{r_arc:.4f} 0 0,{sweep_ad} '
                     f'{dx:.4f},{-dy:.4f}" '
                     f'fill="none" stroke="{color}" stroke-width="{width}"/>\n')
            arcs += (f'  <line x1="{dx:.4f}" y1="{-dy:.4f}" '
                     f'x2="{gx:.4f}" y2="{-gy:.4f}" '
                     f'stroke="{color}" stroke-width="{width}"/>\n')
            arcs += (f'  <path d="M {gx:.4f},{-gy:.4f} '
                     f'A {r_ef:.4f},{r_ef:.4f} 0 0,{sweep_gf} '
                     f'{fx:.4f},{-fy:.4f}" '
                     f'fill="none" stroke="{color}" stroke-width="{width}"/>\n')
            arcs += (f'  <line x1="{fx:.4f}" y1="{-fy:.4f}" '
                     f'x2="{ex:.4f}" y2="{-ey:.4f}" '
                     f'stroke="{color}" stroke-width="{width}"/>\n')
    return arcs


# ===========================================================================
print("Erzeuge FAIL-SVGs ...")

# ===========================================================================
# SCHRITT 17 FAIL: Bogen-Integration in Shapely scheitert
# Arc points as polygon overlap with rotated versions -> topology error
# ===========================================================================

# Generate arc points for A->D that form a polygon
def arc_points_ad(sx_val, n=20):
    """Generate points along arc from A to D (or mirrored)."""
    ax, ay = sx_val * A_x, A_y
    dx, dy = sx_val * D_x, D_y
    mx, my = sx_val * M_x, M_y  # mirror M for left side
    # Angles from center M to A and D
    a_start = math.atan2(ay - my, ax - mx)
    a_end = math.atan2(dy - my, dx - mx)
    if sx_val == 1 and a_end < a_start:
        a_end += 2 * math.pi
    if sx_val == -1 and a_end > a_start:
        a_end -= 2 * math.pi
    pts = []
    for i in range(n + 1):
        t = a_start + (a_end - a_start) * i / n
        pts.append((mx + r_arc * math.cos(t), my + r_arc * math.sin(t)))
    return pts

# Build a failed arc-polygon that shows topology overlap
# The polygon tries to include the arc bulge area for the top slot
fail_poly_right = arc_points_ad(1, 30)
# Close it with straight lines back through A
fail_poly_right.append((A_x, A_y))
fail_poly_right_coords = fail_poly_right

# Also build for left side - these overlap!
fail_poly_left = arc_points_ad(-1, 30)
fail_poly_left.append((-A_x, A_y))

# Rotate some of these to show they overlap
fail_svg_17 = ''
# Show the failed arc-polygons with dashed red lines for top slot
for pts_list, label in [(fail_poly_right_coords, 'R'), (fail_poly_left, 'L')]:
    d = f'M {pts_list[0][0]:.3f},{-pts_list[0][1]:.3f}'
    for p in pts_list[1:]:
        d += f' L {p[0]:.3f},{-p[1]:.3f}'
    d += ' Z'
    fail_svg_17 += (f'  <path d="{d}" fill="rgba(255,0,0,0.15)" '
                    f'stroke="darkred" stroke-width="0.25" '
                    f'stroke-dasharray="0.5,0.3"/>\n')

# Show rotated version (90 deg) that overlaps with the original
for pts_list in [fail_poly_right_coords, fail_poly_left]:
    rot_pts = [rot_xy(x, y, 90) for x, y in pts_list]
    d = f'M {rot_pts[0][0]:.3f},{-rot_pts[0][1]:.3f}'
    for p in rot_pts[1:]:
        d += f' L {p[0]:.3f},{-p[1]:.3f}'
    d += ' Z'
    fail_svg_17 += (f'  <path d="{d}" fill="rgba(255,100,0,0.15)" '
                    f'stroke="darkred" stroke-width="0.25" '
                    f'stroke-dasharray="0.5,0.3"/>\n')

# Mark overlap area
fail_svg_17 += ('  <text x="6" y="-10" fill="darkred" font-size="1.2" '
                'font-family="sans-serif" transform="rotate(-45,6,-10)">'
                'TopologyException!</text>\n')

save_svg('schritt17_FAIL_bogen_integration.svg', base_profile,
         extra_svg=fail_svg_17,
         description='Shapely: Arc-Polygon verursacht TopologyException')


# ===========================================================================
# SCHRITT 18 FAIL: v2.py SVG-direct - Boegen in falsche Richtung (convex)
# Arcs curve OUTWARD instead of inward
# ===========================================================================

wrong_arcs = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        ax, ay = rot_xy(sx_val * A_x, A_y, angle)
        dx, dy = rot_xy(sx_val * D_x, D_y, angle)
        gx, gy = rot_xy(sx_val * G_x, G_y, angle)
        fx, fy = rot_xy(sx_val * F_x, F_y, angle)
        ex, ey = rot_xy(sx_val * E_x, E_y, angle)

        # WRONG sweep flags: flipped from correct
        sweep_ad = 1 if sx_val == 1 else 0   # opposite of correct
        sweep_gf = 1 if sx_val == 1 else 0   # opposite of correct

        # Arc A->D (WRONG direction - convex/outward)
        wrong_arcs += (f'  <path d="M {ax:.4f},{-ay:.4f} '
                       f'A {r_arc:.4f},{r_arc:.4f} 0 0,{sweep_ad} '
                       f'{dx:.4f},{-dy:.4f}" '
                       f'fill="none" stroke="darkred" stroke-width="0.35"/>\n')
        # Line D->G
        wrong_arcs += (f'  <line x1="{dx:.4f}" y1="{-dy:.4f}" '
                       f'x2="{gx:.4f}" y2="{-gy:.4f}" '
                       f'stroke="darkred" stroke-width="0.25"/>\n')
        # Arc G->F (WRONG direction)
        wrong_arcs += (f'  <path d="M {gx:.4f},{-gy:.4f} '
                       f'A {r_ef:.4f},{r_ef:.4f} 0 0,{sweep_gf} '
                       f'{fx:.4f},{-fy:.4f}" '
                       f'fill="none" stroke="darkred" stroke-width="0.35"/>\n')
        # Line F->E
        wrong_arcs += (f'  <line x1="{fx:.4f}" y1="{-fy:.4f}" '
                       f'x2="{ex:.4f}" y2="{-ey:.4f}" '
                       f'stroke="darkred" stroke-width="0.25"/>\n')

save_svg('schritt18_FAIL_v2_svg.svg', base_profile,
         extra_svg=wrong_arcs,
         description='v2.py: SVG-Boegen in falsche Richtung (konvex statt konkav)')


# ===========================================================================
# SCHRITT 19 FAIL: Bogen D-A nur auf gespiegelter Seite korrekt
# Right side of each slot has straight lines, left side has arcs
# ===========================================================================

mixed_arcs = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        ax, ay = rot_xy(sx_val * A_x, A_y, angle)
        dx, dy = rot_xy(sx_val * D_x, D_y, angle)
        gx, gy = rot_xy(sx_val * G_x, G_y, angle)
        fx, fy = rot_xy(sx_val * F_x, F_y, angle)
        ex, ey = rot_xy(sx_val * E_x, E_y, angle)

        if sx_val == -1:
            # LEFT side: correct arcs (this works)
            sweep_ad = 1
            sweep_gf = 1
            mixed_arcs += (f'  <path d="M {ax:.4f},{-ay:.4f} '
                           f'A {r_arc:.4f},{r_arc:.4f} 0 0,{sweep_ad} '
                           f'{dx:.4f},{-dy:.4f}" '
                           f'fill="none" stroke="green" stroke-width="0.25"/>\n')
            mixed_arcs += (f'  <line x1="{dx:.4f}" y1="{-dy:.4f}" '
                           f'x2="{gx:.4f}" y2="{-gy:.4f}" '
                           f'stroke="green" stroke-width="0.25"/>\n')
            mixed_arcs += (f'  <path d="M {gx:.4f},{-gy:.4f} '
                           f'A {r_ef:.4f},{r_ef:.4f} 0 0,{sweep_gf} '
                           f'{fx:.4f},{-fy:.4f}" '
                           f'fill="none" stroke="green" stroke-width="0.25"/>\n')
            mixed_arcs += (f'  <line x1="{fx:.4f}" y1="{-fy:.4f}" '
                           f'x2="{ex:.4f}" y2="{-ey:.4f}" '
                           f'stroke="green" stroke-width="0.25"/>\n')
        else:
            # RIGHT side: straight lines only (arc failed here)
            mixed_arcs += (f'  <line x1="{ax:.4f}" y1="{-ay:.4f}" '
                           f'x2="{ex:.4f}" y2="{-ey:.4f}" '
                           f'stroke="#cc0000" stroke-width="0.3" '
                           f'stroke-dasharray="0.4,0.3"/>\n')

# Add labels on right side of top slot to show where the problem is
pts_labeled = [
    ('A', A_x, A_y), ('B', B_x, B_y), ('C', C_x, C_y),
    ('D', D_x, D_y), ('E', E_x, E_y),
]

save_svg('schritt19_FAIL_bogen_falsche_seite.svg', base_profile,
         extra_svg=mixed_arcs, points=pts_labeled,
         description='Bogen nur auf gespiegelter Seite (links), rechts nur Gerade')


# ===========================================================================
# SCHRITT 22 FAIL: "Fadenkreuz" bei C - sweep=1 erzeugt Vollkreis
# Full circle artifact at C instead of quarter-arc rounding
# ===========================================================================

# Draw full circles at every C location
c_circles = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        cx_r, cy_r = rot_xy(sx_val * C_x, C_y, angle)
        c_circles += (f'  <circle cx="{cx_r:.4f}" cy="{-cy_r:.4f}" r="1" '
                      f'fill="rgba(255,0,0,0.12)" stroke="darkred" '
                      f'stroke-width="0.2"/>\n')
        # Add a small crosshair at the center
        c_circles += (f'  <line x1="{cx_r - 1.5:.4f}" y1="{-cy_r:.4f}" '
                      f'x2="{cx_r + 1.5:.4f}" y2="{-cy_r:.4f}" '
                      f'stroke="darkred" stroke-width="0.1"/>\n')
        c_circles += (f'  <line x1="{cx_r:.4f}" y1="{-(cy_r - 1.5):.4f}" '
                      f'x2="{cx_r:.4f}" y2="{-(cy_r + 1.5):.4f}" '
                      f'stroke="darkred" stroke-width="0.1"/>\n')

# Also show the correct arc overlay for context
arc_overlay_thin = build_arc_overlay('red', '0.15')

save_svg('schritt22_FAIL_c_sweep1.svg', base_profile,
         extra_svg=arc_overlay_thin + c_circles,
         points=[('C', C_x, C_y)],
         description='sweep=1 bei C erzeugt Vollkreis-Artefakt statt Viertelkreis')


# ===========================================================================
# SCHRITT 25 FAIL: C-Rundung erzeugt Extra-Punkt (Spike/Zag bei C)
# Arc goes back to original C point before continuing to E
# ===========================================================================

# Build the spike: path goes P -> arc -> Q -> back to C -> then to E
spike_svg = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        px_r, py_r = rot_xy(sx_val * P_x, P_y, angle)
        qx_r, qy_r = rot_xy(sx_val * Q_x, Q_y, angle)
        cx_r, cy_r = rot_xy(sx_val * C_x, C_y, angle)
        ex_r, ey_r = rot_xy(sx_val * E_x, E_y, angle)

        sweep = 1 if sx_val == 1 else 0
        # Correct arc from P to Q
        spike_svg += (f'  <path d="M {px_r:.4f},{-py_r:.4f} '
                      f'A 1,1 0 0,{sweep} '
                      f'{qx_r:.4f},{-qy_r:.4f}" '
                      f'fill="none" stroke="green" stroke-width="0.2"/>\n')
        # WRONG: extra segment Q -> C (goes back to original corner)
        spike_svg += (f'  <line x1="{qx_r:.4f}" y1="{-qy_r:.4f}" '
                      f'x2="{cx_r:.4f}" y2="{-cy_r:.4f}" '
                      f'stroke="darkred" stroke-width="0.3"/>\n')
        # Then C -> E (the original straight segment)
        spike_svg += (f'  <line x1="{cx_r:.4f}" y1="{-cy_r:.4f}" '
                      f'x2="{ex_r:.4f}" y2="{-ey_r:.4f}" '
                      f'stroke="darkred" stroke-width="0.3"/>\n')
        # Small red dot at the spike point C
        spike_svg += (f'  <circle cx="{cx_r:.4f}" cy="{-cy_r:.4f}" r="0.35" '
                      f'fill="darkred"/>\n')

save_svg('schritt25_FAIL_c_extra_punkt.svg', base_profile,
         extra_svg=arc_overlay_thin + spike_svg,
         points=[('C', C_x, C_y), ('P', P_x, P_y), ('Q', Q_x, Q_y)],
         description='C-Rundung: Extra-Punkt erzeugt Zacke (Q zurueck zu C)')


# ===========================================================================
# SCHRITT 29 FAIL: C-Rundung konkav statt konvex
# R1 at C curves INTO the material instead of away
# ===========================================================================

# Concave arc: center at C itself (4,15.5) instead of (5,16.5)
# This means the arc curves inward (into the material)
concave_arcs = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        px_r, py_r = rot_xy(sx_val * P_x, P_y, angle)
        qx_r, qy_r = rot_xy(sx_val * Q_x, Q_y, angle)
        cx_r, cy_r = rot_xy(sx_val * C_x, C_y, angle)

        # WRONG sweep: arc goes concave (inward) instead of convex (outward)
        sweep = 0 if sx_val == 1 else 1  # opposite of correct

        concave_arcs += (f'  <path d="M {px_r:.4f},{-py_r:.4f} '
                         f'A 1,1 0 0,{sweep} '
                         f'{qx_r:.4f},{-qy_r:.4f}" '
                         f'fill="none" stroke="darkred" stroke-width="0.35"/>\n')
        # Shade the wrong area lightly
        # Small filled arc segment showing the concave cut
        concave_arcs += (f'  <path d="M {px_r:.4f},{-py_r:.4f} '
                         f'A 1,1 0 0,{sweep} '
                         f'{qx_r:.4f},{-qy_r:.4f} '
                         f'L {cx_r:.4f},{-cy_r:.4f} Z" '
                         f'fill="rgba(255,0,0,0.2)" stroke="none"/>\n')

save_svg('schritt29_FAIL_c_konkav.svg', base_profile,
         extra_svg=arc_overlay_thin + concave_arcs,
         points=[('C', C_x, C_y), ('P', P_x, P_y), ('Q', Q_x, Q_y)],
         description='C-Rundung konkav (ins Material) statt konvex (nach aussen)')


print("Fertig! Alle 6 FAIL-SVGs erzeugt.")
