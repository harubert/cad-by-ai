#!/usr/bin/env python3
"""
GZ-Aufgaben: 10 Standardaufgaben aus dem österreichischen
Geometrisches Zeichnen (GZ) Lehrplan für Sekundarstufe I.

Erzeugt SVG-Lösungen für jede Aufgabe.
"""

import math
from pathlib import Path

# ── Output directory ──────────────────────────────────────────────
OUT = Path(r"e:/2026_GoogleDrive/00 Arbeit/01 PH/Veranstaltungen/"
           r"2026_04_09 Graz KI im Geometrieunterricht/CAD_by_AI/output/gz")
OUT.mkdir(parents=True, exist_ok=True)

# ── SVG helpers ───────────────────────────────────────────────────

def svg_header(title: str, nr: int) -> str:
    """A4 landscape SVG with frame and title block."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="297mm" height="210mm"
     viewBox="0 0 297 210">
  <defs>
    <style>
      .visible {{ stroke: black; stroke-width: 0.25; fill: none; }}
      .hidden  {{ stroke: black; stroke-width: 0.1; fill: none;
                  stroke-dasharray: 2,1; }}
      .center  {{ stroke: red;   stroke-width: 0.1; fill: none;
                  stroke-dasharray: 4,1,1,1; }}
      .dim     {{ stroke: black; stroke-width: 0.1; fill: none; }}
      .proj    {{ stroke: #888;  stroke-width: 0.1; fill: none; }}
      .fill-section {{ fill: #dde; stroke: black; stroke-width: 0.25; }}
      .fill-light   {{ fill: #f5f5f5; stroke: black; stroke-width: 0.25; }}
      text {{ font-family: Arial, sans-serif; }}
    </style>
  </defs>
  <!-- Drawing frame: 20mm left, 10mm other sides -->
  <rect x="20" y="10" width="267" height="190"
        stroke="black" stroke-width="0.5" fill="none"/>
  <!-- Title block -->
  <rect x="197" y="185" width="90" height="15"
        stroke="black" stroke-width="0.35" fill="white"/>
  <text x="200" y="193" font-size="3.5" fill="black">Aufgabe {nr}: {title}</text>
  <text x="200" y="198" font-size="2.5" fill="black">GZ Sekundarstufe I | CAD_by_AI</text>
"""

def svg_footer() -> str:
    return "</svg>\n"

def line(x1, y1, x2, y2, cls="visible"):
    return f'  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{cls}"/>\n'

def rect(x, y, w, h, cls="visible"):
    return f'  <rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" class="{cls}"/>\n'

def circle_el(cx, cy, r, cls="visible"):
    return f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" class="{cls}"/>\n'

def ellipse_el(cx, cy, rx, ry, cls="visible", rot=0):
    if rot != 0:
        return (f'  <ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
                f'class="{cls}" transform="rotate({rot:.1f},{cx:.2f},{cy:.2f})"/>\n')
    return (f'  <ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
            f'class="{cls}"/>\n')

def polyline(pts, cls="visible", close=False):
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    tag = "polygon" if close else "polyline"
    return f'  <{tag} points="{d}" class="{cls}"/>\n'

def text_el(x, y, txt, size=3, anchor="start", color="black"):
    return (f'  <text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color}">{txt}</text>\n')

def path_d(cmds, cls="visible"):
    return f'  <path d="{cmds}" class="{cls}"/>\n'

def write_svg(name: str, content: str):
    p = OUT / name
    p.write_text(content, encoding="utf-8")
    print(f"  -> {p}")


