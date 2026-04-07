"""Erzeugt alle Schritt-fuer-Schritt SVGs fuer die Alu-Profil-Konstruktionsdoku.

Aufruf: "D:/Programme/python/scripts/python.bat" src/schritte_alle.py
"""

import math
import numpy as np
from shapely.geometry import Polygon, Point, box, MultiPolygon, LineString
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

# Points for rounding at C
P_x, P_y = 4, 16.5   # C + (0, 1) on vertical line
Q_x, Q_y = 5, 15.5   # C + (1, 0) on horizontal line

# Arc center M (center of circular arc A->D, radius 8)
S_xm = (A_x + D_x) / 2
S_ym = (A_y + D_y) / 2
ad_dir = math.atan2(D_y - A_y, D_x - A_x)
nx = math.cos(ad_dir + math.pi / 2)
ny = math.sin(ad_dir + math.pi / 2)
half_chord = math.sqrt((D_x - A_x)**2 + (D_y - A_y)**2) / 2
sagitta = math.sqrt(8**2 - half_chord**2)
M_x = S_xm + sagitta * nx
M_y = S_ym + sagitta * ny

r_arc = 8.0  # radius A-D arc
r_ef = 2.5   # radius G-F arc (quarter circle)

# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def geom_to_svg_path(geom):
    """Convert shapely geometry to SVG path d-string (y-flipped)."""
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


