"""
Aufgabe 03: Normgerechte Darstellungen des Alu-Profils 40x40, 100mm hoch.
1) Schrägriss (Kavalierprojektion, 45 Grad, Verkuerzung 0.5)
2) Grund-, Auf- und Kreuzriss (Dreitafelprojektion)
Jeweils auf A4 Querformat mit Schriftfeld.
"""

import math
import numpy as np
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output'
SVG_FILE = OUT / 'aufgabe01_path.svg'

# Profil-Parameter
HOEHE = 100  # mm Extrusion
PROFIL_W = 40

# Profil-Punkte (aus aufgabe01)
sw = 4; sb = 7.5; cd_y = 15.5; e_x = 7
F_x, F_y = 7, 18; G_x, G_y = 9.5, 15.5
D_x = 9.5; D_y = 7.5 + math.sqrt(64 - 5.5**2)

# === Profil-Kontur aus SVG laden ===
svg_text = SVG_FILE.read_text(encoding='utf-8')
d_matches = re.findall(r'd="([^"]+)"', svg_text)
profil_d = max(d_matches, key=len)

# === A4 Rahmen-Helfer ===
A4_W, A4_H = 297, 210
RAND_L, RAND_R, RAND_T, RAND_B = 20, 10, 10, 10
ZF_W = A4_W - RAND_L - RAND_R
ZF_H = A4_H - RAND_T - RAND_B
SF_W, SF_H = 180, 28
SF_X = A4_W - RAND_R - SF_W
SF_Y = A4_H - RAND_B - SF_H
DC = '#333'

def schriftfeld(titel, nr, massstab='1:2'):
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
# 1) SCHRAEGRISS (Kavalierprojektion)
# ================================================================
# Kavalierprojektion: Frontansicht + 45-Grad-Tiefe mit Verkuerzung 0.5
# x' = x + z * cos(45) * 0.5
# y' = y + z * sin(45) * 0.5
# Profil liegt in x-y-Ebene, Extrusion geht in z-Richtung

SCALE_S = 0.8  # Darstellungsmassstab
ANGLE = 30
VERK = 0.5  # Verkuerzungsfaktor
dx_z = math.cos(math.radians(ANGLE)) * VERK  # x-Verschiebung pro z-Einheit
dy_z = -math.sin(math.radians(ANGLE)) * VERK  # y-Verschiebung (SVG y nach oben)

# Profil-Pfad transformieren: Vorder- und Hinterseite
def transform_path(d_string, z_offset):
    """Verschiebt einen SVG-Pfad um die Schraegriss-Projektion von z_offset."""
    ox = z_offset * dx_z
    oy = z_offset * dy_z
    # Alle Koordinaten im Pfad verschieben
    tokens = re.findall(r'[MLAZmlaz]|[-+]?\d*\.?\d+', d_string)
    result = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in 'MLAZ':
            result.append(t)
            i += 1
            if t in 'ML':
                x = float(tokens[i]) + ox
                y = float(tokens[i+1]) + oy
                result.append(f'{x:.3f}')
                result.append(f'{y:.3f}')
                i += 2
            elif t == 'A':
                # A rx ry rot large sweep x y
                result.append(tokens[i])    # rx
                result.append(tokens[i+1])  # ry
                result.append(tokens[i+2])  # rot
                result.append(tokens[i+3])  # large
                result.append(tokens[i+4])  # sweep
                x = float(tokens[i+5]) + ox
                y = float(tokens[i+6]) + oy
                result.append(f'{x:.3f}')
                result.append(f'{y:.3f}')
                i += 7
        else:
            result.append(t)
            i += 1
    return ' '.join(result)

# Vorderseite (z=0)
front_d = profil_d
# Hinterseite (z=100)
back_d = transform_path(profil_d, HOEHE)

# Schraegriss: Umhuellende Kanten
# Die aeussersten Verbindungslinien liegen an den 45-Grad-Tangentenpunkten der R4.5-Rundung
corner_lines = ''

# R4.5 Rundung: Mittelpunkte der 4 Viertelkreise
R_ECKE = 4.5
# Oben-rechts: Mitte bei (20-4.5, -(20-4.5)) = (15.5, -15.5) im SVG
# Tangentenpunkt bei 45 Grad (Schraegrichtung): Mitte + R * (cos(45+90), sin(45+90))
# = Mitte + R * (cos(135), sin(135)) = Mitte + R * (-0.707, 0.707)
# Das ist der aeusserste Punkt in 45-Grad-Schraegsicht
import math as m2
# Tangentenpunkte: Der aeusserste Punkt in Schraeg-Richtung liegt
# auf der Rundung in Richtung senkrecht zur Projektionsrichtung.
# Projektionsrichtung ist (cos(ANGLE), -sin(ANGLE)), also Normale dazu = (sin(ANGLE), cos(ANGLE))
# Obere Umhuellende: Tangentenpunkt in Richtung (sin, cos) vom Eckrundungs-Mittelpunkt
t_ang = m2.radians(ANGLE)
# Oben-rechts Ecke: Mitte bei (15.5, -15.5) im SVG
ecke_mitte_or = (20 - R_ECKE, -(20 - R_ECKE))
# Aeusserster Punkt: Mitte + R in Richtung (sin(30), -cos(30)) = (0.5, -0.866)
tang_or = (ecke_mitte_or[0] + R_ECKE * m2.sin(t_ang),
           ecke_mitte_or[1] - R_ECKE * m2.cos(t_ang))

