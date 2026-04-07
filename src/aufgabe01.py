"""Aufgabe 01: Quadrat 40x40mm, R4.5 Ecken, Bohrung 6.8, 4 Nutoeffnungen 8mm, R2"""

import numpy as np
import math
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'
OUT.mkdir(exist_ok=True)

# --- Geometrie ---

# 1) Quadrat 40x40 mit abgerundeten Ecken R4.5
square = box(-20, -20, 20, 20)
rounded = square.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)

# 2) 4 Nuten mit Hinterschnitt
SLOT_W = 8
SLOT_DEPTH = 12.5
CD_DEPTH = 4.5        # Tiefe von C ab Aussenkante
E_EXT = 3             # Verbreiterung ab C nach aussen

sw = SLOT_W / 2       # 4
sb = 20 - SLOT_DEPTH  # 7.5  (Nutboden y)
cd_y = 20 - CD_DEPTH  # 15   (C y)
e_x = sw + E_EXT      # 7    (E x)

# Punkte (rechte Seite obere Nut)
A_x, A_y = sw, sb         # (4, 7.5)
B_x, B_y = sw, 20         # (4, 20)
C_x, C_y = sw, cd_y       # (4, 15)
E_x, E_y = e_x, cd_y      # (7, 15)
F_x, F_y = E_x, E_y + 2.5                     # 2.5mm ueber E
G_x, G_y = E_x + 2.5, E_y                     # 2.5mm rechts von E (original)
# D liegt exakt unterhalb von G, 8mm Abstand von A
D_x = G_x
D_y = A_y + math.sqrt(8**2 - (D_x - A_x)**2)
P_x, P_y = C_x, C_y + 1       # 1mm ueber C
Q_x, Q_y = C_x + 1, C_y       # 1mm rechts von C
Cs_x, Cs_y = Q_x, P_y         # C' = Spiegelung von C an Achse PQ = (5, 16.5)
# R und S: 0.5mm vor und nach E (gleicher Ansatz wie P/Q bei C)
R_x, R_y = E_x, E_y + 0.5    # 0.5mm ueber E (auf Linie F->E)
S_x, S_y = E_x - 0.5, E_y    # 0.5mm links von E (auf Linie Q->E)
# T und U: 0.5mm vor F (Rundung Gerade->Bogen)
T_x, T_y = F_x, F_y - 0.5   # 0.5mm unter F (auf Gerade R->F)
# U: 0.5mm vor F auf dem Bogen G->F (Bogen um E mit R2.5, F bei 90°)
# F ist bei 90° auf dem Kreis um E. 0.5mm davor (Richtung G) = etwas weniger als 90°
fillet_angle = 0.5 / 2.5     # Winkelinkrement fuer 0.5mm Bogenstrecke bei R2.5
U_angle = math.pi/2 - fillet_angle  # knapp unter 90°
U_x = E_x + 2.5 * math.cos(U_angle)
U_y = E_y + 2.5 * math.sin(U_angle)

# Schritt 1: Einfacher Schlitz (nur Hals, ohne Hinterschnitt)
slot_simple_top = box(-sw, cd_y, sw, 20.1)
all_simple = unary_union([
    slot_simple_top,
    affinity.rotate(slot_simple_top,  90, origin=(0, 0)),
    affinity.rotate(slot_simple_top, 180, origin=(0, 0)),
    affinity.rotate(slot_simple_top, 270, origin=(0, 0)),
])
profile = rounded.difference(all_simple)

# Schritt 2: R2 Verrundung bei B (Eintrittskante) -- C existiert noch nicht
profile = profile.buffer(-2, join_style=1).buffer(2, join_style=1)

# Schritt 3: Hinterschnitt -- A -> G -arc-> F -> E (Umweg ueber Viertelkreis)
# Kreisbogen F -> G um Mittelpunkt E, Radius |EG| = |EF| = 2.5
r_GF = math.sqrt((E_x - G_x)**2 + (E_y - G_y)**2)
angle_G_arc = math.atan2(G_y - E_y, G_x - E_x)  # 0 (rechts)
angle_F_arc = math.atan2(F_y - E_y, F_x - E_x)  # pi/2 (oben)
# Bogen von G nach F (gegen Uhrzeiger)
if angle_F_arc < angle_G_arc:
    angle_F_arc += 2 * math.pi
