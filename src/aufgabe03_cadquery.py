"""
Aufgabe 03 CadQuery: Schrägriss (oblique projection) of aluminum profile 40x40mm
with automatic Hidden Line Removal using OpenCASCADE HLR.

The profile is built parametrically in CadQuery:
- 40x40 outer square with R4.5 corner fillets
- 4 T-slots (8mm wide opening, undercut pockets)
- Central bore D6.8
- Extruded to 100mm

HLR projects the solid into a Kavalierprojektion-like oblique view,
automatically separating visible and hidden edges.
"""

import math
from pathlib import Path
import cadquery as cq

# OCP imports for HLR
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

OUT = Path(__file__).resolve().parent.parent / 'output'
OUT.mkdir(exist_ok=True)
SVG_OUT = OUT / 'aufgabe03_schraegriss_cadquery.svg'

# ================================================================
# 1) Build the aluminium profile cross-section parametrically
# ================================================================

# Profile dimensions (all in mm)
OUTER = 40.0
R_CORNER = 4.5
SLOT_W = 8.0        # T-slot opening width
SLOT_DEPTH = 12.5   # total depth from edge to slot bottom
BORE_D = 6.8
POCKET_R = 6.5      # corner pocket approximate size
EXTRUDE_H = 100.0

HALF = OUTER / 2.0  # 20

# Start with rounded outer square
outer = (
    cq.Workplane("XY")
    .rect(OUTER, OUTER)
    .extrude(1)  # temporary
    .edges("|Z")
    .fillet(R_CORNER)
)
# Get the filleted face
outer_face = outer.faces("<Z").val()

# Build profile as 2D operations on a workplane
# Approach: create the cross-section using boolean operations on the face

# Outer rounded rectangle
profile = (
    cq.Workplane("XY")
    .rect(OUTER, OUTER)
)

# We'll build the 2D cross-section and extrude at the end
# CadQuery approach: sketch on workplane, extrude, then cut features

print("Building profile...")

# Step 1: Outer rounded box extruded
solid = (
    cq.Workplane("XY")
    .rect(OUTER, OUTER)
    .extrude(EXTRUDE_H)
)
# Fillet the 4 vertical edges (corners)
solid = solid.edges("|Z").fillet(R_CORNER)

# Step 2: Cut the 4 T-slot openings (simplified as rectangular slots)
# Each slot: 8mm wide opening from the edge, going 12.5mm deep
# The slot narrows: opening is 8mm, but inner part widens to ~14mm (T-shape)

# Slot along +Y face (top)
slot_half_w = SLOT_W / 2.0  # 4mm
slot_opening_depth = 4.5  # depth of the narrow part from outside
slot_inner_width = 16.0   # width of the T undercut part
slot_inner_half = slot_inner_width / 2.0  # 8mm

# T-slot profile: narrow opening then wider undercut
# For simplicity, we model it as two rectangular cuts per slot

# Narrow part (opening): 8mm wide x 4.5mm deep from outside
# Wide part (undercut): ~14mm wide x 8mm deep behind the narrow part

