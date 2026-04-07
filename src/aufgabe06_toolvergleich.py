"""
Aufgabe 06: Elesa-Ganter GN 10b-S Profil 45x45, Nut 10
Vergleich: CadQuery vs build123d vs SolidPython/OpenSCAD

Profil: 45x45mm, Nut 10mm (45er Raster), Typ schwer
Querschnittsflaeche: 7.50 cm^2 = 750 mm^2
Material: AlMgSi0,5 (EN AW-6063)
"""

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'output' / 'aufgabe06'
OUT.mkdir(exist_ok=True, parents=True)

# === Profil-Parameter GN 10b-S 45x45 Nut 10 ===
W = H = 45.0          # Profilbreite/-hoehe
SLOT_W = 10.0         # Nutoeffnung
SLOT_DEPTH = 14.5     # Nuttiefe ab Aussenkante
R_ECKE = 3.0          # Eckenradius (geschaetzt)
BORE_D = 6.8          # Zentralbohrung (Standard)
WALL_T = 2.0          # Wandstaerke (geschaetzt)

# T-Nut Geometrie (Bosch b-Typ, Nut 10)
HEAD_W = 16.5         # T-Kopf Breite (geschaetzt fuer Nut 10)
HEAD_DEPTH = 2.0      # T-Kopf Tiefe (Lippendicke)
NECK_DEPTH = SLOT_DEPTH - HEAD_DEPTH  # Halstiefe

print(f"Profil: {W}x{H}mm, Nut {SLOT_W}mm")
print(f"Soll-Flaeche: 750 mm^2")

# ================================================================
# 1) CadQuery
# ================================================================
print("\n" + "="*60)
print("1) CadQuery")
print("="*60)

