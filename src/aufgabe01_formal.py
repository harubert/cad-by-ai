"""
Aufgabe 01: Technische Zeichnung mit vollstaendiger Bemassung.
Normen: EN ISO 128 (Linienarten), EN ISO 129-1 (Bemassung),
        EN ISO 128-50 (Schraffur Schnittdarstellung)
"""

import math
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from shapely.validation import make_valid
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'

# === Parameter ===
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
P_x, P_y = C_x, C_y + 1
Q_x, Q_y = C_x + 1, C_y
R_x, R_y = E_x, E_y + 0.5
S_x, S_y = E_x - 0.5, E_y
T_x, T_y = F_x, F_y - 0.5
fillet_angle = 0.5 / 2.5
U_angle = math.pi/2 - fillet_angle
U_x = E_x + 2.5 * math.cos(U_angle)
U_y = E_y + 2.5 * math.sin(U_angle)

# === Geometrie (identisch mit aufgabe01.py) ===
square = box(-20, -20, 20, 20)
rounded = square.buffer(-4.5, join_style=1).buffer(4.5, join_style=1)

slot_simple_top = box(-sw, cd_y, sw, 20.1)
all_simple = unary_union([
    slot_simple_top,
    affinity.rotate(slot_simple_top, 90, origin=(0,0)),
    affinity.rotate(slot_simple_top, 180, origin=(0,0)),
    affinity.rotate(slot_simple_top, 270, origin=(0,0)),
])
profile = rounded.difference(all_simple)
profile = profile.buffer(-2, join_style=1).buffer(2, join_style=1)

r_GF = 2.5
angle_G_arc = math.atan2(G_y - E_y, G_x - E_x)
arc_GF_r = [(E_x + r_GF * math.cos(a), E_y + r_GF * math.sin(a))
            for a in np.linspace(angle_G_arc, U_angle, 12)]
arc_GF_l = [(-x, y) for x, y in reversed(arc_GF_r)]

pts_top = []
pts_top.append((-P_x, P_y))
pts_top.append((-Q_x, Q_y))
pts_top.append((-S_x, S_y))
pts_top.append((-R_x, R_y))
pts_top.append((-T_x, T_y))
pts_top.append((-U_x, U_y))
pts_top.extend(arc_GF_l)
pts_top.append((-G_x, G_y))
pts_top.append((-D_x, D_y))
pts_top.append((-sw, sb))
pts_top.append((sw, sb))
pts_top.append((D_x, D_y))
pts_top.append((G_x, G_y))
pts_top.extend(arc_GF_r)
pts_top.append((U_x, U_y))
pts_top.append((T_x, T_y))
pts_top.append((R_x, R_y))
pts_top.append((S_x, S_y))
pts_top.append((Q_x, Q_y))
pts_top.append((P_x, P_y))

hinterschnitt_top = Polygon(pts_top)
for angle in [0, 90, 180, 270]:
    h_rot = make_valid(affinity.rotate(hinterschnitt_top, angle, origin=(0,0)))
    profile = make_valid(profile.difference(h_rot))

bore = Point(0, 0).buffer(6.8/2, resolution=64)
profile = profile.difference(bore)

POCKET_SIZE = 6.5
POCKET_OFFSET = 2.0

def make_pocket(cx_sign, cy_sign):
    ex, ey = cx_sign*20, cy_sign*20
    x_inner = ex - cx_sign*(POCKET_OFFSET+POCKET_SIZE)
    x_outer = ex - cx_sign*POCKET_OFFSET
    y_inner = ey - cy_sign*(POCKET_OFFSET+POCKET_SIZE)
    y_outer = ey - cy_sign*POCKET_OFFSET
    x1, x2 = min(x_inner,x_outer), max(x_inner,x_outer)
    y1, y2 = min(y_inner,y_outer), max(y_inner,y_outer)
    pocket = box(x1,y1,x2,y2).buffer(-0.5,join_style=1).buffer(0.5,join_style=1)
    pocket_big = box(x1,y1,x2,y2).buffer(-2,join_style=1).buffer(2,join_style=1)
    mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
    if cx_sign>0 and cy_sign>0: clip=box(mid_x,mid_y,x2+1,y2+1)
    elif cx_sign<0 and cy_sign>0: clip=box(x1-1,mid_y,mid_x,y2+1)
    elif cx_sign>0 and cy_sign<0: clip=box(mid_x,y1-1,x2+1,mid_y)
    else: clip=box(x1-1,y1-1,mid_x,mid_y)
    return pocket.difference(clip).union(pocket_big.intersection(clip))