# Bogen endet bei U statt F (0.5mm kuerzer)
arc_GF_r = [(E_x + r_GF * math.cos(a), E_y + r_GF * math.sin(a))
            for a in np.linspace(angle_G_arc, U_angle, 12)]
# Gespiegelt fuer linke Seite
arc_GF_l = [(-x, y) for x, y in reversed(arc_GF_r)]

pts_top = []
pts_top.append((-P_x, P_y))         # P links (statt C links)
pts_top.append((-Q_x, Q_y))         # Q links
pts_top.append((-S_x, S_y))         # S links (statt E)
pts_top.append((-R_x, R_y))         # R links
pts_top.append((-T_x, T_y))         # T links (statt F)
pts_top.append((-U_x, U_y))         # U links (Bogenstart)
pts_top.extend(arc_GF_l)            # Bogen U -> G links
pts_top.append((-G_x, G_y))         # G links
pts_top.append((-D_x, D_y))         # D links
pts_top.append((-sw, sb))           # A links
pts_top.append(( sw, sb))           # A rechts
pts_top.append(( D_x, D_y))         # D rechts
pts_top.append(( G_x, G_y))         # G rechts
pts_top.extend(arc_GF_r)            # Bogen G -> U rechts
pts_top.append(( U_x, U_y))         # U rechts (Bogenende)
pts_top.append(( T_x, T_y))         # T rechts (statt F)
pts_top.append(( R_x, R_y))         # R rechts (statt E)
pts_top.append(( S_x, S_y))         # S rechts
pts_top.append(( Q_x, Q_y))         # Q rechts
pts_top.append(( P_x, P_y))         # P rechts (statt C rechts)

hinterschnitt_top = Polygon(pts_top)
from shapely.validation import make_valid
for angle in [0, 90, 180, 270]:
    h_rot = make_valid(affinity.rotate(hinterschnitt_top, angle, origin=(0, 0)))
    profile = make_valid(profile.difference(h_rot))

# 4) Bohrung
bore = Point(0, 0).buffer(6.8 / 2, resolution=64)
profile = profile.difference(bore)

# 5) Eck-Quadrate (Inseln, 6.5mm Seite, 3mm von Aussenkante)
POCKET_SIZE = 6.5
POCKET_OFFSET = 2.0  # von Aussenkante
POCKET_R_SMALL = 0.5
POCKET_R_BIG = 2.0

# Oben-rechts: Aussenkante bei (20, 20)
# Quadrat von (20-3-6.5, 20-3-6.5) bis (20-3, 20-3) = (10.5, 10.5) bis (17, 17)
def make_pocket(cx_sign, cy_sign):
    """Erzeugt ein Eck-Quadrat mit unterschiedlichen Radien."""
    # Ecke des Profils
    ex = cx_sign * 20
    ey = cy_sign * 20
    # Quadrat-Grenzen
    x_inner = ex - cx_sign * (POCKET_OFFSET + POCKET_SIZE)
    x_outer = ex - cx_sign * POCKET_OFFSET
    y_inner = ey - cy_sign * (POCKET_OFFSET + POCKET_SIZE)
    y_outer = ey - cy_sign * POCKET_OFFSET
    x1 = min(x_inner, x_outer)
    x2 = max(x_inner, x_outer)
    y1 = min(y_inner, y_outer)
    y2 = max(y_inner, y_outer)

    # Quadrat mit R0.5 an allen Ecken
    pocket = box(x1, y1, x2, y2)
    pocket = pocket.buffer(-POCKET_R_SMALL, join_style=1).buffer(POCKET_R_SMALL, join_style=1)

    # Aussere Ecke (nahe Profilecke) auf R2 vergroessern
    # Dazu: R2-Kreis an der Aussenecke, vereinigen, dann wieder R0.5 abziehen
    # Einfacher: nochmal mit R2 nur an der Aussenecke buffern
    # Besser: Quadrat mit R2 erzeugen, Aussenecke ausschneiden, vereinigen
    pocket_big = box(x1, y1, x2, y2)
    pocket_big = pocket_big.buffer(-POCKET_R_BIG, join_style=1).buffer(POCKET_R_BIG, join_style=1)

    # Kombination: R2-Quadrat in der Aussenecke, R0.5-Quadrat sonst
    # Schneide die Aussenecke aus dem R0.5-Quadrat und ersetze durch R2
    outer_corner_x = x2 if cx_sign > 0 else x1
    outer_corner_y = y2 if cy_sign > 0 else y1
    # Clip-Box fuer die Aussenecke
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    if cx_sign > 0 and cy_sign > 0:
        clip = box(mid_x, mid_y, x2 + 1, y2 + 1)
    elif cx_sign < 0 and cy_sign > 0:
        clip = box(x1 - 1, mid_y, mid_x, y2 + 1)
    elif cx_sign > 0 and cy_sign < 0:
        clip = box(mid_x, y1 - 1, x2 + 1, mid_y)
    else:
        clip = box(x1 - 1, y1 - 1, mid_x, mid_y)

    # Aussenecke aus R0.5 entfernen, aus R2 hinzufuegen
    pocket = pocket.difference(clip).union(pocket_big.intersection(clip))

    return pocket