# Unten-links: gespiegelt
ecke_mitte_ul = (-(20 - R_ECKE), (20 - R_ECKE))
tang_ul = (ecke_mitte_ul[0] - R_ECKE * m2.sin(t_ang),
           ecke_mitte_ul[1] + R_ECKE * m2.cos(t_ang))

# Obere Umhuellende (sichtbar, durchgezogen)
px, py = tang_or
x2 = px + HOEHE * dx_z
y2 = py + HOEHE * dy_z
corner_lines += f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="black" stroke-width="0.25"/>\n'

# Punkt H: Silhouette Eckbogen links oben (vorn -> hinten, sichtbar)
# Bei 30° Projektion liegt der Silhouettenpunkt bei 30° auf dem Bogen
H_x = -15.5 - R_ECKE * m2.sin(t_ang)
H_y = -(15.5 + R_ECKE * m2.cos(t_ang))
H_x2 = H_x + HOEHE * dx_z
H_y2 = H_y + HOEHE * dy_z
corner_lines += f'<line x1="{H_x:.2f}" y1="{H_y:.2f}" x2="{H_x2:.2f}" y2="{H_y2:.2f}" stroke="black" stroke-width="0.25"/>\n'

# Punkt H': Silhouette Eckbogen rechts unten (diagonal gegenüber, auch sichtbar)
H2_x = 15.5 + R_ECKE * m2.sin(t_ang)
H2_y = (15.5 + R_ECKE * m2.cos(t_ang))  # gespiegelt: positives y im SVG
H2_x2 = H2_x + HOEHE * dx_z
H2_y2 = H2_y + HOEHE * dy_z
corner_lines += f'<line x1="{H2_x:.2f}" y1="{H2_y:.2f}" x2="{H2_x2:.2f}" y2="{H2_y2:.2f}" stroke="black" stroke-width="0.25"/>\n'

R_B = 2  # R2-Eintrittskanten-Radius

# === Sichtbare Hinterkanten-Strecken (oben + rechts) ===
# Diese Strecken auf der Hinterseite sind sichtbar und muessen durchgezogen ueber
# die gestrichelte Hinterseite gezeichnet werden.

# Obere Kante Hinterseite: von linkem R4.5-Ende bis rechtem R4.5-Ende (y=-20, verschoben)
# Unterbrochen durch die Nut (x=-6 bis x=+6 wegen R2)
off_x = HOEHE * dx_z
off_y = HOEHE * dy_z
# Links: von -15.5 bis -(sw+R_B) = -6
corner_lines += f'<line x1="{-15.5 + off_x:.2f}" y1="{-20 + off_y:.2f}" x2="{-(sw+R_B) + off_x:.2f}" y2="{-20 + off_y:.2f}" stroke="black" stroke-width="0.2"/>\n'
# Rechts: von (sw+R_B)=6 bis 15.5
corner_lines += f'<line x1="{(sw+R_B) + off_x:.2f}" y1="{-20 + off_y:.2f}" x2="{15.5 + off_x:.2f}" y2="{-20 + off_y:.2f}" stroke="black" stroke-width="0.2"/>\n'

# Rechte Kante Hinterseite: von oberem R4.5-Ende bis unterem R4.5-Ende (x=20, verschoben)
# Unterbrochen durch die Nut (y=-6 bis y=+6 wegen R2)
# Oben: von -15.5 bis -(sw+R_B) = -6
corner_lines += f'<line x1="{20 + off_x:.2f}" y1="{-15.5 + off_y:.2f}" x2="{20 + off_x:.2f}" y2="{-(sw+R_B) + off_y:.2f}" stroke="black" stroke-width="0.2"/>\n'
# Unten: von (sw+R_B)=6 bis 15.5
corner_lines += f'<line x1="{20 + off_x:.2f}" y1="{(sw+R_B) + off_y:.2f}" x2="{20 + off_x:.2f}" y2="{15.5 + off_y:.2f}" stroke="black" stroke-width="0.2"/>\n'

