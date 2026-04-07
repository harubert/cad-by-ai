"""
Alu-Strangpressprofil 40x40mm - Technische Schnittzeichnung
Art.Nr. 60800 (Item-kompatibel)

Konstruktionsprinzip: MATERIALAUFBAU
Das Profil besteht aus diesen Materialteilen:
  1. Aussenrahmen (4 Wandsegmente mit Nutoeiffnungen)
  2. T-Nut-Stege (Hinterschnitt-Leisten an der Wand-Innenseite)
  3. Kreuzsteg (4 Arme von Nabe zur Wand, DURCH die T-Nut)
  4. Nabe (zylindrisch um Zentralbohrung)
  5. Eckhaken (C-foermige Viertelringe)
Der Innenraum ist EIN zusammenhaengender Hohlraum.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.image as mpimg
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity

BASE = Path(__file__).resolve().parent.parent
OUTPUT = BASE / 'output'

# ============================================================
# Geometrie-Parameter (mm) – aus Bild-Analyse + Katalogdaten
# ============================================================
W = H = 40.0
HW = W / 2              # 20

# Rahmen
WALL_T = 1.8             # Wandstaerke (aus Detailzeichnung)

# T-Nut
SLOT_W = 8.2             # Nutoeffnung (8.2 aus Detailbild)
SLOT_HW = SLOT_W / 2     # 4.1
HEAD_EXT = (14 - SLOT_W) / 2  # Kopf ragt 2.9mm ueber Nut hinaus (total 14mm)
HEAD_HW = 14.0 / 2       # 7.0 (halbe Kopfbreite = 14/2, aus Detailbild)
HEAD_DEPTH = 10.2 - WALL_T  # T-Kopf ragt 8.4mm ab Wand-Innenseite (total 10.2 ab Flaeche)
LIP_T = 1.3               # Lippendicke (Materialstaerke der Hinterschnitt-Leiste)
IW = HW - WALL_T         # Wand-Innenseite = 18.2

# Kreuzsteg
WEB_W = 1.5              # Stegbreite (aus Detailbild – deutlich duenner!)
WEB_HW = WEB_W / 2       # 0.75

# Nabe
HUB_R = 5.5              # Nabenradius (Bore r=3.4, Wandstaerke ~2.1)
BORE_D = 6.8

# Eckhaken
CORNER_CUT = 4.5          # Eckaussparung ab Kante (aus Detailbild)
HOOK_RO = 4.5             # Haken Aussenradius (4-R4.5 aus Detailbild)
HOOK_RI = 2.0             # Haken Innenradius (geschaetzt, Kanalbreite ~2.5mm)

# Verrundung
FILLET = 0.3

# ============================================================
# Zeichnungsstil
# ============================================================
C_BG = '#FFFFFF'
C_LINE = '#000000'
C_DIM = '#222222'
C_CENTER = '#CC0000'
C_HATCH_BG = '#E8E8E8'
C_HATCH_FG = '#444444'
LW_THICK = 0.70
LW_THIN = 0.30


# ============================================================
# Geometrie-Aufbau
# ============================================================

def mirror4(geom):
    return unary_union([
        geom,
        affinity.scale(geom, xfact=-1, origin=(0,0)),
        affinity.scale(geom, yfact=-1, origin=(0,0)),
        affinity.scale(geom, xfact=-1, yfact=-1, origin=(0,0)),
    ])


def create_profile():
    """Baut das 40x40 Profil aus Material-Komponenten auf."""

    # 1) RAHMEN: 40x40 Quadratrahmen, Wandstaerke WALL_T
    frame = box(-HW, -HW, HW, HW).difference(box(-IW, -IW, IW, IW))
    # Nutoeffnungen ausschneiden
    slot_top = box(-SLOT_HW, IW, SLOT_HW, HW + 0.1)
    frame = frame.difference(mirror4(slot_top))

    # 2) T-NUT-STEGE: L-foermige Hinterschnitt-Leisten
    #    Lippe (waagrecht, LIP_T dick) + Stiel (senkrecht an Wand)
    y_lip = IW - HEAD_DEPTH  # Unterkante der Lippe
    # Rechte Leiste: Lippe + Stiel
    lip_r = box(SLOT_HW, y_lip, HEAD_HW, y_lip + LIP_T)
    stem_r = box(HEAD_HW - LIP_T, y_lip, HEAD_HW, IW)
    ridge_top_r = lip_r.union(stem_r)
    # Linke Leiste: gespiegelt
    lip_l = box(-HEAD_HW, y_lip, -SLOT_HW, y_lip + LIP_T)
    stem_l = box(-HEAD_HW, y_lip, -HEAD_HW + LIP_T, IW)
    ridge_top_l = lip_l.union(stem_l)
    ridges_top = ridge_top_r.union(ridge_top_l)
    all_ridges = unary_union([
        ridges_top,
        affinity.rotate(ridges_top, 90, origin=(0,0)),
        affinity.rotate(ridges_top, 180, origin=(0,0)),
        affinity.rotate(ridges_top, 270, origin=(0,0)),
    ])

    # 3) KREUZSTEG: 4 Arme von Nabe zur Wand (DURCH die T-Nut)
    arm_top = box(-WEB_HW, 0, WEB_HW, IW)
    all_arms = unary_union([
        arm_top,
        affinity.rotate(arm_top, 90, origin=(0,0)),
        affinity.rotate(arm_top, 180, origin=(0,0)),
        affinity.rotate(arm_top, 270, origin=(0,0)),
    ])

    # 4) NABE: zylindrisch um Bohrung
    hub = Point(0, 0).buffer(HUB_R, resolution=64)

    # 5) ECKHAKEN: C-foermige Viertelringe
    cs = HW - CORNER_CUT  # ~15.2
    def make_hook(sx, sy):
        cx, cy = sx * HW, sy * HW
        ring = Point(cx, cy).buffer(HOOK_RO, resolution=64).difference(
               Point(cx, cy).buffer(HOOK_RI, resolution=64))
        clip = box(min(sx*cs, cx), min(sy*cs, cy),
                   max(sx*cs, cx), max(sy*cs, cy))
        return ring.intersection(clip)

    all_hooks = unary_union([make_hook(1,1), make_hook(-1,1),
                             make_hook(1,-1), make_hook(-1,-1)])

    # 6) ECKAUSSPARUNGEN aus dem Rahmen schneiden
    corner_cut_tr = box(cs, cs, HW + 0.1, HW + 0.1)
    all_cuts = mirror4(corner_cut_tr)

    # === ZUSAMMENBAU ===
    material = unary_union([frame, all_ridges, all_arms, hub])
    material = material.difference(all_cuts)

    # Verrundung (vor Haken-Addition)
    if FILLET > 0:
        material = material.buffer(-FILLET, join_style=1).buffer(FILLET, join_style=1)
        material = material.buffer(FILLET, join_style=1).buffer(-FILLET, join_style=1)

    # Haken hinzufuegen (nach Verrundung)
    material = material.union(all_hooks)

    # Bohrung abziehen
    bore = Point(0, 0).buffer(BORE_D / 2, resolution=64)
    material = material.difference(bore)

    print(f"Material-Flaeche: {material.area:.1f}mm^2 (Katalog: ~534mm^2)")
    return material


# ============================================================
# Rendering
# ============================================================

def geom_to_patches(geom):
    geoms = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    patches = []
    for g in geoms:
        v, c = [], []
        for ring in [g.exterior] + list(g.interiors):
            coords = list(ring.coords)
            v.extend(coords)
            c.extend([mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(coords) - 2)
                      + [mpath.Path.CLOSEPOLY])
        patches.append(mpatches.PathPatch(mpath.Path(v, c)))
    return patches


def render(material, with_dims=True, with_hatch=True, path=None):
    plt.rcParams['hatch.color'] = C_HATCH_FG
    plt.rcParams['hatch.linewidth'] = 0.5

    fig, ax = plt.subplots(figsize=(8, 8), dpi=200)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    for p in geom_to_patches(material):
        p.set_facecolor(C_HATCH_BG if with_hatch else 'none')
        p.set_edgecolor(C_LINE)
        p.set_linewidth(LW_THICK)
        if with_hatch:
            p.set_hatch('////')
        p.set_zorder(2)
        ax.add_patch(p)

    # Mittellinien
    for xs, ys in [([-24,24],[0,0]), ([0,0],[-24,24])]:
        ax.plot(xs, ys, color=C_CENTER, lw=0.25, ls='-.', zorder=1)

    if with_dims:
        _dims(ax)

    fig.text(0.95, 0.02,
             'Alu-Profil 40x40 | Art.Nr. 60800 | M 2:1 | AlMgSi0,5 | OENORM',
             ha='right', va='bottom', fontsize=6, color='#777')

    ax.set_aspect('equal')
    ax.set_xlim(-36, 36)
    ax.set_ylim(-36, 36)
    ax.axis('off')
    plt.tight_layout(pad=1)

    if path:
        fig.savefig(path, bbox_inches='tight', facecolor=C_BG, dpi=200)
        print(f"  OK: {path}")
    plt.close()


def _dims(ax):
    kw = dict(color=C_DIM, lw=LW_THIN)
    tkw = dict(fontsize=7.5, color=C_DIM,
               bbox=dict(facecolor='white', edgecolor='none', pad=0.5, alpha=0.85))

    def dim_h(x1, x2, y, off, txt):
        yo = y + off
        s = np.sign(off)
        ax.plot([x1,x1],[y+.5*s,yo+s], **kw)
        ax.plot([x2,x2],[y+.5*s,yo+s], **kw)
        ax.annotate('', xy=(x2,yo), xytext=(x1,yo),
                     arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
        ax.text((x1+x2)/2, yo+.5*s, txt,
                ha='center', va='bottom' if off>0 else 'top', **tkw)

    def dim_v(y1, y2, x, off, txt):
        xo = x + off
        s = np.sign(off)
        ax.plot([x+.5*s,xo+s],[y1,y1], **kw)
        ax.plot([x+.5*s,xo+s],[y2,y2], **kw)
        ax.annotate('', xy=(xo,y2), xytext=(xo,y1),
                     arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
        ax.text(xo+.5*s, (y1+y2)/2, txt,
                ha='left' if off>0 else 'right', va='center', rotation=90, **tkw)

    dim_h(-HW, HW, HW, 7, '40')
    dim_v(-HW, HW, HW, 7, '40')
    dim_h(-SLOT_HW, SLOT_HW, -HW, -5, '8')
    dim_v(-HW, -HW+12.25, -HW, -7, '12,25')

    r = BORE_D / 2
    a = np.radians(45)
    ax.annotate('', xy=(r*np.cos(a),r*np.sin(a)),
                xytext=(-r*np.cos(a),-r*np.sin(a)),
                arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
    ax.plot([r*np.cos(a),13*np.cos(a)],[r*np.sin(a),13*np.sin(a)], **kw)
    ax.text(14*np.cos(a), 14*np.sin(a), '\u00D86,8', ha='left', va='bottom', **tkw)


# ============================================================
if __name__ == '__main__':
    OUTPUT.mkdir(exist_ok=True)

    print("=== Profil aufbauen ===")
    material = create_profile()

    print("\n=== Zeichnungen ===")
    render(material, True, True, str(OUTPUT / 'alu_40x40_schnitt.png'))
    render(material, True, True, str(OUTPUT / 'alu_40x40_schnitt.svg'))
    render(material, False, True, str(OUTPUT / 'alu_40x40_kontur.png'))

    # Vergleich
    orig = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)
    axes[0].imshow(mpimg.imread(str(orig)))
    axes[0].set_title('Original (Datenblatt)', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    axes[1].imshow(mpimg.imread(str(OUTPUT / 'alu_40x40_schnitt.png')))
    axes[1].set_title('Generiert (Materialaufbau)', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    fig.tight_layout()
    fig.savefig(str(OUTPUT / 'vergleich_40x40.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print("  OK: vergleich_40x40.png")