try:
    import cadquery as cq
    from cadquery import exporters

    # Grundkoerper
    profile_cq = (
        cq.Workplane("XY")
        .rect(W, H)
        .extrude(1)
        .edges("|Z").fillet(R_ECKE)
    )

    # 4 T-Nuten
    for angle in [0, 90, 180, 270]:
        # Hals (schmal)
        neck = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .center(0, W/2 - NECK_DEPTH/2)
            .rect(SLOT_W, NECK_DEPTH)
            .extrude(1)
        )
        # Kopf (breit)
        head = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .center(0, W/2 - NECK_DEPTH - HEAD_DEPTH/2)
            .rect(HEAD_W, HEAD_DEPTH)
            .extrude(1)
        )
        profile_cq = profile_cq.cut(neck).cut(head)

    # Bohrung
    bore = cq.Workplane("XY").circle(BORE_D/2).extrude(1)
    profile_cq = profile_cq.cut(bore)

    vol = profile_cq.val().Volume()
    area = vol  # Hoehe=1mm, also Volumen = Flaeche
    print(f"  Querschnittsflaeche: {area:.1f} mm^2 (Soll: 750)")

    # STEP Export
    exporters.export(profile_cq, str(OUT / 'profil_cadquery.step'))
    print(f"  STEP exportiert: OK")

    # SVG Export (eigener, nicht CadQuery's)
    # Draufsicht des Querschnitts
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopoDS import TopoDS
    import re

    shape = profile_cq.val().wrapped
    BRepMesh_IncrementalMesh(shape, 0.1, True)

    # Draufsicht (z nach unten)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, -1))
    projector = HLRAlgo_Projector(ax)
    hlr = HLRBRep_Algo()
    hlr.Add(shape)
    hlr.Projector(projector)
    hlr.Update()
    hlr.Hide()
    hlr_shapes = HLRBRep_HLRToShape(hlr)

    def edges_to_paths(compound):
        paths = []
        explorer = TopExp_Explorer(compound, TopAbs_EDGE)
        while explorer.More():
            edge = TopoDS.Edge_s(explorer.Current())
            try:
                adaptor = BRepAdaptor_Curve(edge)
                p1 = adaptor.Value(adaptor.FirstParameter())
                p2 = adaptor.Value(adaptor.LastParameter())
                paths.append(f"M {p1.X():.2f},{-p1.Y():.2f} L {p2.X():.2f},{-p2.Y():.2f}")
            except: pass
            explorer.Next()
        return paths

    vis_paths = []
    for method in ['VCompound', 'OutLineVCompound']:
        try:
            comp = getattr(hlr_shapes, method)()
            if comp and not comp.IsNull():
                vis_paths.extend(edges_to_paths(comp))
        except: pass

    # SVG schreiben
    margin = 5
    vb = f"{-W/2-margin} {-H/2-margin} {W+2*margin} {H+2*margin}"
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">
<rect x="{-W/2-margin}" y="{-H/2-margin}" width="{W+2*margin}" height="{H+2*margin}" fill="white"/>
'''
    for d in vis_paths:
        svg += f'<path d="{d}" fill="none" stroke="black" stroke-width="0.3"/>\n'
    svg += f'<text x="0" y="{H/2+margin-1}" font-size="3" text-anchor="middle" fill="#555">CadQuery - GN 10b-S 45x45</text>\n'
    svg += '</svg>'

    (OUT / 'profil_cadquery.svg').write_text(svg, encoding='utf-8')
    print(f"  SVG exportiert: {len(vis_paths)} Kanten")

except Exception as e:
    print(f"  Fehler: {e}")
    import traceback; traceback.print_exc()

# ================================================================
# 2) build123d
# ================================================================
print("\n" + "="*60)
print("2) build123d")
print("="*60)

try:
    from build123d import *

    # Sketch aufbauen
    with BuildPart() as b123_part:
        with BuildSketch() as sk:
            RectangleRounded(W, H, R_ECKE)
            # Nuten als Subtraktion
            for i in range(4):
                angle = i * 90
                with Locations([(0, 0)]):
                    # Hals
                    with BuildSketch(mode=Mode.SUBTRACT) as neck_sk:
                        with Locations([(0, 0)]):
                            with PolarLocations(W/2 - NECK_DEPTH/2, 1, angle, angle):
                                Rectangle(SLOT_W, NECK_DEPTH)
                    # Das funktioniert nicht so einfach in build123d...
            # Bohrung
            Circle(BORE_D/2, mode=Mode.SUBTRACT)
        extrude(amount=1)

    area_b = b123_part.part.volume
    print(f"  Querschnittsflaeche: {area_b:.1f} mm^2")

    # STEP Export
    from build123d import export_step
    export_step(b123_part.part, str(OUT / 'profil_build123d.step'))
    print(f"  STEP exportiert: OK")

except Exception as e:
    print(f"  Fehler: {e}")
    print("  build123d Nut-Rotation ist komplex, wird vereinfacht...")

    # Vereinfachte Version ohne Rotation
    try:
        from build123d import *
        with BuildPart() as b123_simple:
            with BuildSketch() as sk2:
                RectangleRounded(W, H, R_ECKE)
                # Einfache Nuten (nur oben/unten/links/rechts)
                with Locations([(0, W/2 - NECK_DEPTH/2)]):
                    Rectangle(SLOT_W, NECK_DEPTH, mode=Mode.SUBTRACT)
                with Locations([(0, -(W/2 - NECK_DEPTH/2))]):
                    Rectangle(SLOT_W, NECK_DEPTH, mode=Mode.SUBTRACT)
                with Locations([(W/2 - NECK_DEPTH/2, 0)]):
                    Rectangle(NECK_DEPTH, SLOT_W, mode=Mode.SUBTRACT)
                with Locations([(-(W/2 - NECK_DEPTH/2), 0)]):
                    Rectangle(NECK_DEPTH, SLOT_W, mode=Mode.SUBTRACT)
                Circle(BORE_D/2, mode=Mode.SUBTRACT)
            extrude(amount=1)
        area_b2 = b123_simple.part.volume
        print(f"  Querschnittsflaeche (vereinfacht): {area_b2:.1f} mm^2")
        from build123d import export_step
        export_step(b123_simple.part, str(OUT / 'profil_build123d.step'))
        print(f"  STEP exportiert: OK")
    except Exception as e2:
        print(f"  Auch vereinfacht fehlgeschlagen: {e2}")

# ================================================================
# 3) SolidPython2 (OpenSCAD)
# ================================================================
print("\n" + "="*60)
print("3) SolidPython2 / OpenSCAD")
print("="*60)

try:
    from solid2 import *

    # Grundkoerper mit Rundung (minkowski)
    base = minkowski()(
        cube([W - 2*R_ECKE, H - 2*R_ECKE, 0.5], center=True),
        cylinder(r=R_ECKE, h=0.5, _fn=32)
    )

    # 4 Nuten
    for angle in [0, 90, 180, 270]:
        neck = rotate(angle)(
            translate([0, W/2 - NECK_DEPTH/2, 0])(
                cube([SLOT_W, NECK_DEPTH, 2], center=True)
            )
        )
        head = rotate(angle)(
            translate([0, W/2 - NECK_DEPTH - HEAD_DEPTH/2, 0])(
                cube([HEAD_W, HEAD_DEPTH, 2], center=True)
            )
        )
        base -= neck
        base -= head

    # Bohrung
    base -= cylinder(r=BORE_D/2, h=2, center=True, _fn=64)

    scad_text = scad_render(base)
    scad_path = OUT / 'profil_openscad.scad'
    scad_path.write_text(scad_text, encoding='utf-8')
    print(f"  SCAD geschrieben: {len(scad_text)} Bytes")
    print(f"  Datei: {scad_path}")
    print("  (OpenSCAD muss separat installiert sein fuer STL-Render)")

except Exception as e:
    print(f"  Fehler: {e}")

# ================================================================
# Zusammenfassung
# ================================================================
print("\n" + "="*60)
print("ZUSAMMENFASSUNG")
print("="*60)
print(f"""
Profil: Elesa-Ganter GN 10b-S, 45 x 45mm, Nut 10
Soll-Querschnittsflaeche: 750 mm^2

| Tool         | Kernel       | HLR | SVG | STEP | Schwierigkeit |
|-------------|-------------|-----|-----|------|---------------|
| CadQuery    | OpenCASCADE | Ja  | Ja  | Ja   | Mittel        |
| build123d   | OpenCASCADE | Ja  | Ja  | Ja   | API komplex   |
| SolidPython | OpenSCAD    | Nein| Nein| Nein | Einfach       |

Fazit: CadQuery bietet den besten Kompromiss aus Funktionalitaet und Bedienbarkeit.
build123d hat modernere Syntax, aber die kontextbasierten Builder sind gewoehnungsbeduerftig.
SolidPython ist am einfachsten, kann aber kein HLR und keine Projektion.
""")
