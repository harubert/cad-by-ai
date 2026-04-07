"""
Aufgabe 04: Normgerechte Darstellungen einer quadratischen Pyramide.
  Basis: 50x50mm, Hoehe: 70mm, Spitze zentriert ueber Basis.
1) Schraegriss (Kavalierprojektion, 45 Grad, Verkuerzung 0.5)
2) Dreitafelprojektion (Grund-, Auf-, Kreuzriss)
Jeweils auf A4 Querformat mit Schriftfeld.
"""

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'

# Pyramiden-Parameter
BASE = 50    # mm Seitenlaenge
HALF = BASE / 2  # 25
HEIGHT = 70  # mm Hoehe

# === A4 Rahmen-Helfer ===
A4_W, A4_H = 297, 210
RAND_L, RAND_R, RAND_T, RAND_B = 20, 10, 10, 10
ZF_W = A4_W - RAND_L - RAND_R
ZF_H = A4_H - RAND_T - RAND_B
SF_W, SF_H = 180, 28
SF_X = A4_W - RAND_R - SF_W
SF_Y = A4_H - RAND_B - SF_H
DC = '#333'


def schriftfeld(titel, nr, massstab='1:1'):
    return f'''
<rect x="{SF_X}" y="{SF_Y}" width="{SF_W}" height="{SF_H}" fill="white" stroke="black" stroke-width="0.35"/>
<line x1="{SF_X}" y1="{SF_Y+10}" x2="{SF_X+SF_W}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+50}" y1="{SF_Y}" x2="{SF_X+50}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+100}" y1="{SF_Y}" x2="{SF_X+100}" y2="{SF_Y+SF_H}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+140}" y1="{SF_Y}" x2="{SF_X+140}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<text x="{SF_X+2}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Erstellt</text>
<text x="{SF_X+2}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Claude Code (KI)</text>
<text x="{SF_X+52}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Geprüft</text>
<text x="{SF_X+52}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Mensch</text>
<text x="{SF_X+102}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Maßstab</text>
<text x="{SF_X+102}" y="{SF_Y+8}" font-size="3.5" font-family="sans-serif" fill="black" font-weight="bold">{massstab}</text>
<text x="{SF_X+142}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Datum</text>
<text x="{SF_X+142}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">2026-04-01</text>
<text x="{SF_X+2}" y="{SF_Y+15}" font-size="2.5" font-family="sans-serif" fill="#666">Benennung</text>
<text x="{SF_X+2}" y="{SF_Y+22}" font-size="4.5" font-family="sans-serif" fill="black" font-weight="bold">{titel}</text>
<text x="{SF_X+102}" y="{SF_Y+15}" font-size="2.5" font-family="sans-serif" fill="#666">Zeichnungs-Nr.</text>
<text x="{SF_X+102}" y="{SF_Y+22}" font-size="4" font-family="sans-serif" fill="black" font-weight="bold">{nr}</text>
'''


def a4_rahmen():
    return f'''<rect x="0" y="0" width="{A4_W}" height="{A4_H}" fill="white" stroke="none"/>
<rect x="{RAND_L}" y="{RAND_T}" width="{ZF_W}" height="{ZF_H}" fill="none" stroke="black" stroke-width="0.5"/>
'''


# ================================================================
# Kavalierprojektion helper
# ================================================================
# Coordinate system: x right, y up (height), z towards viewer (depth)
# Base in x-z plane at y=0, apex at (0, HEIGHT, 0)
# Kavalier: screen_x = x + z * cos(45) * 0.5
#           screen_y = -(y + z * sin(45) * 0.5)   [SVG y inverted]

ANGLE = math.radians(45)
VERK = 0.5
COS45 = math.cos(ANGLE) * VERK  # ~0.3536
SIN45 = math.sin(ANGLE) * VERK  # ~0.3536


def project_kav(x, y, z):
    """Kavalierprojektion: 3D -> 2D screen coords (SVG y inverted)."""
    sx = x + z * COS45
    sy = -(y + z * SIN45)
    return (sx, sy)


# 3D corners of the pyramid
# Base corners (y=0): front-left, front-right, back-right, back-left
# "front" = z negative (closer to viewer), "back" = z positive
FL_3d = (-HALF, 0, -HALF)  # front-left
FR_3d = ( HALF, 0, -HALF)  # front-right
BR_3d = ( HALF, 0,  HALF)  # back-right
BL_3d = (-HALF, 0,  HALF)  # back-left
APEX_3d = (0, HEIGHT, 0)