# R2-Bogen auf der Hinterseite: von U (Silhouettenpunkt) bis zur oberen Kante
# U liegt bei Winkel (180+30)=210° vom R2-Mittelpunkt (gemessen von x-Achse)
# Obere Kante tangiert bei Winkel 270° (oben am Kreis, also y=-20)
# Bogen von U nach oben (zur oberen Geraden)
U_cx = (sw + R_B) + off_x  # R2-Mittelpunkt Hinterseite x
U_cy = -(20 - R_B) + off_y  # R2-Mittelpunkt Hinterseite y (SVG)
# U-Punkt
U_px = (sw + R_B) - R_B * m2.sin(t_ang) + off_x
U_py = -(20 - R_B) - R_B * m2.cos(t_ang) + off_y
# Endpunkt: Tangente an obere Gerade = (sw+R_B, -20) + offset
U_end_x = (sw + R_B) + off_x
U_end_y = -20 + off_y
corner_lines += f'<path d="M {U_px:.2f},{U_py:.2f} A {R_B},{R_B} 0 0,1 {U_end_x:.2f},{U_end_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# Hinterkanten-Rundungsboegen (R4.5, sichtbar): oben-rechts auf der Hinterseite
# Viertelkreis von (15.5, -20) nach (20, -15.5), verschoben
corner_lines += f'<path d="M {15.5+off_x:.2f},{-20+off_y:.2f} A {R_ECKE},{R_ECKE} 0 0,1 {20+off_x:.2f},{-15.5+off_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# R4.5-Bogen bei H auf der Hinterseite: vom Silhouettenpunkt bis zur oberen Kante
# H liegt links oben, Mittelpunkt (-15.5, -15.5 im SVG)
# Silhouettenpunkt H auf Hinterseite:
H_back_px = H_x + off_x
H_back_py = H_y + off_y
# Endpunkt: Tangente an obere Gerade y=-20 -> (-15.5, -20) + offset
H_end_x = -15.5 + off_x
H_end_y = -20 + off_y
corner_lines += f'<path d="M {H_back_px:.2f},{H_back_py:.2f} A {R_ECKE},{R_ECKE} 0 0,1 {H_end_x:.2f},{H_end_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# R4.5-Bogen bei H' auf der Hinterseite: vom Silhouettenpunkt bis zur rechten Geraden
# Silhouettenpunkt H' auf R4.5: Mittelpunkt (15.5, 15.5) + R4.5 in Richtung (sin30, cos30)
H2_back_px = H2_x + off_x  # H' verschoben auf Hinterseite
H2_back_py = H2_y + off_y
# Endpunkt: Tangente an rechte Gerade x=20 -> (20, 15.5) + offset
H2_end_x = 20 + off_x
H2_end_y = 15.5 + off_y
corner_lines += f'<path d="M {H2_back_px:.2f},{H2_back_py:.2f} A {R_ECKE},{R_ECKE} 0 0,0 {H2_end_x:.2f},{H2_end_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# Und auch vom Silhouettenpunkt H' bis zur unteren Geraden y=20
H2_end2_x = 15.5 + off_x
H2_end2_y = 20 + off_y
corner_lines += f'<path d="M {H2_back_px:.2f},{H2_back_py:.2f} A {R_ECKE},{R_ECKE} 0 0,1 {H2_end2_x:.2f},{H2_end2_y:.2f}" fill="none" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'

# === Gerade Aussenstrecken (Rundung bis Nut-Einschnitt) ===
# Obere Seite: von Ende R4.5 (bei x=±15.5, y=-20) bis R2-Tangente (x=±6, y=-20) -- sichtbar
for x1, x2_val in [(-15.5, -(sw+R_B)), (sw+R_B, 15.5)]:
    px1, py1 = x1, -20
    px2, py2 = x2_val, -20
    line_x1 = px1 + HOEHE * dx_z
    line_y1 = py1 + HOEHE * dy_z
    line_x2 = px2 + HOEHE * dx_z
    line_y2 = py2 + HOEHE * dy_z
    # Vorderkante ist schon im Profil-Pfad, nur Hinterkante zeichnen
    corner_lines += f'<line x1="{line_x1:.2f}" y1="{line_y1:.2f}" x2="{line_x2:.2f}" y2="{line_y2:.2f}" stroke="black" stroke-width="0.2"/>\n'

# Rechte Seite: von Ende R4.5 (bei x=20, y=±15.5) bis R2-Tangente (x=20, y=±6) -- sichtbar
for y1, y2_val in [(-15.5, -(sw+R_B)), (sw+R_B, 15.5)]:
    px1, py1 = 20, y1
    px2, py2 = 20, y2_val
    line_x1 = px1 + HOEHE * dx_z
    line_y1 = py1 + HOEHE * dy_z
    line_x2 = px2 + HOEHE * dx_z
    line_y2 = py2 + HOEHE * dy_z
    corner_lines += f'<line x1="{line_x1:.2f}" y1="{line_y1:.2f}" x2="{line_x2:.2f}" y2="{line_y2:.2f}" stroke="black" stroke-width="0.2"/>\n'

# Untere Seite: verdeckt (gestrichelt)
for x1, x2_val in [(-15.5, -(sw+R_B)), (sw+R_B, 15.5)]:
    px1, py1 = x1, 20
    px2, py2 = x2_val, 20
    line_x1 = px1 + HOEHE * dx_z
    line_y1 = py1 + HOEHE * dy_z
    line_x2 = px2 + HOEHE * dx_z
    line_y2 = py2 + HOEHE * dy_z
    corner_lines += f'<line x1="{line_x1:.2f}" y1="{line_y1:.2f}" x2="{line_x2:.2f}" y2="{line_y2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'

# Linke Seite: verdeckt (gestrichelt)
for y1, y2_val in [(-15.5, -(sw+R_B)), (sw+R_B, 15.5)]:
    px1, py1 = -20, y1
    px2, py2 = -20, y2_val
    line_x1 = px1 + HOEHE * dx_z
    line_y1 = py1 + HOEHE * dy_z
    line_x2 = px2 + HOEHE * dx_z
    line_y2 = py2 + HOEHE * dy_z
    corner_lines += f'<line x1="{line_x1:.2f}" y1="{line_y1:.2f}" x2="{line_x2:.2f}" y2="{line_y2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'

# === Nut-Einschnitte (Silhouette der R2-Zylinderfläche in 30°-Blickrichtung) ===
# Der Silhouettenpunkt liegt auf dem R2-Kreis senkrecht zur Projektionsrichtung
# Projektionsrichtung: (cos30, -sin30), Normale dazu: (-sin30, -cos30) und (sin30, cos30)
# R2-Kreismittelpunkt bei oberer rechter Nut: (sw+R_B, -(20-R_B)) = (6, -18) im SVG