for sx in [1, -1]:
    for sy in [1, -1]:
        pocket = make_pocket(sx, sy)
        profile = profile.difference(pocket)

# --- Kreisbogen-Radius fuer SVG-Export vorberechnen ---
S_x_m = (A_x + D_x) / 2
S_y_m = (A_y + D_y) / 2
n_x_m = math.cos(math.radians(135))
n_y_m = math.sin(math.radians(135))
M_x_c = S_x_m + 6 * n_x_m
M_y_c = S_y_m + 6 * n_y_m
r_arc_AD = math.sqrt((M_x_c - A_x)**2 + (M_y_c - A_y)**2)

# --- SVG-Export ---

def coords_to_svg_path(coords):
    """Konvertiert Shapely-Koordinaten zu SVG-Pfad.
    Erkennt D->A Paare (und gespiegelt) und ersetzt sie durch SVG-Arc."""
    pts = list(coords)
    d = f'M {pts[0][0]:.3f},{-pts[0][1]:.3f}'

    # Toleranz fuer Punkterkennung
    TOL = 0.1

    def is_near(p, ref_x, ref_y):
        return abs(p[0] - ref_x) < TOL and abs(p[1] - ref_y) < TOL

    # Alle 8 D/A-Paare (4 Rotationen x 2 Spiegelungen)
    # Fuer jede Rotation: D und A Koordinaten berechnen
    arc_pairs = []  # (von_pt, nach_pt, radius, sweep)
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        ca, sa = math.cos(rad), math.sin(rad)
        def rot(x, y):
            return (x*ca - y*sa, x*sa + y*ca)
        for sx in [1, -1]:
            d_pt = rot(sx * D_x, D_y)
            a_pt = rot(sx * A_x, A_y)
            p_pt = rot(sx * P_x, P_y)
            q_pt = rot(sx * Q_x, Q_y)
            # D/A Bogen (grosser Radius)
            arc_pairs.append((d_pt, a_pt, r_arc_AD, 1 if sx == 1 else 0))
            arc_pairs.append((a_pt, d_pt, r_arc_AD, 0 if sx == 1 else 1))
            # P/Q Bogen (R1 bei C)
            arc_pairs.append((q_pt, p_pt, 1.0, 1 if sx == 1 else 0))
            arc_pairs.append((p_pt, q_pt, 1.0, 0 if sx == 1 else 1))
            # R/S Bogen (R0.5 bei E)
            r_pt = rot(sx * R_x, R_y)
            s_pt = rot(sx * S_x, S_y)
            arc_pairs.append((s_pt, r_pt, 0.5, 0 if sx == 1 else 1))
            arc_pairs.append((r_pt, s_pt, 0.5, 1 if sx == 1 else 0))
            # T/U Bogen (R0.5 bei F, Gerade->Bogen Uebergang)
            t_pt = rot(sx * T_x, T_y)
            u_pt = rot(sx * U_x, U_y)
            arc_pairs.append((t_pt, u_pt, 0.5, 1 if sx == 1 else 0))
            arc_pairs.append((u_pt, t_pt, 0.5, 0 if sx == 1 else 1))

    for i in range(1, len(pts)):
        p = pts[i]
        prev = pts[i-1]
        replaced = False

        # D/A Bogen-Replacement
        for from_pt, to_pt, radius, sweep in arc_pairs:
            if is_near(prev, from_pt[0], from_pt[1]) and is_near(p, to_pt[0], to_pt[1]):
                d += f' A {radius:.3f},{radius:.3f} 0 0,{sweep} {p[0]:.3f},{-p[1]:.3f}'
                replaced = True
                break

        if not replaced:
            d += f' L {p[0]:.3f},{-p[1]:.3f}'

    return d + ' Z'

