"""Erzeugt Schritt-fuer-Schritt SVGs fuer die Konstruktionsdoku."""

import math
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output' / 'schritte'
OUT.mkdir(exist_ok=True, parents=True)

# Parameter (gleich wie aufgabe01.py)
SLOT_W = 8
SLOT_DEPTH = 12.5
CD_DEPTH = 4.5
E_EXT = 3
sw = SLOT_W / 2
sb = 20 - SLOT_DEPTH
cd_y = 20 - CD_DEPTH
e_x = sw + E_EXT

A_x, A_y = sw, sb
B_x, B_y = sw, 20
C_x, C_y = sw, cd_y
E_x, E_y = e_x, cd_y
F_x, F_y = E_x, E_y + 2.5
G_x, G_y = E_x + 2.5, E_y
D_x = G_x
D_y = A_y + math.sqrt(8**2 - (D_x - A_x)**2)


def geom_to_svg_path(geom):
    from shapely.geometry import MultiPolygon as MP
    polys = list(geom.geoms) if isinstance(geom, MP) else [geom]
    paths = []
    for poly in polys:
        pts = list(poly.exterior.coords)
        d = f'M {pts[0][0]:.3f},{-pts[0][1]:.3f}'
        for p in pts[1:]:
            d += f' L {p[0]:.3f},{-p[1]:.3f}'
        d += ' Z'
        for interior in poly.interiors:
            pts = list(interior.coords)
            d += f' M {pts[0][0]:.3f},{-pts[0][1]:.3f}'
            for p in pts[1:]:
                d += f' L {p[0]:.3f},{-p[1]:.3f}'
            d += ' Z'
        paths.append(d)
    return ' '.join(paths)


def save_svg(filename, profile, extra_svg='', points=None):
    margin = 5
    vb = f'{-20-margin} {-20-margin} {40+2*margin} {40+2*margin}'
    d = geom_to_svg_path(profile)

    labels = ''
    if points:
        for name, px, py in points:
            labels += f'  <circle cx="{px:.2f}" cy="{-py:.2f}" r="0.3" fill="blue"/>\n'
            labels += (f'  <text x="{px+0.7:.2f}" y="{-(py+0.7):.2f}" '
                       f'font-size="1.1" font-family="sans-serif" fill="blue">{name}</text>\n')

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">
  <path d="{d}" fill="none" stroke="red" stroke-width="0.2" fill-rule="evenodd"/>
{extra_svg}{labels}</svg>'''
    (OUT / filename).write_text(svg, encoding='utf-8')
    print(f"  OK: {filename}")


print("Erzeuge Schritt-SVGs...")

# Schritt 1: Quadrat
s1 = box(-20, -20, 20, 20)
save_svg('schritt01_quadrat.svg', s1)

# Schritt 2: R4.5
s2 = s1.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)
save_svg('schritt02_r45.svg', s2)

# Schritt 3: Bohrung
bore = Point(0, 0).buffer(6.8/2, resolution=64)
s3 = s2.difference(bore)
save_svg('schritt03_bohrung.svg', s3)

# Schritt 4: Einfache Nuten (Tiefe 12.5)
slot_top = box(-sw, 20-SLOT_DEPTH, sw, 20.1)
all_slots_simple = unary_union([
    slot_top,
    affinity.rotate(slot_top, 90, origin=(0,0)),
    affinity.rotate(slot_top, 180, origin=(0,0)),
    affinity.rotate(slot_top, 270, origin=(0,0)),
])
s4 = s2.difference(all_slots_simple).difference(bore)
save_svg('schritt04_nuten.svg', s4)

# Schritt 5: R2 an Eintrittskanten
s5 = s4.buffer(-2, join_style=1).buffer(2, join_style=1)
save_svg('schritt05_r2.svg', s5, points=[('B', B_x, B_y)])

# Schritt 6: Hinterschnitt (gerade A->E)
hinterschnitt_top = Polygon([
    (-sw, cd_y + 0.01), (-e_x, cd_y), (-sw, sb),
    (sw, sb), (e_x, cd_y), (sw, cd_y + 0.01),
])
all_h = unary_union([
    hinterschnitt_top,
    affinity.rotate(hinterschnitt_top, 90, origin=(0,0)),
    affinity.rotate(hinterschnitt_top, 180, origin=(0,0)),
    affinity.rotate(hinterschnitt_top, 270, origin=(0,0)),
])
s6 = s5.difference(all_h)
save_svg('schritt06_hinterschnitt.svg', s6,
         points=[('A', A_x, A_y), ('B', B_x, B_y), ('C', C_x, C_y), ('E', E_x, E_y)])

# Schritt 7: Punkte D, F, G, M
S_xm = (A_x + D_x) / 2
S_ym = (A_y + D_y) / 2
ad_dir = math.atan2(D_y - A_y, D_x - A_x)
nx = math.cos(ad_dir + math.pi/2)
ny = math.sin(ad_dir + math.pi/2)
M_x = S_xm + 6 * nx
M_y = S_ym + 6 * ny

save_svg('schritt07_punkte.svg', s6,
         points=[('A', A_x, A_y), ('B', B_x, B_y), ('C', C_x, C_y),
                 ('D', D_x, D_y), ('E', E_x, E_y), ('F', F_x, F_y),
                 ('G', G_x, G_y), ('M', M_x, M_y)])

# Schritt 8: Gruene Boegen als Overlay
r_arc = math.sqrt((M_x - A_x)**2 + (M_y - A_y)**2)
r_ef = math.sqrt((E_x - G_x)**2 + (E_y - G_y)**2)

green = ''
for angle in [0, 90, 180, 270]:
    rad = math.radians(angle)
    ca, sa = math.cos(rad), math.sin(rad)
    def rot(x, y):
        return (x*ca - y*sa, x*sa + y*ca)
    for sx in [1, -1]:
        ax, ay = rot(sx*A_x, A_y)
        dx, dy = rot(sx*D_x, D_y)
        gx, gy = rot(sx*G_x, G_y)
        fx, fy = rot(sx*F_x, F_y)
        ex, ey = rot(sx*E_x, E_y)
        sweep_ad = 0 if sx == 1 else 1
        sweep_gf = 0 if sx == 1 else 1
        green += (f'  <path d="M {ax:.3f},{-ay:.3f} A {r_arc:.3f},{r_arc:.3f} 0 0,{sweep_ad} '
                  f'{dx:.3f},{-dy:.3f}" fill="none" stroke="green" stroke-width="0.2"/>\n')
        green += (f'  <line x1="{dx:.3f}" y1="{-dy:.3f}" x2="{gx:.3f}" y2="{-gy:.3f}" '
                  f'stroke="green" stroke-width="0.2"/>\n')
        green += (f'  <path d="M {gx:.3f},{-gy:.3f} A {r_ef:.3f},{r_ef:.3f} 0 0,{sweep_gf} '
                  f'{fx:.3f},{-fy:.3f}" fill="none" stroke="green" stroke-width="0.2"/>\n')
        green += (f'  <line x1="{fx:.3f}" y1="{-fy:.3f}" x2="{ex:.3f}" y2="{-ey:.3f}" '
                  f'stroke="green" stroke-width="0.2"/>\n')

save_svg('schritt08_boegen.svg', s6, extra_svg=green,
         points=[('A', A_x, A_y), ('B', B_x, B_y), ('C', C_x, C_y),
                 ('D', D_x, D_y), ('E', E_x, E_y), ('F', F_x, F_y),
                 ('G', G_x, G_y), ('M', M_x, M_y)])

print("Fertig!")
