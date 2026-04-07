"""
Aufgabe 01 v2: Shapely fuer Grundform, SVG direkt fuer Boegen.
Erster Test: nur obere Nut, rechte Seite.
"""

import math
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
from shapely import affinity
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'
OUT.mkdir(exist_ok=True)

# === Parameter ===
SLOT_W = 8
SLOT_DEPTH = 12.5
CD_DEPTH = 4.5
E_EXT = 3

sw = SLOT_W / 2       # 4
sb = 20 - SLOT_DEPTH   # 7.5
cd_y = 20 - CD_DEPTH   # 15.5
e_x = sw + E_EXT       # 7

A_x, A_y = sw, sb
B_x, B_y = sw, 20
C_x, C_y = sw, cd_y
E_x, E_y = e_x, cd_y
F_x, F_y = E_x, E_y + 2.5
G_x, G_y = E_x + 2.5, E_y
D_x = G_x
D_y = A_y + math.sqrt(8**2 - (D_x - A_x)**2)

# M (Kreismittelpunkt fuer Bogen A-D)
S_x = (A_x + D_x) / 2
S_y = (A_y + D_y) / 2
ad_dir = math.atan2(D_y - A_y, D_x - A_x)
n_x = math.cos(ad_dir + math.pi/2)
n_y = math.sin(ad_dir + math.pi/2)
M_x = S_x + 6 * n_x
M_y = S_y + 6 * n_y
r_AD = math.sqrt((M_x - A_x)**2 + (M_y - A_y)**2)
r_GF = math.sqrt((E_x - G_x)**2 + (E_y - G_y)**2)

# === Shapely: nur Grundform (Quadrat + R4.5 + einfache Schlitze + R2 + Bohrung) ===
square = box(-20, -20, 20, 20)
rounded = square.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)

# Einfache Schlitze (Hals bis cd_y, ohne Hinterschnitt)
slot_top = box(-sw, cd_y, sw, 20.1)
all_slots = unary_union([
    slot_top,
    affinity.rotate(slot_top, 90, origin=(0,0)),
    affinity.rotate(slot_top, 180, origin=(0,0)),
    affinity.rotate(slot_top, 270, origin=(0,0)),
])
profile = rounded.difference(all_slots)
profile = profile.buffer(-2, join_style=1).buffer(2, join_style=1)
bore = Point(0, 0).buffer(6.8/2, resolution=64)
profile = profile.difference(bore)

# === SVG: Grundform aus Shapely ===
from shapely.geometry import MultiPolygon as MP
polys = list(profile.geoms) if isinstance(profile, MP) else [profile]

def coords_to_L(coords):
    """Koordinaten -> SVG L-Befehle (ohne M am Anfang)."""
    pts = list(coords)
    parts = []
    for p in pts:
        parts.append(f'L {p[0]:.3f},{-p[1]:.3f}')
    return ' '.join(parts)

# Grundform als SVG-Pfad (wird spaeter modifiziert)
base_paths = []
for poly in polys:
    ext = list(poly.exterior.coords)
    d = f'M {ext[0][0]:.3f},{-ext[0][1]:.3f} '
    for p in ext[1:]:
        d += f'L {p[0]:.3f},{-p[1]:.3f} '
    d += 'Z'
    for interior in poly.interiors:
        ic = list(interior.coords)
        d += f' M {ic[0][0]:.3f},{-ic[0][1]:.3f} '
        for p in ic[1:]:
            d += f'L {p[0]:.3f},{-p[1]:.3f} '
        d += 'Z'
    base_paths.append(d)

base_d = ' '.join(base_paths)

# === SVG: Hinterschnitt-Pfade direkt mit Arc-Befehlen ===
# Fuer jede der 4 Nuten, je 2 Seiten (links/rechts)
# Pfad pro Seite: C -> E -> F -arc-> G -> D -arc-> A
# Das ist ein offener Pfad der die Nutwand INNEN beschreibt