# Fuer jede der 4 Nuten: Silhouettenpunkt auf dem R2-Bogen berechnen
# Obere Nut, rechte B-Rundung: Mitte (sw+R_B, -(20-R_B))
# Silhouettenpunkt: Mitte + R_B * (-sin30, -cos30) = Richtung nach links-unten (in Geo)
# In SVG: Mitte + R_B * (-sin30, cos30) [y invertiert]
sin30 = m2.sin(t_ang)
cos30 = m2.cos(t_ang)

# Obere Nut: 2 B-Punkte (links und rechts)
for sign_x in [-1, 1]:
    # Kreismittelpunkt der R2-Rundung
    cx_r2 = sign_x * (sw + R_B)  # ±6
    cy_r2 = -(20 - R_B)          # -18 im SVG
    # Silhouettenpunkt: senkrecht zur Blickrichtung
    # Blickrichtung in SVG: (cos30, -sin30), Normale: (sin30, cos30)
    # Der Punkt auf der Außenseite (weg vom Betrachter)
    sx_pt = cx_r2 - sign_x * R_B * sin30
    sy_pt = cy_r2 - R_B * cos30
    sx2 = sx_pt + HOEHE * dx_z
    sy2 = sy_pt + HOEHE * dy_z
    corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.2"/>\n'

# Rechte Nut: Silhouettenpunkte auf R2 in 30-Grad-Blickrichtung
# R2-Mittelpunkte: (18, ±6)
# Tangente in 30°: Mitte + R2 * (cos30, ±sin30) -- nach aussen (rechts)
for sign_y in [-1, 1]:
    cx_r2 = 20 - R_B              # 18
    cy_r2 = sign_y * (sw + R_B)   # ±6
    # Silhouettenpunkt: nach rechts-aussen
    sx_pt = cx_r2 + R_B * cos30   # 18 + 1.73 = 19.73
    sy_pt = cy_r2 + sign_y * R_B * sin30  # ±(6 + 1) = ±7

    # Sichtbar bis zur rechten Wand (x=20)
    if dx_z != 0:
        z_hidden = (20 - sx_pt) / dx_z
        if z_hidden > 0 and z_hidden < HOEHE:
            vis_end_x = 20
            vis_end_y = sy_pt + z_hidden * dy_z
            # Durchgezogen bis Profilkante
            corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{vis_end_x:.2f}" y2="{vis_end_y:.2f}" stroke="black" stroke-width="0.2"/>\n'
            # Gestrichelt dahinter
            sx2 = sx_pt + HOEHE * dx_z
            sy2 = sy_pt + HOEHE * dy_z
            corner_lines += f'<line x1="{vis_end_x:.2f}" y1="{vis_end_y:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'
        else:
            sx2 = sx_pt + HOEHE * dx_z
            sy2 = sy_pt + HOEHE * dy_z
            corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.2"/>\n'

    # R2-Bogen vom Silhouettenpunkt zur rechten Geraden (x=20)
    bogen_end_x = 20
    bogen_end_y = cy_r2  # Tangentenpunkt an x=20
    sweep = "1" if sign_y < 0 else "0"
    corner_lines += f'<path d="M {sx_pt:.2f},{sy_pt:.2f} A {R_B},{R_B} 0 0,{sweep} {bogen_end_x:.2f},{bogen_end_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# Untere Nut: verdeckt
for sign_x in [-1, 1]:
    cx_r2 = sign_x * (sw + R_B)
    cy_r2 = 20 - R_B              # +18
    sx_pt = cx_r2 - sign_x * R_B * sin30
    sy_pt = cy_r2 + R_B * cos30
    sx2 = sx_pt + HOEHE * dx_z
    sy2 = sy_pt + HOEHE * dy_z
    corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'

# Linke Nut: Silhouettenlinie -- erst sichtbar (bis Profil verdeckt), dann gestrichelt
for sign_y in [-1, 1]:
    cx_r2 = -(20 - R_B)           # -18
    cy_r2 = sign_y * (sw + R_B)   # ±6
    # Silhouettenpunkt: senkrecht zur 30°-Blickrichtung, nach aussen (links)
    sx_pt = cx_r2 - R_B * sin30   # -19
    sy_pt = cy_r2 - R_B * cos30 * sign_y  # ±4.27

    # Die Linie wird verdeckt, sobald sie hinter die Aussenwand (x=-20) taucht
    # Bei x=-20: wie viel Tiefe z braucht man?
    # sx_pt + z * dx_z = -20  -> z = (-20 - sx_pt) / dx_z
    if dx_z != 0:
        z_hidden = (-20 - sx_pt) / dx_z
        # Sichtbarer Teil: von sx_pt bis z_hidden
        vis_end_x = sx_pt + z_hidden * dx_z  # = -20
        vis_end_y = sy_pt + z_hidden * dy_z
        # Durchgezogen: sichtbarer Teil
        corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{vis_end_x:.2f}" y2="{vis_end_y:.2f}" stroke="black" stroke-width="0.2"/>\n'
        # Gestrichelt: verdeckter Rest
        sx2 = sx_pt + HOEHE * dx_z
        sy2 = sy_pt + HOEHE * dy_z
        corner_lines += f'<line x1="{vis_end_x:.2f}" y1="{vis_end_y:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'
    else:
        sx2 = sx_pt + HOEHE * dx_z
        sy2 = sy_pt + HOEHE * dy_z
        corner_lines += f'<line x1="{sx_pt:.2f}" y1="{sy_pt:.2f}" x2="{sx2:.2f}" y2="{sy2:.2f}" stroke="black" stroke-width="0.12" stroke-dasharray="1,0.5"/>\n'

    # Sichtbarer R2-Bogen: vom Silhouettenpunkt bis zur linken Geraden (x=-20)
    bogen_end_x = -20
    bogen_end_y = cy_r2
    sweep = "0" if sign_y > 0 else "1"
    corner_lines += f'<path d="M {sx_pt:.2f},{sy_pt:.2f} A {R_B},{R_B} 0 0,{sweep} {bogen_end_x:.2f},{bogen_end_y:.2f}" fill="none" stroke="black" stroke-width="0.2"/>\n'