# Project all points
FL = project_kav(*FL_3d)
FR = project_kav(*FR_3d)
BR = project_kav(*BR_3d)
BL = project_kav(*BL_3d)
APEX = project_kav(*APEX_3d)
BASE_CENTER = project_kav(0, 0, 0)

# ================================================================
# 1) SCHRAEGRISS
# ================================================================
SCALE_S = 1.0  # 1:1 scale

# Center the drawing in the available area (above title block)
draw_area_h = SF_Y - RAND_T - 5  # available height above title block
cx_s = RAND_L + ZF_W * 0.45
cy_s = RAND_T + draw_area_h * 0.55  # slightly below center to account for apex going up

# Build visible and hidden edges
visible_lines = ''
hidden_lines = ''
centerlines = ''

# Line helper
def svg_line(p1, p2, **kwargs):
    stroke = kwargs.get('stroke', 'black')
    sw = kwargs.get('stroke_width', '0.25')
    dash = kwargs.get('dash', '')
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{p1[0]:.3f}" y1="{p1[1]:.3f}" '
            f'x2="{p2[0]:.3f}" y2="{p2[1]:.3f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{extra}/>\n')


# Visible base edges: front-left to front-right, front-right to back-right,
# front-left to back-left (the three visible edges from this view angle)
# Hidden: back-left to back-right (the far edge hidden behind the body)
# For Kavalierprojektion with z going back-right at 45 deg:
#   Visible base: FL-FR (front), FR-BR (right side), BL-FL is left-front...
#   Actually all 4 base edges are visible since the base is at the bottom.
#   But the back-left edge (BL to BR going along the back) is partially hidden
#   by the pyramid body when viewed from front. Let's think:
#   - The base is on the ground, viewer looks from front.
#   - All 4 base edges are visible (the base is at bottom, nothing covers it).
#   - Wait: the back-left to back-right edge IS visible (the base sits on the ground plane).
#   - For lateral edges: FL->APEX, FR->APEX are clearly visible (front face).
#     BR->APEX: the right-back lateral edge is visible.
#     BL->APEX: the left-back lateral edge is hidden behind the front faces.

# Base edges - sichtbar: vorne (FL-FR) und rechts (FR-BR)
visible_lines += svg_line(FL, FR)
visible_lines += svg_line(FR, BR)
# Base edges - verdeckt: hinten (BR-BL) und links (BL-FL)
hidden_lines += svg_line(BR, BL, stroke='black', stroke_width='0.1', dash='1.5,0.8')
hidden_lines += svg_line(BL, FL, stroke='black', stroke_width='0.1', dash='1.5,0.8')

# Lateral edges
# Visible: FL->APEX, FR->APEX, BR->APEX
visible_lines += svg_line(FL, APEX)
visible_lines += svg_line(FR, APEX)
visible_lines += svg_line(BR, APEX)

# Hidden: BL->APEX (back-left lateral edge, hidden by the front triangular faces)
hidden_lines += svg_line(BL, APEX, stroke='black', stroke_width='0.1', dash='1.5,0.8')

# Centerlines: vertical from base center to apex, and base diagonals
centerlines += svg_line(BASE_CENTER, APEX, stroke='#C00', stroke_width='0.05', dash='2,0.4,0.3,0.4')
# Height line from apex down to base center (visible part as centerline)
centerlines += svg_line(BASE_CENTER, project_kav(0, 0, 0), stroke='#C00', stroke_width='0.05', dash='2,0.4,0.3,0.4')

# Base diagonals as centerlines
centerlines += svg_line(FL, BR, stroke='#C00', stroke_width='0.05', dash='2,0.4,0.3,0.4')
centerlines += svg_line(FR, BL, stroke='#C00', stroke_width='0.05', dash='2,0.4,0.3,0.4')

schraegriss_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  {a4_rahmen()}
  {schriftfeld('Pyramide 50x50, h=70 - Schrägriss', 'CAD-AI-005', '1:1')}
  <g transform="translate({cx_s:.1f},{cy_s:.1f}) scale({SCALE_S},{SCALE_S})">
    <!-- Centerlines -->
    {centerlines}
    <!-- Hidden edges -->
    {hidden_lines}
    <!-- Visible edges -->
    {visible_lines}
  </g>