def build_hinterschnitt_svg():
    """Erzeugt SVG-Pfade fuer den Hinterschnitt auf allen 8 Stellen."""
    paths = ''
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        ca, sa = math.cos(rad), math.sin(rad)
        def rot(x, y):
            return (x*ca - y*sa, x*sa + y*ca)

        for sx in [1, -1]:
            # Alle Punkte rotieren und spiegeln
            c = rot(sx * C_x, C_y)
            e = rot(sx * E_x, E_y)
            f = rot(sx * F_x, F_y)
            g = rot(sx * G_x, G_y)
            d = rot(sx * D_x, D_y)
            a = rot(sx * A_x, A_y)

            sweep_ad = 0 if sx == 1 else 1
            sweep_gf = 0 if sx == 1 else 1

            # Geschlossener Pfad: C -> E -> F -arc-> G -> D -arc-> A -> (Nutboden) -> A_gegenüber -> ... -> C
            # Wir zeichnen nur die Kontur des Hinterschnitts als geschlossene Flaeche
            # C -> E (gerade)
            # E -> F (gerade, senkrecht)
            # F -> G (Bogen um E)
            # G -> D (gerade, senkrecht)
            # D -> A (Bogen um M)
            # A -> C (gerade, senkrecht zurueck zur Nutwand)
            paths += (
                f'  <path d="'
                f'M {c[0]:.3f},{-c[1]:.3f} '           # C
                f'L {e[0]:.3f},{-e[1]:.3f} '           # E
                f'L {f[0]:.3f},{-f[1]:.3f} '           # F
                f'A {r_GF:.3f},{r_GF:.3f} 0 0,{sweep_gf} {g[0]:.3f},{-g[1]:.3f} '  # Bogen F->G
                f'L {d[0]:.3f},{-d[1]:.3f} '           # D (senkrecht unter G)
                f'A {r_AD:.3f},{r_AD:.3f} 0 0,{sweep_ad} {a[0]:.3f},{-a[1]:.3f} '  # Bogen D->A
                f'Z" '
                f'fill="none" stroke="red" stroke-width="0.2"/>\n'
            )
    return paths

hinterschnitt_svg = build_hinterschnitt_svg()

# === Labels ===
labels_svg = ''
dot_r = 0.3
font_size = 1.1
points = [
    ('A', A_x, A_y), ('B', B_x, B_y), ('C', C_x, C_y),
    ('D', D_x, D_y), ('E', E_x, E_y), ('F', F_x, F_y),
    ('G', G_x, G_y), ('M', M_x, M_y),
]
for name, px, py in points:
    labels_svg += f'  <circle cx="{px:.2f}" cy="{-py:.2f}" r="{dot_r}" fill="blue"/>\n'
    ox = 0.7 if px >= 0 else -0.7
    oy = 0.7 if py >= 0 else -0.7
    anchor = 'start' if px >= 0 else 'end'
    labels_svg += (f'  <text x="{px+ox:.2f}" y="{-(py+oy):.2f}" '
                   f'font-size="{font_size}" font-family="sans-serif" '
                   f'fill="blue" text-anchor="{anchor}">{name}</text>\n')

# === Zusammenbauen ===
margin = 5
vb = f'{-20-margin} {-20-margin} {40+2*margin} {40+2*margin}'

# Hintergrundbild
import base64
img_path = Path(__file__).resolve().parent.parent / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
scale_img = 40.0 / 223.0
bg = ''
if img_path.exists():
    b64 = base64.b64encode(img_path.read_bytes()).decode('ascii')
    bg = (f'  <image href="data:image/jpeg;base64,{b64}" '
          f'x="{-20 - 35*scale_img:.2f}" y="{-20 - 52*scale_img:.2f}" '
          f'width="{300*scale_img:.2f}" height="{300*scale_img:.2f}" opacity="0.25"/>\n')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="{vb}" width="600" height="600">
{bg}  <path d="{base_d}" fill="none" stroke="red" stroke-width="0.2" fill-rule="evenodd"/>
{hinterschnitt_svg}{labels_svg}</svg>'''

(OUT / 'aufgabe01_v2.svg').write_text(svg, encoding='utf-8')
print("OK: aufgabe01_v2.svg")