# Untere Umhuellende (verdeckt, gestrichelt)
px, py = tang_ul
x2 = px + HOEHE * dx_z
y2 = py + HOEHE * dy_z
corner_lines += f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="black" stroke-width="0.15" stroke-dasharray="1,0.5"/>\n'

# Zentrierung auf dem Blatt
cx_s = RAND_L + ZF_W * 0.45
cy_s = RAND_T + (ZF_H - SF_H) * 0.5

schraegriss_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  {a4_rahmen()}
  {schriftfeld('Alu-Profil 40x40 - Schrägriss', 'CAD-AI-003', '1:1.25')}
  <g transform="translate({cx_s},{cy_s}) scale({SCALE_S},{SCALE_S})">
    <!-- Hinterseite (gestrichelt) -->
    <path d="{back_d}" fill="none" stroke="#999" stroke-width="0.15" stroke-dasharray="1,0.5" fill-rule="evenodd"/>
    <!-- Verbindungslinien -->
    {corner_lines}
    <!-- Vorderseite -->
    <path d="{front_d}" fill="none" stroke="black" stroke-width="0.25" fill-rule="evenodd"/>
    <!-- Punktbeschriftungen an der Vorderflaeche (nur rechte Seite obere Nut) -->
    <!-- Punkt H: Mitte des Eckbogens links oben -->
    <circle cx="{H_x:.2f}" cy="{H_y:.2f}" r="0.4" fill="blue"/>
    <text x="{H_x - 1.5:.2f}" y="{H_y - 0.5:.2f}" font-size="1.5" fill="blue" font-family="sans-serif">H</text>
    <!-- Punkt H': Silhouette Eckbogen rechts unten -->
    <circle cx="{H2_x:.2f}" cy="{H2_y:.2f}" r="0.4" fill="blue"/>
    <text x="{H2_x + 1:.2f}" y="{H2_y + 0.5:.2f}" font-size="1.5" fill="blue" font-family="sans-serif">H'</text>
    <!-- Punkt V: Silhouettenpunkt R2 rechte Nut unten -->
    <circle cx="{20 - R_B + R_B * cos30:.2f}" cy="{(sw+R_B) + R_B * sin30:.2f}" r="0.3" fill="blue"/>
    <text x="{20 - R_B + R_B * cos30 + 0.8:.2f}" y="{(sw+R_B) + R_B * sin30 + 0.8:.2f}" font-size="1.2" fill="blue" font-family="sans-serif">V</text>
    <!-- Rote Punkte: Anfangspunkte der gestrichelten (verdeckten) Linien -->
    <!-- Untere Nut: x=±4, y=+20 -->
    <circle cx="-{sw}" cy="20" r="0.3" fill="red"/>
    <text x="-{sw+1.2}" y="20.8" font-size="1.2" fill="red" font-family="sans-serif">I</text>
    <circle cx="{sw}" cy="20" r="0.3" fill="red"/>
    <text x="{sw+0.5}" y="20.8" font-size="1.2" fill="red" font-family="sans-serif">J</text>
    <!-- Linke Nut: x=-20, y=±4 -->
    <circle cx="-20" cy="-{sw}" r="0.3" fill="red"/>
    <text x="-21.5" y="-{sw+0.3}" font-size="1.2" fill="red" font-family="sans-serif">K</text>
    <circle cx="{-(20-R_B) - R_B * sin30:.2f}" cy="{(sw+R_B) - R_B * cos30:.2f}" r="0.3" fill="red"/>
    <text x="{-(20-R_B) - R_B * sin30 - 1.5:.2f}" y="{(sw+R_B) - R_B * cos30 + 0.8:.2f}" font-size="1.2" fill="red" font-family="sans-serif">L</text>
    <!-- Punkt X: Schnittpunkt der Silhouettenlinie von L mit der Vorderflaechenkontur -->
    <circle cx="-20" cy="4.85" r="0.3" fill="red"/>
    <text x="-21.5" y="5.5" font-size="1.2" fill="red" font-family="sans-serif">X</text>
    <!-- Untere Aussenstrecken: x=±15.5, y=+20 -->
    <circle cx="-15.5" cy="20" r="0.3" fill="red"/>
    <text x="-17" y="21" font-size="1.2" fill="red" font-family="sans-serif">M</text>
    <circle cx="15.5" cy="20" r="0.3" fill="red"/>
    <text x="16" y="21" font-size="1.2" fill="red" font-family="sans-serif">N</text>
    <!-- Linke Aussenstrecken: x=-20, y=±15.5 -->
    <circle cx="-20" cy="-15.5" r="0.3" fill="red"/>
    <text x="-21.5" y="-15" font-size="1.2" fill="red" font-family="sans-serif">O</text>
    <circle cx="-20" cy="15.5" r="0.3" fill="red"/>
    <text x="-21.5" y="16" font-size="1.2" fill="red" font-family="sans-serif">P</text>
    <!-- Untere Umhuellende -->
    <circle cx="{tang_ul[0]:.2f}" cy="{tang_ul[1]:.2f}" r="0.3" fill="red"/>
    <text x="{tang_ul[0]-1.5:.2f}" y="{tang_ul[1]+1:.2f}" font-size="1.2" fill="red" font-family="sans-serif">Q</text>
    <circle cx="{sw}" cy="{-sb}" r="0.4" fill="blue"/>
    <text x="{sw+1}" y="{-sb+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">A</text>
    <circle cx="{sw}" cy="-20" r="0.4" fill="blue"/>
    <text x="{sw+1}" y="-19.5" font-size="1.5" fill="blue" font-family="sans-serif">B</text>
    <circle cx="{sw}" cy="{-cd_y}" r="0.4" fill="blue"/>
    <text x="{sw+1}" y="{-cd_y+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">C</text>
    <circle cx="{D_x}" cy="{-D_y}" r="0.4" fill="blue"/>
    <text x="{D_x+1}" y="{-D_y+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">D</text>
    <circle cx="{e_x}" cy="{-cd_y}" r="0.4" fill="blue"/>
    <text x="{e_x+1}" y="{-cd_y+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">E</text>
    <circle cx="{F_x}" cy="{-F_y}" r="0.4" fill="blue"/>
    <text x="{F_x+1}" y="{-F_y+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">F</text>
    <circle cx="{G_x}" cy="{-G_y}" r="0.4" fill="blue"/>
    <text x="{G_x+1}" y="{-G_y+0.5}" font-size="1.5" fill="blue" font-family="sans-serif">G</text>
  </g>
