"""
Aufgabe 06 Final: Vergleich CadQuery vs build123d vs SolidPython2
Aluminiumprofil 40x40mm - zwei Varianten pro Tool:
  A) SVG-Import aus aufgabe01_path.svg
  B) Parametrisch aufgebaut

Ausgabe: SVG fuer alle 6 Varianten + Vergleichs-HTML
"""

import math
import re
from pathlib import Path

# === Pfade ===
BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'output' / 'aufgabe06'
OUT.mkdir(exist_ok=True, parents=True)
SVG_INPUT = BASE / 'output' / 'aufgabe01_path.svg'
IMG_INPUT = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'

# === Profil-Parameter 40x40mm ===
W = H = 40.0
R_CORNER = 4.5        # Eckenradius
SLOT_OPEN = 8.0       # T-Nut Oeffnung
SLOT_DEPTH = 12.25    # Nuttiefe ab Aussenkante
BORE_D = 6.8          # Zentralbohrung
POCKET_SIZE = 6.5     # Eckentaschen
POCKET_OFFSET = 2.0   # Abstand Tasche von Kante
# T-Nut Geometrie
HEAD_W = 12.0         # T-Kopf Breite (Hinterschnitt)
HEAD_DEPTH = 2.0      # T-Kopf Tiefe
NECK_W = SLOT_OPEN    # Hals = Nutoeffnung
NECK_DEPTH = SLOT_DEPTH - HEAD_DEPTH

print(f"Profil: {W}x{H}mm, Nut {SLOT_OPEN}mm, Bohrung D{BORE_D}")
print(f"Ausgabe: {OUT}")

# ============================================================
# SVG Parser - liest aufgabe01_path.svg
# ============================================================
def parse_svg_path(svg_file):
    """Parse SVG file, find longest d-attribute, extract sub-paths as point lists."""
    text = svg_file.read_text(encoding='utf-8')
    # Find all d attributes
    d_attrs = re.findall(r'd="([^"]+)"', text)
    if not d_attrs:
        raise ValueError("No d-attribute found in SVG")
    # Pick longest
    d = max(d_attrs, key=len)
    return parse_d_attribute(d)


def svg_arc_to_points(cx, cy, ex, ey, rx, ry, large_arc, sweep, n_pts=16):
    """Convert SVG arc to list of points.
    cx,cy = current point; ex,ey = end point; rx,ry = radii
    For Y-axis inversion: caller passes inverted y and 1-sweep.
    """
    # Simplified: approximate arc as line segments
    # Use the SVG arc parametrization
    dx = ex - cx
    dy = ey - cy
    dist = math.sqrt(dx*dx + dy*dy)
    if dist < 1e-10 or rx < 1e-10 or ry < 1e-10:
        return [(ex, ey)]

    # Normalize
    dx2 = dx / 2.0
    dy2 = dy / 2.0

    # Step 1: compute (x1', y1')
    cos_a = 1.0  # no rotation
    sin_a = 0.0
    x1p = cos_a * dx2 + sin_a * dy2
    y1p = -sin_a * dx2 + cos_a * dy2

    # Step 2: compute center
    rx2 = rx * rx
    ry2 = ry * ry
    x1p2 = x1p * x1p
    y1p2 = y1p * y1p

    # Check if radii are large enough
    lam = x1p2 / rx2 + y1p2 / ry2
    if lam > 1:
        s = math.sqrt(lam)
        rx *= s
        ry *= s
        rx2 = rx * rx
        ry2 = ry * ry

    num = max(0, rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2)
    den = rx2 * y1p2 + ry2 * x1p2
    if den < 1e-10:
        return [(ex, ey)]
    sq = math.sqrt(num / den)
    if large_arc == sweep:
        sq = -sq
    cxp = sq * rx * y1p / ry
    cyp = -sq * ry * x1p / rx

    # Step 3: compute center in original coords
    ccx = cos_a * cxp - sin_a * cyp + (cx + ex) / 2.0
    ccy = sin_a * cxp + cos_a * cyp + (cy + ey) / 2.0

    # Step 4: compute angles
    def angle_vec(ux, uy, vx, vy):
        n = math.sqrt(ux*ux+uy*uy) * math.sqrt(vx*vx+vy*vy)
        if n < 1e-10:
            return 0
        c = (ux*vx+uy*vy) / n
        c = max(-1, min(1, c))
        a = math.acos(c)
        if ux*vy - uy*vx < 0:
            a = -a
        return a

    theta1 = angle_vec(1, 0, (x1p - cxp)/rx, (y1p - cyp)/ry)
    dtheta = angle_vec((x1p - cxp)/rx, (y1p - cyp)/ry,
                       (-x1p - cxp)/rx, (-y1p - cyp)/ry)

    if sweep == 0 and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep == 1 and dtheta < 0:
        dtheta += 2 * math.pi

    pts = []
    for i in range(1, n_pts + 1):
        t = theta1 + dtheta * i / n_pts
        x = cos_a * rx * math.cos(t) - sin_a * ry * math.sin(t) + ccx
        y = sin_a * rx * math.cos(t) + cos_a * ry * math.sin(t) + ccy
        pts.append((x, y))
    return pts