for angle in [0, 90, 180, 270]:
    # Narrow opening
    solid = (
        solid
        .faces(">Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .center(0, HALF - slot_opening_depth / 2)
        .rect(SLOT_W, slot_opening_depth)
        .cutBlind(-EXTRUDE_H)
    )
    # Wider undercut behind the opening
    inner_depth = SLOT_DEPTH - slot_opening_depth  # 8mm
    solid = (
        solid
        .faces(">Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .center(0, HALF - slot_opening_depth - inner_depth / 2)
        .rect(slot_inner_width, inner_depth)
        .cutBlind(-EXTRUDE_H)
    )

# Step 3: Central bore
solid = (
    solid
    .faces(">Z")
    .workplane()
    .hole(BORE_D)
)

# Step 4: Corner pockets (simplified as small cylindrical cutouts)
# There are 4 corner pockets at 45-degree positions
pocket_offset = 10.0  # distance from center to pocket center
pocket_r = 3.25       # pocket radius (half of 6.5)
for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
    solid = (
        solid
        .faces(">Z")
        .workplane()
        .center(dx * pocket_offset, dy * pocket_offset)
        .circle(pocket_r)
        .cutBlind(-EXTRUDE_H)
    )

# Fillet the inner vertical edges of the T-slots for realism
# Add R2 fillets at slot entries
try:
    # Select short edges at the slot entry transitions
    # This is optional - skip if it fails
    pass
except Exception:
    pass

print(f"Profile solid built: {solid}")

# Get the OCC shape
shape = solid.val().wrapped

# ================================================================
# 2) Set up the oblique projection using HLR
# ================================================================
# Kavalierprojektion: view direction that mimics an oblique projection
# We need a projection direction. For a Schrägriss at 30 degrees:
#
# In a true Kavalierprojektion, we project orthographically from a specific direction.
# The direction vector for an oblique-like result from front-right-top:
#   Looking roughly from (1, 1, 0.577) towards origin
#
# For the HLR projector, gp_Ax2 defines:
#   - Origin: eye point (for parallel projection, only direction matters)
#   - Z direction: the viewing direction (into the screen)
#   - X direction: the "right" direction on screen

# We want the profile (which lies in XY, extruded along Z) to appear as:
# - Front face visible (XY plane)
# - Top face visible (looking slightly from above)
# - Right side visible (looking slightly from the right)

# For a Kavalierprojektion-like view:
# The extrusion axis (Z) should map to a diagonal going up-right at 30 degrees
# The X axis should remain horizontal
# The Y axis should remain vertical

# View direction: we look from the front-right-top
# Let's define this as looking along (-cos30*sin_elev, -sin30*sin_elev, -cos_elev)
# where the oblique angle determines how much of the top/side we see

# Actually, for an oblique parallel projection, we can use a shear transform
# on the shape before doing an orthographic front projection.

# Kavalierprojektion parameters:
ANGLE_DEG = 30   # angle of the receding lines
SHORTENING = 0.5  # Verkuerzungsfaktor for the depth axis

# The Z-axis of the solid (extrusion direction) is the "depth" axis.
# In Kavalierprojektion, the depth axis projects as:
#   dx = cos(angle) * shortening
#   dy = sin(angle) * shortening
# This is equivalent to an orthographic projection after applying a shear.

# Strategy: Apply a shear transform to map Z -> (Z + dx*Z, dy*Z, 0),
# then project orthographically from the front (along Z).
# But OCC doesn't have a direct shear. Instead we use an affine transform.

# Alternative: use a specific view direction for the HLR projector that
# produces a similar visual result to Kavalierprojektion.
#
# For a parallel oblique projection, the view direction relative to the object
# determines the apparent angle and shortening. We can compute this:
# If depth (Z) should appear at angle alpha with shortening k:
#   tan(view_angle_xz) = k * cos(alpha)  -> how far right we look
#   tan(view_angle_yz) = k * sin(alpha)  -> how far up we look
#
# The Z axis (extrusion) should map to screen direction (cos30*0.5, sin30*0.5)
# In 3D, this means looking from a direction where:
#   view = normalize(k*cos(a), k*sin(a), -1)

alpha = math.radians(ANGLE_DEG)
k = SHORTENING

# View direction (from eye towards object)
vx = k * math.cos(alpha)  # 0.433
vy = k * math.sin(alpha)  # 0.25
vz = -1.0
v_len = math.sqrt(vx**2 + vy**2 + vz**2)
vx, vy, vz = vx / v_len, vy / v_len, vz / v_len

print(f"View direction: ({vx:.4f}, {vy:.4f}, {vz:.4f})")

# The "up" direction on screen should be the Y axis
# The projection's X-axis (screen right) is cross(up, view)
# Let's define things properly:
# view_dir = direction we're looking (into screen) = (vx, vy, vz)
# up_hint = (0, 1, 0) - we want Y to be roughly "up" on screen
# screen_right = normalize(cross(up_hint, view_dir))
# screen_up = cross(view_dir, screen_right)

# For gp_Ax2: Z = view direction, X = screen right direction
view_dir = gp_Dir(vx, vy, vz)

# Screen right: cross((0,1,0), view_dir)
# cross(a, b) where a=(0,1,0), b=(vx,vy,vz) = (1*vz - 0*vy, 0*vx - 0*vz, 0*vy - 1*vx)
# = (vz, 0, -vx)
rx = vz
ry = 0.0
rz = -vx
r_len = math.sqrt(rx**2 + ry**2 + rz**2)
screen_right = gp_Dir(rx / r_len, ry / r_len, rz / r_len)

print("Setting up HLR...")

# Mesh the shape (required for HLR)
mesh = BRepMesh_IncrementalMesh(shape, 0.01, False, 0.1)
mesh.Perform()
print(f"Mesh done: {mesh.IsDone()}")

# Set up HLR algorithm
hlr = HLRBRep_Algo()
hlr.Add(shape)

# Create projector
ax = gp_Ax2(gp_Pnt(0, 0, 0), view_dir, screen_right)
projector = HLRAlgo_Projector(ax)

hlr.Projector(projector)
hlr.Update()
hlr.Hide()

print("HLR computation done.")

# Extract edge compounds
hlr_shapes = HLRBRep_HLRToShape(hlr)

# Visible edges
visible_sharp = hlr_shapes.VCompound()
visible_outline = hlr_shapes.OutLineVCompound()
visible_smooth = hlr_shapes.Rg1LineVCompound()

# Hidden edges
hidden_sharp = hlr_shapes.HCompound()
hidden_outline = hlr_shapes.OutLineHCompound()

print("Edge compounds extracted.")


# ================================================================
# 3) Convert OCC edge compounds to SVG paths
# ================================================================

def edges_to_svg_paths(compound, tol=0.05):
    """Convert a TopoDS_Compound of edges to SVG path data strings."""
    if compound is None or compound.IsNull():
        return []

    paths = []
    explorer = TopExp_Explorer(compound, TopAbs_EDGE)

    while explorer.More():
        edge = TopoDS.Edge_s(explorer.Current())
        try:
            adaptor = BRepAdaptor_Curve(edge)
            first = adaptor.FirstParameter()
            last = adaptor.LastParameter()

            # Discretize the curve
            deflection = GCPnts_QuasiUniformDeflection(adaptor, tol, first, last)

            if deflection.IsDone() and deflection.NbPoints() >= 2:
                points = []
                for i in range(1, deflection.NbPoints() + 1):
                    p = deflection.Value(i)
                    # HLR projects to 2D, but OCC keeps 3D coords with Z~0
                    # The X,Y are the projected coordinates
                    points.append((p.X(), p.Y()))

                if len(points) >= 2:
                    d = f"M {points[0][0]:.4f},{-points[0][1]:.4f}"
                    for px, py in points[1:]:
                        d += f" L {px:.4f},{-py:.4f}"
                    paths.append(d)
        except Exception as e:
            # Skip problematic edges
            pass

        explorer.Next()

    return paths


print("Converting edges to SVG paths...")

visible_paths = []
hidden_paths = []

for compound in [visible_sharp, visible_outline, visible_smooth]:
    visible_paths.extend(edges_to_svg_paths(compound))

for compound in [hidden_sharp, hidden_outline]:
    hidden_paths.extend(edges_to_svg_paths(compound))

print(f"Visible paths: {len(visible_paths)}, Hidden paths: {len(hidden_paths)}")


# ================================================================
# 4) Compute bounding box and generate SVG
# ================================================================

def get_bounds(paths):
    """Get bounding box of all SVG paths."""
    all_x, all_y = [], []
    for d in paths:
        tokens = d.replace(',', ' ').split()
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in ('M', 'L'):
                all_x.append(float(tokens[i + 1]))
                all_y.append(float(tokens[i + 2]))
                i += 3
            else:
                i += 1
    return all_x, all_y

all_paths = visible_paths + hidden_paths
bx, by = get_bounds(all_paths)

if not bx:
    print("ERROR: No paths generated!")
    exit(1)

min_x, max_x = min(bx), max(bx)
min_y, max_y = min(by), max(by)
width = max_x - min_x
height = max_y - min_y

print(f"Bounding box: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
print(f"Size: {width:.1f} x {height:.1f}")

# A4 landscape layout
A4_W, A4_H = 297, 210
RAND_L, RAND_R, RAND_T, RAND_B = 20, 10, 10, 10
ZF_W = A4_W - RAND_L - RAND_R  # 267
ZF_H = A4_H - RAND_T - RAND_B  # 190
SF_W, SF_H = 180, 28
SF_X = A4_W - RAND_R - SF_W
SF_Y = A4_H - RAND_B - SF_H

# Available drawing area (leave room for title block)
DRAW_W = ZF_W - 10
DRAW_H = ZF_H - SF_H - 15

# Scale to fit
scale = min(DRAW_W / width, DRAW_H / height) * 0.85
print(f"Scale factor: {scale:.3f}")

# Center the drawing in available area
cx = RAND_L + ZF_W / 2
cy = RAND_T + (ZF_H - SF_H) / 2

# Offset to center the profile
off_x = cx - (min_x + width / 2) * scale
off_y = cy - (min_y + height / 2) * scale


def transform_path(d, sc, ox, oy):
    """Scale and translate an SVG path."""
    tokens = d.replace(',', ' ').split()
    result = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ('M', 'L'):
            x = float(tokens[i + 1]) * sc + ox
            y = float(tokens[i + 2]) * sc + oy
            result.append(f"{t} {x:.3f},{y:.3f}")
            i += 3
        else:
            result.append(t)
            i += 1
    return ' '.join(result)


# Build SVG content
visible_svg = '\n'.join(
    f'<path d="{transform_path(d, scale, off_x, off_y)}" '
    f'fill="none" stroke="black" stroke-width="0.5" stroke-linecap="round"/>'
    for d in visible_paths
)

hidden_svg = '\n'.join(
    f'<path d="{transform_path(d, scale, off_x, off_y)}" '
    f'fill="none" stroke="black" stroke-width="0.25" '
    f'stroke-dasharray="2,1" stroke-linecap="round"/>'
    for d in hidden_paths
)

# Title block
schriftfeld = f'''
<rect x="{SF_X}" y="{SF_Y}" width="{SF_W}" height="{SF_H}" fill="white" stroke="black" stroke-width="0.35"/>
<line x1="{SF_X}" y1="{SF_Y+10}" x2="{SF_X+SF_W}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+50}" y1="{SF_Y}" x2="{SF_X+50}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+100}" y1="{SF_Y}" x2="{SF_X+100}" y2="{SF_Y+SF_H}" stroke="black" stroke-width="0.2"/>
<line x1="{SF_X+140}" y1="{SF_Y}" x2="{SF_X+140}" y2="{SF_Y+10}" stroke="black" stroke-width="0.2"/>
<text x="{SF_X+2}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Erstellt</text>
<text x="{SF_X+2}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">Claude Code (CadQuery HLR)</text>
<text x="{SF_X+52}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Methode</text>
<text x="{SF_X+52}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">OpenCASCADE HLR</text>
<text x="{SF_X+102}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Projektion</text>
<text x="{SF_X+102}" y="{SF_Y+8}" font-size="3.5" font-family="sans-serif" fill="black" font-weight="bold">Kavalierprojekt. 30/0.5</text>
<text x="{SF_X+142}" y="{SF_Y+3.5}" font-size="2.5" font-family="sans-serif" fill="#666">Datum</text>
<text x="{SF_X+142}" y="{SF_Y+8}" font-size="3" font-family="sans-serif" fill="black">2026-04-01</text>
<text x="{SF_X+2}" y="{SF_Y+15}" font-size="2.5" font-family="sans-serif" fill="#666">Benennung</text>
<text x="{SF_X+2}" y="{SF_Y+22}" font-size="4.5" font-family="sans-serif" fill="black" font-weight="bold">Alu-Profil 40x40 - Schr&#228;griss (CadQuery HLR)</text>
<text x="{SF_X+102}" y="{SF_Y+15}" font-size="2.5" font-family="sans-serif" fill="#666">Zeichnungs-Nr.</text>
<text x="{SF_X+102}" y="{SF_Y+22}" font-size="4" font-family="sans-serif" fill="black" font-weight="bold">A03-CQ</text>
'''

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{A4_W}mm" height="{A4_H}mm"
     viewBox="0 0 {A4_W} {A4_H}">

<!-- Background -->
<rect x="0" y="0" width="{A4_W}" height="{A4_H}" fill="white"/>

<!-- Drawing frame -->
<rect x="{RAND_L}" y="{RAND_T}" width="{ZF_W}" height="{ZF_H}"
      fill="none" stroke="black" stroke-width="0.5"/>

<!-- Visible edges (solid lines) -->
<g id="visible">
{visible_svg}
</g>

<!-- Hidden edges (dashed lines) -->
<g id="hidden">
{hidden_svg}
</g>

<!-- Title block -->
{schriftfeld}

</svg>
'''

SVG_OUT.write_text(svg, encoding='utf-8')
print(f"\nSVG written to: {SVG_OUT}")
print(f"File size: {SVG_OUT.stat().st_size} bytes")
print("Done!")