</svg>'''

(OUT / 'aufgabe03_schraegriss.svg').write_text(schraegriss_svg, encoding='utf-8')
print("OK: aufgabe03_schraegriss.svg")

# ================================================================
# 2) DREITAFELPROJEKTION (Grund-, Auf-, Kreuzriss)
# ================================================================
# Aufriss = Vorderansicht (x-y) = Profil-Querschnitt
# Grundriss = Draufsicht (x-z) = Rechteck 40 x 100 mit Nuten
# Kreuzriss = Seitenansicht (z-y) = Rechteck 100 x 40 mit Nuten

SCALE_D = 0.7  # kleiner, damit alles auf ein Blatt passt

# Aufriss-Position (links oben)
AR_CX = RAND_L + 50
AR_CY = RAND_T + 45

# Abstände: max 20mm (skaliert)
ABSTAND = 15  # mm zwischen den Rissen

# Grundriss-Position (unter Aufriss)
GR_CX = AR_CX
GR_CY = AR_CY + 20 * SCALE_D + ABSTAND

# Kreuzriss-Position (rechts neben Aufriss)
KR_CX = AR_CX + 20 * SCALE_D + ABSTAND
KR_CY = AR_CY

# Grundriss: Rechteck 40 x 100 mit Nuten + verdeckte Kanten
BORE_R = 3.4
PK_OFF = 2.0
PK_SIZE = 6.5
grundriss = f'''
<rect x="-20" y="0" width="40" height="{HOEHE}" fill="none" stroke="black" stroke-width="0.25"/>
<!-- Nuten links und rechts (durchgehend, sichtbar) -->
<line x1="-4" y1="0" x2="-4" y2="{HOEHE}" stroke="black" stroke-width="0.15"/>
<line x1="4" y1="0" x2="4" y2="{HOEHE}" stroke="black" stroke-width="0.15"/>
<!-- Bohrung (verdeckt, gestrichelt) -->
<line x1="-{BORE_R}" y1="0" x2="-{BORE_R}" y2="{HOEHE}" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<line x1="{BORE_R}" y1="0" x2="{BORE_R}" y2="{HOEHE}" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Pockets (verdeckt, gestrichelt) - links -->
<rect x="-{20-PK_OFF}" y="0" width="{PK_SIZE}" height="{HOEHE}" fill="none" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Pockets - rechts -->
<rect x="{20-PK_OFF-PK_SIZE}" y="0" width="{PK_SIZE}" height="{HOEHE}" fill="none" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Innere Kanten (verdeckt): Hinterschnitt, Boegen -->
<line x1="-{7.0}" y1="0" x2="-{7.0}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="{7.0}" y1="0" x2="{7.0}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="-{9.5}" y1="0" x2="-{9.5}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="{9.5}" y1="0" x2="{9.5}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="-{5.0}" y1="0" x2="-{5.0}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="{5.0}" y1="0" x2="{5.0}" y2="{HOEHE}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<!-- Mittellinie -->
<line x1="0" y1="-3" x2="0" y2="{HOEHE+3}" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
<line x1="-23" y1="{HOEHE/2}" x2="23" y2="{HOEHE/2}" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
'''

# Kreuzriss: Rechteck 100 x 40 + verdeckte Kanten
kreuzriss = f'''
<rect x="0" y="-20" width="{HOEHE}" height="40" fill="none" stroke="black" stroke-width="0.25"/>
<!-- Nuten oben und unten (sichtbar) -->
<line x1="0" y1="-4" x2="{HOEHE}" y2="-4" stroke="black" stroke-width="0.15"/>
<line x1="0" y1="4" x2="{HOEHE}" y2="4" stroke="black" stroke-width="0.15"/>
<!-- Bohrung (verdeckt, gestrichelt) -->
<line x1="0" y1="-{BORE_R}" x2="{HOEHE}" y2="-{BORE_R}" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<line x1="0" y1="{BORE_R}" x2="{HOEHE}" y2="{BORE_R}" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Pockets (verdeckt, gestrichelt) - oben -->
<rect x="0" y="-{20-PK_OFF}" width="{HOEHE}" height="{PK_SIZE}" fill="none" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Pockets - unten -->
<rect x="0" y="{20-PK_OFF-PK_SIZE}" width="{HOEHE}" height="{PK_SIZE}" fill="none" stroke="black" stroke-width="0.1" stroke-dasharray="1,0.5"/>
<!-- Innere Kanten (verdeckt): Hinterschnitt, Boegen -->
<line x1="0" y1="-{7.0}" x2="{HOEHE}" y2="-{7.0}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="0" y1="{7.0}" x2="{HOEHE}" y2="{7.0}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="0" y1="-{9.5}" x2="{HOEHE}" y2="-{9.5}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="0" y1="{9.5}" x2="{HOEHE}" y2="{9.5}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="0" y1="-{5.0}" x2="{HOEHE}" y2="-{5.0}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<line x1="0" y1="{5.0}" x2="{HOEHE}" y2="{5.0}" stroke="black" stroke-width="0.08" stroke-dasharray="0.8,0.4"/>
<!-- Mittellinie -->
<line x1="-3" y1="0" x2="{HOEHE+3}" y2="0" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
<line x1="{HOEHE/2}" y1="-23" x2="{HOEHE/2}" y2="23" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
'''

# Aufriss: Profil-Querschnitt (mit Schraffur)
aufriss = f'''
<defs>
  <pattern id="hatch3" patternUnits="userSpaceOnUse" width="0.75" height="0.75" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="0.75" stroke="#888" stroke-width="0.12"/>
  </pattern>