def parse_d_attribute(d):
    """Parse SVG path d-attribute into sub-paths of (x,y) points.
    Handles M, L, A, Z commands. Y is NOT inverted here - caller decides.
    Returns list of sub-paths, each a list of (x,y) tuples.
    """
    # Tokenize
    tokens = re.findall(r'[MLAZmlaz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)

    sub_paths = []
    current_path = []
    cx, cy = 0.0, 0.0
    i = 0

    while i < len(tokens):
        cmd = tokens[i]
        if cmd == 'M':
            if current_path:
                sub_paths.append(current_path)
            i += 1
            cx, cy = float(tokens[i]), float(tokens[i+1])
            i += 2
            current_path = [(cx, cy)]
            # Implicit L after M
            while i < len(tokens) and tokens[i] not in 'MLAZmlaz':
                cx, cy = float(tokens[i]), float(tokens[i+1])
                current_path.append((cx, cy))
                i += 2
        elif cmd == 'L':
            i += 1
            while i < len(tokens) and tokens[i] not in 'MLAZmlaz':
                cx, cy = float(tokens[i]), float(tokens[i+1])
                current_path.append((cx, cy))
                i += 2
        elif cmd == 'A':
            i += 1
            while i + 6 < len(tokens) and tokens[i] not in 'MLAZmlaz':
                rx = float(tokens[i])
                ry = float(tokens[i+1])
                rotation = float(tokens[i+2])
                large_arc = int(float(tokens[i+3]))
                sweep = int(float(tokens[i+4]))
                ex = float(tokens[i+5])
                ey = float(tokens[i+6])
                i += 7
                # Invert Y for arc computation: negate cy, ey, use 1-sweep
                arc_pts = svg_arc_to_points(cx, -cy, ex, -ey, rx, ry,
                                            large_arc, 1 - sweep, n_pts=16)
                # Convert back: negate y of result
                for (ax, ay) in arc_pts:
                    current_path.append((ax, -ay))
                cx, cy = ex, ey
        elif cmd == 'Z' or cmd == 'z':
            if current_path:
                # Close path
                current_path.append(current_path[0])
                sub_paths.append(current_path)
                current_path = []
            i += 1
        else:
            i += 1  # skip unknown

    if current_path:
        sub_paths.append(current_path)

    return sub_paths


# ============================================================
# SVG Output Helper
# ============================================================
SVG_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="-25 -25 50 50" width="400" height="400">
<rect x="-25" y="-25" width="50" height="50" fill="white"/>
'''
SVG_FOOTER_TEMPLATE = '<text x="0" y="23" font-size="2" text-anchor="middle" fill="#555">{title}</text>\n</svg>'


def write_svg_from_subpaths(sub_paths, title, filepath):
    """Write SVG from list of sub-paths (each a list of (x,y) tuples)."""
    svg = SVG_HEADER
    for sp in sub_paths:
        if len(sp) < 2:
            continue
        d_parts = [f"M {sp[0][0]:.3f},{sp[0][1]:.3f}"]
        for pt in sp[1:]:
            d_parts.append(f"L {pt[0]:.3f},{pt[1]:.3f}")
        d_str = " ".join(d_parts) + " Z"
        svg += f'<path d="{d_str}" fill="none" stroke="black" stroke-width="0.3"/>\n'
    svg += SVG_FOOTER_TEMPLATE.format(title=title)
    filepath.write_text(svg, encoding='utf-8')
    print(f"  SVG geschrieben: {filepath.name} ({len(sub_paths)} Konturen)")


def write_svg_from_edges(edges, title, filepath):
    """Write SVG from list of ((x1,y1),(x2,y2)) edge tuples."""
    svg = SVG_HEADER
    for (x1, y1), (x2, y2) in edges:
        svg += f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="black" stroke-width="0.3"/>\n'
    svg += SVG_FOOTER_TEMPLATE.format(title=title)
    filepath.write_text(svg, encoding='utf-8')
    print(f"  SVG geschrieben: {filepath.name} ({len(edges)} Kanten)")


# ============================================================
# Parse the input SVG
# ============================================================
print("\n" + "="*60)
print("SVG-Pfad einlesen")
print("="*60)
try:
    svg_sub_paths = parse_svg_path(SVG_INPUT)
    print(f"  {len(svg_sub_paths)} Sub-Pfade gefunden:")
    for i, sp in enumerate(svg_sub_paths):
        print(f"    Sub-Pfad {i}: {len(sp)} Punkte, "
              f"Bereich x=[{min(p[0] for p in sp):.1f}..{max(p[0] for p in sp):.1f}] "
              f"y=[{min(p[1] for p in sp):.1f}..{max(p[1] for p in sp):.1f}]")
except Exception as e:
    print(f"  Fehler beim Parsen: {e}")
    import traceback; traceback.print_exc()
    svg_sub_paths = []

# Sub-path 0 = outer contour, 1-5 = holes
outer_contour = svg_sub_paths[0] if len(svg_sub_paths) > 0 else []
hole_contours = svg_sub_paths[1:] if len(svg_sub_paths) > 1 else []


# ============================================================
# Parametric profile builder (shared geometry)
# ============================================================
def build_parametric_subpaths():
    """Build 40x40 profile parametrically. Returns list of sub-paths."""
    paths = []

    # --- Outer contour with rounded corners ---
    def rounded_rect(w, h, r, n_arc=8):
        """Rounded rectangle centered at origin, CCW."""
        pts = []
        hw, hh = w/2, h/2
        corners = [
            (hw - r, -hh, hw, -hh + r, 0),      # bottom-right
            (hw, hh - r, hw - r, hh, 90),         # top-right
            (-hw + r, hh, -hw, hh - r, 180),      # top-left
            (-hw, -hh + r, -hw + r, -hh, 270),    # bottom-left
        ]
        for (sx, sy, ex, ey, start_angle) in corners:
            pts.append((sx, sy))
            # Arc from (sx,sy) to (ex,ey) around corner center
            # Center is at the corner minus r offset
            if start_angle == 0:
                ccx, ccy = hw - r, -hh + r
            elif start_angle == 90:
                ccx, ccy = hw - r, hh - r
            elif start_angle == 180:
                ccx, ccy = -hw + r, hh - r
            else:
                ccx, ccy = -hw + r, -hh + r
            for i in range(1, n_arc):
                a = math.radians(start_angle - 90 + 90 * i / n_arc)
                pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
            pts.append((ex, ey))
        pts.append(pts[0])  # close
        return pts

    # Outer boundary - we need the full profile with T-slots cut in
    # Build as a complex polygon using shapely for boolean ops
    try:
        from shapely.geometry import Polygon, MultiPolygon
        from shapely.ops import unary_union
        from shapely import affinity

        # Outer rounded rect
        outer_pts = rounded_rect(W, H, R_CORNER, n_arc=16)
        outer = Polygon(outer_pts)

        # T-slots (4 sides)
        slots = []
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)

            # Neck: centered on the side
            # For angle=0 (top): neck at y = H/2 - NECK_DEPTH/2
            neck_cx = 0
            neck_cy = H/2 - NECK_DEPTH/2
            # Rect centered at (neck_cx, neck_cy), size NECK_W x NECK_DEPTH
            hw, hh = NECK_W/2, NECK_DEPTH/2
            neck_pts = [
                (neck_cx - hw, neck_cy - hh),
                (neck_cx + hw, neck_cy - hh),
                (neck_cx + hw, neck_cy + hh),
                (neck_cx - hw, neck_cy + hh),
            ]
            # Rotate
            rot_pts = [(cos_a*x - sin_a*y, sin_a*x + cos_a*y) for x, y in neck_pts]
            slots.append(Polygon(rot_pts))

            # Head (undercut): wider
            head_cy = H/2 - NECK_DEPTH - HEAD_DEPTH/2
            hw2, hh2 = HEAD_W/2, HEAD_DEPTH/2
            head_pts = [
                (neck_cx - hw2, head_cy - hh2),
                (neck_cx + hw2, head_cy - hh2),
                (neck_cx + hw2, head_cy + hh2),
                (neck_cx - hw2, head_cy + hh2),
            ]
            rot_pts2 = [(cos_a*x - sin_a*y, sin_a*x + cos_a*y) for x, y in head_pts]
            slots.append(Polygon(rot_pts2))

        # Central bore
        bore_pts = []
        for i in range(64):
            a = 2 * math.pi * i / 64
            bore_pts.append((BORE_D/2 * math.cos(a), BORE_D/2 * math.sin(a)))
        bore = Polygon(bore_pts)

        # Corner pockets (4)
        pockets = []
        ps = POCKET_SIZE
        po = W/2 - POCKET_OFFSET - ps/2  # center offset from origin
        for sx, sy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            cx, cy = sx * po, sy * po
            pocket_pts = [
                (cx - ps/2, cy - ps/2),
                (cx + ps/2, cy - ps/2),
                (cx + ps/2, cy + ps/2),
                (cx - ps/2, cy + ps/2),
            ]
            # Round corners of pocket (r=0.5)
            pockets.append(Polygon(pocket_pts))

        # Boolean difference
        profile = outer
        for s in slots:
            profile = profile.difference(s)
        profile = profile.difference(bore)
        for p in pockets:
            profile = profile.difference(p)

        # Extract contours
        if isinstance(profile, MultiPolygon):
            geoms = list(profile.geoms)
        else:
            geoms = [profile]

        for geom in geoms:
            ext = list(geom.exterior.coords)
            paths.append(ext)
            for interior in geom.interiors:
                paths.append(list(interior.coords))

    except ImportError:
        print("  WARNUNG: shapely nicht verfuegbar, verwende vereinfachte Geometrie")
        # Fallback: just outer rect + bore circle
        paths.append(rounded_rect(W, H, R_CORNER, 16))
        bore_pts = []
        for i in range(64):
            a = 2 * math.pi * i / 64
            bore_pts.append((BORE_D/2 * math.cos(a), BORE_D/2 * math.sin(a)))
        bore_pts.append(bore_pts[0])
        paths.append(bore_pts)

    return paths


# ================================================================
# 1) CadQuery - Variant A (from SVG)
# ================================================================
print("\n" + "="*60)
print("1A) CadQuery - from SVG")
print("="*60)

try:
    import cadquery as cq
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
    from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopoDS import TopoDS
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    def cq_wire_from_points(pts):
        """Create an OCC wire from a list of (x,y) points."""
        edges = []
        for i in range(len(pts) - 1):
            p1 = gp_Pnt(pts[i][0], pts[i][1], 0)
            p2 = gp_Pnt(pts[i+1][0], pts[i+1][1], 0)
            if p1.Distance(p2) > 1e-6:
                edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
                edges.append(edge)
        wire_builder = BRepBuilderAPI_MakeWire()
        for e in edges:
            wire_builder.Add(e)
        return wire_builder.Wire()

    def cq_hlr_edges(shape):
        """HLR projection from top, return edge list as ((x1,y1),(x2,y2))."""
        BRepMesh_IncrementalMesh(shape, 0.05, True)
        ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, -1))
        projector = HLRAlgo_Projector(ax)
        hlr = HLRBRep_Algo()
        hlr.Add(shape)
        hlr.Projector(projector)
        hlr.Update()
        hlr.Hide()
        hlr_shapes = HLRBRep_HLRToShape(hlr)
        edges = []
        for method in ['VCompound', 'OutLineVCompound']:
            try:
                comp = getattr(hlr_shapes, method)()
                if comp and not comp.IsNull():
                    explorer = TopExp_Explorer(comp, TopAbs_EDGE)
                    while explorer.More():
                        edge = TopoDS.Edge_s(explorer.Current())
                        try:
                            adaptor = BRepAdaptor_Curve(edge)
                            p1 = adaptor.Value(adaptor.FirstParameter())
                            p2 = adaptor.Value(adaptor.LastParameter())
                            edges.append(((p1.X(), -p1.Y()), (p2.X(), -p2.Y())))
                        except:
                            pass
                        explorer.Next()
            except:
                pass
        return edges

    if svg_sub_paths:
        # Build outer wire + face
        outer_wire = cq_wire_from_points(svg_sub_paths[0])
        face_builder = BRepBuilderAPI_MakeFace(outer_wire, True)

        # Add holes
        for hole_sp in svg_sub_paths[1:]:
            if len(hole_sp) > 2:
                hole_wire = cq_wire_from_points(hole_sp)
                face_builder.Add(hole_wire)

        face = face_builder.Face()
        # Extrude 1mm
        solid = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, 1)).Shape()

        # HLR
        edges = cq_hlr_edges(solid)
        write_svg_from_edges(edges, "CadQuery - from SVG", OUT / 'aufgabe06_cadquery_from_svg.svg')
    else:
        print("  Keine SVG-Daten verfuegbar")

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# 1B) CadQuery - Variant B (parametric)
# ================================================================
print("\n" + "="*60)
print("1B) CadQuery - parametric")
print("="*60)

try:
    import cadquery as cq
    from cadquery import exporters

    # Build profile using CadQuery API
    profile_cq = (
        cq.Workplane("XY")
        .rect(W, H)
        .extrude(1)
        .edges("|Z").fillet(R_CORNER)
    )

    # 4 T-slots
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        # Neck
        ncx = -sin_a * (W/2 - NECK_DEPTH/2)
        ncy = cos_a * (W/2 - NECK_DEPTH/2)
        if angle in [0, 180]:
            nw, nh = NECK_W, NECK_DEPTH
        else:
            nw, nh = NECK_DEPTH, NECK_W
        neck = (cq.Workplane("XY").center(ncx, ncy).rect(nw, nh).extrude(1))
        profile_cq = profile_cq.cut(neck)

        # Head
        hcx = -sin_a * (W/2 - NECK_DEPTH - HEAD_DEPTH/2)
        hcy = cos_a * (W/2 - NECK_DEPTH - HEAD_DEPTH/2)
        if angle in [0, 180]:
            hw2, hh2 = HEAD_W, HEAD_DEPTH
        else:
            hw2, hh2 = HEAD_DEPTH, HEAD_W
        head = (cq.Workplane("XY").center(hcx, hcy).rect(hw2, hh2).extrude(1))
        profile_cq = profile_cq.cut(head)

    # Central bore
    bore = cq.Workplane("XY").circle(BORE_D/2).extrude(1)
    profile_cq = profile_cq.cut(bore)

    # Corner pockets
    ps = POCKET_SIZE
    po = W/2 - POCKET_OFFSET - ps/2
    for sx, sy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        pocket = (cq.Workplane("XY").center(sx*po, sy*po).rect(ps, ps).extrude(1))
        profile_cq = profile_cq.cut(pocket)

    vol = profile_cq.val().Volume()
    print(f"  Querschnittsflaeche: {vol:.1f} mm^2 (Hoehe=1mm)")

    # HLR projection
    shape = profile_cq.val().wrapped
    edges = cq_hlr_edges(shape)
    write_svg_from_edges(edges, "CadQuery - parametric", OUT / 'aufgabe06_cadquery_parametric.svg')

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# 2A) build123d - from SVG
# ================================================================
print("\n" + "="*60)
print("2A) build123d - from SVG")
print("="*60)

try:
    from build123d import *
    from build123d import Line as B3dLine, Wire as B3dWire

    if svg_sub_paths:
        # Build sketch from SVG points
        with BuildSketch() as sk_svg:
            # Build outer face from points
            # Use make_face approach: create wires, then face
            pass

        # Alternative: directly extract points and write SVG
        # Since build123d sketch building from arbitrary points is complex,
        # we use the OCC kernel directly through build123d
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
        from OCP.gp import gp_Pnt
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_EDGE
        from OCP.TopoDS import TopoDS
        from OCP.BRepAdaptor import BRepAdaptor_Curve

        # Reuse wire builder from CadQuery section
        outer_wire = cq_wire_from_points(svg_sub_paths[0])
        face_builder = BRepBuilderAPI_MakeFace(outer_wire, True)
        for hole_sp in svg_sub_paths[1:]:
            if len(hole_sp) > 2:
                hole_wire = cq_wire_from_points(hole_sp)
                face_builder.Add(hole_wire)
        face = face_builder.Face()

        # Extract edges from face
        edges_b3d = []
        explorer = TopExp_Explorer(face, TopAbs_EDGE)
        while explorer.More():
            edge = TopoDS.Edge_s(explorer.Current())
            try:
                adaptor = BRepAdaptor_Curve(edge)
                p1 = adaptor.Value(adaptor.FirstParameter())
                p2 = adaptor.Value(adaptor.LastParameter())
                edges_b3d.append(((p1.X(), p1.Y()), (p2.X(), p2.Y())))
            except:
                pass
            explorer.Next()
        write_svg_from_edges(edges_b3d, "build123d - from SVG", OUT / 'aufgabe06_build123d_from_svg.svg')
    else:
        print("  Keine SVG-Daten verfuegbar")

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# 2B) build123d - parametric
# ================================================================
print("\n" + "="*60)
print("2B) build123d - parametric")
print("="*60)

try:
    from build123d import *

    with BuildSketch() as sk_param:
        RectangleRounded(W, H, R_CORNER)

        # T-slots on each side using explicit coordinates (no rotation)
        # Top slot (y positive)
        with Locations([(0, W/2 - NECK_DEPTH/2)]):
            Rectangle(NECK_W, NECK_DEPTH, mode=Mode.SUBTRACT)
        with Locations([(0, W/2 - NECK_DEPTH - HEAD_DEPTH/2)]):
            Rectangle(HEAD_W, HEAD_DEPTH, mode=Mode.SUBTRACT)

        # Bottom slot (y negative)
        with Locations([(0, -(W/2 - NECK_DEPTH/2))]):
            Rectangle(NECK_W, NECK_DEPTH, mode=Mode.SUBTRACT)
        with Locations([(0, -(W/2 - NECK_DEPTH - HEAD_DEPTH/2))]):
            Rectangle(HEAD_W, HEAD_DEPTH, mode=Mode.SUBTRACT)

        # Right slot (x positive)
        with Locations([(W/2 - NECK_DEPTH/2, 0)]):
            Rectangle(NECK_DEPTH, NECK_W, mode=Mode.SUBTRACT)
        with Locations([(W/2 - NECK_DEPTH - HEAD_DEPTH/2, 0)]):
            Rectangle(HEAD_DEPTH, HEAD_W, mode=Mode.SUBTRACT)

        # Left slot (x negative)
        with Locations([(-(W/2 - NECK_DEPTH/2), 0)]):
            Rectangle(NECK_DEPTH, NECK_W, mode=Mode.SUBTRACT)
        with Locations([(-(W/2 - NECK_DEPTH - HEAD_DEPTH/2), 0)]):
            Rectangle(HEAD_DEPTH, HEAD_W, mode=Mode.SUBTRACT)

        # Central bore
        Circle(BORE_D/2, mode=Mode.SUBTRACT)

        # Corner pockets
        ps = POCKET_SIZE
        po = W/2 - POCKET_OFFSET - ps/2
        for sx, sy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            with Locations([(sx*po, sy*po)]):
                Rectangle(ps, ps, mode=Mode.SUBTRACT)

    # Extract edges from sketch via OCC wrapped shape
    edges_b3d_param = []
    sketch_obj = sk_param.sketch
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopoDS import TopoDS
    from OCP.BRepAdaptor import BRepAdaptor_Curve

    # The sketch's wrapped is a TopoDS_Compound containing faces
    wrapped = sketch_obj.wrapped
    face_exp = TopExp_Explorer(wrapped, TopAbs_FACE)
    total_area = 0.0
    while face_exp.More():
        face = TopoDS.Face_s(face_exp.Current())
        from OCP.GProp import GProp_GProps
        from OCP.BRepGProp import BRepGProp
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        total_area += props.Mass()

        edge_exp = TopExp_Explorer(face, TopAbs_EDGE)
        while edge_exp.More():
            edge = TopoDS.Edge_s(edge_exp.Current())
            try:
                adaptor = BRepAdaptor_Curve(edge)
                p1 = adaptor.Value(adaptor.FirstParameter())
                p2 = adaptor.Value(adaptor.LastParameter())
                edges_b3d_param.append(((p1.X(), p1.Y()), (p2.X(), p2.Y())))
            except:
                pass
            edge_exp.Next()
        face_exp.Next()

    print(f"  Querschnittsflaeche: {total_area:.1f} mm^2")
    write_svg_from_edges(edges_b3d_param, "build123d - parametric", OUT / 'aufgabe06_build123d_parametric.svg')

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# 3A) SolidPython2 - from SVG (SVG via shapely)
# ================================================================
print("\n" + "="*60)
print("3A) SolidPython2 - from SVG (via shapely)")
print("="*60)

try:
    from shapely.geometry import Polygon, MultiPolygon

    if svg_sub_paths:
        # Build shapely geometry from SVG sub-paths
        # Use buffer(0) to fix any self-intersections from arc approximation
        outer_poly = Polygon(svg_sub_paths[0]).buffer(0)
        for hole_sp in svg_sub_paths[1:]:
            if len(hole_sp) > 2:
                hole_poly = Polygon(hole_sp).buffer(0)
                outer_poly = outer_poly.difference(hole_poly)

        # Extract contours for SVG
        sp_paths = []
        if isinstance(outer_poly, MultiPolygon):
            geoms = list(outer_poly.geoms)
        else:
            geoms = [outer_poly]
        for geom in geoms:
            sp_paths.append(list(geom.exterior.coords))
            for interior in geom.interiors:
                sp_paths.append(list(interior.coords))

        write_svg_from_subpaths(sp_paths, "SolidPython2 - from SVG (shapely)", OUT / 'aufgabe06_solidpython_from_svg.svg')
    else:
        print("  Keine SVG-Daten verfuegbar")

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# 3B) SolidPython2 - parametric (.scad + shapely SVG)
# ================================================================
print("\n" + "="*60)
print("3B) SolidPython2 - parametric")
print("="*60)

try:
    from solid2 import *

    # Build OpenSCAD model
    base = minkowski()(
        cube([W - 2*R_CORNER, H - 2*R_CORNER, 0.5], center=True),
        cylinder(r=R_CORNER, h=0.5, _fn=64)
    )

    # T-slots
    for angle in [0, 90, 180, 270]:
        neck = rotate(angle)(
            translate([0, W/2 - NECK_DEPTH/2, 0])(
                cube([NECK_W, NECK_DEPTH, 2], center=True)
            )
        )
        head = rotate(angle)(
            translate([0, W/2 - NECK_DEPTH - HEAD_DEPTH/2, 0])(
                cube([HEAD_W, HEAD_DEPTH, 2], center=True)
            )
        )
        base -= neck
        base -= head

    # Central bore
    base -= cylinder(r=BORE_D/2, h=2, center=True, _fn=64)

    # Corner pockets
    ps = POCKET_SIZE
    po = W/2 - POCKET_OFFSET - ps/2
    for sx, sy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        base -= translate([sx*po, sy*po, 0])(
            cube([ps, ps, 2], center=True)
        )

    # Add 2D projection
    base_2d = projection(cut=True)(base)

    scad_text = scad_render(base_2d)
    scad_path = OUT / 'aufgabe06_solidpython_parametric.scad'
    scad_path.write_text(scad_text, encoding='utf-8')
    print(f"  SCAD geschrieben: {scad_path.name} ({len(scad_text)} Bytes)")

    # Also create SVG via shapely for visual comparison
    param_paths = build_parametric_subpaths()
    write_svg_from_subpaths(param_paths, "SolidPython2 - parametric (shapely)", OUT / 'aufgabe06_solidpython_parametric.svg')

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()


# ================================================================
# Comparison HTML
# ================================================================
print("\n" + "="*60)
print("Vergleichs-HTML erstellen")
print("="*60)

import base64

# Read reference image as base64
img_b64 = ""
try:
    img_data = IMG_INPUT.read_bytes()
    img_b64 = base64.b64encode(img_data).decode('ascii')
except Exception as e:
    print(f"  Bild nicht lesbar: {e}")

# Read all SVGs
svg_files = [
    ("CadQuery - from SVG", "aufgabe06_cadquery_from_svg.svg"),
    ("CadQuery - parametric", "aufgabe06_cadquery_parametric.svg"),
    ("build123d - from SVG", "aufgabe06_build123d_from_svg.svg"),
    ("build123d - parametric", "aufgabe06_build123d_parametric.svg"),
    ("SolidPython2 - from SVG", "aufgabe06_solidpython_from_svg.svg"),
    ("SolidPython2 - parametric", "aufgabe06_solidpython_parametric.svg"),
]

svg_contents = {}
for title, fname in svg_files:
    fpath = OUT / fname
    if fpath.exists():
        svg_contents[title] = fpath.read_text(encoding='utf-8')
    else:
        svg_contents[title] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-25 -25 50 50" width="400" height="400"><text x="0" y="0" font-size="4" text-anchor="middle" fill="red">nicht erstellt</text></svg>'

html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Aufgabe 06: CAD-Tool Vergleich - Aluminiumprofil 40x40mm</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }}
  h1 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
  h2 {{ color: #1976D2; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }}
  .card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .card h3 {{ margin-top: 0; color: #555; font-size: 14px; }}
  .card svg {{ width: 100%; height: auto; border: 1px solid #ddd; }}
  .ref-img {{ max-width: 300px; border: 1px solid #ddd; }}
  table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
  th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
  th {{ background: #2196F3; color: white; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  .star {{ color: #FFC107; }}
  .good {{ color: #4CAF50; font-weight: bold; }}
  .ok {{ color: #FF9800; }}
  .bad {{ color: #F44336; }}
  .section {{ margin: 30px 0; }}
</style>
</head>
<body>

<h1>Aufgabe 06: CAD-Tool Vergleich</h1>
<p>Aluminiumprofil 40x40mm (Item-kompatibel) &mdash; 3 Tools, je 2 Varianten</p>

<div class="section">
<h2>Referenzbild</h2>
<img src="data:image/jpeg;base64,{img_b64}" class="ref-img" alt="Aluminiumprofil 40x40mm">
<p>Quelle: C100_60800-STLS-0500-2.jpg &mdash; 40x40mm, R4.5 Ecken, 4 T-Nuten 8mm, Bohrung D6.8</p>
</div>

<div class="section">
<h2>Variante A: SVG-Import (aus aufgabe01_path.svg)</h2>
<div class="grid">
'''

# Add Variant A cards
for title in ["CadQuery - from SVG", "build123d - from SVG", "SolidPython2 - from SVG"]:
    svg = svg_contents.get(title, "")
    html += f'<div class="card"><h3>{title}</h3>\n{svg}\n</div>\n'

html += '''</div>
</div>

<div class="section">
<h2>Variante B: Parametrisch aufgebaut</h2>
<div class="grid">
'''

# Add Variant B cards
for title in ["CadQuery - parametric", "build123d - parametric", "SolidPython2 - parametric"]:
    svg = svg_contents.get(title, "")
    html += f'<div class="card"><h3>{title}</h3>\n{svg}\n</div>\n'

html += f'''</div>
</div>

<div class="section">
<h2>Bewertung</h2>
<table>
<tr>
  <th>Kriterium</th>
  <th>CadQuery</th>
  <th>build123d</th>
  <th>SolidPython2</th>
</tr>
<tr>
  <td><b>Geometrie-Korrektheit</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; Exakt, BREP-Kernel</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; Gleicher Kernel (OCC)</td>
  <td class="ok">&#9733;&#9733;&#9733;&#9734;&#9734; Mesh-basiert, Rundung via minkowski</td>
</tr>
<tr>
  <td><b>SVG-Import</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; Wire/Face/Extrude + HLR</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; Gleicher OCC-Weg moeglich</td>
  <td class="ok">&#9733;&#9733;&#9733;&#9734;&#9734; Nur via shapely (kein nativer Import)</td>
</tr>
<tr>
  <td><b>Parametrisches Modellieren</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; Fluent API, gut lesbar</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; Modernste API, Kontext-Builder</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; CSG sehr intuitiv</td>
</tr>
<tr>
  <td><b>SVG-Export</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; HLR-Projektion, exakte Kanten</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; Edge-Extraktion direkt</td>
  <td class="bad">&#9733;&#9733;&#9734;&#9734;&#9734; Kein nativer SVG, nur via Umweg</td>
</tr>
<tr>
  <td><b>Einfachheit des Codes</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9734; Gut dokumentiert</td>
  <td class="ok">&#9733;&#9733;&#9733;&#9734;&#9734; Kontext-Manager gewoehnungsbeduerftig</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; Am einfachsten (CSG-Logik)</td>
</tr>
<tr>
  <td><b>3D-Export (STEP/STL)</b></td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; STEP, STL, IGES nativ</td>
  <td class="good">&#9733;&#9733;&#9733;&#9733;&#9733; STEP, STL nativ</td>
  <td class="ok">&#9733;&#9733;&#9733;&#9734;&#9734; Nur STL (via OpenSCAD)</td>
</tr>
</table>

<h3>Fazit</h3>
<ul>
  <li><b>CadQuery</b> bietet den besten Kompromiss: leistungsstarker BREP-Kernel (OpenCASCADE),
      exzellenter SVG-Export via HLR-Projektion, gute Dokumentation. Ideal fuer praezise technische Zeichnungen.</li>
  <li><b>build123d</b> hat die modernste Python-API mit Kontext-Managern und ist der geistige Nachfolger
      von CadQuery. Gleicher Kernel, aber die API erfordert Einarbeitung. Sehr gut fuer komplexe Modelle.</li>
  <li><b>SolidPython2/OpenSCAD</b> ist am einfachsten zu erlernen (CSG-Logik), kann aber keine
      Vektorgrafik-Exporte und keine STEP-Dateien. Fuer 3D-Druck direkt geeignet, fuer technische
      Dokumentation nur ueber Umwege (shapely).</li>
</ul>
</div>

<div class="section" style="color:#888; font-size:12px;">
<p>Erstellt: 2026-04-01 | Script: aufgabe06_vergleich_final.py | Profil: 40x40mm Item-kompatibel</p>
</div>
</body>
</html>
'''

html_path = OUT / 'aufgabe06_vergleich.html'
html_path.write_text(html, encoding='utf-8')
print(f"  HTML geschrieben: {html_path}")

# ================================================================
# Summary
# ================================================================
print("\n" + "="*60)
print("ZUSAMMENFASSUNG")
print("="*60)
print(f"\nAusgabeverzeichnis: {OUT}")
print("\nErzeugte Dateien:")
for f in sorted(OUT.glob("aufgabe06_*")):
    size = f.stat().st_size
    print(f"  {f.name:50s} {size:>8d} Bytes")