for sx in [1,-1]:
    for sy in [1,-1]:
        profile = profile.difference(make_pocket(sx,sy))

# === SVG Arc Replacement ===
S_x_m = (A_x+D_x)/2
S_y_m = (A_y+D_y)/2
n_x_m = math.cos(math.radians(135))
n_y_m = math.sin(math.radians(135))
M_x_c = S_x_m + 6*n_x_m
M_y_c = S_y_m + 6*n_y_m
r_arc_AD = math.sqrt((M_x_c-A_x)**2+(M_y_c-A_y)**2)

def coords_to_svg_path(coords):
    pts = list(coords)
    d = f'M {pts[0][0]:.3f},{-pts[0][1]:.3f}'
    TOL = 0.1
    def is_near(p,rx,ry): return abs(p[0]-rx)<TOL and abs(p[1]-ry)<TOL
    arc_pairs = []
    for angle in [0,90,180,270]:
        rad = math.radians(angle)
        ca,sa = math.cos(rad),math.sin(rad)
        def rot(x,y): return (x*ca-y*sa, x*sa+y*ca)
        for sx in [1,-1]:
            d_pt,a_pt = rot(sx*D_x,D_y),rot(sx*A_x,A_y)
            p_pt,q_pt = rot(sx*P_x,P_y),rot(sx*Q_x,Q_y)
            r_pt,s_pt = rot(sx*R_x,R_y),rot(sx*S_x,S_y)
            t_pt,u_pt = rot(sx*T_x,T_y),rot(sx*U_x,U_y)
            arc_pairs.append((d_pt,a_pt,r_arc_AD,1 if sx==1 else 0))
            arc_pairs.append((a_pt,d_pt,r_arc_AD,0 if sx==1 else 1))
            arc_pairs.append((q_pt,p_pt,1.0,1 if sx==1 else 0))
            arc_pairs.append((p_pt,q_pt,1.0,0 if sx==1 else 1))
            arc_pairs.append((s_pt,r_pt,0.5,0 if sx==1 else 1))
            arc_pairs.append((r_pt,s_pt,0.5,1 if sx==1 else 0))
            arc_pairs.append((t_pt,u_pt,0.5,1 if sx==1 else 0))
            arc_pairs.append((u_pt,t_pt,0.5,0 if sx==1 else 1))
    for i in range(1,len(pts)):
        p=pts[i]; prev=pts[i-1]; replaced=False
        for from_pt,to_pt,radius,sweep in arc_pairs:
            if is_near(prev,from_pt[0],from_pt[1]) and is_near(p,to_pt[0],to_pt[1]):
                d+=f' A {radius:.3f},{radius:.3f} 0 0,{sweep} {p[0]:.3f},{-p[1]:.3f}'
                replaced=True; break
        if not replaced:
            d+=f' L {p[0]:.3f},{-p[1]:.3f}'
    return d+' Z'

from shapely.geometry import MultiPolygon as MP
polys = list(profile.geoms) if isinstance(profile, MP) else [profile]
paths = []
for poly in polys:
    paths.append(coords_to_svg_path(poly.exterior.coords))
    for interior in poly.interiors:
        paths.append(coords_to_svg_path(interior.coords))
combined_d = ' '.join(paths)

# === Bemassung ===
DC = '#333'
FS = 1.4  # Font-Size fuer Masszahlen
LW = 0.06  # Linienstaerke Masslinien