# ══════════════════════════════════════════════════════════════════
# AUFGABE 1: Dreitafelprojektion eines Quaders 80x50x30
# ══════════════════════════════════════════════════════════════════
def aufgabe_01():
    title = "Dreitafelprojektion Quader 80 x 50 x 30"
    s = svg_header(title, 1)

    # Dimensions in mm (drawing scale 1:1 but we use mm in viewBox)
    bx, by, bz = 80, 50, 30  # Breite, Tiefe, Höhe (x, y, z)
    sc = 0.8  # scale to fit
    W, D, H = bx*sc, by*sc, bz*sc

    # Layout: Grundriss top-left, Aufriss top-right, Kreuzriss bottom-right
    gap = 15  # gap between views

    # Aufriss (Vorderansicht / front) – top-right area
    # Shows width (x) and height (z)
    ax_o, ay_o = 90, 30  # origin of Aufriss (top-left of view)
    s += text_el(ax_o + W/2, ay_o - 3, "Aufriss (Vorderansicht)", 3.5, "middle")
    s += rect(ax_o, ay_o, W, H, "visible")

    # Grundriss (Draufsicht / top) – below Aufriss
    # Shows width (x) and depth (y)
    gx_o = ax_o
    gy_o = ay_o + H + gap
    s += text_el(gx_o + W/2, gy_o - 3, "Grundriss (Draufsicht)", 3.5, "middle")
    s += rect(gx_o, gy_o, W, D, "visible")

    # Kreuzriss (Seitenansicht / side) – right of Aufriss
    # Shows depth (y) and height (z)
    kx_o = ax_o + W + gap
    ky_o = ay_o
    s += text_el(kx_o + D/2, ky_o - 3, "Kreuzriss (Seitenansicht)", 3.5, "middle")
    s += rect(kx_o, ky_o, D, H, "visible")

    # ── Rissachsen (coordinate axes separating views) ──
    # Horizontal axis between Aufriss and Grundriss
    riss_y = ay_o + H + gap / 2
    s += f'  <line x1="20" y1="{riss_y:.2f}" x2="287" y2="{riss_y:.2f}" stroke="#C00" stroke-width="0.3"/>\n'
    # Vertical axis between Aufriss and Kreuzriss
    riss_x = ax_o + W + gap / 2
    s += f'  <line x1="{riss_x:.2f}" y1="10" x2="{riss_x:.2f}" y2="200" stroke="#C00" stroke-width="0.3"/>\n'

    # Projection lines (Ordner)
    # Vertical from Aufriss to Grundriss
    s += line(ax_o, ay_o + H, ax_o, gy_o, "proj")
    s += line(ax_o + W, ay_o + H, ax_o + W, gy_o, "proj")
    # Horizontal from Aufriss to Kreuzriss
    s += line(ax_o + W, ay_o, kx_o, ay_o, "proj")
    s += line(ax_o + W, ay_o + H, kx_o, ay_o + H, "proj")
    # Viertelkreisboegen als Uebertragung Grundriss -> Kreuzriss
    # Ursprung = Schnittpunkt der roten Achsen
    origin_x = riss_x  # ax_o + W + gap/2
    origin_y = riss_y  # ay_o + H + gap/2

    # Fuer jede Tiefenkoordinate: Ordner horizontal vom Grundriss,
    # dann Viertelkreisbogen, dann vertikal zum Kreuzriss
    for d_val in [0, D]:
        gr_y = gy_o + d_val  # y-Position im Grundriss
        kr_x = kx_o + d_val  # x-Position im Kreuzriss
        r = gr_y - origin_y  # Radius = Abstand vom Ursprung

        if r > 0:
            # Horizontal vom Grundriss-Rand zum Ursprung
            s += line(gx_o + W, gr_y, origin_x, gr_y, "proj")
            # Viertelkreisbogen
            s += f'  <path d="M {origin_x:.2f},{gr_y:.2f} A {r:.2f},{r:.2f} 0 0,0 {kr_x:.2f},{origin_y:.2f}" fill="none" stroke="#aaa" stroke-width="0.08"/>\n'
            # Vertikal vom Bogen-Ende zum Kreuzriss
            s += line(kr_x, origin_y, kr_x, ky_o, "proj")

    # Dimension annotations
    s += text_el(ax_o + W/2, ay_o + H + 5, f"{bx}", 2.8, "middle", "#333")
    s += text_el(ax_o - 4, ay_o + H/2, f"{bz}", 2.8, "middle", "#333")
    s += text_el(gx_o + W + 4, gy_o + D/2, f"{by}", 2.8, "middle", "#333")

    s += svg_footer()
    write_svg("aufgabe_01_dreitafelprojektion.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 2: Schraegriss (Kavalierprojektion) Quader 80x50x30
# ══════════════════════════════════════════════════════════════════
def aufgabe_02():
    title = "Schraegriss (Kavalierprojekt.) Quader"
    s = svg_header(title, 2)

    bx, by, bz = 80, 50, 30
    sc = 1.0
    W, D, H = bx*sc, by*sc, bz*sc

    # Cavalier: depth axis at 45 degrees, scale 0.5
    d_scale = 0.5
    angle = math.radians(45)
    dx = D * d_scale * math.cos(angle)
    dy = D * d_scale * math.sin(angle)

    # Origin (front-bottom-left corner)
    ox, oy = 80, 140

    # 8 corners: front face (y=0) and back face (y=D)
    # Front: BL, BR, TR, TL
    f_bl = (ox, oy)
    f_br = (ox + W, oy)
    f_tr = (ox + W, oy - H)
    f_tl = (ox, oy - H)
    # Back: shift by (dx, -dy) -- up and right
    b_bl = (ox + dx, oy - dy)
    b_br = (ox + W + dx, oy - dy)
    b_tr = (ox + W + dx, oy - H - dy)
    b_tl = (ox + dx, oy - H - dy)

    # Visible edges
    # Front face
    s += polyline([f_bl, f_br, f_tr, f_tl], "visible", close=True)
    # Back top and right edges (visible)
    s += line(*b_tl, *b_tr, "visible")
    s += line(*b_tr, *b_br, "visible")
    # Connecting edges (visible: top-left, top-right, bottom-right)
    s += line(*f_tl, *b_tl, "visible")
    s += line(*f_tr, *b_tr, "visible")
    s += line(*f_br, *b_br, "visible")

    # Hidden edges (back face bottom and left, connecting bottom-left)
    s += line(*b_bl, *b_br, "hidden")
    s += line(*b_bl, *b_tl, "hidden")
    s += line(*f_bl, *b_bl, "hidden")

    # Dimension labels
    s += text_el(ox + W/2, oy + 6, f"Breite = {bx} mm", 3.5, "middle")
    s += text_el(ox - 5, oy - H/2, f"H\u00f6he = {bz}", 2.8, "end")
    s += text_el(ox + W + dx/2 + 3, oy - dy/2 + 2, f"Tiefe = {by}", 2.8, "start")

    # Axes
    s += text_el(ox + W + 5, oy + 2, "x", 3, "start", "blue")
    s += text_el(ox - 2, oy - H - 3, "z", 3, "end", "blue")
    s += text_el(ox + dx + 3, oy - dy - 2, "y", 3, "start", "blue")

    s += text_el(153, 40, "Kavalierprojektion", 5, "middle")
    s += text_el(153, 47, "Verkürzung Tiefe: 1:2, Winkel: 45\u00b0", 3, "middle", "#555")

    s += svg_footer()
    write_svg("aufgabe_02_schraegriss_quader.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 3: Normalriss Pyramide (Basis 60x60, Höhe 80)
# ══════════════════════════════════════════════════════════════════
def aufgabe_03():
    title = "Normalriss Pyramide (60 x 60, h=80)"
    s = svg_header(title, 3)

    base = 60
    h = 80
    sc = 0.8
    B = base * sc
    H = h * sc

    # Aufriss (front view): triangle
    ax_o, ay_o = 55, 30  # top-left of bounding box
    # Bottom edge
    s += line(ax_o, ay_o + H, ax_o + B, ay_o + H, "visible")
    # Left and right slant edges to apex
    apex_x = ax_o + B/2
    apex_y = ay_o
    s += line(ax_o, ay_o + H, apex_x, apex_y, "visible")
    s += line(ax_o + B, ay_o + H, apex_x, apex_y, "visible")
    # Center line (axis)
    s += line(apex_x, apex_y - 3, apex_x, ay_o + H + 3, "center")
    s += text_el(ax_o + B/2, ay_o - 5, "Aufriss", 3.5, "middle")

    # Grundriss (top view): square with diagonals (SICHTBAR = Seitenkanten von oben!)
    gap3 = 15  # gleicher Abstand wie vertikal
    gx_o = ax_o
    gy_o = ay_o + H + gap3
    s += rect(gx_o, gy_o, B, B, "visible")
    # Diagonals = Seitenkanten, von oben sichtbar -> durchgezogen!
    s += line(gx_o, gy_o, gx_o + B, gy_o + B, "visible")
    s += line(gx_o + B, gy_o, gx_o, gy_o + B, "visible")
    # Apex projection (center point)
    cx, cy = gx_o + B/2, gy_o + B/2
    s += circle_el(cx, cy, 0.5, "visible")
    # Center lines
    s += line(cx, gy_o - 3, cx, gy_o + B + 3, "center")
    s += line(gx_o - 3, cy, gx_o + B + 3, cy, "center")
    s += text_el(gx_o + B/2, gy_o - 5, "Grundriss", 3.5, "middle")

    # Kreuzriss (side view): same triangle shape, gleicher Abstand
    kx_o = ax_o + B + gap3
    ky_o = ay_o
    s += line(kx_o, ky_o + H, kx_o + B, ky_o + H, "visible")
    s += line(kx_o, ky_o + H, kx_o + B/2, ky_o, "visible")
    s += line(kx_o + B, ky_o + H, kx_o + B/2, ky_o, "visible")
    s += line(kx_o + B/2, ky_o - 3, kx_o + B/2, ky_o + H + 3, "center")
    s += text_el(kx_o + B/2, ky_o - 5, "Kreuzriss", 3.5, "middle")

    # ── Rissachsen ──
    riss_h_y = ay_o + H + gap3 / 2
    riss_v_x = ax_o + B + gap3 / 2
    s += f'  <line x1="20" y1="{riss_h_y:.2f}" x2="287" y2="{riss_h_y:.2f}" stroke="#C00" stroke-width="0.3"/>\n'
    s += f'  <line x1="{riss_v_x:.2f}" y1="10" x2="{riss_v_x:.2f}" y2="200" stroke="#C00" stroke-width="0.3"/>\n'

    # Ordner (feinste durchgezogene Linien, NICHT punktiert)
    # Vertikal: Aufriss -> Grundriss
    for x_val in [ax_o, ax_o + B, apex_x]:
        s += f'  <line x1="{x_val:.2f}" y1="{ay_o - 3:.2f}" x2="{x_val:.2f}" y2="{gy_o + B + 3:.2f}" stroke="#888" stroke-width="0.1"/>\n'
    # Horizontal: Aufriss -> Kreuzriss (inkl. Spitze!)
    for y_val in [ay_o, ay_o + H, apex_y]:
        s += f'  <line x1="{ax_o - 3:.2f}" y1="{y_val:.2f}" x2="{kx_o + B + 3:.2f}" y2="{y_val:.2f}" stroke="#888" stroke-width="0.1"/>\n'

    # Viertelkreisboegen: Grundriss -> Kreuzriss
    origin_x = riss_v_x
    origin_y = riss_h_y
    for d_val in [0, B]:
        gr_y = gy_o + d_val
        kr_x = kx_o + d_val
        r = gr_y - origin_y
        if r > 0:
            s += f'  <line x1="{gx_o + B:.2f}" y1="{gr_y:.2f}" x2="{origin_x:.2f}" y2="{gr_y:.2f}" stroke="#888" stroke-width="0.1"/>\n'
            s += f'  <path d="M {origin_x:.2f},{gr_y:.2f} A {r:.2f},{r:.2f} 0 0,0 {kr_x:.2f},{origin_y:.2f}" fill="none" stroke="#888" stroke-width="0.1"/>\n'
            s += f'  <line x1="{kr_x:.2f}" y1="{origin_y:.2f}" x2="{kr_x:.2f}" y2="{ky_o - 3:.2f}" stroke="#888" stroke-width="0.1"/>\n'

    # Annotations
    s += text_el(ax_o + B/2, ay_o + H + 6, f"{base}", 2.8, "middle", "#333")
    s += text_el(ax_o - 5, ay_o + H/2, f"{h}", 2.8, "end", "#333")

    s += svg_footer()
    write_svg("aufgabe_03_normalriss_pyramide.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 4: Abwicklung (Netz) eines Würfels (40mm)
# ══════════════════════════════════════════════════════════════════
def aufgabe_04():
    title = "Abwicklung (Netz) Würfel 40mm"
    s = svg_header(title, 4)

    a = 40
    sc = 1.0
    A = a * sc

    # Cross-shaped net: standard layout
    # Row of 4 going down (top, front, bottom, back), plus left and right
    # Origin: top-left of the "front" face
    ox, oy = 100, 25

    # Top face (above front)
    s += rect(ox, oy, A, A, "visible")
    s += text_el(ox + A/2, oy + A/2 + 1, "Oben", 3, "middle", "#888")

    # Front face
    s += rect(ox, oy + A, A, A, "visible")
    s += text_el(ox + A/2, oy + A + A/2 + 1, "Vorne", 3, "middle", "#888")

    # Bottom face (below front)
    s += rect(ox, oy + 2*A, A, A, "visible")
    s += text_el(ox + A/2, oy + 2*A + A/2 + 1, "Unten", 3, "middle", "#888")

    # Back face (below bottom)
    s += rect(ox, oy + 3*A, A, A, "visible")
    s += text_el(ox + A/2, oy + 3*A + A/2 + 1, "Hinten", 3, "middle", "#888")

    # Left face (left of front)
    s += rect(ox - A, oy + A, A, A, "visible")
    s += text_el(ox - A/2, oy + A + A/2 + 1, "Links", 3, "middle", "#888")

    # Right face (right of front)
    s += rect(ox + A, oy + A, A, A, "visible")
    s += text_el(ox + A + A/2, oy + A + A/2 + 1, "Rechts", 3, "middle", "#888")

    # Fold lines (dashed) - where faces connect
    s += line(ox, oy + A, ox + A, oy + A, "hidden")  # top-front
    s += line(ox, oy + 2*A, ox + A, oy + 2*A, "hidden")  # front-bottom
    s += line(ox, oy + 3*A, ox + A, oy + 3*A, "hidden")  # bottom-back
    s += line(ox, oy + A, ox, oy + 2*A, "hidden")  # front-left
    s += line(ox + A, oy + A, ox + A, oy + 2*A, "hidden")  # front-right

    # Annotation
    s += text_el(ox + A/2, oy - 5, "Netz eines Würfels", 4.5, "middle")
    s += text_el(ox + A/2, oy - 1, f"Kantenlaenge a = {a} mm", 3, "middle", "#555")

    s += svg_footer()
    write_svg("aufgabe_04_abwicklung_wuerfel.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 5: Abwicklung Zylinder (d=40, h=60)
# ══════════════════════════════════════════════════════════════════
def aufgabe_05():
    title = "Abwicklung Zylinder (d=40, h=60)"
    s = svg_header(title, 5)

    d = 40
    h = 60
    r = d / 2
    sc = 0.9

    R = r * sc
    H = h * sc
    U = math.pi * d * sc  # Umfang (circumference)

    # Mantelflaeche (lateral surface) - rectangle
    mx, my = 30, 30
    s += rect(mx, my, U, H, "visible")
    s += text_el(mx + U/2, my - 5, "Mantelflaeche", 3.5, "middle")
    s += text_el(mx + U/2, my + H + 6, f"U = \u03c0 \u00b7 d = \u03c0 \u00b7 {d} \u2248 {math.pi*d:.1f} mm", 2.8, "middle", "#555")
    s += text_el(mx - 3, my + H/2, f"h={h}", 2.5, "end", "#333")

    # Top circle
    cx1 = mx + U + 25 + R
    cy1 = my + R + 5
    s += circle_el(cx1, cy1, R, "visible")
    s += line(cx1 - R - 2, cy1, cx1 + R + 2, cy1, "center")
    s += line(cx1, cy1 - R - 2, cx1, cy1 + R + 2, "center")
    s += text_el(cx1, cy1 - R - 4, "Deckflaeche", 3, "middle")

    # Bottom circle
    cy2 = cy1 + 2*R + 20
    s += circle_el(cx1, cy2, R, "visible")
    s += line(cx1 - R - 2, cy2, cx1 + R + 2, cy2, "center")
    s += line(cx1, cy2 - R - 2, cx1, cy2 + R + 2, "center")
    s += text_el(cx1, cy2 - R - 4, "Grundflaeche", 3, "middle")

    s += text_el(cx1, cy2 + R + 6, f"r = {r} mm", 2.8, "middle", "#555")

    s += text_el(153, 170, "Abwicklung eines Zylinders", 5, "middle")

    s += svg_footer()
    write_svg("aufgabe_05_abwicklung_zylinder.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 6: Parallelprojektion Prisma (gleichseitiges Dreieck 50, h=70)
# ══════════════════════════════════════════════════════════════════
def aufgabe_06():
    title = "Parallelprojektion Dreiecksprisma"
    s = svg_header(title, 6)

    a = 50  # side of equilateral triangle
    h_prism = 70
    sc = 0.9

    A = a * sc
    H = h_prism * sc
    tri_h = A * math.sqrt(3) / 2  # triangle height

    # Cavalier projection: depth axis 45 deg, scale 0.5
    d_scale = 0.5
    angle = math.radians(45)

    # Front triangle vertices (bottom-left origin)
    ox, oy = 80, 160
    # Front triangle: equilateral, base at bottom
    f_bl = (ox, oy)
    f_br = (ox + A, oy)
    f_top = (ox + A/2, oy - tri_h)

    # Back triangle: shifted along depth axis
    dx = H * d_scale * math.cos(angle)
    dy = H * d_scale * math.sin(angle)
    b_bl = (f_bl[0] + dx, f_bl[1] - dy)
    b_br = (f_br[0] + dx, f_br[1] - dy)
    b_top = (f_top[0] + dx, f_top[1] - dy)

    # Front face (triangle)
    s += polyline([f_bl, f_br, f_top], "visible", close=True)

    # Back face (triangle) - partially visible
    s += line(*b_bl, *b_br, "hidden")
    s += line(*b_br, *b_top, "visible")
    s += line(*b_top, *b_bl, "hidden")

    # Connecting edges
    s += line(*f_bl, *b_bl, "hidden")
    s += line(*f_br, *b_br, "visible")
    s += line(*f_top, *b_top, "visible")

    # Labels
    s += text_el(153, 30, "Parallelprojektion eines Dreiecksprismas", 4.5, "middle")
    s += text_el(153, 37, f"Gleichseitiges Dreieck a = {a} mm, Höhe = {h_prism} mm", 3, "middle", "#555")
    s += text_el(ox + A/2, oy + 7, f"a = {a}", 2.8, "middle", "#333")

    s += svg_footer()
    write_svg("aufgabe_06_parallelprojektion_prisma.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 7: Durchdringung Quader-Quader
# ══════════════════════════════════════════════════════════════════
def aufgabe_07():
    title = "Durchdringung Quader-Quader"
    s = svg_header(title, 7)

    # Standing cuboid: 40x40x60 (centered at origin)
    # Lying cuboid: 30x30x80 (through the middle, along y-axis)
    sc = 1.0
    col_stand = "black"    # standing cuboid color
    col_lying = "#0055cc"  # lying cuboid color (blue)

    # We show Aufriss (front), Grundriss (top), Kreuzriss (side)
    gap = 30  # gap between views (groesser fuer bessere Lesbarkeit)

    # AUFRISS (front view, xz-plane)
    ax_o, ay_o = 50, 15  # origin top-left area

    # Standing cuboid front view: 40 wide, 60 tall
    sw, sh = 40*sc, 60*sc
    s += f'  <rect x="{ax_o:.2f}" y="{ay_o:.2f}" width="{sw:.2f}" height="{sh:.2f}" fill="none" stroke="{col_stand}" stroke-width="0.25"/>\n'
    s += text_el(ax_o + sw/2, ay_o - 4, "Aufriss", 3.5, "middle")

    # Lying cuboid front view: 30 wide, 30 tall, centered vertically
    lw, lh = 30*sc, 30*sc
    lx = ax_o + (sw - lw)/2
    ly = ay_o + (sh - lh)/2  # centered in standing cuboid
    s += f'  <rect x="{lx:.2f}" y="{ly:.2f}" width="{lw:.2f}" height="{lh:.2f}" fill="none" stroke="{col_lying}" stroke-width="0.25"/>\n'

    # Durchdringungskanten in Aufriss
    s += f'  <line x1="{lx:.2f}" y1="{ly:.2f}" x2="{lx+lw:.2f}" y2="{ly:.2f}" stroke="{col_lying}" stroke-width="0.25"/>\n'
    s += f'  <line x1="{lx:.2f}" y1="{ly+lh:.2f}" x2="{lx+lw:.2f}" y2="{ly+lh:.2f}" stroke="{col_lying}" stroke-width="0.25"/>\n'

    # GRUNDRISS (top view, xy-plane)
    gx_o = ax_o
    gy_o = ay_o + sh + gap

    # Standing cuboid top: 40x40 square
    s += f'  <rect x="{gx_o:.2f}" y="{gy_o:.2f}" width="{40*sc:.2f}" height="{40*sc:.2f}" fill="none" stroke="{col_stand}" stroke-width="0.25"/>\n'
    s += text_el(gx_o + 20*sc, gy_o - 4, "Grundriss", 3.5, "middle")

    # Lying cuboid top: 30 wide (x), 80 long (y) centered
    lt_w = 30*sc
    lt_h = 80*sc
    lt_x = gx_o + (40*sc - lt_w)/2
    lt_y = gy_o + (40*sc - lt_h)/2  # extends beyond standing cuboid
    s += f'  <rect x="{lt_x:.2f}" y="{lt_y:.2f}" width="{lt_w:.2f}" height="{lt_h:.2f}" fill="none" stroke="{col_lying}" stroke-width="0.25"/>\n'

    # Hidden parts of lying cuboid inside standing cuboid
    s += f'  <line x1="{lt_x:.2f}" y1="{gy_o:.2f}" x2="{lt_x:.2f}" y2="{gy_o+40*sc:.2f}" stroke="{col_lying}" stroke-width="0.1" stroke-dasharray="2,1"/>\n'
    s += f'  <line x1="{lt_x+lt_w:.2f}" y1="{gy_o:.2f}" x2="{lt_x+lt_w:.2f}" y2="{gy_o+40*sc:.2f}" stroke="{col_lying}" stroke-width="0.1" stroke-dasharray="2,1"/>\n'

    # KREUZRISS (side view, yz-plane)
    kx_o = ax_o + sw + gap
    ky_o = ay_o

    # Standing cuboid side: 40 deep, 60 tall
    s += f'  <rect x="{kx_o:.2f}" y="{ky_o:.2f}" width="{40*sc:.2f}" height="{sh:.2f}" fill="none" stroke="{col_stand}" stroke-width="0.25"/>\n'
    s += text_el(kx_o + 20*sc, ky_o - 4, "Kreuzriss", 3.5, "middle")

    # Lying cuboid side: 80 along y (horizontal), 30 in z (vertical), centered
    lk_w = 80*sc
    lk_x = kx_o + (40*sc - lk_w)/2  # extends beyond
    lk_y = ky_o + (sh - 30*sc)/2
    s += f'  <rect x="{lk_x:.2f}" y="{lk_y:.2f}" width="{lk_w:.2f}" height="{30*sc:.2f}" fill="none" stroke="{col_lying}" stroke-width="0.25"/>\n'

    # Hidden lines inside standing cuboid in Kreuzriss
    s += f'  <line x1="{kx_o:.2f}" y1="{lk_y:.2f}" x2="{kx_o+40*sc:.2f}" y2="{lk_y:.2f}" stroke="{col_lying}" stroke-width="0.1" stroke-dasharray="2,1"/>\n'
    s += f'  <line x1="{kx_o:.2f}" y1="{lk_y+30*sc:.2f}" x2="{kx_o+40*sc:.2f}" y2="{lk_y+30*sc:.2f}" stroke="{col_lying}" stroke-width="0.1" stroke-dasharray="2,1"/>\n'

    # ── Rissachsen (red coordinate axes centered between views) ──
    riss_h_y = ay_o + sh + gap / 2  # correct: gap/2 as float
    s += f'  <line x1="20" y1="{riss_h_y:.2f}" x2="287" y2="{riss_h_y:.2f}" stroke="#C00" stroke-width="0.3"/>\n'
    riss_v_x = ax_o + sw + gap / 2  # correct: gap/2 as float
    s += f'  <line x1="{riss_v_x:.2f}" y1="10" x2="{riss_v_x:.2f}" y2="200" stroke="#C00" stroke-width="0.3"/>\n'

    # ── Ordner (projection lines): finest solid lines, NOT dashed ──
    # Vertical: Aufriss -> Grundriss
    for x_val in [ax_o, ax_o + sw, lx, lx + lw]:
        s += f'  <line x1="{x_val:.2f}" y1="{ay_o - 3:.2f}" x2="{x_val:.2f}" y2="{gy_o + 40*sc + 3:.2f}" stroke="#888" stroke-width="0.1"/>\n'
    # Horizontal: Aufriss -> Kreuzriss
    for y_val in [ay_o, ay_o + sh, ly, ly + lh]:
        s += f'  <line x1="{ax_o - 3:.2f}" y1="{y_val:.2f}" x2="{kx_o + 40*sc + 3:.2f}" y2="{y_val:.2f}" stroke="#888" stroke-width="0.1"/>\n'

    # ── Viertelkreisboegen: Grundriss -> Kreuzriss transfer ──
    origin_x = riss_v_x
    origin_y = riss_h_y
    for d_val in [0, 40*sc]:
        gr_y = gy_o + d_val  # y-position in Grundriss
        kr_x = kx_o + d_val  # x-position in Kreuzriss
        r = gr_y - origin_y  # radius from origin
        if r > 0:
            # Horizontal from Grundriss edge to origin
            s += f'  <line x1="{gx_o + sw:.2f}" y1="{gr_y:.2f}" x2="{origin_x:.2f}" y2="{gr_y:.2f}" stroke="#888" stroke-width="0.1"/>\n'
            # Quarter-circle arc
            s += f'  <path d="M {origin_x:.2f},{gr_y:.2f} A {r:.2f},{r:.2f} 0 0,0 {kr_x:.2f},{origin_y:.2f}" fill="none" stroke="#888" stroke-width="0.1"/>\n'
            # Vertical from arc end to Kreuzriss
            s += f'  <line x1="{kr_x:.2f}" y1="{origin_y:.2f}" x2="{kr_x:.2f}" y2="{ky_o - 3:.2f}" stroke="#888" stroke-width="0.1"/>\n'

    # Annotations
    s += text_el(153, 175, "Stehender Quader: 40 x 40 x 60 mm", 3, "middle", "#555")
    s += text_el(153, 180, "Liegender Quader: 30 x 30 x 80 mm (durch die Mitte)", 3, "middle", "#555")

    s += svg_footer()
    write_svg("aufgabe_07_durchdringung.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 8: Ebenenschnitt durch einen Würfel (diagonal)
# ══════════════════════════════════════════════════════════════════
def aufgabe_08():
    title = "Ebenenschnitt Würfel (diagonal)"
    s = svg_header(title, 8)

    a = 60
    sc = 0.8
    A = a * sc

    # Cavalier projection of cube with diagonal cut plane
    d_scale = 0.5
    angle = math.radians(45)
    dx = A * d_scale * math.cos(angle)
    dy = A * d_scale * math.sin(angle)

    ox, oy = 70, 140

    # Front face corners
    f_bl = (ox, oy)
    f_br = (ox + A, oy)
    f_tr = (ox + A, oy - A)
    f_tl = (ox, oy - A)

    # Back face corners
    b_bl = (ox + dx, oy - dy)
    b_br = (ox + A + dx, oy - dy)
    b_tr = (ox + A + dx, oy - A - dy)
    b_tl = (ox + dx, oy - A - dy)

    # Draw cube
    # Front
    s += polyline([f_bl, f_br, f_tr, f_tl], "visible", close=True)
    # Back visible
    s += line(*b_tl, *b_tr, "visible")
    s += line(*b_tr, *b_br, "visible")
    # Back hidden
    s += line(*b_bl, *b_br, "hidden")
    s += line(*b_bl, *b_tl, "hidden")
    # Connecting
    s += line(*f_tl, *b_tl, "visible")
    s += line(*f_tr, *b_tr, "visible")
    s += line(*f_br, *b_br, "visible")
    s += line(*f_bl, *b_bl, "hidden")

    # Diagonal cut plane: from front-top-left to front-bottom-right
    # to back-bottom-right to back-top-left
    # This creates a diagonal section through the cube
    cut_pts = [f_tl, f_br, b_br, b_tl]
    # Semi-transparent cutting plane
    cut_d = " ".join(f"{x:.2f},{y:.2f}" for x, y in cut_pts)
    s += f'  <polygon points="{cut_d}" fill="#6699ff" fill-opacity="0.3" stroke="black" stroke-width="0.25"/>\n'

    # Redraw edges that the fill might cover
    s += line(*f_tl, *f_br, "visible")
    s += line(*f_br, *b_br, "visible")
    s += line(*b_br, *b_tl, "visible")
    s += line(*b_tl, *f_tl, "visible")

    # Label
    s += text_el(153, 30, "Ebenenschnitt durch einen Würfel", 4.5, "middle")
    s += text_el(153, 37, "Diagonale Schnittebene (blau hervorgehoben)", 3, "middle", "#555")
    s += text_el(153, 170, f"Würfel a = {a} mm", 3, "middle", "#555")

    s += svg_footer()
    write_svg("aufgabe_08_ebenenschnitt.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 9: Kreis im Schraegriss (Ellipse, d=50)
# ══════════════════════════════════════════════════════════════════
def aufgabe_09():
    title = "Kreis im Schraegriss (Ellipse)"
    s = svg_header(title, 9)

    d = 50
    r = d / 2
    sc = 1.0
    R = r * sc

    # Show original circle and its appearance in cavalier projection
    # on different planes

    # 1) Circle in front plane (xz) - remains a circle
    cx1, cy1 = 70, 100
    s += circle_el(cx1, cy1, R, "visible")
    s += line(cx1 - R - 3, cy1, cx1 + R + 3, cy1, "center")
    s += line(cx1, cy1 - R - 3, cx1, cy1 + R + 3, "center")
    s += text_el(cx1, cy1 - R - 6, "Kreis in Frontalebene", 3, "middle")
    s += text_el(cx1, cy1 - R - 2, "(bleibt Kreis)", 2.5, "middle", "#555")

    # 2) Circle in horizontal plane (xy) - becomes ellipse
    # In cavalier proj: x stays, y gets compressed (0.5) and rotated 45 deg
    cx2, cy2 = 180, 100

    # For a circle in the xy-plane (horizontal):
    # Semi-axis along x = R (unchanged)
    # Semi-axis along y-depth = R * 0.5 (cavalier shortening)
    # The y-axis is at 45 degrees
    # This produces an ellipse. We approximate with SVG ellipse + rotation.
    # The major axis is R, minor axis is R*0.5, rotated -45/2 degrees
    # More precisely: parametric circle in xy plane under cavalier:
    # x'(t) = R*cos(t) + R*sin(t)*0.5*cos(45)
    # y'(t) = -R*sin(t)*0.5*sin(45)  (negative because SVG y is down)

    # Generate points for the ellipse
    pts = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        px = cx2 + R * math.cos(t) + R * math.sin(t) * 0.5 * math.cos(math.radians(45))
        py = cy2 - R * math.sin(t) * 0.5 * math.sin(math.radians(45))
        pts.append((px, py))
    s += polyline(pts, "visible", close=True)

    # Center lines
    s += line(cx2 - R - 5, cy2, cx2 + R + 10, cy2, "center")
    s += line(cx2 + R*0.5*0.707, cy2 - R*0.5*0.707 - 5,
              cx2 - R*0.5*0.707, cy2 + R*0.5*0.707 + 5, "center")

    s += text_el(cx2, cy2 - R - 6, "Kreis in Horizontalebene", 3, "middle")
    s += text_el(cx2, cy2 - R - 2, "(wird zur Ellipse)", 2.5, "middle", "#555")

    # 3) Circle in side plane (yz) - becomes ellipse
    cx3, cy3 = 70, 50
    # In yz-plane: z stays (vertical), y gets compressed
    # Similar to horizontal but different orientation
    pts2 = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        px = cx3 + R * math.cos(t) * 0.5 * math.cos(math.radians(45))
        py = cy3 - R * math.sin(t) - R * math.cos(t) * 0.5 * math.sin(math.radians(45))
        pts2.append((px, py))

    # Actually let's show this on the right side instead
    cx3, cy3 = 180, 50
    pts2 = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        px = cx3 + R * math.cos(t) * 0.5 * math.cos(math.radians(45))
        py = cy3 - R * math.sin(t) + R * math.cos(t) * 0.5 * math.sin(math.radians(45))
        pts2.append((px, py))

    # Let's keep it simpler - just show 2 cases
    s += text_el(153, 155, f"Kreisdurchmesser d = {d} mm", 3, "middle", "#555")
    s += text_el(153, 160, "Kavalierprojektion: Verkürzung 1:2, Winkel 45\u00b0", 3, "middle", "#555")
    s += text_el(153, 30, "Kreis im Schraegriss", 5, "middle")

    s += svg_footer()
    write_svg("aufgabe_09_kreis_schraegriss.svg", s)


# ══════════════════════════════════════════════════════════════════
# AUFGABE 10: Zusammengesetzter Körper: Quader + Pyramide
# ══════════════════════════════════════════════════════════════════
def aufgabe_10():
    title = "Quader mit aufgesetzter Pyramide"
    s = svg_header(title, 10)

    # Quader: 60x60x40, Pyramide on top: base 60x60, height 50
    qw, qd, qh = 60, 60, 40
    ph = 50  # pyramid height
    sc = 0.75

    QW = qw * sc
    QD = qd * sc
    QH = qh * sc
    PH = ph * sc

    d_scale = 0.5
    angle = math.radians(45)
    dx = QD * d_scale * math.cos(angle)
    dy = QD * d_scale * math.sin(angle)

    ox, oy = 80, 160  # front-bottom-left

    # Front face of cuboid
    f_bl = (ox, oy)
    f_br = (ox + QW, oy)
    f_tr = (ox + QW, oy - QH)
    f_tl = (ox, oy - QH)

    # Back face of cuboid
    b_bl = (ox + dx, oy - dy)
    b_br = (ox + QW + dx, oy - dy)
    b_tr = (ox + QW + dx, oy - QH - dy)
    b_tl = (ox + dx, oy - QH - dy)

    # Pyramid apex
    apex = (ox + QW/2 + dx/2, oy - QH - PH - dy/2)

    # Kein Koordinatenkreuz bei Schrägriss (stört hier)

    # Draw cuboid
    # Front face
    s += polyline([f_bl, f_br, f_tr, f_tl], "visible", close=True)
    # Back edges (visible top and right, hidden bottom and left)
    s += line(*b_tl, *b_tr, "hidden")  # hidden - under pyramid
    s += line(*b_tr, *b_br, "visible")
    s += line(*b_bl, *b_br, "hidden")
    s += line(*b_bl, *b_tl, "hidden")
    # Connecting edges
    s += line(*f_tl, *b_tl, "hidden")  # hidden - under pyramid
    s += line(*f_tr, *b_tr, "hidden")  # hidden - under pyramid
    s += line(*f_br, *b_br, "visible")
    s += line(*f_bl, *b_bl, "hidden")

    # Draw pyramid
    # Base is top of cuboid: f_tl, f_tr, b_tr, b_tl
    # Front edges to apex
    s += line(*f_tl, *apex, "visible")
    s += line(*f_tr, *apex, "visible")
    # Back edges to apex
    s += line(*b_tr, *apex, "visible")
    s += line(*b_tl, *apex, "hidden")

    # Top edges of cuboid (= base of pyramid) - front visible
    s += line(*f_tl, *f_tr, "visible")
    # Right side visible
    s += line(*f_tr, *b_tr, "visible")

    # Diagonal construction lines on top face of Quader (to locate apex)
    s += f'  <line x1="{f_tl[0]:.2f}" y1="{f_tl[1]:.2f}" x2="{b_tr[0]:.2f}" y2="{b_tr[1]:.2f}" stroke="#aaa" stroke-width="0.08"/>\n'
    s += f'  <line x1="{f_tr[0]:.2f}" y1="{f_tr[1]:.2f}" x2="{b_tl[0]:.2f}" y2="{b_tl[1]:.2f}" stroke="#aaa" stroke-width="0.08"/>\n'

    # Center line through apex
    mid_base_x = ox + QW/2 + dx/2
    mid_base_y = oy - QH - dy/2
    s += line(mid_base_x, mid_base_y + 2, apex[0], apex[1] - 3, "center")

    # Labels
    s += text_el(153, 25, "Zusammengesetzter Körper", 5, "middle")
    s += text_el(153, 32, "Quader mit aufgesetzter Pyramide", 3.5, "middle", "#555")
    s += text_el(ox + QW/2, oy + 7, f"Quader: {qw} x {qd} x {qh} mm", 2.8, "middle", "#333")
    s += text_el(ox + QW/2, oy + 12, f"Pyramide: Basis {qw} x {qd}, h={ph} mm", 2.8, "middle", "#333")

    s += svg_footer()
    write_svg("aufgabe_10_zusammengesetzter_koerper.svg", s)


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("GZ-Aufgaben: 10 Standardaufgaben - SVG-Generierung")
    print("=" * 60)

    tasks = [
        (aufgabe_01, "Dreitafelprojektion Quader"),
        (aufgabe_02, "Schraegriss Quader"),
        (aufgabe_03, "Normalriss Pyramide"),
        (aufgabe_04, "Abwicklung Würfel"),
        (aufgabe_05, "Abwicklung Zylinder"),
        (aufgabe_06, "Parallelprojektion Prisma"),
        (aufgabe_07, "Durchdringung Quader-Quader"),
        (aufgabe_08, "Ebenenschnitt Würfel"),
        (aufgabe_09, "Kreis im Schraegriss"),
        (aufgabe_10, "Zusammengesetzter Körper"),
    ]

    for i, (fn, name) in enumerate(tasks, 1):
        print(f"\nAufgabe {i}: {name}")
        try:
            fn()
            print(f"  [OK]")
        except Exception as e:
            print(f"  [FEHLER] {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Ausgabeverzeichnis: {OUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
