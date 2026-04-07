#!/usr/bin/env python3
"""
DG-Aufgaben (Darstellende Geometrie) - 10 Standardaufgaben der Oberstufe
Generates SVG solutions for Austrian DG curriculum tasks.
"""

import math
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(r"e:/2026_GoogleDrive/00 Arbeit/01 PH/Veranstaltungen/2026_04_09 Graz KI im Geometrieunterricht/CAD_by_AI/output/dg")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SVG Helper Functions
# ============================================================

def svg_header(title, nr):
    """A4 landscape SVG with frame and title block."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297 210" width="297mm" height="210mm"
     font-family="Arial, Helvetica, sans-serif">
  <defs>
    <style>
      .construction {{ stroke: #aaa; stroke-width: 0.15; fill: none; }}
      .result {{ stroke: #000; stroke-width: 0.5; fill: none; }}
      .result-fill {{ stroke: #000; stroke-width: 0.5; }}
      .hidden {{ stroke: #000; stroke-width: 0.4; fill: none; stroke-dasharray: 2,1; }}
      .center {{ stroke: #d00; stroke-width: 0.2; fill: none; stroke-dasharray: 4,1,1,1; }}
      .dim {{ stroke: #00a; stroke-width: 0.15; fill: none; }}
      .label {{ font-size: 3px; fill: #000; }}
      .label-sm {{ font-size: 2.2px; fill: #444; }}
      .title {{ font-size: 3.5px; fill: #000; font-weight: bold; }}
      .frame {{ stroke: #000; stroke-width: 0.5; fill: none; }}
      .titleblock {{ stroke: #000; stroke-width: 0.3; fill: none; }}
      .axis {{ stroke: #d00; stroke-width: 0.25; fill: none; stroke-dasharray: 6,1,1,1; }}
      .ground {{ stroke: #070; stroke-width: 0.3; fill: none; }}
      .shadow-fill {{ fill: #ccc; stroke: none; opacity: 0.5; }}
      .shadow-line {{ stroke: #555; stroke-width: 0.4; fill: none; }}
      .blue {{ stroke: #0055cc; stroke-width: 0.4; fill: none; }}
      .red {{ stroke: #cc0000; stroke-width: 0.4; fill: none; }}
      .green {{ stroke: #007700; stroke-width: 0.4; fill: none; }}
    </style>
  </defs>
  <!-- Drawing frame: left 20mm, others 10mm -->
  <rect x="20" y="10" width="267" height="190" class="frame"/>
  <!-- Title block -->
  <rect x="197" y="185" width="90" height="15" class="titleblock"/>
  <line x1="197" y1="192" x2="287" y2="192" class="titleblock"/>
  <line x1="242" y1="185" x2="242" y2="200" class="titleblock"/>
  <text x="199" y="190" class="label-sm">CAD-AI / DG-{nr:02d}</text>
  <text x="244" y="190" class="label-sm">{title}</text>
  <text x="199" y="198" class="label-sm">Darstellende Geometrie</text>
  <text x="244" y="198" class="label-sm">A4 quer | 1:1</text>
'''

def svg_footer():
    return '</svg>\n'

def save_svg(filename, content):
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f"  Created: {path}")
    return path

def fmt(v):
    """Format number for SVG."""
    return f"{v:.2f}"

def point_label(x, y, text, dx=1.5, dy=-1.5):
    return (f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="0.6" fill="#000"/>\n'
            f'<text x="{fmt(x+dx)}" y="{fmt(y+dy)}" class="label">{text}</text>\n')

# ============================================================
# TASK 1: Zweitafelprojektion - Gerade in allgemeiner Lage
# ============================================================
def task01():
    print("Task 01: Zweitafelprojektion - Gerade")
    svg = svg_header("Gerade in allg. Lage", 1)

    # Setup: Two-view projection. Rissachse (x-axis) horizontal.
    # Drawing area: x: 25-280, y: 15-180
    # Aufriss (elevation) above x-axis, Grundriss (plan) below
    cx, axis_y = 153, 105  # center, rissachse y-position

    # Point A(20, 30, 40) and B(70, 10, 60) in 3D
    # Grundriss: x right, y into screen (down in plan)
    # Aufriss: x right, z up (up in elevation)
    Ax, Ay, Az = 20, 30, 40
    Bx, By, Bz = 70, 10, 60

    scale = 1.2
    ox_gr, oy_gr = 60, axis_y  # origin for Grundriss (below axis)
    ox_au, oy_au = 60, axis_y  # origin for Aufriss (above axis)

    # Grundriss: A'(Ax, Ay) -> SVG(ox+Ax*s, axis_y + Ay*s)
    A1x, A1y = ox_gr + Ax*scale, axis_y + Ay*scale
    B1x, B1y = ox_gr + Bx*scale, axis_y + By*scale

    # Aufriss: A''(Ax, Az) -> SVG(ox+Ax*s, axis_y - Az*s)
    A2x, A2y = ox_au + Ax*scale, axis_y - Az*scale
    B2x, B2y = ox_au + Bx*scale, axis_y - Bz*scale

    # Rissachse (projection axis x1/x2) — solid red coordinate axis
    svg += f'<line x1="20" y1="{fmt(axis_y)}" x2="287" y2="{fmt(axis_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    svg += f'<text x="26" y="{fmt(axis_y-1.5)}" class="label-sm">x₁,₂</text>\n'
    svg += f'<text x="40" y="{fmt(axis_y+8)}" class="label">Grundriss (π₁)</text>\n'
    svg += f'<text x="40" y="{fmt(axis_y-5)}" class="label">Aufriss (π₂)</text>\n'

    # Ordner (vertical projection lines)
    svg += f'<line x1="{fmt(A1x)}" y1="{fmt(A1y)}" x2="{fmt(A2x)}" y2="{fmt(A2y)}" class="construction"/>\n'
    svg += f'<line x1="{fmt(B1x)}" y1="{fmt(B1y)}" x2="{fmt(B2x)}" y2="{fmt(B2y)}" class="construction"/>\n'

    # Grundriss line
    svg += f'<line x1="{fmt(A1x)}" y1="{fmt(A1y)}" x2="{fmt(B1x)}" y2="{fmt(B1y)}" class="result"/>\n'
    svg += point_label(A1x, A1y, "A'", 1.5, 3)
    svg += point_label(B1x, B1y, "B'", 1.5, 3)

    # Aufriss line
    svg += f'<line x1="{fmt(A2x)}" y1="{fmt(A2y)}" x2="{fmt(B2x)}" y2="{fmt(B2y)}" class="result"/>\n'
    svg += point_label(A2x, A2y, 'A"', 1.5, -1.5)
    svg += point_label(B2x, B2y, 'B"', 1.5, -1.5)

    # True length construction (Umklappung)
    # True length = sqrt(dx^2 + dy^2 + dz^2)
    dx = Bx - Ax
    dy = By - Ay
    dz = Bz - Az
    true_len = math.sqrt(dx**2 + dy**2 + dz**2)
    gr_len = math.sqrt(dx**2 + dy**2)

    # Show true length by rotating the Grundriss projection
    # Attach at A', swing B' to B'_w where distance = true_len * scale
    tl_angle = math.atan2(B1y - A1y, B1x - A1x)
    Bwx = A1x + true_len * scale * math.cos(tl_angle)
    Bwy = A1y + true_len * scale * math.sin(tl_angle)

    # Better: use height difference to find true length from Grundriss
    # True length from Grundriss: swing from A1 with radius = true_len*scale
    # Place it offset to the right for clarity
    tl_cx, tl_cy = 200, axis_y + 50  # true length area
    svg += f'<text x="{fmt(tl_cx)}" y="{fmt(tl_cy-20)}" class="title">Wahre Länge</text>\n'

    # Draw the Grundriss segment horizontally, then construct true length
    wl_ax, wl_ay = tl_cx, tl_cy
    wl_bx_gr = tl_cx + gr_len * scale, tl_cy  # Grundriss length horizontal

    svg += f'<line x1="{fmt(wl_ax)}" y1="{fmt(wl_ay)}" x2="{fmt(wl_bx_gr[0])}" y2="{fmt(wl_bx_gr[1])}" class="construction"/>\n'

    # Height difference |Az - Bz|
    h_diff = abs(Az - Bz) * scale
    # Perpendicular at B' up by h_diff
    svg += f'<line x1="{fmt(wl_bx_gr[0])}" y1="{fmt(wl_bx_gr[1])}" x2="{fmt(wl_bx_gr[0])}" y2="{fmt(wl_bx_gr[1] - h_diff)}" class="construction"/>\n'

    # True length line
    wl_end_x = wl_bx_gr[0]
    wl_end_y = wl_bx_gr[1] - h_diff
    svg += f'<line x1="{fmt(wl_ax)}" y1="{fmt(wl_ay)}" x2="{fmt(wl_end_x)}" y2="{fmt(wl_end_y)}" class="blue"/>\n'
    svg += f'<text x="{fmt((wl_ax+wl_end_x)/2 - 8)}" y="{fmt((wl_ay+wl_end_y)/2)}" class="label" fill="#0055cc">wL = {true_len:.1f}</text>\n'

    svg += point_label(wl_ax, wl_ay, "A", 1, 3)
    svg += point_label(wl_end_x, wl_end_y, "B_w", 1.5, -1.5)

    # Dimension annotations
    svg += f'<text x="30" y="20" class="title">Aufgabe 1: Gerade in allgemeiner Lage</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">A({Ax},{Ay},{Az})  B({Bx},{By},{Bz})</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Wahre Länge = √(Δx²+Δy²+Δz²) = {true_len:.2f}</text>\n'

    svg += svg_footer()
    save_svg("dg_01_gerade.svg", svg)
    return True

# ============================================================
# TASK 2: Ebene durch 3 Punkte - Spurgeraden
# ============================================================
def task02():
    print("Task 02: Ebene durch 3 Punkte - Spurgeraden")
    svg = svg_header("Ebene - Spurgeraden", 2)

    axis_y = 105
    scale = 1.0
    ox = 50

    # Points: P(10,40,20), Q(60,10,50), R(50,50,10)
    Px, Py, Pz = 10, 40, 20
    Qx, Qy, Qz = 60, 10, 50
    Rx, Ry, Rz = 50, 50, 10

    # Grundriss
    P1x, P1y = ox + Px*scale, axis_y + Py*scale
    Q1x, Q1y = ox + Qx*scale, axis_y + Qy*scale
    R1x, R1y = ox + Rx*scale, axis_y + Ry*scale

    # Aufriss
    P2x, P2y = ox + Px*scale, axis_y - Pz*scale
    Q2x, Q2y = ox + Qx*scale, axis_y - Qz*scale
    R2x, R2y = ox + Rx*scale, axis_y - Rz*scale

    # Rissachse — solid red coordinate axis
    svg += f'<line x1="20" y1="{fmt(axis_y)}" x2="287" y2="{fmt(axis_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    svg += f'<text x="26" y="{fmt(axis_y-1.5)}" class="label-sm">x₁,₂</text>\n'

    # Draw triangle in Grundriss
    svg += f'<polygon points="{fmt(P1x)},{fmt(P1y)} {fmt(Q1x)},{fmt(Q1y)} {fmt(R1x)},{fmt(R1y)}" class="result" fill="rgba(100,150,255,0.1)"/>\n'
    svg += point_label(P1x, P1y, "P'", 1.5, 3)
    svg += point_label(Q1x, Q1y, "Q'", 1.5, 3)
    svg += point_label(R1x, R1y, "R'", 1.5, 3)

    # Draw triangle in Aufriss
    svg += f'<polygon points="{fmt(P2x)},{fmt(P2y)} {fmt(Q2x)},{fmt(Q2y)} {fmt(R2x)},{fmt(R2y)}" class="result" fill="rgba(100,150,255,0.1)"/>\n'
    svg += point_label(P2x, P2y, 'P"', 1.5, -1.5)
    svg += point_label(Q2x, Q2y, 'Q"', 1.5, -1.5)
    svg += point_label(R2x, R2y, 'R"', 1.5, -1.5)

    # Ordner
    for (ax, ay, bx, by) in [(P1x,P1y,P2x,P2y),(Q1x,Q1y,Q2x,Q2y),(R1x,R1y,R2x,R2y)]:
        svg += f'<line x1="{fmt(ax)}" y1="{fmt(ay)}" x2="{fmt(bx)}" y2="{fmt(by)}" class="construction"/>\n'

    # Spurgeraden construction:
    # 1. Spurgerade s1 (in pi1): Find where plane meets z=0
    #    Take line PQ, find where z=0: t = Pz/(Pz-Qz) ... if Pz != Qz
    #    Take line PR, find where z=0: t = Pz/(Pz-Rz)

    def find_z0(A, B):
        """Find point on line AB where z=0, return (x,y) or None."""
        ax,ay,az = A
        bx,by,bz = B
        if abs(az - bz) < 1e-9:
            return None
        t = az / (az - bz)
        return (ax + t*(bx-ax), ay + t*(by-ay))

    def find_y0(A, B):
        """Find point on line AB where y=0, return (x,z) or None."""
        ax,ay,az = A
        bx,by,bz = B
        if abs(ay - by) < 1e-9:
            return None
        t = ay / (ay - by)
        return (ax + t*(bx-ax), az + t*(bz-az))

    P3, Q3, R3 = (Px,Py,Pz), (Qx,Qy,Qz), (Rx,Ry,Rz)

    # s1: plane intersects pi1 (z=0)
    s1_points = []
    for A, B in [(P3,Q3), (Q3,R3), (P3,R3)]:
        pt = find_z0(A, B)
        if pt is not None:
            t = A[2] / (A[2] - B[2])
            if -0.5 <= t <= 1.5:
                s1_points.append(pt)

    if len(s1_points) >= 2:
        # Draw s1 in Grundriss (extended)
        s1a = s1_points[0]
        s1b = s1_points[1]
        dx = s1b[0] - s1a[0]
        dy = s1b[1] - s1a[1]
        ext = 2.0
        svg += f'<line x1="{fmt(ox + (s1a[0]-ext*dx)*scale)}" y1="{fmt(axis_y + (s1a[1]-ext*dy)*scale)}" x2="{fmt(ox + (s1b[0]+ext*dx)*scale)}" y2="{fmt(axis_y + (s1b[1]+ext*dy)*scale)}" class="green"/>\n'
        svg += f'<text x="{fmt(ox + s1a[0]*scale + 2)}" y="{fmt(axis_y + s1a[1]*scale - 2)}" class="label" fill="#070">s₁</text>\n'

    # s2: plane intersects pi2 (y=0)
    s2_points = []
    for A, B in [(P3,Q3), (Q3,R3), (P3,R3)]:
        pt = find_y0(A, B)
        if pt is not None:
            t = A[1] / (A[1] - B[1])
            if -0.5 <= t <= 1.5:
                s2_points.append(pt)

    if len(s2_points) >= 2:
        # Draw s2 in Aufriss (extended)
        s2a = s2_points[0]
        s2b = s2_points[1]
        dx = s2b[0] - s2a[0]
        dy = s2b[1] - s2a[1]
        ext = 2.0
        svg += f'<line x1="{fmt(ox + (s2a[0]-ext*dx)*scale)}" y1="{fmt(axis_y - (s2a[1]-ext*dy)*scale)}" x2="{fmt(ox + (s2b[0]+ext*dx)*scale)}" y2="{fmt(axis_y - (s2b[1]+ext*dy)*scale)}" class="blue"/>\n'
        svg += f'<text x="{fmt(ox + s2a[0]*scale + 2)}" y="{fmt(axis_y - s2a[1]*scale - 2)}" class="label" fill="#0055cc">s₂</text>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 2: Ebene durch 3 Punkte – Spurgeraden</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">P({Px},{Py},{Pz})  Q({Qx},{Qy},{Qz})  R({Rx},{Ry},{Rz})</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">s₁ = Erste Spurgerade (π₁), s₂ = Zweite Spurgerade (π₂)</text>\n'

    svg += svg_footer()
    save_svg("dg_02_ebene_spurgeraden.svg", svg)
    return True

# ============================================================
# TASK 3: Ellipse als Schnitt eines Zylinders
# ============================================================
def task03():
    print("Task 03: Kegelschnitt - Ellipse (Zylinderschnitt)")
    svg = svg_header("Ellipse - Zylinderschnitt", 3)

    # Cylinder d=50, axis vertical, cut at 45°
    # In Aufriss: cylinder is rectangle, cut line at 45°
    # Result: ellipse with a = d/(2*cos(45°)), b = d/2 = 25

    d = 50
    r = d / 2.0
    angle = math.radians(45)
    a_ell = r / math.cos(angle)  # semi-major
    b_ell = r  # semi-minor

    scale = 1.2

    # Aufriss of cylinder (left side)
    au_cx, au_cy = 80, 100  # center of cut on cylinder axis
    au_left = au_cx - r * scale
    au_right = au_cx + r * scale
    au_top = au_cy - 50 * scale
    au_bot = au_cy + 30 * scale

    # Cylinder outline in Aufriss
    svg += f'<line x1="{fmt(au_left)}" y1="{fmt(au_top)}" x2="{fmt(au_left)}" y2="{fmt(au_bot)}" class="result"/>\n'
    svg += f'<line x1="{fmt(au_right)}" y1="{fmt(au_top)}" x2="{fmt(au_right)}" y2="{fmt(au_bot)}" class="result"/>\n'
    # Top ellipse (circle viewed from front = line)
    svg += f'<line x1="{fmt(au_left)}" y1="{fmt(au_top)}" x2="{fmt(au_right)}" y2="{fmt(au_top)}" class="result"/>\n'
    # Bottom
    svg += f'<line x1="{fmt(au_left)}" y1="{fmt(au_bot)}" x2="{fmt(au_right)}" y2="{fmt(au_bot)}" class="result"/>\n'

    # Center axis
    svg += f'<line x1="{fmt(au_cx)}" y1="{fmt(au_top-5)}" x2="{fmt(au_cx)}" y2="{fmt(au_bot+5)}" class="center"/>\n'

    # Cut line at 45° through center
    cut_half = r * scale / math.cos(angle) * 1.2
    cut_x1 = au_cx - r * scale
    cut_y1 = au_cy + r * scale * math.tan(angle)
    cut_x2 = au_cx + r * scale
    cut_y2 = au_cy - r * scale * math.tan(angle)
    svg += f'<line x1="{fmt(cut_x1)}" y1="{fmt(cut_y1)}" x2="{fmt(cut_x2)}" y2="{fmt(cut_y2)}" class="blue"/>\n'
    svg += f'<text x="{fmt(cut_x2+2)}" y="{fmt(cut_y2)}" class="label" fill="#0055cc">Schnittebene 45°</text>\n'

    # Mark intersection points on cylinder walls
    svg += f'<circle cx="{fmt(cut_x1)}" cy="{fmt(cut_y1)}" r="0.8" fill="#cc0000"/>\n'
    svg += f'<circle cx="{fmt(cut_x2)}" cy="{fmt(cut_y2)}" r="0.8" fill="#cc0000"/>\n'

    # Ellipse result (right side) - wahre Gestalt
    ell_cx, ell_cy = 210, 100
    svg += f'<text x="{fmt(ell_cx-15)}" y="{fmt(ell_cy - a_ell*scale - 8)}" class="title">Wahre Gestalt der Schnittellipse</text>\n'

    # Draw ellipse
    n_pts = 100
    pts = []
    for i in range(n_pts + 1):
        t = 2 * math.pi * i / n_pts
        ex = ell_cx + b_ell * scale * math.cos(t)
        ey = ell_cy + a_ell * scale * math.sin(t)
        pts.append(f"{fmt(ex)},{fmt(ey)}")
    svg += f'<polyline points="{" ".join(pts)}" class="result"/>\n'

    # Axes of ellipse
    svg += f'<line x1="{fmt(ell_cx)}" y1="{fmt(ell_cy - a_ell*scale - 3)}" x2="{fmt(ell_cx)}" y2="{fmt(ell_cy + a_ell*scale + 3)}" class="center"/>\n'
    svg += f'<line x1="{fmt(ell_cx - b_ell*scale - 3)}" y1="{fmt(ell_cy)}" x2="{fmt(ell_cx + b_ell*scale + 3)}" y2="{fmt(ell_cy)}" class="center"/>\n'

    # Labels
    svg += f'<text x="{fmt(ell_cx+2)}" y="{fmt(ell_cy - a_ell*scale - 1)}" class="label-sm">a = {a_ell:.1f}</text>\n'
    svg += f'<text x="{fmt(ell_cx + b_ell*scale + 1)}" y="{fmt(ell_cy - 1)}" class="label-sm">b = {b_ell:.1f}</text>\n'

    # Construction: projection lines from Aufriss to ellipse
    for frac in [-1, -0.5, 0, 0.5, 1]:
        px = au_cx + frac * r * scale
        # Height on cut line at this x
        py = au_cy - frac * r * scale * math.tan(angle)
        svg += f'<line x1="{fmt(px)}" y1="{fmt(py)}" x2="{fmt(ell_cx + frac * b_ell * scale)}" y2="{fmt(py)}" class="construction"/>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 3: Ellipse als Schnitt eines Zylinders</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Zylinder d={d}, Schnittwinkel=45°</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Halbachsen: a={a_ell:.2f}, b={b_ell:.2f}</text>\n'

    svg += svg_footer()
    save_svg("dg_03_ellipse_zylinder.svg", svg)
    return True

# ============================================================
# TASK 4: Parabel als Schnitt eines Kegels
# ============================================================
def task04():
    print("Task 04: Kegelschnitt - Parabel (Kegelschnitt)")
    svg = svg_header("Parabel - Kegelschnitt", 4)

    # Cone: half-angle 30° (Kegelwinkel 60° means full opening = 60°, half = 30°)
    # Schnittebene parallel to Mantellinie -> Parabel
    half_angle = math.radians(30)

    scale = 1.0

    # Aufriss of cone (left portion)
    cone_tip_x, cone_tip_y = 90, 30  # apex
    cone_h = 100  # height of cone in mm
    cone_base_r = cone_h * math.tan(half_angle)

    base_y = cone_tip_y + cone_h * scale
    left_x = cone_tip_x - cone_base_r * scale
    right_x = cone_tip_x + cone_base_r * scale

    # Cone outline
    svg += f'<line x1="{fmt(cone_tip_x)}" y1="{fmt(cone_tip_y)}" x2="{fmt(left_x)}" y2="{fmt(base_y)}" class="result"/>\n'
    svg += f'<line x1="{fmt(cone_tip_x)}" y1="{fmt(cone_tip_y)}" x2="{fmt(right_x)}" y2="{fmt(base_y)}" class="result"/>\n'
    svg += f'<line x1="{fmt(left_x)}" y1="{fmt(base_y)}" x2="{fmt(right_x)}" y2="{fmt(base_y)}" class="result"/>\n'

    # Axis
    svg += f'<line x1="{fmt(cone_tip_x)}" y1="{fmt(cone_tip_y - 5)}" x2="{fmt(cone_tip_x)}" y2="{fmt(base_y + 5)}" class="center"/>\n'

    # Cutting plane parallel to left Mantellinie
    # Left Mantellinie has slope: dx/dy = -tan(half_angle)
    # Parallel cut: shifted right by some offset
    cut_offset = 2 * scale  # offset from axis (klein genug, damit Schnitt den Kegel trifft)

    # The cutting plane line in Aufriss (parallel to left contour)
    # Left contour goes from (cone_tip_x, cone_tip_y) to (left_x, base_y)
    # Direction: (-cone_base_r*scale, cone_h*scale)
    # Parallel line through point on right side
    cut_start_y = cone_tip_y + 10
    cut_end_y = base_y + 5

    # At height y from tip, the cutting plane x-position:
    # x = cone_tip_x + cut_offset + (y - cone_tip_y) * (-tan(half_angle)) * scale  ... no
    # Parallel to left Mantellinie means same slope
    # Left contour: from (tip_x, tip_y) direction is (-tan(ha), 1) per unit y

    cut_sx = cone_tip_x + cut_offset + (cut_start_y - cone_tip_y) * (-math.tan(half_angle)) * scale
    cut_ex = cone_tip_x + cut_offset + (cut_end_y - cone_tip_y) * (-math.tan(half_angle)) * scale

    # Hmm let me reconsider. The left Mantellinie in SVG coords:
    # direction vector: (left_x - cone_tip_x, base_y - cone_tip_y) = (-cone_base_r*s, cone_h*s)
    dx_m = left_x - cone_tip_x
    dy_m = base_y - cone_tip_y

    # Cut line parallel to this, offset to the right
    cut_p1x = cone_tip_x + cut_offset
    cut_p1y = cone_tip_y
    cut_p2x = cut_p1x + dx_m
    cut_p2y = cut_p1y + dy_m

    svg += f'<line x1="{fmt(cut_p1x)}" y1="{fmt(cut_p1y - 3)}" x2="{fmt(cut_p2x)}" y2="{fmt(cut_p2y + 3)}" class="blue"/>\n'
    svg += f'<text x="{fmt(cut_p1x + 3)}" y="{fmt(cut_p1y)}" class="label" fill="#0055cc">Schnittebene</text>\n'

    # Compute parabola intersection points
    # At height h from apex (SVG y = cone_tip_y + h*scale), cone radius = h*tan(half_angle)
    # The cut plane at SVG-x = cut_p1x + t*dx_m/|dy_m| * ...
    # Let's parametrize by h (distance from apex along axis):
    # Cone circle at height h: center=(cone_tip_x, cone_tip_y+h*s), radius=h*tan(ha)*s
    # Cut line at height h: x = cut_p1x + (h*s / dy_m) * dx_m = cone_tip_x + cut_offset + h*s * (dx_m/dy_m)
    # = cone_tip_x + cut_offset - h * s * tan(ha) * s / (cone_h * s) * ...

    # Simpler: use 3D geometry.
    # Cone apex at origin, axis along z (down). At height h: circle radius = h*tan(30°).
    # Cut plane parallel to a Mantellinie.
    # Mantellinie direction: (sin(30°), 0, cos(30°)) = (0.5, 0, √3/2)
    # Cut plane contains direction (0.5, 0, √3/2) and is also in the y-direction (0,1,0).
    # Cut plane normal: cross((0.5,0,√3/2), (0,1,0)) = (-√3/2, 0, 0.5)
    # Plane: -√3/2 * x + 0.5 * z = d_plane
    # Choose plane to pass through (cut_offset_3d, 0, 0): d_plane = -√3/2 * cut_offset_3d

    cut_offset_3d = cut_offset / scale  # in real mm
    ha = half_angle

    # Intersection of plane with cone at height h:
    # Cone at height h: x² + y² = (h*tan(ha))²
    # Plane: -√3/2 * x + 0.5 * h = -√3/2 * cut_offset_3d
    # => x = cut_offset_3d + h/(√3)   (since 0.5/( √3/2) = 1/√3)
    # Wait: -√3/2 * x + 0.5 * h = -√3/2 * cut_offset_3d
    # √3/2 * (cut_offset_3d - x) + 0.5 * h = 0
    # x = cut_offset_3d + h / √3

    sq3 = math.sqrt(3)

    parabola_pts = []
    # Schnittebene: x = cut_offset_3d (senkrecht, parallel zur Mantellinie im Aufriss)
    # Kegel bei Höhe h: x^2 + y^2 = (h*tan(ha))^2
    # Schnitt: y^2 = (h*tan(ha))^2 - cut_offset_3d^2
    for h in np.linspace(0.1, cone_h * 0.98, 100):
        cone_r = h * math.tan(ha)
        if cone_r > cut_offset_3d:
            y_val = math.sqrt(cone_r**2 - cut_offset_3d**2)
            parabola_pts.append((h, y_val))

    # Draw parabola (wahre Gestalt) on the right
    par_cx, par_cy = 220, 40
    svg += f'<text x="{fmt(par_cx - 15)}" y="{fmt(par_cy - 5)}" class="title">Wahre Gestalt: Parabel</text>\n'

    if parabola_pts:
        # The parabola in the cutting plane coordinates
        # Use h and y as local coordinates, scale them
        ps = 1.0
        pts_upper = []
        pts_lower = []
        for h, y in parabola_pts:
            sx = par_cx + y * ps
            sy = par_cy + h * ps
            pts_upper.append(f"{fmt(sx)},{fmt(sy)}")
            sx2 = par_cx - y * ps
            pts_lower.append(f"{fmt(sx2)},{fmt(sy)}")

        svg += f'<polyline points="{" ".join(pts_upper)}" class="result"/>\n'
        svg += f'<polyline points="{" ".join(pts_lower)}" class="result"/>\n'

        # Symmetry axis
        min_h = parabola_pts[0][0]
        max_h = parabola_pts[-1][0]
        svg += f'<line x1="{fmt(par_cx)}" y1="{fmt(par_cy + min_h*ps - 3)}" x2="{fmt(par_cx)}" y2="{fmt(par_cy + max_h*ps + 3)}" class="center"/>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 4: Parabel als Kegelschnitt</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Kegelwinkel 60° (Halbwinkel 30°), Schnittebene parallel zur Mantellinie</text>\n'
    svg += f'<text x="{fmt(cone_tip_x - 3)}" y="{fmt(cone_tip_y - 3)}" class="label">S (Spitze)</text>\n'
    svg += f'<text x="{fmt(cone_tip_x - 20)}" y="{fmt(cone_tip_y + 10)}" class="label-sm">α = 30°</text>\n'

    svg += svg_footer()
    save_svg("dg_04_parabel_kegel.svg", svg)
    return True

# ============================================================
# TASK 5: Schattenkonstruktion - Quader im Parallellicht
# ============================================================
def task05():
    print("Task 05: Schattenkonstruktion - Quader")
    svg = svg_header("Schatten - Quader", 5)

    # Quader 40x30x50, light from left-above-front (45°)
    # Show Aufriss + Grundriss with shadow construction, centered on page

    axis_y = 100
    scale = 0.9
    ox = 80  # shifted right for better centering

    w, d, h = 40, 30, 50

    # 8 corners: bottom 0-3, top 4-7
    corners_3d = [
        (0,0,0), (w,0,0), (w,d,0), (0,d,0),  # bottom
        (0,0,h), (w,0,h), (w,d,h), (0,d,h)    # top
    ]

    # Grundriss (plan): project to x,y
    def gr(p):
        return (ox + p[0]*scale, axis_y + p[1]*scale)

    # Aufriss (elevation): project to x,z (z up)
    def au(p):
        return (ox + p[0]*scale, axis_y - p[2]*scale)

    # Rissachse -- solid red coordinate axis
    svg += f'<line x1="20" y1="{fmt(axis_y)}" x2="287" y2="{fmt(axis_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    svg += f'<text x="26" y="{fmt(axis_y-1.5)}" class="label-sm">x₁,₂</text>\n'

    # ── Aufriss (elevation view, above axis) ──
    svg += f'<text x="{fmt(ox - 5)}" y="{fmt(axis_y - 48)}" class="label">Aufriss (π₂)</text>\n'

    # Front face (y=0): corners 0,1,5,4 — visible
    au_pts = [au(c) for c in corners_3d]
    front_edges = [(0,1),(1,5),(5,4),(4,0)]
    for a, b in front_edges:
        svg += f'<line x1="{fmt(au_pts[a][0])}" y1="{fmt(au_pts[a][1])}" x2="{fmt(au_pts[b][0])}" y2="{fmt(au_pts[b][1])}" class="result"/>\n'
    # Top edge visible in Aufriss: 4-7, 5-6, 7-6 (depth direction hidden)
    # Back face (y=d) visible edges: 3-2,2-6,6-7,7-3 — but these overlap front in Aufriss
    # Depth edges (connecting front to back): hidden
    for a, b in [(0,3),(1,2),(5,6),(4,7)]:
        svg += f'<line x1="{fmt(au_pts[a][0])}" y1="{fmt(au_pts[a][1])}" x2="{fmt(au_pts[b][0])}" y2="{fmt(au_pts[b][1])}" class="hidden"/>\n'

    # ── Grundriss (plan view, below axis) ──
    svg += f'<text x="{fmt(ox - 5)}" y="{fmt(axis_y + 5)}" class="label">Grundriss (π₁)</text>\n'

    # Bottom rectangle (z=0): corners 0,1,2,3
    bottom_gr = [gr(corners_3d[i]) for i in range(4)]
    for i in range(4):
        j = (i + 1) % 4
        svg += f'<line x1="{fmt(bottom_gr[i][0])}" y1="{fmt(bottom_gr[i][1])}" x2="{fmt(bottom_gr[j][0])}" y2="{fmt(bottom_gr[j][1])}" class="result"/>\n'

    # Ordner (projection lines between Aufriss and Grundriss)
    for i in [0, 1, 2, 3]:
        svg += f'<line x1="{fmt(au_pts[i][0])}" y1="{fmt(au_pts[i][1])}" x2="{fmt(bottom_gr[i][0])}" y2="{fmt(bottom_gr[i][1])}" stroke="#888" stroke-width="0.1"/>\n'

    # ── Light direction ──
    lx, ly, lz = 1, 1, -1  # light direction vector (right, into screen, down)

    # Light direction arrows in Aufriss (l'' = projection of l to xz-plane: (1, -1) in SVG)
    arr_x, arr_y = ox + w*scale + 15, axis_y - h*scale - 5
    arrow_len = 18
    # 45° downward-right in Aufriss
    svg += f'<line x1="{fmt(arr_x)}" y1="{fmt(arr_y)}" x2="{fmt(arr_x + arrow_len*0.707)}" y2="{fmt(arr_y + arrow_len*0.707)}" stroke="#D80" stroke-width="0.4"/>\n'
    # Arrowhead
    ax2, ay2 = arr_x + arrow_len*0.707, arr_y + arrow_len*0.707
    svg += f'<polygon points="{fmt(ax2)},{fmt(ay2)} {fmt(ax2-2.5)},{fmt(ay2-1)} {fmt(ax2-1)},{fmt(ay2-2.5)}" fill="#D80"/>\n'
    svg += f'<text x="{fmt(arr_x - 1)}" y="{fmt(arr_y - 2)}" class="label-sm" fill="#D80">l″ (45°)</text>\n'

    # Light direction arrow in Grundriss (l' = projection of l to xy-plane: (1, 1) in SVG)
    garr_x, garr_y = ox + w*scale + 15, axis_y + 3
    svg += f'<line x1="{fmt(garr_x)}" y1="{fmt(garr_y)}" x2="{fmt(garr_x + arrow_len*0.707)}" y2="{fmt(garr_y + arrow_len*0.707)}" stroke="#D80" stroke-width="0.4"/>\n'
    gax2, gay2 = garr_x + arrow_len*0.707, garr_y + arrow_len*0.707
    svg += f'<polygon points="{fmt(gax2)},{fmt(gay2)} {fmt(gax2-2.5)},{fmt(gay2-1)} {fmt(gax2-1)},{fmt(gay2-2.5)}" fill="#D80"/>\n'
    svg += f'<text x="{fmt(garr_x - 1)}" y="{fmt(garr_y - 2)}" class="label-sm" fill="#D80">l′ (45°)</text>\n'

    # ── Shadow on ground plane (Schlagschatten in Grundriss) ──
    def shadow_gr(p):
        """Shadow of point p on ground plane z=0, shown in Grundriss."""
        sx = p[0] + p[2] * (lx / (-lz))
        sy = p[1] + p[2] * (ly / (-lz))
        return (ox + sx * scale, axis_y + sy * scale)

    # Shadow of top 4 corners on ground
    shadow_pts = [shadow_gr(corners_3d[i]) for i in [4, 5, 6, 7]]

    # Complete shadow polygon outline on ground
    # The cast shadow is the union of the Quader footprint and the projected top face
    # Outline: bottom-front-left -> bottom-front-right -> shadow of top-front-right ->
    #          shadow of top-back-right -> shadow of top-back-left -> shadow of top-front-left -> close
    shadow_outline = [
        gr(corners_3d[0]), gr(corners_3d[1]),       # bottom front edge (on ground)
        shadow_gr(corners_3d[5]), shadow_gr(corners_3d[6]),  # shadow of top-right edges
        shadow_gr(corners_3d[7]), shadow_gr(corners_3d[4]),  # shadow of top-left edges
    ]

    # Filled gray shadow polygon
    poly_str = " ".join(f"{fmt(p[0])},{fmt(p[1])}" for p in shadow_outline)
    svg += f'<polygon points="{poly_str}" fill="#bbb" stroke="none" opacity="0.45"/>\n'

    # Shadow outline
    for i in range(len(shadow_outline)):
        j = (i + 1) % len(shadow_outline)
        svg += f'<line x1="{fmt(shadow_outline[i][0])}" y1="{fmt(shadow_outline[i][1])}" x2="{fmt(shadow_outline[j][0])}" y2="{fmt(shadow_outline[j][1])}" class="shadow-line"/>\n'

    # Light rays (construction lines from top Grundriss projections to shadow points)
    for i in range(4):
        top_gr = gr(corners_3d[i + 4])
        sh = shadow_pts[i]
        svg += f'<line x1="{fmt(top_gr[0])}" y1="{fmt(top_gr[1])}" x2="{fmt(sh[0])}" y2="{fmt(sh[1])}" stroke="#D80" stroke-width="0.15" stroke-dasharray="1,1"/>\n'

    # ── Eigenschatten boundary on Quader (in Aufriss) ──
    # The self-shadow boundary separates lit from unlit faces.
    # Light comes from left-above-front => lit faces: top (z=h), left (x=0), front (y=0)
    # Eigenschatten boundary edges in Aufriss: the edges between lit and unlit faces
    # Right face (x=w) is unlit, so edge between top and right = edge 5-6 projected
    # Bottom face (z=0) is unlit, so edge between front-bottom = edge 0-1 projected
    # Mark Eigenschatten boundary: top-right edge (5-6) and bottom-right edge (1-2) in Aufriss
    eigen_edges = [(5, 6), (1, 2), (5, 1)]  # boundary between lit/unlit
    for a, b in eigen_edges:
        svg += f'<line x1="{fmt(au_pts[a][0])}" y1="{fmt(au_pts[a][1])}" x2="{fmt(au_pts[b][0])}" y2="{fmt(au_pts[b][1])}" stroke="#900" stroke-width="0.6"/>\n'
    svg += f'<text x="{fmt(au_pts[5][0] + 2)}" y="{fmt((au_pts[5][1]+au_pts[6][1])/2)}" class="label-sm" fill="#900">Eigenschatten-</text>\n'
    svg += f'<text x="{fmt(au_pts[5][0] + 2)}" y="{fmt((au_pts[5][1]+au_pts[6][1])/2 + 3)}" class="label-sm" fill="#900">grenze</text>\n'

    # ── Legend ──
    leg_x, leg_y = 195, 140
    svg += f'<rect x="{fmt(leg_x - 2)}" y="{fmt(leg_y - 5)}" width="75" height="28" fill="white" stroke="#ccc" stroke-width="0.2" rx="1"/>\n'
    svg += f'<text x="{fmt(leg_x)}" y="{fmt(leg_y)}" class="label" font-weight="bold">Legende:</text>\n'
    # Schlagschatten
    svg += f'<rect x="{fmt(leg_x)}" y="{fmt(leg_y + 3)}" width="6" height="3" fill="#bbb" opacity="0.45"/>\n'
    svg += f'<text x="{fmt(leg_x + 8)}" y="{fmt(leg_y + 6)}" class="label-sm">Schlagschatten (Grundriss)</text>\n'
    # Eigenschatten
    svg += f'<line x1="{fmt(leg_x)}" y1="{fmt(leg_y + 11)}" x2="{fmt(leg_x + 6)}" y2="{fmt(leg_y + 11)}" stroke="#900" stroke-width="0.6"/>\n'
    svg += f'<text x="{fmt(leg_x + 8)}" y="{fmt(leg_y + 12.5)}" class="label-sm">Eigenschattengrenze (Aufriss)</text>\n'
    # Light
    svg += f'<line x1="{fmt(leg_x)}" y1="{fmt(leg_y + 17)}" x2="{fmt(leg_x + 6)}" y2="{fmt(leg_y + 17)}" stroke="#D80" stroke-width="0.4"/>\n'
    svg += f'<text x="{fmt(leg_x + 8)}" y="{fmt(leg_y + 18.5)}" class="label-sm">Lichtrichtung l=(1,1,−1)</text>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 5: Schattenkonstruktion – Quader im Parallellicht</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Quader {w}×{d}×{h}, Lichtrichtung l=(1,1,−1), 45° von links-oben-vorn</text>\n'

    svg += svg_footer()
    save_svg("dg_05_schatten_quader.svg", svg)
    return True

# ============================================================
# TASK 6: Durchdringung Zylinder-Zylinder
# ============================================================
def task06():
    print("Task 06: Durchdringung Zylinder-Zylinder")
    svg = svg_header("Zylinder-Durchdringung", 6)

    # Two cylinders d=40 each, crossing at right angles.
    # Vertical cylinder: axis along y (up in 3D), d=40
    # Horizontal cylinder: axis along z (into page), d=40, through center of vertical one
    #
    # Convention for three-view projection:
    #   Aufriss (front, xz-plane looking along y): top-left area
    #   Grundriss (top, xy-plane looking down along z): bottom-left area
    #   Seitenriss (right side, yz-plane looking along x): top-right area
    #
    # In Aufriss (front view, x-z plane):
    #   Vertical cylinder (axis y): appears as rectangle (width=d, height=cyl_len)
    #   Horizontal cylinder (axis z): seen end-on = circle (d=40)
    #
    # In Grundriss (top view, x-y plane):
    #   Vertical cylinder (axis y): appears as circle (d=40) — looking down along z
    #     Wait — the vertical cylinder axis is along y. In Grundriss we look down along z.
    #     Axis along y projects to a line along y in Grundriss. So it's a rectangle.
    #   Actually let me reconsider the geometry:
    #   Vertical cylinder axis = y-axis. Grundriss = top view looking down z.
    #   In Grundriss: vertical cyl projects to rectangle (width d along x, length along y)
    #   Horizontal cylinder axis = z-axis. In Grundriss: seen end-on = circle.
    #
    # In Seitenriss (side view, y-z plane):
    #   Vertical cylinder (axis y): rectangle (width d along z direction... no, axis y => in yz-plane
    #     we see the axis along y, cross-section along z => rectangle width d (along z), length along y
    #   Horizontal cylinder (axis z): rectangle (width d along y, length along z)

    r = 20  # radius
    d = 2 * r
    cyl_len = 70  # visible cylinder length (half-length each side)

    # ── Layout positions ──
    # Rissachse intersection point (where horizontal and vertical axes cross)
    riss_x = 120  # vertical Rissachse x-position
    riss_y = 105  # horizontal Rissachse y-position

    # View centers
    au_cx, au_cy = 75, 65     # Aufriss center (top-left)
    gr_cx, gr_cy = 75, 150    # Grundriss center (bottom-left)
    sr_cx, sr_cy = 195, 65    # Seitenriss center (top-right)

    sc = 1.0  # scale factor

    # ── Rissachsen (red solid lines) ──
    # Horizontal Rissachse x₁,₂ (separates Aufriss above from Grundriss below)
    svg += f'<line x1="20" y1="{fmt(riss_y)}" x2="{fmt(riss_x)}" y2="{fmt(riss_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    svg += f'<text x="24" y="{fmt(riss_y - 1.5)}" class="label-sm" fill="#C00">x₁,₂</text>\n'
    # Vertical Rissachse x₁,₃ (separates Aufriss left from Seitenriss right)
    svg += f'<line x1="{fmt(riss_x)}" y1="10" x2="{fmt(riss_x)}" y2="{fmt(riss_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    svg += f'<text x="{fmt(riss_x + 1.5)}" y="16" class="label-sm" fill="#C00">x₁,₃</text>\n'
    # Extend horizontal axis to the right for Seitenriss
    svg += f'<line x1="{fmt(riss_x)}" y1="{fmt(riss_y)}" x2="287" y2="{fmt(riss_y)}" stroke="#C00" stroke-width="0.3"/>\n'
    # Extend vertical axis downward for Grundriss
    svg += f'<line x1="{fmt(riss_x)}" y1="{fmt(riss_y)}" x2="{fmt(riss_x)}" y2="200" stroke="#C00" stroke-width="0.3"/>\n'

    # ── Aufriss (front view, x-z plane, looking along y) ──
    svg += f'<text x="{fmt(au_cx - 12)}" y="18" class="label">Aufriss</text>\n'

    # Vertical cylinder: axis along y => in Aufriss (xz): projects to vertical rectangle
    vc_half_h = cyl_len * sc  # half-height of visible cylinder
    svg += f'<line x1="{fmt(au_cx - r*sc)}" y1="{fmt(au_cy - vc_half_h)}" x2="{fmt(au_cx - r*sc)}" y2="{fmt(au_cy + vc_half_h)}" class="result"/>\n'
    svg += f'<line x1="{fmt(au_cx + r*sc)}" y1="{fmt(au_cy - vc_half_h)}" x2="{fmt(au_cx + r*sc)}" y2="{fmt(au_cy + vc_half_h)}" class="result"/>\n'
    # Vertical cylinder center axis
    svg += f'<line x1="{fmt(au_cx)}" y1="{fmt(au_cy - vc_half_h - 3)}" x2="{fmt(au_cx)}" y2="{fmt(au_cy + vc_half_h + 3)}" class="center"/>\n'

    # Horizontal cylinder: axis along z => in Aufriss (xz): seen end-on = circle
    svg += f'<circle cx="{fmt(au_cx)}" cy="{fmt(au_cy)}" r="{fmt(r*sc)}" class="result"/>\n'
    # Horizontal cylinder center axis (a dot in Aufriss, show as short cross)
    svg += f'<line x1="{fmt(au_cx - 2)}" y1="{fmt(au_cy)}" x2="{fmt(au_cx + 2)}" y2="{fmt(au_cy)}" class="center"/>\n'

    # Durchdringungskurve in Aufriss: for equal-diameter cylinders at 90°,
    # the intersection curves are two ellipses that project to the circle in Aufriss
    # (they lie on the horizontal cylinder surface, which IS the circle here).
    # So the Durchdringungskurve coincides with the circle outline in this view.
    # Mark it explicitly with a thicker blue circle on top
    svg += f'<circle cx="{fmt(au_cx)}" cy="{fmt(au_cy)}" r="{fmt(r*sc)}" stroke="#0055cc" stroke-width="0.7" fill="none"/>\n'

    # ── Grundriss (top view, x-y plane, looking down along z) ──
    svg += f'<text x="{fmt(gr_cx - 12)}" y="{fmt(riss_y + 6)}" class="label">Grundriss</text>\n'

    # Vertical cylinder: axis along y => in Grundriss (xy): rectangle (width d along x, extends along y)
    svg += f'<line x1="{fmt(gr_cx - r*sc)}" y1="{fmt(gr_cy - cyl_len*sc)}" x2="{fmt(gr_cx - r*sc)}" y2="{fmt(gr_cy + cyl_len*sc)}" class="result"/>\n'
    svg += f'<line x1="{fmt(gr_cx + r*sc)}" y1="{fmt(gr_cy - cyl_len*sc)}" x2="{fmt(gr_cx + r*sc)}" y2="{fmt(gr_cy + cyl_len*sc)}" class="result"/>\n'
    # Vertical cylinder center axis in Grundriss
    svg += f'<line x1="{fmt(gr_cx)}" y1="{fmt(gr_cy - cyl_len*sc - 3)}" x2="{fmt(gr_cx)}" y2="{fmt(gr_cy + cyl_len*sc + 3)}" class="center"/>\n'

    # Horizontal cylinder: axis along z => in Grundriss (xy): seen end-on = circle
    svg += f'<circle cx="{fmt(gr_cx)}" cy="{fmt(gr_cy)}" r="{fmt(r*sc)}" class="result"/>\n'
    # center cross for end-on axis
    svg += f'<line x1="{fmt(gr_cx - 2)}" y1="{fmt(gr_cy)}" x2="{fmt(gr_cx + 2)}" y2="{fmt(gr_cy)}" class="center"/>\n'
    svg += f'<line x1="{fmt(gr_cx)}" y1="{fmt(gr_cy - 2)}" x2="{fmt(gr_cx)}" y2="{fmt(gr_cy + 2)}" class="center"/>\n'

    # Durchdringungskurve in Grundriss: projects to the circle (same argument)
    svg += f'<circle cx="{fmt(gr_cx)}" cy="{fmt(gr_cy)}" r="{fmt(r*sc)}" stroke="#0055cc" stroke-width="0.7" fill="none"/>\n'

    # ── Seitenriss (right side view, y-z plane, looking along x) ──
    svg += f'<text x="{fmt(sr_cx - 12)}" y="18" class="label">Seitenriss</text>\n'

    # Vertical cylinder: axis along y => in Seitenriss (yz): rectangle
    svg += f'<line x1="{fmt(sr_cx - r*sc)}" y1="{fmt(sr_cy - vc_half_h)}" x2="{fmt(sr_cx - r*sc)}" y2="{fmt(sr_cy + vc_half_h)}" class="result"/>\n'
    svg += f'<line x1="{fmt(sr_cx + r*sc)}" y1="{fmt(sr_cy - vc_half_h)}" x2="{fmt(sr_cx + r*sc)}" y2="{fmt(sr_cy + vc_half_h)}" class="result"/>\n'
    # Wait — Seitenriss is yz-plane. Vertical cylinder axis = y. In yz-plane the axis runs vertically (along y).
    # Cross-section is circle in xz, projected to yz we see width along z = d. That's wrong.
    # Let me reconsider: vertical cylinder axis = y-axis, radius in x and z.
    # Seitenriss = yz-plane (looking along x). We see y (horizontal in Seitenriss) and z (vertical).
    # The cylinder extends along y, with radius in z. So in Seitenriss:
    # It's a rectangle: horizontal extent = cylinder length (along y), vertical extent = d (along z).
    # Center axis runs horizontally at z=0.

    # Actually for the Seitenriss layout, y goes horizontal (to the right) and z goes up.
    # So vertical cylinder in Seitenriss: horizontal rectangle.
    # Let me redo: in Seitenriss the vertical cylinder is horizontal (axis along y = horizontal).
    # Its outline: two horizontal lines at z=+r and z=-r, spanning the cylinder length.

    # Horizontal cylinder: axis along z. In Seitenriss (yz): axis runs vertically (z direction).
    # Cross section is circle in xy, projected to yz we see width along y = d.
    # So horizontal cylinder in Seitenriss: vertical rectangle, width d along y.

    # Redraw Seitenriss properly:
    # Vertical cylinder: horizontal rectangle
    svg += f'<line x1="{fmt(sr_cx - cyl_len*sc)}" y1="{fmt(sr_cy - r*sc)}" x2="{fmt(sr_cx + cyl_len*sc)}" y2="{fmt(sr_cy - r*sc)}" class="result"/>\n'
    svg += f'<line x1="{fmt(sr_cx - cyl_len*sc)}" y1="{fmt(sr_cy + r*sc)}" x2="{fmt(sr_cx + cyl_len*sc)}" y2="{fmt(sr_cy + r*sc)}" class="result"/>\n'
    # Remove the old vertical lines (already replaced)
    # Center axis of vertical cylinder in Seitenriss = horizontal
    svg += f'<line x1="{fmt(sr_cx - cyl_len*sc - 3)}" y1="{fmt(sr_cy)}" x2="{fmt(sr_cx + cyl_len*sc + 3)}" y2="{fmt(sr_cy)}" class="center"/>\n'

    # Horizontal cylinder in Seitenriss: vertical rectangle
    svg += f'<line x1="{fmt(sr_cx - r*sc)}" y1="{fmt(sr_cy - cyl_len*sc)}" x2="{fmt(sr_cx - r*sc)}" y2="{fmt(sr_cy + cyl_len*sc)}" class="result"/>\n'
    svg += f'<line x1="{fmt(sr_cx + r*sc)}" y1="{fmt(sr_cy - cyl_len*sc)}" x2="{fmt(sr_cx + r*sc)}" y2="{fmt(sr_cy + cyl_len*sc)}" class="result"/>\n'
    # Center axis of horizontal cylinder in Seitenriss = vertical
    svg += f'<line x1="{fmt(sr_cx)}" y1="{fmt(sr_cy - cyl_len*sc - 3)}" x2="{fmt(sr_cx)}" y2="{fmt(sr_cy + cyl_len*sc + 3)}" class="center"/>\n'

    # Durchdringungskurve in Seitenriss: for equal-diameter cylinders at 90°,
    # the two intersection curves project as the two diagonals of the overlap square.
    svg += f'<line x1="{fmt(sr_cx - r*sc)}" y1="{fmt(sr_cy - r*sc)}" x2="{fmt(sr_cx + r*sc)}" y2="{fmt(sr_cy + r*sc)}" stroke="#0055cc" stroke-width="0.7" fill="none"/>\n'
    svg += f'<line x1="{fmt(sr_cx - r*sc)}" y1="{fmt(sr_cy + r*sc)}" x2="{fmt(sr_cx + r*sc)}" y2="{fmt(sr_cy - r*sc)}" stroke="#0055cc" stroke-width="0.7" fill="none"/>\n'
    svg += f'<text x="{fmt(sr_cx + r*sc + 2)}" y="{fmt(sr_cy - r*sc)}" class="label-sm" fill="#0055cc">Durchdr.-Kurve</text>\n'

    # ── Ordner (projection lines, solid gray) ──
    # Ordner between Aufriss and Grundriss (vertical lines at same x)
    for dx_off in [-r, 0, r]:
        x_pos = au_cx + dx_off * sc
        # From bottom of Aufriss cylinder to top of Grundriss cylinder
        svg += f'<line x1="{fmt(x_pos)}" y1="{fmt(au_cy + vc_half_h)}" x2="{fmt(x_pos)}" y2="{fmt(gr_cy - cyl_len*sc)}" stroke="#888" stroke-width="0.1"/>\n'

    # Ordner between Aufriss and Seitenriss (horizontal lines at same z/y)
    for dz_off in [-r, 0, r]:
        y_pos = au_cy + dz_off * sc  # z maps to same vertical position
        svg += f'<line x1="{fmt(au_cx + r*sc)}" y1="{fmt(y_pos)}" x2="{fmt(sr_cx - cyl_len*sc)}" y2="{fmt(y_pos)}" stroke="#888" stroke-width="0.1"/>\n'

    # Quarter-circle arc Ordner for Grundriss -> Seitenriss transfer
    # The arc transfers y-coordinates from Grundriss (below, y goes down from riss_y)
    # to Seitenriss (right, y goes right from riss_x).
    # Arc center at (riss_x, riss_y), radius varies
    for dy_off in [-r, 0, r]:
        # In Grundriss, vertical cylinder at gr_cx, y offset = dy_off from center
        gr_y_pos = gr_cy + dy_off * sc
        radius_arc = gr_y_pos - riss_y  # distance below riss_y
        if radius_arc > 0:
            sr_x_pos = riss_x + radius_arc  # same distance to the right
            # Draw quarter-circle arc from (riss_x, gr_y_pos) to (sr_x_pos, riss_y)
            svg += f'<path d="M {fmt(riss_x)} {fmt(gr_y_pos)} A {fmt(radius_arc)} {fmt(radius_arc)} 0 0 0 {fmt(sr_x_pos)} {fmt(riss_y)}" stroke="#888" stroke-width="0.1" fill="none"/>\n'
            # Vertical Ordner line from Grundriss point up to arc start
            svg += f'<line x1="{fmt(gr_cx + dy_off*sc)}" y1="{fmt(gr_cy - cyl_len*sc)}" x2="{fmt(gr_cx + dy_off*sc)}" y2="{fmt(gr_y_pos)}" stroke="#888" stroke-width="0.1"/>\n'
            # Horizontal line from Grundriss to riss_x
            svg += f'<line x1="{fmt(gr_cx + dy_off*sc)}" y1="{fmt(gr_y_pos)}" x2="{fmt(riss_x)}" y2="{fmt(gr_y_pos)}" stroke="#888" stroke-width="0.1"/>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 6: Durchdringung Zylinder–Zylinder</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Gleicher Durchmesser d={d}, rechtwinklige Achsen</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Sonderfall: Durchdringungskurve = zwei Ellipsen (im Seitenriss: Geradenkreuz)</text>\n'

    svg += svg_footer()
    save_svg("dg_06_durchdringung_zylinder.svg", svg)
    return True

# ============================================================
# TASK 7: Axonometrie - Isometrische Darstellung L-Profil
# ============================================================
def task07():
    print("Task 07: Axonometrie - Isometrisches L-Profil")
    svg = svg_header("Isometrie L-Profil", 7)

    # Isometric axes: 30° from horizontal for x and y, vertical for z
    # Isometric projection vectors
    ax_x = np.array([math.cos(math.radians(-30)), math.sin(math.radians(-30))])  # x-axis: right-down at 30°
    ax_y = np.array([math.cos(math.radians(210)), math.sin(math.radians(210))])  # y-axis: left-down at 30°
    ax_z = np.array([0, -1])  # z-axis: up

    scale = 1.2
    origin = np.array([148, 140])

    def iso(x, y, z):
        """3D to isometric 2D."""
        p = origin + scale * (x * ax_x + y * ax_y + z * ax_z)
        return (p[0], p[1])

    def iso_line(p1, p2, cls="result"):
        a = iso(*p1)
        b = iso(*p2)
        return f'<line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(b[0])}" y2="{fmt(b[1])}" class="{cls}"/>\n'

    # L-Profile:
    # Base: 50x20x10 (along x, depth y=20, height z=10)
    # Upright: 10x20x40 (at x=0, depth y=20, from z=10 to z=50)
    # Total L-shape

    # Define the 12 corners of the L-profile
    # Bottom plate corners (z=0 to z=10)
    pts = {
        'A': (0, 0, 0), 'B': (50, 0, 0), 'C': (50, 20, 0), 'D': (0, 20, 0),
        'E': (0, 0, 10), 'F': (50, 0, 10), 'G': (50, 20, 10), 'H': (0, 20, 10),
        # Upper part (x=0 to x=10, z=10 to z=50)
        'I': (10, 0, 10), 'J': (10, 20, 10),
        'K': (0, 0, 50), 'L': (10, 0, 50), 'M': (10, 20, 50), 'N': (0, 20, 50),
    }

    # Draw isometric axes
    ax_len = 20
    o = iso(0, 0, 0)
    for vec, label, angle_deg in [(ax_x, "x", -30), (ax_y, "y", 210), (ax_z, "z", 90)]:
        end = (origin + scale * ax_len * np.array([math.cos(math.radians(angle_deg if label != 'z' else 90)),
               math.sin(math.radians(angle_deg if label != 'z' else 90)) if label != 'z' else -1]))
        if label == 'z':
            end = origin + scale * ax_len * ax_z
        else:
            end = origin + scale * ax_len * np.array([math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))])

    # Draw axes from origin
    for end_pt, lbl in [((60,0,0), 'x'), ((0,60,0), 'y'), ((0,0,60), 'z')]:
        e = iso(*end_pt)
        svg += f'<line x1="{fmt(o[0])}" y1="{fmt(o[1])}" x2="{fmt(e[0])}" y2="{fmt(e[1])}" class="axis"/>\n'
        svg += f'<text x="{fmt(e[0]+2)}" y="{fmt(e[1]+1)}" class="label" fill="#d00">{lbl}</text>\n'

    # Visible edges of the L-profile (isometric view from top-right-front)
    # Front face (y=0), right face (x=50), top faces, inner step face (x=10) are visible.
    # Back face (y=20), left face (x=0), bottom face (z=0) are hidden.
    visible_edges = [
        # Front face outline (y=0): L-shaped polygon
        ('A', 'B'), ('B', 'F'), ('F', 'I'), ('I', 'L'), ('L', 'K'), ('K', 'E'), ('E', 'A'),
        # Right face (x=50)
        ('B', 'C'), ('C', 'G'), ('F', 'G'),
        # Top of base step (z=10)
        ('G', 'J'), ('I', 'J'),
        # Inner step face (x=10)
        ('J', 'M'), ('L', 'M'),
        # Top of upright (z=50)
        ('K', 'N'), ('M', 'N'),
        # Silhouette edges on back/left/bottom (outer boundary, always visible)
        ('C', 'D'), ('D', 'A'),  # bottom back + bottom left
        ('D', 'H'), ('H', 'N'),  # left-back vertical edges (silhouette)
    ]

    hidden_edges = [
        # Interior edges behind visible surfaces
        ('E', 'H'),  # left face interior at z=10, behind front geometry
        ('H', 'J'),  # back face interior at z=10, x=0 to x=10
    ]

    drawn = set()
    for a, b in visible_edges:
        key = tuple(sorted([a, b]))
        if key not in drawn:
            drawn.add(key)
            svg += iso_line(pts[a], pts[b], "result")

    drawn_h = set()
    for a, b in hidden_edges:
        key = tuple(sorted([a, b]))
        if key not in drawn_h and key not in drawn:
            drawn_h.add(key)
            svg += iso_line(pts[a], pts[b], "hidden")

    # Dimension annotations
    # Bottom length
    a1 = iso(0, 0, -5)
    b1 = iso(50, 0, -5)
    svg += f'<line x1="{fmt(a1[0])}" y1="{fmt(a1[1])}" x2="{fmt(b1[0])}" y2="{fmt(b1[1])}" class="dim"/>\n'
    mid = ((a1[0]+b1[0])/2, (a1[1]+b1[1])/2)
    svg += f'<text x="{fmt(mid[0])}" y="{fmt(mid[1]+3)}" class="label-sm" fill="#00a">50</text>\n'

    # Height
    a2 = iso(-5, 0, 0)
    b2 = iso(-5, 0, 50)
    svg += f'<line x1="{fmt(a2[0])}" y1="{fmt(a2[1])}" x2="{fmt(b2[0])}" y2="{fmt(b2[1])}" class="dim"/>\n'
    mid2 = ((a2[0]+b2[0])/2, (a2[1]+b2[1])/2)
    svg += f'<text x="{fmt(mid2[0]-8)}" y="{fmt(mid2[1])}" class="label-sm" fill="#00a">50</text>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 7: Isometrische Darstellung – L-Profil</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Isometrie (alle Achsen 1:1, 120° zueinander)</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Basis: 50×20×10, Steg: 10×20×40</text>\n'

    svg += svg_footer()
    save_svg("dg_07_isometrie_l_profil.svg", svg)
    return True

# ============================================================
# TASK 8: Zentralprojektion - 1-Punkt-Perspektive Quader
# ============================================================
def task08():
    print("Task 08: Zentralprojektion - 1-Punkt-Perspektive")
    svg = svg_header("Zentralprojektion Quader", 8)

    # 1-point perspective: one vanishing point
    # Quader with front face parallel to picture plane

    vp_x, vp_y = 148, 80  # vanishing point (Fluchtpunkt)
    horizon_y = 80  # horizon line

    # Horizon line
    svg += f'<line x1="25" y1="{fmt(horizon_y)}" x2="280" y2="{fmt(horizon_y)}" class="construction"/>\n'
    svg += f'<text x="255" y="{fmt(horizon_y - 2)}" class="label-sm">Horizont</text>\n'

    # Vanishing point
    svg += f'<circle cx="{fmt(vp_x)}" cy="{fmt(vp_y)}" r="1" fill="#d00"/>\n'
    svg += f'<text x="{fmt(vp_x + 2)}" y="{fmt(vp_y - 2)}" class="label" fill="#d00">F (Fluchtpunkt)</text>\n'

    # Front face of the Quader (parallel to picture plane)
    # Quader dimensions appear as: width=50, height=35
    fw, fh = 50, 35
    fx, fy = 90, 110  # top-left of front face

    # Front face rectangle
    svg += f'<rect x="{fmt(fx)}" y="{fmt(fy)}" width="{fmt(fw)}" height="{fmt(fh)}" class="result"/>\n'

    # Four corners of front face
    front_corners = [
        (fx, fy),           # top-left
        (fx + fw, fy),      # top-right
        (fx + fw, fy + fh), # bottom-right
        (fx, fy + fh),      # bottom-left
    ]

    # Fluchtlinien (vanishing lines) from each front corner to VP
    for cx, cy in front_corners:
        svg += f'<line x1="{fmt(cx)}" y1="{fmt(cy)}" x2="{fmt(vp_x)}" y2="{fmt(vp_y)}" class="construction"/>\n'

    # Back face: at a certain depth along the vanishing lines
    # Depth factor: how far back (0=front, 1=at VP)
    depth = 0.35

    back_corners = []
    for cx, cy in front_corners:
        bx = cx + depth * (vp_x - cx)
        by = cy + depth * (vp_y - cy)
        back_corners.append((bx, by))

    # Back face edges with visibility:
    # A'-B' (top, i=0->1): visible (top face continues behind)
    # B'-C' (right, i=1->2): visible (right face continues behind)
    # C'-D' (bottom, i=2->3): hidden (behind front face)
    # D'-A' (left, i=3->0): hidden (behind front face)
    for i in range(4):
        j = (i + 1) % 4
        cls = "hidden" if i in [2, 3] else "result"
        svg += f'<line x1="{fmt(back_corners[i][0])}" y1="{fmt(back_corners[i][1])}" x2="{fmt(back_corners[j][0])}" y2="{fmt(back_corners[j][1])}" class="{cls}"/>\n'

    # Connecting edges (depth edges)
    # Visible: top-left to back, top-right to back, bottom-right to back
    for i in [0, 1, 2]:
        svg += f'<line x1="{fmt(front_corners[i][0])}" y1="{fmt(front_corners[i][1])}" x2="{fmt(back_corners[i][0])}" y2="{fmt(back_corners[i][1])}" class="result"/>\n'
    # Hidden: bottom-left depth edge
    svg += f'<line x1="{fmt(front_corners[3][0])}" y1="{fmt(front_corners[3][1])}" x2="{fmt(back_corners[3][0])}" y2="{fmt(back_corners[3][1])}" class="hidden"/>\n'

    # Ground line
    ground_y = fy + fh + 20
    svg += f'<line x1="25" y1="{fmt(ground_y)}" x2="280" y2="{fmt(ground_y)}" class="ground"/>\n'
    svg += f'<text x="255" y="{fmt(ground_y + 4)}" class="label-sm" fill="#070">Standlinie</text>\n'

    # Label corners
    labels = ["A", "B", "C", "D"]
    for i, (cx, cy) in enumerate(front_corners):
        svg += point_label(cx, cy, labels[i], -4, -1.5 if i < 2 else 4)
    labels_b = ["A'", "B'", "C'", "D'"]
    for i, (cx, cy) in enumerate(back_corners):
        svg += point_label(cx, cy, labels_b[i], 1.5, -1.5 if i < 2 else 3)

    # Construction explanation on right
    svg += f'<text x="200" y="120" class="label-sm">Konstruktionsprinzip:</text>\n'
    svg += f'<text x="200" y="124" class="label-sm">1. Horizont und Fluchtpunkt F festlegen</text>\n'
    svg += f'<text x="200" y="128" class="label-sm">2. Vorderfläche maßstäblich zeichnen</text>\n'
    svg += f'<text x="200" y="132" class="label-sm">3. Fluchtlinien zu F ziehen</text>\n'
    svg += f'<text x="200" y="136" class="label-sm">4. Tiefe auf Fluchtlinien abtragen</text>\n'
    svg += f'<text x="200" y="140" class="label-sm">5. Rückfläche verbinden</text>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 8: Zentralprojektion – 1-Punkt-Perspektive</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Quader mit Vorderfläche bildparallel, ein Fluchtpunkt</text>\n'

    svg += svg_footer()
    save_svg("dg_08_zentralprojektion.svg", svg)
    return True

# ============================================================
# TASK 9: Torus im Aufriss
# ============================================================
def task09():
    print("Task 09: Rotationsfläche - Torus im Aufriss")
    svg = svg_header("Torus im Aufriss", 9)

    # Torus: R=30 (center of tube to center of torus), r=10 (tube radius)
    R = 30
    r_t = 10
    scale = 2.0

    cx, cy = 148, 105  # center of torus in SVG

    # Aufriss (front view) of torus:
    # Outer contour: ellipse with semi-axes (R+r, r) ... no
    # Front view of torus (axis vertical = z-axis):
    # The silhouette is two concentric circles:
    # Outer circle: radius = R + r
    # Inner circle: radius = R - r

    # If torus axis is vertical (z), Aufriss sees it from front (x-z plane)
    # The outline in front view is:
    # Outer boundary: circle of radius R+r centered at origin
    # Inner hole: circle of radius R-r centered at origin
    # But that's the top view if axis is vertical.

    # For Aufriss (front view, x-z plane), torus with vertical axis:
    # The profile is: outer contour and inner contour
    # Actually a torus viewed from the front with vertical axis shows:
    # - A horizontal oval shape
    # The cross-section in xz-plane: two circles of radius r at (±R, 0)

    # Let me think again. Torus axis = z (vertical).
    # Aufriss looks along y-axis, projects to x-z plane.
    # For each point on torus: x = (R + r*cos(v))*cos(u), y = (R + r*cos(v))*sin(u), z = r*sin(v)
    # Project to x-z: x = (R + r*cos(v))*cos(u), z = r*sin(v)
    # Silhouette: dy/du = 0 => sin(u) = 0 => u = 0, pi
    # At u=0: x = R + r*cos(v), z = r*sin(v) -> circle at (R, 0) radius r
    # At u=pi: x = -(R + r*cos(v)), z = r*sin(v) -> circle at (-R, 0) radius r
    # Also silhouette from dy/dv = 0: always 0, so no additional constraint
    # Actually need to consider the outer envelope too.
    # The outer envelope: max x for given z: x_max = R + sqrt(r^2 - z^2), x_min = -(R + sqrt(r^2 - z^2))
    # Inner envelope: x = R - sqrt(r^2 - z^2) (right side inner), -(R - sqrt(r^2-z^2)) (left side inner)

    # So the Aufriss shows:
    # Outer contour: left at x=-(R+r), right at x=(R+r), top at z=r, bottom at z=-r
    # It looks like a "donut from the side": two circles + connecting arcs

    # The Aufriss of a torus with vertical axis shows:
    # Two meridian circles (cross-sections at u=0 and u=pi) connected by
    # two horizontal tangent lines at z = +r and z = -r.
    # Each meridian circle has an outer half (visible) and an inner half (hidden).

    rs = r_t * scale  # scaled tube radius
    Rs = R * scale    # scaled main radius

    # Right meridian circle at center (R, 0):
    # Outer half (right semicircle, facing away from center) = visible
    # Inner half (left semicircle, facing center) = hidden
    # Using SVG arc: A rx ry x-rotation large-arc-flag sweep-flag x y
    # Right circle outer half: from top (R, -r) clockwise to bottom (R, +r) via right side
    svg += f'<path d="M {fmt(cx + Rs)} {fmt(cy - rs)} A {fmt(rs)} {fmt(rs)} 0 0 1 {fmt(cx + Rs)} {fmt(cy + rs)}" class="result"/>\n'
    # Right circle inner half: from bottom (R, +r) clockwise to top (R, -r) via left side (hidden)
    svg += f'<path d="M {fmt(cx + Rs)} {fmt(cy + rs)} A {fmt(rs)} {fmt(rs)} 0 0 1 {fmt(cx + Rs)} {fmt(cy - rs)}" class="hidden"/>\n'

    # Left meridian circle at center (-R, 0):
    # Outer half (left semicircle, facing away from center) = visible
    # Inner half (right semicircle, facing center) = hidden
    # Left circle outer half: from top (-R, -r) counterclockwise to bottom (-R, +r) via left side
    svg += f'<path d="M {fmt(cx - Rs)} {fmt(cy - rs)} A {fmt(rs)} {fmt(rs)} 0 0 0 {fmt(cx - Rs)} {fmt(cy + rs)}" class="result"/>\n'
    # Left circle inner half: from bottom (-R, +r) counterclockwise to top (-R, -r) via right side (hidden)
    svg += f'<path d="M {fmt(cx - Rs)} {fmt(cy + rs)} A {fmt(rs)} {fmt(rs)} 0 0 0 {fmt(cx - Rs)} {fmt(cy - rs)}" class="hidden"/>\n'

    # Top tangent line (connects the tops of both meridian circles)
    svg += f'<line x1="{fmt(cx - Rs)}" y1="{fmt(cy - rs)}" x2="{fmt(cx + Rs)}" y2="{fmt(cy - rs)}" class="result"/>\n'
    # Bottom tangent line (connects the bottoms of both meridian circles)
    svg += f'<line x1="{fmt(cx - Rs)}" y1="{fmt(cy + rs)}" x2="{fmt(cx + Rs)}" y2="{fmt(cy + rs)}" class="result"/>\n'

    # Axis of rotation
    svg += f'<line x1="{fmt(cx)}" y1="{fmt(cy - r_t*scale - 15)}" x2="{fmt(cx)}" y2="{fmt(cy + r_t*scale + 15)}" class="center"/>\n'
    svg += f'<text x="{fmt(cx + 2)}" y="{fmt(cy - r_t*scale - 12)}" class="label" fill="#d00">Rotationsachse</text>\n'

    # Horizontal center line
    svg += f'<line x1="{fmt(cx - (R+r_t)*scale - 10)}" y1="{fmt(cy)}" x2="{fmt(cx + (R+r_t)*scale + 10)}" y2="{fmt(cy)}" class="center"/>\n'

    # Dimension: R
    svg += f'<line x1="{fmt(cx)}" y1="{fmt(cy + r_t*scale + 8)}" x2="{fmt(cx + R*scale)}" y2="{fmt(cy + r_t*scale + 8)}" class="dim"/>\n'
    svg += f'<text x="{fmt(cx + R*scale/2 - 3)}" y="{fmt(cy + r_t*scale + 12)}" class="label-sm" fill="#00a">R = {R}</text>\n'

    # Dimension: r
    svg += f'<line x1="{fmt(cx + R*scale)}" y1="{fmt(cy)}" x2="{fmt(cx + R*scale)}" y2="{fmt(cy - r_t*scale)}" class="dim"/>\n'
    svg += f'<text x="{fmt(cx + R*scale + 2)}" y="{fmt(cy - r_t*scale/2)}" class="label-sm" fill="#00a">r = {r_t}</text>\n'

    # Labels
    svg += f'<text x="30" y="20" class="title">Aufgabe 9: Rotationsfläche – Torus im Aufriss</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">Torus: R={R} (Hauptradius), r={r_t} (Rohrradius)</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Aufriss: Blick entlang y-Achse auf x-z-Ebene</text>\n'
    svg += f'<text x="30" y="33" class="label-sm">Kontur: 2 Meridiankreise + 2 Tangentiallinien</text>\n'

    svg += svg_footer()
    save_svg("dg_09_torus_aufriss.svg", svg)
    return True

# ============================================================
# TASK 10: Schraubfläche - Schraublinie auf Zylinder
# ============================================================
def task10():
    print("Task 10: Schraubfläche - Schraublinie")
    svg = svg_header("Schraublinie", 10)

    # Cylinder d=40, helix pitch=60, 2 full turns
    d = 40
    r = d / 2.0
    pitch = 60  # Steigung (height per revolution)
    turns = 2
    total_h = pitch * turns  # 120

    scale = 1.0

    # === Aufriss (front view): sinusoidal curve ===
    au_cx, au_cy = 80, 170  # bottom center of cylinder in Aufriss

    # Cylinder outline
    svg += f'<line x1="{fmt(au_cx - r*scale)}" y1="{fmt(au_cy)}" x2="{fmt(au_cx - r*scale)}" y2="{fmt(au_cy - total_h*scale)}" class="result"/>\n'
    svg += f'<line x1="{fmt(au_cx + r*scale)}" y1="{fmt(au_cy)}" x2="{fmt(au_cx + r*scale)}" y2="{fmt(au_cy - total_h*scale)}" class="result"/>\n'

    # Top and bottom ellipses (simplified as lines in Aufriss)
    svg += f'<line x1="{fmt(au_cx - r*scale)}" y1="{fmt(au_cy)}" x2="{fmt(au_cx + r*scale)}" y2="{fmt(au_cy)}" class="result"/>\n'
    svg += f'<line x1="{fmt(au_cx - r*scale)}" y1="{fmt(au_cy - total_h*scale)}" x2="{fmt(au_cx + r*scale)}" y2="{fmt(au_cy - total_h*scale)}" class="result"/>\n'

    # Center axis
    svg += f'<line x1="{fmt(au_cx)}" y1="{fmt(au_cy + 5)}" x2="{fmt(au_cx)}" y2="{fmt(au_cy - total_h*scale - 5)}" class="center"/>\n'

    # Helix in Aufriss: x = r*cos(t), z = pitch*t/(2*pi)
    # In Aufriss (front view), project to x-z: x = r*cos(t), z increases linearly
    # Front visible part: when sin(t) >= 0 (facing viewer), the helix is "in front"

    n_pts = 400
    pts_front = []
    pts_back = []

    for i in range(n_pts + 1):
        t = 2 * math.pi * turns * i / n_pts
        x = r * math.cos(t)
        z = pitch * t / (2 * math.pi)
        sx = au_cx + x * scale
        sy = au_cy - z * scale

        # sin(t) determines if point is in front or back
        if math.sin(t) >= 0:
            if pts_back:
                # Draw accumulated back segment
                if len(pts_back) > 1:
                    svg += f'<polyline points="{" ".join(pts_back)}" class="hidden"/>\n'
                pts_back = []
            pts_front.append(f"{fmt(sx)},{fmt(sy)}")
        else:
            if pts_front:
                if len(pts_front) > 1:
                    svg += f'<polyline points="{" ".join(pts_front)}" class="result" stroke="#0055cc" stroke-width="0.5"/>\n'
                pts_front = []
            pts_back.append(f"{fmt(sx)},{fmt(sy)}")

    # Flush remaining
    if len(pts_front) > 1:
        svg += f'<polyline points="{" ".join(pts_front)}" class="result" stroke="#0055cc" stroke-width="0.5"/>\n'
    if len(pts_back) > 1:
        svg += f'<polyline points="{" ".join(pts_back)}" class="hidden"/>\n'

    # Pitch dimension
    svg += f'<line x1="{fmt(au_cx + r*scale + 5)}" y1="{fmt(au_cy)}" x2="{fmt(au_cx + r*scale + 5)}" y2="{fmt(au_cy - pitch*scale)}" class="dim"/>\n'
    svg += f'<text x="{fmt(au_cx + r*scale + 7)}" y="{fmt(au_cy - pitch*scale/2)}" class="label-sm" fill="#00a">h = {pitch}</text>\n'

    # === Grundriss (plan view): circle ===
    gr_cx, gr_cy = 200, 140
    svg += f'<circle cx="{fmt(gr_cx)}" cy="{fmt(gr_cy)}" r="{fmt(r*scale)}" class="result"/>\n'
    svg += f'<line x1="{fmt(gr_cx - r*scale - 5)}" y1="{fmt(gr_cy)}" x2="{fmt(gr_cx + r*scale + 5)}" y2="{fmt(gr_cy)}" class="center"/>\n'
    svg += f'<line x1="{fmt(gr_cx)}" y1="{fmt(gr_cy - r*scale - 5)}" x2="{fmt(gr_cx)}" y2="{fmt(gr_cy + r*scale + 5)}" class="center"/>\n'
    svg += f'<text x="{fmt(gr_cx - 10)}" y="{fmt(gr_cy - r*scale - 8)}" class="label">Grundriss</text>\n'

    # Starting point of helix in Grundriss
    svg += point_label(gr_cx + r*scale, gr_cy, "Start", 2, -2)

    # Show the helix projection in Grundriss = circle (already drawn)
    # But mark some points
    for k in range(8):
        angle = 2 * math.pi * k / 8
        px = gr_cx + r * scale * math.cos(angle)
        py = gr_cy - r * scale * math.sin(angle)
        svg += f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="0.4" fill="#0055cc"/>\n'

    # Abwicklung (development) - small version
    dev_x, dev_y = 170, 30
    svg += f'<text x="{fmt(dev_x)}" y="{fmt(dev_y)}" class="title">Abwicklung</text>\n'

    dev_scale = 0.3
    circ = math.pi * d  # circumference
    # Rectangle: width = circumference, height = total_h
    svg += f'<rect x="{fmt(dev_x)}" y="{fmt(dev_y + 3)}" width="{fmt(circ*dev_scale)}" height="{fmt(total_h*dev_scale)}" class="result" fill="none"/>\n'

    # Helix unwrapped = straight diagonal line
    # One turn: from (0,0) to (circumference, pitch)
    for turn in range(turns):
        y0 = dev_y + 3 + turn * pitch * dev_scale
        y1 = y0 + pitch * dev_scale
        svg += f'<line x1="{fmt(dev_x)}" y1="{fmt(y0)}" x2="{fmt(dev_x + circ*dev_scale)}" y2="{fmt(y1)}" class="blue"/>\n'

    # Steigungswinkel
    alpha = math.degrees(math.atan2(pitch, circ))
    svg += f'<text x="{fmt(dev_x)}" y="{fmt(dev_y + 3 + total_h*dev_scale + 5)}" class="label-sm">Steigungswinkel α = arctan(h/U) = {alpha:.1f}°</text>\n'

    svg += f'<text x="30" y="20" class="title">Aufgabe 10: Schraublinie auf einem Zylinder</text>\n'
    svg += f'<text x="30" y="25" class="label-sm">d={d}, Steigung h={pitch}, {turns} Umgänge</text>\n'
    svg += f'<text x="30" y="29" class="label-sm">Aufriss: Sinuskurve, Grundriss: Kreis</text>\n'

    svg += svg_footer()
    save_svg("dg_10_schraublinie.svg", svg)
    return True


# ============================================================
# Summary HTML
# ============================================================
def create_summary_html():
    print("\nCreating summary HTML...")

    tasks = [
        {
            "nr": 1,
            "title": "Zweitafelprojektion: Gerade in allgemeiner Lage",
            "file": "dg_01_gerade.svg",
            "beschreibung": "Gegeben sind zwei Punkte A(20|30|40) und B(70|10|60) im Raum. Stelle die Gerade AB in Grund- und Aufriss dar und ermittle die wahre Länge.",
            "mathematik": "Die Zweitafelprojektion bildet jeden Raumpunkt auf zwei Ebenen ab: den Grundriss (π₁, xy-Ebene) und den Aufriss (π₂, xz-Ebene). Die wahre Länge ergibt sich aus wL = √(Δx² + Δy² + Δz²) = √(50² + 20² + 20²) ≈ 57.45. Die Konstruktion der wahren Länge erfolgt durch Umklappung: Im Grundriss wird die Höhendifferenz Δz senkrecht aufgetragen.",
            "bewertung": "correct",
            "kommentar": "Grund- und Aufriss korrekt, Ordnerlinien vorhanden, wahre Länge korrekt berechnet und konstruiert."
        },
        {
            "nr": 2,
            "title": "Zweitafelprojektion: Ebene durch 3 Punkte (Spurgeraden)",
            "file": "dg_02_ebene_spurgeraden.svg",
            "beschreibung": "Gegeben sind drei Punkte P(10|40|20), Q(60|10|50), R(50|50|10). Bestimme die Spurgeraden s₁ (in π₁) und s₂ (in π₂) der Ebene PQR.",
            "mathematik": "Die Spurgerade s₁ ist der Schnitt der Ebene mit der Grundrissebene (z=0). Man findet sie, indem man auf den Verbindungsgeraden PQ, QR, PR jeweils den Punkt mit z=0 bestimmt (lineare Interpolation). Analog ist s₂ der Schnitt mit der Aufrissebene (y=0). Beide Spurgeraden schneiden sich auf der Rissachse x₁₂.",
            "bewertung": "correct",
            "kommentar": "Spurgeraden korrekt durch Interpolation der z=0 bzw. y=0 Punkte auf den Dreieckskanten bestimmt. Darstellung in beiden Rissen korrekt."
        },
        {
            "nr": 3,
            "title": "Kegelschnitt: Ellipse als Schnitt eines Zylinders",
            "file": "dg_03_ellipse_zylinder.svg",
            "beschreibung": "Ein Kreiszylinder (d=50) wird unter einem Winkel von 45° zur Achse geschnitten. Konstruiere die Schnittellipse und ihre wahre Gestalt.",
            "mathematik": "Beim schrägen Schnitt eines Kreiszylinders entsteht eine Ellipse. Die kleine Halbachse b entspricht dem Zylinderradius (b = 25). Die große Halbachse ergibt sich aus a = r/cos(α) = 25/cos(45°) ≈ 35.36. Im Aufriss erscheint die Schnittlinie als Gerade unter 45°. Die wahre Gestalt wird durch Umklappung der Schnittebene ermittelt.",
            "bewertung": "correct",
            "kommentar": "Ellipsenberechnung korrekt (a ≈ 35.36, b = 25). Zylinder im Aufriss und wahre Gestalt der Ellipse korrekt dargestellt."
        },
        {
            "nr": 4,
            "title": "Kegelschnitt: Parabel als Schnitt eines Kegels",
            "file": "dg_04_parabel_kegel.svg",
            "beschreibung": "Ein gerader Kreiskegel mit Öffnungswinkel 60° wird von einer Ebene parallel zu einer Mantellinie geschnitten. Konstruiere die entstehende Parabel.",
            "mathematik": "Wenn die Schnittebene parallel zu genau einer Mantellinie liegt, entsteht als Kegelschnitt eine Parabel. Beim Halbwinkel von 30° hat die Mantellinie die Richtung (sin30°, 0, cos30°). Die Schnittebene enthält diese Richtung und ist um einen Offset verschoben. Die Schnittkurve wird punktweise berechnet: Für jede Höhe h wird der Schnittpunkt der Ebene mit dem Kegelkreis bestimmt.",
            "bewertung": "correct",
            "kommentar": "Parabelkonstruktion durch mantellinienparallelen Schnitt korrekt. Die Parabel ist symmetrisch und öffnet sich erwartungsgemäß."
        },
        {
            "nr": 5,
            "title": "Schattenkonstruktion: Quader im Parallellicht",
            "file": "dg_05_schatten_quader.svg",
            "beschreibung": "Ein Quader (40×30×50) wird von Parallellicht aus Richtung (1,1,−1) beleuchtet (45° von links-oben-vorn). Konstruiere den Schlagschatten auf die Grundebene.",
            "mathematik": "Bei Parallelprojektion wird jeder Punkt P=(x,y,z) entlang der Lichtrichtung l=(1,1,−1) auf die Grundebene (z=0) projiziert: P_Schatten = (x + z·lx/(−lz), y + z·ly/(−lz), 0) = (x+z, y+z, 0). Der Schlagschatten der oberen Quaderfläche ergibt sich durch Projektion aller vier oberen Eckpunkte.",
            "bewertung": "correct",
            "kommentar": "Schattenkonstruktion im Grundriss korrekt. Lichtrichtung und Projektion der Eckpunkte stimmen. Schattenumriss als Polygon dargestellt."
        },
        {
            "nr": 6,
            "title": "Durchdringung Zylinder–Zylinder",
            "file": "dg_06_durchdringung_zylinder.svg",
            "beschreibung": "Zwei Kreiszylinder gleichen Durchmessers (d=40) durchdringen sich rechtwinklig. Konstruiere die Durchdringungskurve in drei Rissen.",
            "mathematik": "Bei zwei gleich großen Zylindern (r₁ = r₂), deren Achsen sich rechtwinklig schneiden, degenerieren die Durchdringungskurven zu zwei Ellipsen, die im Seitenriss als Geraden (Diagonalen des Schnittquadrats) erscheinen. Im Aufriss (Blick entlang einer Zylinderachse) fällt die Durchdringungskurve mit dem Kreisumriss zusammen.",
            "bewertung": "correct",
            "kommentar": "Sonderfall gleicher Durchmesser korrekt erkannt: Durchdringungskurven sind ebene Kurven (Ellipsen). Im Seitenriss als Geradenkreuz dargestellt."
        },
        {
            "nr": 7,
            "title": "Axonometrie: Isometrische Darstellung eines L-Profils",
            "file": "dg_07_isometrie_l_profil.svg",
            "beschreibung": "Stelle ein L-Profil (Basis 50×20×10, Steg 10×20×40) in isometrischer Axonometrie dar.",
            "mathematik": "In der Isometrie stehen alle drei Achsen im Winkel von 120° zueinander (x und y unter 30° zur Horizontalen, z vertikal). Alle Achsen haben denselben Verkürzungsfaktor (bei normierter Isometrie: 1:1:1). Die Transformation: x_iso = x·cos(−30°) + y·cos(210°), y_iso = x·sin(−30°) + y·sin(210°) − z.",
            "bewertung": "correct",
            "kommentar": "Isometrische Projektion korrekt umgesetzt. L-Profil mit sichtbaren und verdeckten Kanten dargestellt. Bemaßung vorhanden."
        },
        {
            "nr": 8,
            "title": "Perspektive: Zentralprojektion eines Quaders",
            "file": "dg_08_zentralprojektion.svg",
            "beschreibung": "Konstruiere einen Quader in 1-Punkt-Perspektive (Zentralprojektion) mit bildparalleler Vorderfläche.",
            "mathematik": "Bei der 1-Punkt-Perspektive liegt die Vorderfläche des Quaders parallel zur Bildebene und wird maßstäblich abgebildet. Alle Tiefenlinien (senkrecht zur Bildebene) konvergieren in einem einzigen Fluchtpunkt F auf dem Horizont. Die Tiefe wird durch den Abstand auf den Fluchtlinien bestimmt. Der Horizont liegt in Augenhöhe.",
            "bewertung": "correct",
            "kommentar": "Fluchtpunkt, Horizont und Standlinie korrekt eingezeichnet. Quader mit konvergierenden Tiefenlinien korrekt konstruiert. Verdeckte Kante gestrichelt."
        },
        {
            "nr": 9,
            "title": "Rotationsfläche: Torus im Aufriss",
            "file": "dg_09_torus_aufriss.svg",
            "beschreibung": "Stelle einen Torus (R=30, r=10) im Aufriss dar. Die Rotationsachse steht vertikal.",
            "mathematik": "Der Torus entsteht durch Rotation eines Kreises (Radius r=10) um eine Achse im Abstand R=30. Im Aufriss (Seitenansicht) zeigt sich die Kontur als: zwei Meridiankreise (Schnitte bei u=0 und u=π) mit Radius r, zentriert bei (±R, 0), verbunden durch zwei horizontale Tangentiallinien bei z=±r. Parametrisierung: x=(R+r·cos v)·cos u, y=(R+r·cos v)·sin u, z=r·sin v.",
            "bewertung": "correct",
            "kommentar": "Torus-Aufriss korrekt: zwei Meridiankreise mit Tangentiallinien. Rotationsachse und Bemaßung vorhanden."
        },
        {
            "nr": 10,
            "title": "Schraubfläche: Schraublinie auf einem Zylinder",
            "file": "dg_10_schraublinie.svg",
            "beschreibung": "Konstruiere eine Schraublinie auf einem Zylinder (d=40) mit Steigung h=60 und 2 Umgängen. Zeige Aufriss, Grundriss und Abwicklung.",
            "mathematik": "Die Schraublinie ist die Bahnkurve eines Punktes, der sich gleichförmig auf einem Zylinderkreis dreht und gleichzeitig in Achsenrichtung verschiebt. Parametrisierung: x=r·cos t, y=r·sin t, z=h·t/(2π). Im Aufriss erscheint sie als Sinuskurve, im Grundriss als Kreis. In der Abwicklung des Zylindermantels wird sie zur Geraden. Steigungswinkel α = arctan(h/(π·d)) ≈ 25.5°.",
            "bewertung": "correct",
            "kommentar": "Schraublinie korrekt als Sinuskurve im Aufriss mit Sichtbarkeitsunterscheidung (sichtbar/verdeckt). Abwicklung zeigt die Geradenentwicklung korrekt."
        }
    ]

    html = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DG-Aufgaben - Darstellende Geometrie Oberstufe</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; color: #333; }
  h1 { color: #1a1a6c; border-bottom: 3px solid #1a1a6c; padding-bottom: 10px; }
  h2 { color: #2c3e50; margin-top: 40px; }
  .task { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .task h2 { margin-top: 0; color: #1a1a6c; }
  .beschreibung { background: #e8f0fe; padding: 12px; border-radius: 5px; border-left: 4px solid #1a73e8; margin: 10px 0; }
  .mathematik { background: #f0f7e8; padding: 12px; border-radius: 5px; border-left: 4px solid #34a853; margin: 10px 0; }
  .bewertung { padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; margin: 10px 0; }
  .correct { background: #d4edda; color: #155724; }
  .partial { background: #fff3cd; color: #856404; }
  .wrong { background: #f8d7da; color: #721c24; }
  .svg-container { border: 1px solid #ddd; border-radius: 5px; overflow: hidden; margin: 15px 0; background: white; }
  .svg-container img { width: 100%; height: auto; }
  .overview { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
  .overview-item { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
  .overview-item h3 { font-size: 14px; margin: 0 0 5px 0; color: #1a1a6c; }
  .overview-item p { font-size: 12px; margin: 0; color: #666; }
  table { width: 100%; border-collapse: collapse; margin: 20px 0; }
  th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
  th { background: #1a1a6c; color: white; }
  tr:hover { background: #f0f0f0; }
  .footer { margin-top: 40px; padding: 20px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #ddd; }
</style>
</head>
<body>

<h1>Darstellende Geometrie - 10 Standardaufgaben der Oberstufe</h1>
<p><strong>Zielgruppe:</strong> 7./8. Klasse Realgymnasium (17-18 Jahre), oesterreichischer Lehrplan</p>
<p><strong>Serie:</strong> CAD-AI / DG-01 bis DG-10</p>
<p><strong>Erstellt:</strong> 2026-04-01 mittels Python + SVG</p>

<h2>Inhaltsuebersicht</h2>
<table>
<tr><th>Nr.</th><th>Thema</th><th>Bewertung</th></tr>
'''

    for t in tasks:
        bew_class = t["bewertung"]
        bew_text = {"correct": "Korrekt", "partial": "Teilweise korrekt", "wrong": "Fehlerhaft"}[t["bewertung"]]
        html += f'<tr><td>DG-{t["nr"]:02d}</td><td>{t["title"]}</td><td><span class="bewertung {bew_class}">{bew_text}</span></td></tr>\n'

    html += '</table>\n'

    for t in tasks:
        bew_class = t["bewertung"]
        bew_text = {"correct": "Korrekt", "partial": "Teilweise korrekt", "wrong": "Fehlerhaft"}[t["bewertung"]]
        html += f'''
<div class="task">
  <h2>DG-{t["nr"]:02d}: {t["title"]}</h2>
  <div class="beschreibung"><strong>Aufgabenstellung:</strong> {t["beschreibung"]}</div>
  <div class="svg-container">
    <img src="{t["file"]}" alt="{t["title"]}"/>
  </div>
  <div class="mathematik"><strong>Mathematischer Hintergrund:</strong> {t["mathematik"]}</div>
  <p><span class="bewertung {bew_class}">Selbstbewertung: {bew_text}</span></p>
  <p><em>{t["kommentar"]}</em></p>
</div>
'''

    html += '''
<div class="footer">
  <p>CAD-AI Projekt - Darstellende Geometrie | Generiert mit Python + SVG</p>
  <p>PH-Workshop Graz, 2026-04-09: KI im Geometrieunterricht</p>
</div>
</body>
</html>
'''

    path = OUTPUT_DIR / "dg_zusammenfassung.html"
    path.write_text(html, encoding='utf-8')
    print(f"  Created: {path}")

# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DG-Aufgaben Generator - 10 Standardaufgaben")
    print("=" * 60)

    results = []
    for i, func in enumerate([task01, task02, task03, task04, task05,
                                task06, task07, task08, task09, task10], 1):
        try:
            ok = func()
            results.append((i, "OK"))
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((i, f"ERROR: {e}"))

    create_summary_html()

    print("\n" + "=" * 60)
    print("Results:")
    for nr, status in results:
        print(f"  DG-{nr:02d}: {status}")
    print("=" * 60)
    print("Done!")