def _l(x1,y1,x2,y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{DC}" stroke-width="{LW}"/>\n'

def _al(x1,y1,x2,y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{DC}" stroke-width="{LW}" marker-start="url(#arr)" marker-end="url(#arr)"/>\n'

def _t(x,y,txt,anchor='middle',size=None,rot=0):
    fs = size or FS
    transform = f' transform="rotate({rot},{x:.2f},{y:.2f})"' if rot else ''
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{fs}" font-family="sans-serif" fill="{DC}" text-anchor="{anchor}"{transform}>{txt}</text>\n'

dim = ''
px1 = 20-2-6.5  # Pocket links
px2 = 20-2       # Pocket rechts
py_pocket = 20-2  # Pocket oben

# ================================================================
# OBEN: Gesamtbreite + Nutbreite + C-Tiefe (gestaffelt)
# ================================================================
# Gesamtbreite 40 (oberste Masslinie)
yo1 = -20-8
dim += _l(-20, -20-0.5, -20, yo1-1)
dim += _l(20, -20-0.5, 20, yo1-1)
dim += _al(-20, yo1, 20, yo1)
dim += _t(0, yo1-0.6, '40')

# Nutbreite 8 (zweite Masslinie, naeher)
yo2 = -20-4
dim += _l(-sw, -20-0.5, -sw, yo2-1)
dim += _l(sw, -20-0.5, sw, yo2-1)
dim += _al(-sw, yo2, sw, yo2)
dim += _t(0, yo2-0.6, '8')

# C-Tiefe 4.5 (oben, zwischen Nut und Ecke)
yo3 = -20-4
dim += _l(sw, -20-0.5, sw, yo3-1)
dim += _l(e_x, -cd_y-0.3, e_x, yo3-1)
dim += _al(sw, yo3, e_x, yo3)
dim += _t((sw+e_x)/2+2, yo3-0.6, '3', size=1.1)

# ================================================================
# RECHTS: Gesamthoehe + Nuttiefe + Hinterschnitt-Tiefe (gestaffelt)
# ================================================================
# Gesamthoehe 40 (aeusserste)
xo1 = 20+8
dim += _l(20+0.5, -20, xo1+1, -20)
dim += _l(20+0.5, 20, xo1+1, 20)
dim += _al(xo1, -20, xo1, 20)
dim += _t(xo1+1.5, 0.5, '40')

# Nuttiefe 12.5 (zweite Linie)
xo2 = 20+4.5
dim += _l(20+0.5, -20, xo2+0.5, -20)
dim += _l(sb-0.3, 0, xo2+0.5, -(20-SLOT_DEPTH))  # Nutboden
dim += _al(xo2, -20, xo2, -(20-SLOT_DEPTH))
dim += _t(xo2+1.2, -(20-SLOT_DEPTH/2)+0.5, '12,5', size=1.1)

# C-Tiefe 4.5 ab Oberkante (innerste)
xo3 = sw + 2.5
dim += _l(sw+0.3, -20, xo3+0.5, -20)
dim += _l(sw+0.3, -cd_y, xo3+0.5, -cd_y)
dim += _al(xo3, -20, xo3, -cd_y)
dim += _t(xo3-1.5, -(20-CD_DEPTH/2)+0.5, '4,5', size=1.1)

# ================================================================
# LINKS: Pocket-Masse (6.5 + 2)
# ================================================================
xo4 = -20-5
dim += _l(-20-0.5, -(20-2), xo4-1, -(20-2))
dim += _l(-20-0.5, -(20-2-6.5), xo4-1, -(20-2-6.5))
dim += _al(xo4, -(20-2), xo4, -(20-2-6.5))
dim += _t(xo4-1.2, -(20-2-3.25)+0.5, '6,5', size=1.1)

xo5 = -20-5
dim += _l(-20-0.5, -20, xo5-3.5, -20)
dim += _al(xo5-3, -(20-2), xo5-3, -20)
dim += _t(xo5-3-1.2, -(20-1)+0.5, '2', size=1.1)

# ================================================================
# UNTEN: Nutbreite der seitlichen Nut (zur Kontrolle)
# ================================================================
yo4 = 20+4
dim += _l(-sw, 20+0.5, -sw, yo4+1)
dim += _l(sw, 20+0.5, sw, yo4+1)
dim += _al(-sw, yo4, sw, yo4)
dim += _t(0, yo4-0.6, '8')

# ================================================================
# BOHRUNG (Durchmesser direkt im Kreis beschriften)
# ================================================================
dim += _t(0, 0.5, '\u00D86,8', size=1.2)

# ================================================================
# RADIEN (je 2 pro Ecke, schraege Hinweislinien nach aussen)
# ================================================================

# LINKS OBEN: R4.5 (Profilecke) + R2 (Eintrittskante)
dim += _l(-16, 16, -24, 24)           # R4.5 schraeg
dim += _l(-24, 24, -28, 24)
dim += _t(-28.5, 23.7, 'R4,5', size=1.1, anchor='end')

dim += _l(-sw-1, -18.5, -18, -24)     # R2 schraeg nach links unten
dim += _l(-18, -24, -28, -24)
dim += _t(-28.5, -24.3, 'R2', size=1.1, anchor='end')

# RECHTS OBEN: R1 (C) + R0.5 (F)
dim += _l(Q_x+0.5, -C_y+0.5, 18, -24)  # R1 schraeg nach rechts oben
dim += _l(18, -24, 28, -24)
dim += _t(28.5, -24.3, 'R1', size=1.1, anchor='start')

dim += _l(T_x+0.5, -T_y-0.5, 18, -27)  # R0.5 F schraeg
dim += _l(18, -27, 28, -27)
dim += _t(28.5, -27.3, 'R0,5', size=1.0, anchor='start')

# RECHTS MITTE: R2.5 (Bogen GF)
dim += _l(E_x+2, -(E_y+1.8), 22, -12)  # R2.5 schraeg
dim += _l(22, -12, 28, -12)
dim += _t(28.5, -12.3, 'R2,5', size=1.0, anchor='start')

# LINKS UNTEN: R0.5 (E, an linker Nut)
dim += _l(-cd_y-0.5, sw+0.5, -24, 18)  # schraeg nach links unten
dim += _l(-24, 18, -28, 18)
dim += _t(-28.5, 17.7, 'R0,5', size=1.0, anchor='end')

# RECHTS UNTEN: Pocket R0.5 (Innenecken) + R2 (Aussenecke)
dim += _l(px1+1, 20-2-1, 18, 24)        # R0.5 Pocket schraeg
dim += _l(18, 24, 28, 24)
dim += _t(28.5, 23.7, 'R0,5', size=0.9, anchor='start')

dim += _l(px2-0.5, 20-2+0.5, 18, 27)   # R2 Pocket schraeg
dim += _l(18, 27, 28, 27)
dim += _t(28.5, 26.7, 'R2', size=0.9, anchor='start')

# Mittellinien (Strichpunkt)
cl = ''
cl += f'<line x1="-26" y1="0" x2="26" y2="0" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n'
cl += f'<line x1="0" y1="-26" x2="0" y2="26" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n'

# Schriftfeld (altes, nicht mehr verwendet)
sf = f'''<g><!-- leer, Schriftfeld ist im A4-Rahmen -->
  <text x="17" y="25.7" font-size="1.3" font-family="sans-serif" fill="{DC}" text-anchor="middle" font-weight="bold">Alu-Strangpressprofil 40x40</text>
</g>
'''

# === A4 Zeichnungsrahmen (Querformat) ===
# A4 = 297 x 210 mm, Rand 10mm links (Heftrand 20mm), 10mm sonst
# Alles in mm, 1:1 Koordinaten
A4_W = 297
A4_H = 210
RAND_L = 20   # Heftrand links
RAND_R = 10
RAND_T = 10
RAND_B = 10

# Zeichenflaeche
ZF_X = RAND_L
ZF_Y = RAND_T
ZF_W = A4_W - RAND_L - RAND_R
ZF_H = A4_H - RAND_T - RAND_B

# Schriftfeld: rechts unten, 180mm breit, 30mm hoch (EN ISO 7200 vereinfacht)
SF_W = 180
SF_H = 32
SF_X = A4_W - RAND_R - SF_W
SF_Y = A4_H - RAND_B - SF_H

# Profil-Position: zentriert in der Zeichenflaeche (oberhalb Schriftfeld)
# Massstab 2:1 -> 40mm Profil wird 80mm gross
SCALE = 2.0
PROF_CX = ZF_X + ZF_W / 2
PROF_CY = ZF_Y + (ZF_H - SF_H) / 2

# SVG: y-Achse geht nach unten
def mm_to_svg(content_mm, cx, cy, scale):
    """Verpackt Inhalt in eine Gruppe mit Translation und Skalierung."""
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({scale},{scale})">\n'
            f'{content_mm}</g>\n')

# Profil-SVG (alles was bisher im inneren SVG war)
profil_inner = f'''  {cl}
  <path d="{combined_d}" fill="none" stroke="black" stroke-width="{0.2/SCALE}" fill-rule="evenodd"/>
  {dim}
'''

# Rahmen + Schriftfeld
rahmen = f'''<!-- A4 Rahmen -->
<rect x="0" y="0" width="{A4_W}" height="{A4_H}" fill="white" stroke="none"/>
<rect x="{RAND_L}" y="{RAND_T}" width="{ZF_W}" height="{ZF_H}"
      fill="none" stroke="black" stroke-width="0.5"/>
<!-- Aeusserer Schnittrand -->
<rect x="0" y="0" width="{A4_W}" height="{A4_H}"
      fill="none" stroke="#ccc" stroke-width="0.2"/>

<!-- Schriftfeld -->
<rect x="{SF_X}" y="{SF_Y}" width="{SF_W}" height="{SF_H}"
      fill="white" stroke="black" stroke-width="0.35"/>
<!-- Horizontale Trennlinien -->
<line x1="{SF_X}" y1="{SF_Y+10}" x2="{SF_X+SF_W}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X}" y1="{SF_Y+20}" x2="{SF_X+SF_W}" y2="{SF_Y+20}" stroke="black" stroke-width="0.2"/>
<!-- Vertikale Trennlinien (nur in Zeile 1, danach Benennung braucht Platz) -->
<line x1="{SF_X+50}" y1="{SF_Y}" x2="{SF_X+50}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+100}" y1="{SF_Y}" x2="{SF_X+100}" y2="{SF_Y+SF_H}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+140}" y1="{SF_Y}" x2="{SF_X+140}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>

<!-- Schriftfeld-Texte -->
<!-- Zeile 1: Kopfzeilen -->
<text x="{SF_X+2}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Erstellt</text>
<text x="{SF_X+52}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Geprueft</text>
<text x="{SF_X+102}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Norm</text>
<text x="{SF_X+142}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Datum</text>

<!-- Zeile 1: Werte -->
<text x="{SF_X+2}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Claude Code (KI)</text>
<text x="{SF_X+52}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Mensch</text>
<text x="{SF_X+102}" y="{SF_Y+8}" font-size="2.5" font-family="sans-serif" fill="black">EN ISO 128 / 129-1</text>
<text x="{SF_X+142}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">2026-04-01</text>

<!-- Zeile 2: Bezeichnung -->
<text x="{SF_X+2}" y="{SF_Y+13.5}" font-size="2.5" font-family="sans-serif" fill="#666">Benennung</text>
<text x="{SF_X+2}" y="{SF_Y+18}" font-size="4.5" font-family="sans-serif" fill="black" font-weight="bold">Alu-Strangpressprofil 40x40</text>

<!-- Zeile 2 rechts: Werkstoff + Massstab -->
<text x="{SF_X+102}" y="{SF_Y+13.5}" font-size="2.5" font-family="sans-serif" fill="#666">Werkstoff</text>
<text x="{SF_X+102}" y="{SF_Y+18}" font-size="3.5" font-family="sans-serif" fill="black">AlMgSi0,5</text>
<text x="{SF_X+142}" y="{SF_Y+13.5}" font-size="2.5" font-family="sans-serif" fill="#666">Massstab</text>
<text x="{SF_X+142}" y="{SF_Y+18}" font-size="3.5" font-family="sans-serif" fill="black" font-weight="bold">2:1 / 1:1</text>

<!-- Zeile 3: Zeichnungsnummer -->
<text x="{SF_X+2}" y="{SF_Y+23.5}" font-size="2.5" font-family="sans-serif" fill="#666">Zeichnungs-Nr.</text>
<text x="{SF_X+2}" y="{SF_Y+29}" font-size="5" font-family="sans-serif" fill="black" font-weight="bold">CAD-AI-001</text>
<text x="{SF_X+102}" y="{SF_Y+23.5}" font-size="2.5" font-family="sans-serif" fill="#666">Art.Nr.</text>
<text x="{SF_X+102}" y="{SF_Y+29}" font-size="4" font-family="sans-serif" fill="black">60800</text>
<text x="{SF_X+142}" y="{SF_Y+23.5}" font-size="2.5" font-family="sans-serif" fill="#666">Blatt</text>
<text x="{SF_X+142}" y="{SF_Y+29}" font-size="4" font-family="sans-serif" fill="black">1 / 1</text>
'''

# === 1:1 Schnittdarstellung mit Schraffur (rechts) ===
schnitt_inner = f'''
  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="0.75" height="0.75"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="0.75" stroke="#888" stroke-width="0.15"/>
    </pattern>
  </defs>
  <path d="{combined_d}" fill="url(#hatch)" stroke="black" stroke-width="0.25" fill-rule="evenodd"/>
  {cl}
'''

# 2:1 Ansicht links, 1:1 Schnitt rechts
# Zeichenflaeche nutzen: links 60%, rechts 40%
PROF_CX_LEFT = ZF_X + ZF_W * 0.38  # 2:1 bemasstm leicht links
PROF_CY_TOP = ZF_Y + (ZF_H - SF_H) / 2
SCHNITT_CX = ZF_X + ZF_W * 0.78     # 1:1 Schnitt rechts
SCHNITT_CY = PROF_CY_TOP

# Beschriftungen unter den Ansichten
view_labels = f'''
<text x="{PROF_CX_LEFT}" y="{PROF_CY_TOP + 28*SCALE}" font-size="4" font-family="sans-serif" fill="{DC}" text-anchor="middle" font-style="italic">Bemassung (M 2:1)</text>
<text x="{SCHNITT_CX}" y="{SCHNITT_CY + 28}" font-size="4" font-family="sans-serif" fill="{DC}" text-anchor="middle" font-style="italic">Schnitt A-A (M 1:1)</text>
'''

# === Zusammenbauen ===
svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  <defs>
    <marker id="arr" markerWidth="2.5" markerHeight="2" refX="1.25" refY="1"
            orient="auto" markerUnits="strokeWidth">
      <path d="M 0,0 L 2.5,1 L 0,2 Z" fill="{DC}"/>
    </marker>
  </defs>
  {rahmen}
  {mm_to_svg(profil_inner, PROF_CX_LEFT, PROF_CY_TOP, SCALE)}
  {mm_to_svg(schnitt_inner, SCHNITT_CX, SCHNITT_CY, 1.0)}
  {view_labels}
</svg>'''

(OUT / 'aufgabe01_path_formal.svg').write_text(svg, encoding='utf-8')
print("OK: aufgabe01_path_formal.svg")