def profile_to_svg(geom, filepath, with_background=False, with_labels=True,
                   hatch_spacing=1.5, with_hatch=True):
    margin = 5
    vb = f'{-20-margin} {-20-margin} {40+2*margin} {40+2*margin}'

    from shapely.geometry import MultiPolygon as MP
    polys = list(geom.geoms) if isinstance(geom, MP) else [geom]
    paths = []
    for poly in polys:
        paths.append(coords_to_svg_path(poly.exterior.coords))
        for interior in poly.interiors:
            paths.append(coords_to_svg_path(interior.coords))
    combined_d = ' '.join(paths)

    bg_element = ''
    if with_background:
        import base64
        img_path = Path(__file__).resolve().parent.parent / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
        if img_path.exists():
            scale = 40.0 / 223.0
            img_x = -20 - 35 * scale
            img_y = -20 - 52 * scale
            img_w = 300 * scale
            img_h = 300 * scale
            b64 = base64.b64encode(img_path.read_bytes()).decode('ascii')
            bg_element = (
                f'  <image href="data:image/jpeg;base64,{b64}" '
                f'x="{img_x:.2f}" y="{img_y:.2f}" '
                f'width="{img_w:.2f}" height="{img_h:.2f}" '
                f'opacity="0.25"/>\n'
            )

    # Beschriftung
    labels_svg = ''
    dot_r = 0.3
    font_size = 1.1
    # M = Spitze gleichschenkliges Dreieck ADM, Hoehe 15 auf Basis AD, links ueber A
    S_x = (A_x + D_x) / 2
    S_y = (A_y + D_y) / 2
    n_x = math.cos(math.radians(135))
    n_y = math.sin(math.radians(135))
    M_x = S_x + 6 * n_x
    M_y = S_y + 6 * n_y

    points = [
        ('A', A_x, A_y),
        ('B', B_x, B_y),
        ('C', C_x, C_y),
        ('P', P_x, P_y),
        ('Q', Q_x, Q_y),
        ('D', D_x, D_y),
        ('E', E_x, E_y),
        ('F', F_x, F_y),
        ('G', G_x, G_y),
    ]
    for name, px, py in points:
        labels_svg += (
            f'  <circle cx="{px:.2f}" cy="{-py:.2f}" r="{dot_r}" '
            f'fill="blue" stroke="none"/>\n'
        )
        ox = 0.7 if px >= 0 else -0.7
        oy = 0.7 if py >= 0 else -0.7
        anchor = 'start' if px >= 0 else 'end'
        labels_svg += (
            f'  <text x="{px + ox:.2f}" y="{-(py + oy):.2f}" '
            f'font-size="{font_size}" font-family="sans-serif" '
            f'fill="blue" text-anchor="{anchor}">{name}</text>\n'
        )

    # Gruene Overlay-Linien entfernt -- Boegen sind jetzt in der roten Kontur
    arc_svg = ''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="{vb}" width="600" height="600">
{bg_element}  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="{hatch_spacing}" height="{hatch_spacing}"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="{hatch_spacing}" stroke="#888" stroke-width="0.15"/>
    </pattern>
  </defs>
  <path d="{combined_d}"
        fill="{'url(#hatch)' if with_hatch else 'none'}" stroke="red" stroke-width="0.2"
        fill-rule="evenodd"/>
{arc_svg}{labels_svg if with_labels else ''}</svg>'''

    Path(filepath).write_text(svg, encoding='utf-8')
    print(f"OK: {filepath}")

# Arbeitsversion (mit Punkten, einfache Schraffur)
profile_to_svg(profile, OUT / 'aufgabe01.svg')
profile_to_svg(profile, OUT / 'aufgabe01_overlay.svg', with_background=True)

# Dichtere Schraffur (doppelt), mit Punkten
profile_to_svg(profile, OUT / 'aufgabe01_dicht.svg', hatch_spacing=0.75)

# Final-Schnitt: dichte Schraffur, OHNE Punkte
profile_to_svg(profile, OUT / 'aufgabe01_Final-Schnitt.svg',
               hatch_spacing=0.75, with_labels=False)

# Path: nur Kontur, keine Schraffur, keine Punkte
profile_to_svg(profile, OUT / 'aufgabe01_path.svg',
               with_hatch=False, with_labels=False)