def save_svg(filename, profile, extra_svg='', points=None,
             fail=False, hatch=False, bg_white=True):
    """Write SVG file. viewBox centered, 400x400px."""
    vb = '-25 -25 50 50'
    d = geom_to_svg_path(profile)

    labels = ''
    if points:
        for name, px, py in points:
            labels += f'  <circle cx="{px:.3f}" cy="{-py:.3f}" r="0.3" fill="blue"/>\n'
            labels += (f'  <text x="{px + 0.5:.3f}" y="{-(py + 0.5):.3f}" '
                       f'font-size="1.1" font-family="sans-serif" fill="blue">{name}</text>\n')

    fail_text = ''
    if fail:
        fail_text = '  <text x="15" y="-18" fill="red" font-size="3" font-weight="bold">FAIL</text>\n'

    hatch_defs = ''
    hatch_rect = ''
    if hatch:
        hatch_defs = '''  <defs>
    <pattern id="hatch" width="1.5" height="1.5" patternUnits="userSpaceOnUse"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="1.5" stroke="red" stroke-width="0.08"/>
    </pattern>
    <clipPath id="profileClip">
      <path d="{d}" fill-rule="evenodd"/>
    </clipPath>
  </defs>\n'''.replace('{d}', d)
        hatch_rect = '  <rect x="-25" y="-25" width="50" height="50" fill="url(#hatch)" clip-path="url(#profileClip)"/>\n'

    bg = '  <rect x="-25" y="-25" width="50" height="50" fill="white"/>\n' if bg_white else ''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">
{bg}{hatch_defs}  <path d="{d}" fill="none" stroke="red" stroke-width="0.2" fill-rule="evenodd"/>
{hatch_rect}{extra_svg}{labels}{fail_text}</svg>'''
    (OUT / filename).write_text(svg, encoding='utf-8')
    print(f"  OK: {filename}")


# ---------------------------------------------------------------------------
# Rotation helpers
# ---------------------------------------------------------------------------

def four_rotations(geom):
    """Return union of geom rotated 0/90/180/270 around origin."""
    parts = [geom]
    for a in [90, 180, 270]:
        r = affinity.rotate(geom, a, origin=(0, 0))
        r = make_valid(r)
        parts.append(r)
    return unary_union(parts)


def rot_xy(x, y, angle_deg):
    """Rotate point (x,y) around origin."""
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    return (x * c - y * s, x * s + y * c)


# ---------------------------------------------------------------------------
# Generate steps
# ---------------------------------------------------------------------------
print("Erzeuge Schritt-SVGs ...")

# ===== SCHRITT 01: Quadrat 40x40 =====
s1 = box(-20, -20, 20, 20)
save_svg('schritt01_quadrat.svg', s1)

# ===== SCHRITT 02: R4.5 Eckrundung =====
s2 = s1.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)
save_svg('schritt02_r45.svg', s2)

# ===== SCHRITT 03: Bohrung D6.8 =====
bore = Point(0, 0).buffer(6.8 / 2, resolution=64)
s3 = s2.difference(bore)
save_svg('schritt03_bohrung.svg', s3)

# ===== SCHRITT 04: Nuten 8x5 (erster Versuch, zu flach) =====
slot_shallow = box(-sw, 20 - 5, sw, 20.1)
all_slots_shallow = four_rotations(slot_shallow)
s4 = s2.difference(all_slots_shallow).difference(bore)
save_svg('schritt04_nuten_8x5.svg', s4)

# ===== SCHRITT 05: Nuten 8x12.5 (korrigiert) =====
slot_deep = box(-sw, sb, sw, 20.1)
all_slots_deep = four_rotations(slot_deep)
s5 = s2.difference(all_slots_deep).difference(bore)
save_svg('schritt05_nuten_8x12.5.svg', s5)

# ===== SCHRITT 06: R2 an Eintrittskanten (richtig) =====
s6 = s5.buffer(-2, join_style=1).buffer(2, join_style=1)
save_svg('schritt06_r2_richtig.svg', s6)

# ===== SCHRITT 07: Punkte A, B, C, E (rechte Seite obere Nut) =====
save_svg('schritt07_punkte_ABCE.svg', s6,
         points=[('A', A_x, A_y), ('B', B_x, B_y),
                 ('C', C_x, C_y), ('E', E_x, E_y)])

# ===== SCHRITT 08: Hinterschnitt (gerade A->E Linie) =====
# Undercut polygon for top slot (both sides mirrored)
hinterschnitt_top = Polygon([
    (-sw, cd_y + 0.01), (-e_x, cd_y), (-sw, sb),
    (sw, sb), (e_x, cd_y), (sw, cd_y + 0.01),
])
all_h = four_rotations(hinterschnitt_top)
s8 = s6.difference(all_h)
save_svg('schritt08_hinterschnitt.svg', s8,
         points=[('A', A_x, A_y), ('B', B_x, B_y),
                 ('C', C_x, C_y), ('E', E_x, E_y)])

# ===== SCHRITT 05_FAIL: R2 an falscher Stelle (am Nutboden) =====
# Simulate: apply R2 AFTER undercut instead of before
s5_fail_base = s2.difference(all_slots_deep).difference(bore)
# Add undercut first, then round -> rounds bottom corners wrong
s5_fail_with_h = s5_fail_base.difference(all_h)
s5_fail = s5_fail_with_h.buffer(-2, join_style=1).buffer(2, join_style=1)
save_svg('schritt05_FAIL_r2_falsch.svg', s5_fail, fail=True)

# ===== SCHRITT 08_FAIL: T-Nut (rechteckiger Absatz statt schraeger Linie) =====
# T-slot: rectangular step instead of angled undercut
tnut_top = Polygon([
    (-e_x, cd_y), (-e_x, sb), (-sw, sb), (-sw, cd_y),
    (sw, cd_y), (sw, sb), (e_x, sb), (e_x, cd_y),
])
all_tnut = four_rotations(tnut_top)
s8_fail = s6.difference(all_tnut)
save_svg('schritt08_FAIL_tnut.svg', s8_fail, fail=True)

# ===== SCHRITT 09: Alle Punkte A,B,C,D,E,F,G,M =====
save_svg('schritt09_punkte_ABCDEFGM.svg', s8,
         points=[('A', A_x, A_y), ('B', B_x, B_y),
                 ('C', C_x, C_y), ('D', D_x, D_y),
                 ('E', E_x, E_y), ('F', F_x, F_y),
                 ('G', G_x, G_y), ('M', M_x, M_y)])

# ===== SCHRITT 10: Gruener Bogen A->D Overlay =====
green_arcs = ''
for angle in [0, 90, 180, 270]:
    for sx in [1, -1]:
        ax, ay = rot_xy(sx * A_x, A_y, angle)
        dx, dy = rot_xy(sx * D_x, D_y, angle)
        sweep = 0 if sx == 1 else 1
        green_arcs += (f'  <path d="M {ax:.4f},{-ay:.4f} '
                       f'A {r_arc:.4f},{r_arc:.4f} 0 0,{sweep} '
                       f'{dx:.4f},{-dy:.4f}" '
                       f'fill="none" stroke="green" stroke-width="0.25"/>\n')

save_svg('schritt10_gruener_bogen.svg', s8, extra_svg=green_arcs,
         points=[('A', A_x, A_y), ('D', D_x, D_y)])

# ===== SCHRITT 11: Bogen D-A integriert (finales Profil mit Bogen) =====
# Build profile path with arcs replacing straight A->E segments
# We construct the SVG path manually for the top-right slot area,
# then rotate for all four sides.

def build_arc_slot_path_one_side(sx=1):
    """Return SVG sub-path for one side of top slot with arc.
    sx=1 for right side, sx=-1 for left side (mirrored).
    Points bottom-up: A -> arc -> D -> G -> arc(G->F) -> F -> E -> C -> B(top)
    """
    a = (sx * A_x, A_y)
    d = (sx * D_x, D_y)
    g = (sx * G_x, G_y)
    f = (sx * F_x, F_y)
    e = (sx * E_x, E_y)
    c = (sx * C_x, C_y)
    b = (sx * B_x, B_y)
    return a, d, g, f, e, c, b


def build_full_profile_svg_path():
    """Build the SVG path with arcs for the full profile.
    This replaces straight lines A->E with arc A->D, line D->G, arc G->F, line F->E.
    We trace the outline of the profile, slot by slot.
    """
    # For simplicity, we generate the profile with shapely for the basic shape,
    # then add arc overlays. For the integrated version, we replace the
    # straight-line A-E segments in the SVG path with arc commands.
    # However, building the full path analytically is complex.
    # Instead: use the shapely profile (s8) as base, but add green arcs
    # as the actual stroke, making them red and part of the profile.

    # Build arcs for all 8 sides (4 rotations x 2 mirrors)
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

            # Arc A->D (R=8)
            arcs += (f'  <path d="M {ax:.4f},{-ay:.4f} '
                     f'A {r_arc:.4f},{r_arc:.4f} 0 0,{sweep_ad} '
                     f'{dx:.4f},{-dy:.4f}" '
                     f'fill="none" stroke="red" stroke-width="0.2"/>\n')
            # Line D->G
            arcs += (f'  <line x1="{dx:.4f}" y1="{-dy:.4f}" '
                     f'x2="{gx:.4f}" y2="{-gy:.4f}" '
                     f'stroke="red" stroke-width="0.2"/>\n')
            # Arc G->F (R=2.5)
            arcs += (f'  <path d="M {gx:.4f},{-gy:.4f} '
                     f'A {r_ef:.4f},{r_ef:.4f} 0 0,{sweep_gf} '
                     f'{fx:.4f},{-fy:.4f}" '
                     f'fill="none" stroke="red" stroke-width="0.2"/>\n')
            # Line F->E (vertical)
            arcs += (f'  <line x1="{fx:.4f}" y1="{-fy:.4f}" '
                     f'x2="{ex:.4f}" y2="{-ey:.4f}" '
                     f'stroke="red" stroke-width="0.2"/>\n')

    return arcs


arc_overlay = build_full_profile_svg_path()
save_svg('schritt11_bogen_integriert.svg', s8, extra_svg=arc_overlay)

# ===== SCHRITT 12_FAIL: C-Rundung Fadenkreuz-Artefakt =====
# Simulate wrong C rounding: buffer the whole profile with small radius
# that creates "crosshair" artifacts at sharp internal corners
# We show: try to round C with buffer approach on the undercut profile -> artifact
s12_fail = s8.buffer(-1, join_style=1).buffer(1, join_style=1)
save_svg('schritt12_FAIL_c_fadenkreuz.svg', s12_fail, fail=True,
         points=[('C', C_x, C_y)])

# ===== SCHRITT 13: C-Rundung korrekt via P/Q =====
# R1 at C using points P and Q
# Replace the sharp corner at C with a quarter-circle arc from P to Q
# P = (4, 16.5), Q = (5, 15.5), center = (5, 16.5), R=1
# We do this by cutting a small square at C and adding a circle
c_round_cut = Polygon([
    (C_x, C_y), (Q_x, C_y), (Q_x, P_y), (C_x, P_y)
])
c_round_add = Point(Q_x, P_y).buffer(1.0, resolution=64)
c_round_piece = c_round_cut.difference(c_round_add)

# Apply to all 8 C-corners (4 rotations x 2 mirrors)
all_c_cuts = []
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        piece = affinity.scale(c_round_piece, xfact=sx_val, yfact=1, origin=(0, 0))
        piece = affinity.rotate(piece, angle, origin=(0, 0))
        piece = make_valid(piece)
        all_c_cuts.append(piece)

s13 = s8
for piece in all_c_cuts:
    s13 = s13.difference(piece)
s13 = make_valid(s13)

# Add arc overlays at C for precise rendering
c_arcs = ''
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        px_r, py_r = rot_xy(sx_val * P_x, P_y, angle)
        qx_r, qy_r = rot_xy(sx_val * Q_x, Q_y, angle)
        sweep = 1 if sx_val == 1 else 0
        c_arcs += (f'  <path d="M {px_r:.4f},{-py_r:.4f} '
                   f'A 1,1 0 0,{sweep} '
                   f'{qx_r:.4f},{-qy_r:.4f}" '
                   f'fill="none" stroke="red" stroke-width="0.2"/>\n')

save_svg('schritt13_c_rundung_ok.svg', s13,
         extra_svg=arc_overlay + c_arcs,
         points=[('C', C_x, C_y), ('P', P_x, P_y), ('Q', Q_x, Q_y)])

# ===== SCHRITT 14: R0.5 an E =====
# R0.5 at E: round the corner at E where horizontal and angled lines meet
e_round_cut = Polygon([
    (E_x, E_y), (E_x + 0.5, E_y), (E_x + 0.5, E_y - 0.5), (E_x, E_y - 0.5)
])
e_round_add = Point(E_x + 0.5, E_y - 0.5).buffer(0.5, resolution=64)
e_round_piece = e_round_cut.difference(e_round_add)

# We need to think about E more carefully.
# E = (7, 15.5). The corner is between the horizontal line (from C to E at y=15.5)
# and the angled line going down to A. We approximate with a small fillet.
all_e_cuts = []
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        piece = affinity.scale(e_round_piece, xfact=sx_val, yfact=1, origin=(0, 0))
        piece = affinity.rotate(piece, angle, origin=(0, 0))
        piece = make_valid(piece)
        all_e_cuts.append(piece)

s14 = s13
for piece in all_e_cuts:
    s14 = s14.difference(piece)
s14 = make_valid(s14)

save_svg('schritt14_e_rundung.svg', s14,
         extra_svg=arc_overlay + c_arcs,
         points=[('E', E_x, E_y)])

# ===== SCHRITT 15: R0.5 an F (Linie-zu-Bogen Uebergang) =====
# F = (7, 18). Corner between vertical line (E up to F) and arc G->F.
# Small fillet R0.5
f_round_cut = Polygon([
    (F_x, F_y), (F_x + 0.5, F_y), (F_x + 0.5, F_y + 0.5), (F_x, F_y + 0.5)
])
f_round_add = Point(F_x + 0.5, F_y + 0.5).buffer(0.5, resolution=64)
f_round_piece = f_round_cut.difference(f_round_add)

all_f_cuts = []
for angle in [0, 90, 180, 270]:
    for sx_val in [1, -1]:
        piece = affinity.scale(f_round_piece, xfact=sx_val, yfact=1, origin=(0, 0))
        piece = affinity.rotate(piece, angle, origin=(0, 0))
        piece = make_valid(piece)
        all_f_cuts.append(piece)

s15 = s14
for piece in all_f_cuts:
    s15 = s15.difference(piece)
s15 = make_valid(s15)

save_svg('schritt15_f_rundung.svg', s15,
         extra_svg=arc_overlay + c_arcs,
         points=[('F', F_x, F_y)])

# ===== SCHRITT 16: Eckquadrate (corner pockets) =====
# Corner pocket squares: 6.5mm side, 2mm offset from edges
# These sit in the rounded corners of the outer profile
# Square at top-right corner: from (20-6.5-2, 20-6.5-2) to (20-2, 20-2)
# = (11.5, 11.5) to (18, 18)
cp_size = 6.5
cp_offset = 2
cp_box = box(20 - cp_offset - cp_size, 20 - cp_offset - cp_size,
             20 - cp_offset, 20 - cp_offset)
all_cp = four_rotations(cp_box)
s16 = s15.difference(all_cp)
s16 = make_valid(s16)

save_svg('schritt16_eckquadrate.svg', s16, extra_svg=arc_overlay + c_arcs)

# ===== SCHRITT 17: Schraffur (final with hatch) =====
save_svg('schritt17_schraffur.svg', s16, extra_svg=arc_overlay + c_arcs,
         hatch=True)

print("Fertig! Alle 17 SVGs erzeugt.")
