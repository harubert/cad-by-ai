"""
Erzeugt STL aus dem fertigen SVG (aufgabe01_path.svg).
Das SVG hat alle korrekten Boegen -- wir parsen die Pfade und extrudieren.
"""

import numpy as np
import trimesh
from trimesh.creation import extrude_polygon
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid
from pathlib import Path
import re
import math

OUT = Path(__file__).resolve().parent.parent / 'output'
SVG_FILE = OUT / 'aufgabe01_path.svg'

def parse_svg_path(d_string):
    """Parst einen SVG path d-String und gibt Koordinaten zurueck.
    Unterstuetzt M, L, A, Z Befehle."""
    # Tokens extrahieren
    tokens = re.findall(r'[MLAZmlaz]|[-+]?\d*\.?\d+', d_string)

    points = []
    i = 0
    cx, cy = 0, 0  # current point

    while i < len(tokens):
        cmd = tokens[i]
        i += 1

        if cmd == 'M':
            cx, cy = float(tokens[i]), float(tokens[i+1])
            points.append((cx, -cy))  # SVG y -> Geometrie y
            i += 2
        elif cmd == 'L':
            cx, cy = float(tokens[i]), float(tokens[i+1])
            points.append((cx, -cy))
            i += 2
        elif cmd == 'A':
            # A rx ry rotation large-arc sweep x y
            rx = float(tokens[i])
            ry = float(tokens[i+1])
            rot = float(tokens[i+2])
            large_arc = int(tokens[i+3])
            sweep = int(tokens[i+4])
            ex, ey = float(tokens[i+5]), float(tokens[i+6])
            i += 7

            # SVG Arc zu Punktliste konvertieren
            # Y-Inversion kehrt sweep-Richtung um
            arc_pts = svg_arc_to_points(cx, -cy, ex, -ey, rx, large_arc, 1 - sweep)
            points.extend(arc_pts[1:])  # erstes = Startpunkt (schon drin)
            cx, cy = ex, ey
        elif cmd == 'Z':
            pass  # Pfad schliessen
        else:
            # Eventuell implizite L-Befehle (Zahlen ohne Buchstabe)
            try:
                cx, cy = float(cmd), float(tokens[i])
                points.append((cx, -cy))
                i += 1
            except (ValueError, IndexError):
                pass

    return points


def svg_arc_to_points(x1, y1, x2, y2, r, large_arc, sweep, n=24):
    """Konvertiert SVG Arc-Parameter zu Punktliste."""
    # Mittelpunkt berechnen (SVG Arc Algorithmus)
    dx = (x1 - x2) / 2
    dy = (y1 - y2) / 2

    d_sq = dx*dx + dy*dy
    r_sq = r*r

    if r_sq < d_sq:
        r = math.sqrt(d_sq) * 1.001
        r_sq = r*r

    sq = max(0, (r_sq - d_sq) / d_sq)
    sq = math.sqrt(sq)

    if large_arc == sweep:
        sq = -sq

    cx = sq * dy + (x1 + x2) / 2
    cy = -sq * dx + (y1 + y2) / 2

    # Winkel
    a1 = math.atan2(y1 - cy, x1 - cx)
    a2 = math.atan2(y2 - cy, x2 - cx)

    # Sweep-Richtung
    if sweep == 0:  # gegen Uhrzeiger
        if a2 > a1:
            a2 -= 2 * math.pi
    else:  # Uhrzeiger
        if a2 < a1:
            a2 += 2 * math.pi

    angles = np.linspace(a1, a2, n)
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in angles]


def main():
    # SVG lesen
    svg_text = SVG_FILE.read_text(encoding='utf-8')

    # Alle path d-Attribute extrahieren
    d_matches = re.findall(r'd="([^"]+)"', svg_text)

    if not d_matches:
        print("Keine Pfade gefunden!")
        return

    # Nimm den laengsten Pfad (der mit der Geometrie, nicht das hatch-Pattern)
    full_d = max(d_matches, key=len)

    # In Sub-Pfade aufteilen (jedes "M " startet einen neuen)
    sub_paths = re.split(r'(?=M )', full_d.strip())
    sub_paths = [s.strip() for s in sub_paths if s.strip() and len(s) > 10]

    print(f"Gefunden: {len(sub_paths)} Sub-Pfade")

    polygons = []
    for i, sp in enumerate(sub_paths):
        pts = parse_svg_path(sp)
        if len(pts) >= 3:
            try:
                poly = Polygon(pts)
                if poly.is_valid and poly.area > 1:
                    polygons.append(poly)
                    print(f"  Sub-Pfad {i}: {len(pts)} Punkte, {poly.area:.1f}mm^2")
                elif not poly.is_valid:
                    poly = make_valid(poly)
                    if poly.area > 1:
                        polygons.append(poly)
                        print(f"  Sub-Pfad {i}: {len(pts)} Punkte, {poly.area:.1f}mm^2 (repariert)")
            except Exception as e:
                print(f"  Sub-Pfad {i}: Fehler: {e}")

    if not polygons:
        print("Keine gueltigen Polygone!")
        return

    # Erstes Polygon = Aussenkontur, Rest = Loecher (via evenodd)
    outer = polygons[0]
    for hole in polygons[1:]:
        outer = outer.difference(hole)
    outer = make_valid(outer)

    print(f"\nProfil-Flaeche: {outer.area:.1f}mm^2")
    print("Extrudiere auf 100mm...")

    # Extrusion
    if isinstance(outer, MultiPolygon):
        meshes = [extrude_polygon(p, height=100.0) for p in outer.geoms if p.area > 0.5]
        mesh = trimesh.util.concatenate(meshes)
    else:
        mesh = extrude_polygon(outer, height=100.0)

    print(f"Mesh: {len(mesh.vertices)} Vertices, {len(mesh.faces)} Faces")

    stl_path = OUT / 'aufgabe01_profil_100mm.stl'
    mesh.export(str(stl_path))
    print(f"OK: {stl_path}")
    print(f"Dateigroesse: {stl_path.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