</defs>
<path d="{profil_d}" fill="url(#hatch3)" stroke="black" stroke-width="0.25" fill-rule="evenodd"/>
<!-- Mittellinien -->
<line x1="-23" y1="0" x2="23" y2="0" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
<line x1="0" y1="-23" x2="0" y2="23" stroke="#C00" stroke-width="0.05" stroke-dasharray="2,0.4,0.3,0.4"/>
'''

# === Koordinatenachsen (durchgezogene rote Linien, trennen die Risse) ===
# Vertikale Achse: zwischen Aufriss und Kreuzriss (y-Achse / x_Achse Kreuzriss)
achse_x = AR_CX + 20 * SCALE_D + ABSTAND / 2  # Mitte zwischen Aufriss und Kreuzriss
# Horizontale Achse: zwischen Aufriss und Grundriss
achse_y = AR_CY + 20 * SCALE_D + ABSTAND / 2  # Mitte zwischen Aufriss und Grundriss

proj_lines = ''
# Vertikale Trennlinie (geht von oben bis unten durch)
proj_lines += f'<line x1="{achse_x}" y1="{RAND_T+2}" x2="{achse_x}" y2="{SF_Y-2}" stroke="#C00" stroke-width="0.3"/>\n'
# Horizontale Trennlinie
proj_lines += f'<line x1="{RAND_L+2}" y1="{achse_y}" x2="{A4_W-RAND_R-2}" y2="{achse_y}" stroke="#C00" stroke-width="0.3"/>\n'

# Achsenbeschriftung
proj_lines += f'<text x="{achse_x-3}" y="{RAND_T+6}" font-size="3" fill="#C00" font-family="sans-serif">y</text>\n'
proj_lines += f'<text x="{RAND_L+3}" y="{achse_y-2}" font-size="3" fill="#C00" font-family="sans-serif">x</text>\n'

# === Ordner / Zuordnungslinien (feine durchgezogene Linien) ===
ordner_col = '#999'
ordner_w = '0.03'

# Vertikale Ordner: vom Aufriss nach unten zum Grundriss
# Sichtbare Kanten + verdeckte Kanten (Bohrung, Pockets)
BORE_R_val = 3.4
PK_OFF_val = 2.0
PK_SIZE_val = 6.5
E_x_val = 7.0
G_x_val = 9.5
Q_x_val = 5.0
# Alle x-Koordinaten an denen im Querschnitt Kanten liegen
all_x_edges = sorted(set([
    -20, -4, 0, 4, 20,                          # Aussen + Nuten
    -BORE_R_val, BORE_R_val,                     # Bohrung
    -(20-PK_OFF_val), -(20-PK_OFF_val-PK_SIZE_val),  # Pockets links
    (20-PK_OFF_val), (20-PK_OFF_val-PK_SIZE_val),    # Pockets rechts
    -E_x_val, E_x_val,                          # Hinterschnitt E
    -G_x_val, G_x_val,                          # Hinterschnitt G/D
    -Q_x_val, Q_x_val,                          # C-Rundung Q
]))
for x in all_x_edges:
    x_pos = AR_CX + x * SCALE_D
    proj_lines += (f'<line x1="{x_pos}" y1="{AR_CY - 22*SCALE_D - 3}" '
                   f'x2="{x_pos}" y2="{GR_CY + HOEHE*SCALE_D + 5}" '
                   f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# Horizontale Ordner: vom Aufriss nach rechts zum Kreuzriss
all_y_edges = sorted(set([
    -20, -4, 0, 4, 20,
    -BORE_R_val, BORE_R_val,
    -(20-PK_OFF_val), -(20-PK_OFF_val-PK_SIZE_val),
    (20-PK_OFF_val), (20-PK_OFF_val-PK_SIZE_val),
    -E_x_val, E_x_val,
    -G_x_val, G_x_val,
    -Q_x_val, Q_x_val,
]))
for y in all_y_edges:
    y_pos = AR_CY + y * SCALE_D
    proj_lines += (f'<line x1="{AR_CX - 22*SCALE_D}" y1="{y_pos}" '
                   f'x2="{KR_CX + HOEHE*SCALE_D + 3}" y2="{y_pos}" '
                   f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# === 45-Grad-Ordner (Viertelbogen rechts unten) ===
# Uebertraegt z-Koordinaten vom Grundriss zum Kreuzriss
# Mittelpunkt = Schnittpunkt der Achsen
import math as m2
bogen_cx = achse_x
bogen_cy = achse_y

# Fuer jede z-Koordinate: Ordnerlinie vom Grundriss ueber 45-Grad-Bogen zum Kreuzriss
for z_val in [0, HOEHE]:
    z_gr = GR_CY + z_val * SCALE_D  # y-Position im Grundriss
    z_kr = KR_CX + z_val * SCALE_D  # x-Position im Kreuzriss
    r = z_gr - bogen_cy  # Radius = Abstand von Achse

    if r > 0:
        # Horizontale Linie vom Grundriss-Rand nach rechts zur Achse
        proj_lines += (f'<line x1="{AR_CX + 22*SCALE_D}" y1="{z_gr}" '
                       f'x2="{bogen_cx}" y2="{z_gr}" '
                       f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

        # Viertelbogen von (bogen_cx, z_gr) nach (z_kr, bogen_cy)
        # SVG Arc: von Startpunkt zum Endpunkt
        proj_lines += (f'<path d="M {bogen_cx:.1f},{z_gr:.1f} '
                       f'A {r:.1f},{r:.1f} 0 0,0 {z_kr:.1f},{bogen_cy:.1f}" '
                       f'fill="none" stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

        # Vertikale Linie vom Bogen-Ende nach oben zum Kreuzriss
        proj_lines += (f'<line x1="{z_kr}" y1="{bogen_cy}" '
                       f'x2="{z_kr}" y2="{KR_CY - 22*SCALE_D}" '
                       f'stroke="{ordner_col}" stroke-width="{ordner_w}"/>\n')

# Beschriftungen
labels_d = f'''
<text x="{AR_CX}" y="{AR_CY - 22*SCALE_D - 3}" font-size="3.5" font-family="sans-serif" fill="{DC}" text-anchor="middle">Aufriss (Schnitt A-A)</text>
<text x="{GR_CX}" y="{GR_CY - 3}" font-size="3.5" font-family="sans-serif" fill="{DC}" text-anchor="middle">Grundriss</text>
<text x="{KR_CX + HOEHE*SCALE_D/2}" y="{KR_CY - 22*SCALE_D - 3}" font-size="3.5" font-family="sans-serif" fill="{DC}" text-anchor="middle">Kreuzriss</text>
'''

# Keine Achsenbeschriftungen
dim_d = ''

dreitafel_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {A4_W} {A4_H}" width="1190" height="842">
  <defs>
    <marker id="arr" markerWidth="3" markerHeight="3" refX="1.5" refY="1.5"
            orient="auto" markerUnits="strokeWidth">
      <path d="M 0,0 L 3,1.5 L 0,3 Z" fill="{DC}"/>
    </marker>
  </defs>
  {a4_rahmen()}
  {schriftfeld('Alu-Profil 40x40 - Dreitafelprojektion', 'CAD-AI-004', '1:1.4')}
  <!-- Projektionslinien -->
  {proj_lines}
  <!-- Aufriss (Querschnitt mit Schraffur) -->
  <g transform="translate({AR_CX},{AR_CY}) scale({SCALE_D},{SCALE_D})">
    {aufriss}
  </g>
  <!-- Grundriss (Draufsicht) -->
  <g transform="translate({GR_CX},{GR_CY}) scale({SCALE_D},{SCALE_D})">
    {grundriss}
  </g>
  <!-- Kreuzriss (Seitenansicht) -->
  <g transform="translate({KR_CX},{KR_CY}) scale({SCALE_D},{SCALE_D})">
    {kreuzriss}
  </g>
  {labels_d}
  {dim_d}
</svg>'''

(OUT / 'aufgabe03_dreitafel.svg').write_text(dreitafel_svg, encoding='utf-8')
print("OK: aufgabe03_dreitafel.svg")