</svg>'''

(OUT / 'aufgabe04_pyramide_schraegriss.svg').write_text(schraegriss_svg, encoding='utf-8')
print("OK: aufgabe04_pyramide_schraegriss.svg")


# ================================================================
# 2) DREITAFELPROJEKTION
# ================================================================
# Aufriss (front view, x-y plane): isosceles triangle, base 50 wide, height 70
# Grundriss (top view, x-z plane): square 50x50
# Kreuzriss (side view, z-y plane): isosceles triangle, base 50 wide, height 70
#
# Layout: Aufriss top-left, Grundriss bottom-left, Kreuzriss top-right
# Coordinate axes (red) separate the views

SCALE_D = 0.85

# Position the coordinate cross (origin where axes meet)
# We want the views close together with ~15mm gap
GAP = 12  # mm gap between views (half on each side of axis)

# Aufriss occupies: width=50, height=70 (scaled)
# Grundriss occupies: width=50, height=50 (scaled)
# Kreuzriss occupies: width=50, height=70 (scaled)

AR_W = BASE * SCALE_D   # 42.5
AR_H = HEIGHT * SCALE_D  # 59.5
GR_W = BASE * SCALE_D   # 42.5
GR_H = BASE * SCALE_D   # 42.5
KR_W = BASE * SCALE_D   # 42.5
KR_H = HEIGHT * SCALE_D  # 59.5

# The coordinate cross position
# Horizontal axis: separates Aufriss (above) from Grundriss (below)
# Vertical axis: separates Aufriss (left) from Kreuzriss (right)

# Place the cross so everything fits nicely
# Total width needed: AR_W/2 + GAP/2 + GAP/2 + KR_W/2 = ~42.5 + 12 + 42.5 = ~97
# Total height needed: AR_H + GAP/2 + GAP/2 + GR_H = ~59.5 + 12 + 42.5 = ~114

# Center in the drawing area (above title block)
draw_w = ZF_W
draw_h = SF_Y - RAND_T - 5
total_w = AR_W + GAP + KR_W
total_h = AR_H + GAP + GR_H

cross_x = RAND_L + (draw_w - total_w) / 2 + AR_W + GAP / 2
cross_y = RAND_T + (draw_h - total_h) / 2 + AR_H + GAP / 2

# View centers
# Aufriss: centered above and left of cross
AR_CX = cross_x - GAP / 2 - AR_W / 2  # center x of Aufriss base
# Aufriss base at cross_y - GAP/2, apex at cross_y - GAP/2 - AR_H
AR_BASE_Y = cross_y - GAP / 2  # bottom of Aufriss (base of pyramid)
AR_TOP_Y = AR_BASE_Y - AR_H    # top of Aufriss (apex)

# Grundriss: below cross, aligned with Aufriss x
GR_TOP_Y = cross_y + GAP / 2   # top of Grundriss
GR_CX = AR_CX + AR_W / 2       # center of Grundriss = center of Aufriss

# Kreuzriss: right of cross, aligned with Aufriss y
KR_LEFT_X = cross_x + GAP / 2  # left edge of Kreuzriss
KR_BASE_Y = AR_BASE_Y          # base aligned with Aufriss base

# Recenter: Aufriss left edge
AR_LEFT_X = cross_x - GAP / 2 - AR_W
AR_RIGHT_X = cross_x - GAP / 2

# === Build the three views ===
dreitafel_content = ''

# --- Aufriss (front view) ---
# Triangle: base from (-25,0) to (25,0), apex at (0,70) in object coords
# In SVG: base at AR_BASE_Y, left at AR_LEFT_X, right at AR_RIGHT_X
# Apex at center, AR_TOP_Y
ar_left = AR_LEFT_X
ar_right = AR_RIGHT_X
ar_base = AR_BASE_Y
ar_apex_x = (AR_LEFT_X + AR_RIGHT_X) / 2
ar_apex_y = AR_TOP_Y

# Visible outline: triangle
dreitafel_content += (f'<polygon points="{ar_left:.2f},{ar_base:.2f} '
                      f'{ar_right:.2f},{ar_base:.2f} '
                      f'{ar_apex_x:.2f},{ar_apex_y:.2f}" '
                      f'fill="none" stroke="black" stroke-width="0.25" stroke-linejoin="miter"/>\n')

# Height line (Mittellinie / centerline) - vertical from apex to base center
dreitafel_content += (f'<line x1="{ar_apex_x:.2f}" y1="{ar_apex_y - 3:.2f}" '
                      f'x2="{ar_apex_x:.2f}" y2="{ar_base + 3:.2f}" '
                      f'stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n')

# --- Grundriss (top view) ---
# Square 50x50 centered under Aufriss
gr_left = ar_apex_x - GR_W / 2
gr_right = ar_apex_x + GR_W / 2
gr_top = GR_TOP_Y
gr_bottom = GR_TOP_Y + GR_H

# Visible outline: square
dreitafel_content += (f'<rect x="{gr_left:.2f}" y="{gr_top:.2f}" '
                      f'width="{GR_W:.2f}" height="{GR_H:.2f}" '
                      f'fill="none" stroke="black" stroke-width="0.25"/>\n')

# Diagonals (sichtbar! - Seitenkanten der Pyramide von oben gesehen)
dreitafel_content += (f'<line x1="{gr_left:.2f}" y1="{gr_top:.2f}" '
                      f'x2="{gr_right:.2f}" y2="{gr_bottom:.2f}" '
                      f'stroke="black" stroke-width="0.2"/>\n')
dreitafel_content += (f'<line x1="{gr_right:.2f}" y1="{gr_top:.2f}" '
                      f'x2="{gr_left:.2f}" y2="{gr_bottom:.2f}" '
                      f'stroke="black" stroke-width="0.2"/>\n')

# Centerlines through the square
gr_cx = ar_apex_x
gr_cy = gr_top + GR_H / 2
dreitafel_content += (f'<line x1="{gr_cx:.2f}" y1="{gr_top - 3:.2f}" '
                      f'x2="{gr_cx:.2f}" y2="{gr_bottom + 3:.2f}" '
                      f'stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n')
dreitafel_content += (f'<line x1="{gr_left - 3:.2f}" y1="{gr_cy:.2f}" '
                      f'x2="{gr_right + 3:.2f}" y2="{gr_cy:.2f}" '
                      f'stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n')

# --- Kreuzriss (side view) ---
# Triangle: base 50 wide (depth axis), height 70
# Left edge at KR_LEFT_X, right at KR_LEFT_X + KR_W
# Base at KR_BASE_Y, apex at KR_BASE_Y - KR_H
kr_left = KR_LEFT_X
kr_right = KR_LEFT_X + KR_W
kr_base = KR_BASE_Y
kr_apex_x = (kr_left + kr_right) / 2
kr_apex_y = KR_BASE_Y - KR_H

# Visible outline: triangle
dreitafel_content += (f'<polygon points="{kr_left:.2f},{kr_base:.2f} '
                      f'{kr_right:.2f},{kr_base:.2f} '
                      f'{kr_apex_x:.2f},{kr_apex_y:.2f}" '
                      f'fill="none" stroke="black" stroke-width="0.25" stroke-linejoin="miter"/>\n')

# Height line (Mittellinie)
dreitafel_content += (f'<line x1="{kr_apex_x:.2f}" y1="{kr_apex_y - 3:.2f}" '
                      f'x2="{kr_apex_x:.2f}" y2="{kr_base + 3:.2f}" '
                      f'stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>\n')

# === Coordinate axes (red, solid) ===
axes = ''
# Vertical axis (separates Aufriss from Kreuzriss)
axes += (f'<line x1="{cross_x:.2f}" y1="{RAND_T + 2:.2f}" '
         f'x2="{cross_x:.2f}" y2="{SF_Y - 2:.2f}" '
         f'stroke="#C00" stroke-width="0.3"/>\n')
# Horizontal axis (separates Aufriss from Grundriss)
axes += (f'<line x1="{RAND_L + 2:.2f}" y1="{cross_y:.2f}" '
         f'x2="{A4_W - RAND_R - 2:.2f}" y2="{cross_y:.2f}" '
         f'stroke="#C00" stroke-width="0.3"/>\n')

# === Ordner (projection lines) - fine gray, solid ===
ordner_col = '#999'
ordner_w = '0.03'
ordner = ''

# Vertical Ordner: from Aufriss down to Grundriss
# Left edge, center, right edge of the triangle base / square
for x_pos in [ar_left, ar_apex_x, ar_right]:
    ordner += (f'<line x1="{x_pos:.2f}" y1="{ar_base + 1:.2f}" '
               f'x2="{x_pos:.2f}" y2="{gr_bottom + 2:.2f}" '
               f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# Also for the square top/bottom edges that align with Aufriss apex
# (The apex x-coord is the center, already drawn)

# Horizontal Ordner: from Aufriss right to Kreuzriss
# Base level, apex level
for y_pos in [ar_base, ar_apex_y]:
    ordner += (f'<line x1="{ar_right + 1:.2f}" y1="{y_pos:.2f}" '
               f'x2="{kr_right + 2:.2f}" y2="{y_pos:.2f}" '
               f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# Ordner from Aufriss triangle sides to Kreuzriss
# The Aufriss left/right base corners connect horizontally to Kreuzriss base
# Already covered by base level ordner

# === 45-degree quarter-circle Ordner (bottom-right, Grundriss z -> Kreuzriss z) ===
# These transfer the depth coordinates from Grundriss to Kreuzriss
# The arc center is at the cross intersection

# Grundriss edges that need transfer: top edge (gr_top) and bottom edge (gr_bottom)
# These map to Kreuzriss: left edge (kr_left) and right edge (kr_right)
for offset in [GR_H / 2, -GR_H / 2]:
    # Position in Grundriss (below cross)
    gr_y = cross_y + GAP / 2 + GR_H / 2 + offset  # actual y position
    # Radius from cross
    r = gr_y - cross_y
    if r > 0.5:
        # Corresponding position in Kreuzriss (right of cross)
        kr_x = cross_x + r  # same distance from cross

        # Horizontal line from Grundriss right edge to the vertical axis
        ordner += (f'<line x1="{gr_right + 1:.2f}" y1="{gr_y:.2f}" '
                   f'x2="{cross_x:.2f}" y2="{gr_y:.2f}" '
                   f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

        # Quarter-circle arc from (cross_x, gr_y) to (kr_x, cross_y)
        ordner += (f'<path d="M {cross_x:.2f},{gr_y:.2f} '
                   f'A {r:.2f},{r:.2f} 0 0,0 {kr_x:.2f},{cross_y:.2f}" '
                   f'fill="none" stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

        # Vertical line from arc end up to Kreuzriss
        ordner += (f'<line x1="{kr_x:.2f}" y1="{cross_y:.2f}" '
                   f'x2="{kr_x:.2f}" y2="{kr_apex_y - 2:.2f}" '
                   f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# Also transfer the center line
r_center = GR_H / 2 * SCALE_D / SCALE_D  # center of Grundriss
# Actually the center of the Grundriss is at gr_cy, distance from cross:
r_c = gr_cy - cross_y
if r_c > 0.5:
    kr_xc = cross_x + r_c
    ordner += (f'<line x1="{gr_right + 1:.2f}" y1="{gr_cy:.2f}" '
               f'x2="{cross_x:.2f}" y2="{gr_cy:.2f}" '
               f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')
    ordner += (f'<path d="M {cross_x:.2f},{gr_cy:.2f} '
               f'A {r_c:.2f},{r_c:.2f} 0 0,0 {kr_xc:.2f},{cross_y:.2f}" '
               f'fill="none" stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')
    ordner += (f'<line x1="{kr_xc:.2f}" y1="{cross_y:.2f}" '
               f'x2="{kr_xc:.2f}" y2="{kr_apex_y - 2:.2f}" '
               f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')


dreitafel_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  {a4_rahmen()}
  {schriftfeld('Pyramide 50x50, h=70 - Dreitafelprojektion', 'CAD-AI-005', '1:1.2')}
  <!-- Ordner (projection lines) -->
  {ordner}
  <!-- Coordinate axes -->
  {axes}
  <!-- Views -->
  {dreitafel_content}
</svg>'''

(OUT / 'aufgabe04_pyramide_dreitafel.svg').write_text(dreitafel_svg, encoding='utf-8')
print("OK: aufgabe04_pyramide_dreitafel.svg")
