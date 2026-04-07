"""
Alu-Profil 40x40 Schnittzeichnung via Image-Trace.
Die Profilkontur wird aus dem Datenblatt-Bild extrahiert und
mit Even-Odd-Fuellregel korrekt als Schnitt dargestellt.
"""

import cv2
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.image as mpimg

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
OUTPUT = BASE / 'output'

# Stil
C_BG = '#FFFFFF'
C_LINE = '#000000'
C_DIM = '#222222'
C_CENTER = '#CC0000'
C_HATCH_BG = '#E8E8E8'
C_HATCH_FG = '#444444'
LW_THICK = 0.70
LW_THIN = 0.30


def extract_contour():
    """
    Extrahiert die Profilkontur aus dem Originalbild.
    Rueckgabe: Konturpunkte in mm (Ursprung = Profilmitte).
    """
    img = cv2.imread(str(INPUT))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

    # Flood-Fill: Aussen markieren
    filled = binary.copy()
    ff_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    for s in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(0,h//2),(w-1,h//2),(w//2,h-1)]:
        if filled[s[1], s[0]] == 255:
            cv2.floodFill(filled, ff_mask, s, 128)

    # Material-Maske: alles was nicht Aussen
    profile_mask = np.where(filled != 128, 255, 0).astype(np.uint8)

    # Closing: Strichluecken schliessen, aber Innenstruktur erhalten
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    profile_mask = cv2.morphologyEx(profile_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Konturen
    contours, hierarchy = cv2.findContours(
        profile_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Groesste Kontur = Profil
    idx = max(range(len(contours)), key=lambda i: cv2.contourArea(contours[i]))
    profile_c = contours[idx]

    # Skalierung
    x0, y0, bw, bh = cv2.boundingRect(profile_c)
    scale = 40.0 / max(bw, bh)
    cx = x0 + bw / 2
    cy = y0 + bh / 2

    def to_mm(c):
        pts = c.reshape(-1, 2).astype(float)
        mm = np.zeros_like(pts)
        mm[:, 0] = (pts[:, 0] - cx) * scale
        mm[:, 1] = -(pts[:, 1] - cy) * scale
        return mm

    # Hauptkontur (fein approximiert)
    eps = 0.002 * cv2.arcLength(profile_c, True)
    outer_mm = to_mm(cv2.approxPolyDP(profile_c, eps, True))

    # Innenkonturen (Kinder der Hauptkontur = Bohrung etc.)
    inner_mms = []
    if hierarchy is not None:
        child = hierarchy[0][idx][2]
        while child != -1:
            area_mm2 = cv2.contourArea(contours[child]) * scale * scale
            if area_mm2 > 5:
                eps_c = 0.005 * cv2.arcLength(contours[child], True)
                inner_mms.append(to_mm(cv2.approxPolyDP(contours[child], eps_c, True)))
            child = hierarchy[0][child][0]

    print(f"Aussenkontur: {len(outer_mm)} Punkte")
    print(f"Innenkonturen: {len(inner_mms)}")
    return outer_mm, inner_mms


def build_profile(outer_mm, inner_mms):
    """
    Baut das Profil-Polygon.
    Die Aussenkontur kreuzt sich selbst (geht in T-Nuten rein/raus).
    make_valid() zerlegt das korrekt in Material-Flaechen.
    """
    # Rohes Polygon (moeglicherweise self-intersecting)
    raw = Polygon(outer_mm)
    print(f"  Roh-Polygon valid: {raw.is_valid}, area: {raw.area:.1f}mm^2")

    # make_valid zerlegt self-intersecting Polygone korrekt
    fixed = make_valid(raw)
    print(f"  Fixed type: {fixed.geom_type}, area: {fixed.area:.1f}mm^2")

    # Bohrung abziehen (manuell, da sie im Closing verloren geht)
    bore = Point(0, 0).buffer(6.8 / 2, resolution=64)
    material = fixed.difference(bore)

    # Falls Innenkonturen gefunden, auch abziehen
    for ic in inner_mms:
        if len(ic) >= 3:
            try:
                hole = Polygon(ic)
                if hole.is_valid and hole.area > 5:
                    material = material.difference(hole)
            except:
                pass

    # Eckhaken parametrisch hinzufuegen
    from shapely.geometry import box as sbox
    hw = 20.0
    cut = 4.8
    hook_ro, hook_ri = 4.3, 1.8
    cs = hw - cut

    for sx, sy in [(1,1), (-1,1), (1,-1), (-1,-1)]:
        cx, cy = sx * hw, sy * hw
        outer_c = Point(cx, cy).buffer(hook_ro, resolution=64)
        inner_c = Point(cx, cy).buffer(hook_ri, resolution=64)
        ring = outer_c.difference(inner_c)
        clip = sbox(min(sx*cs, cx), min(sy*cs, cy), max(sx*cs, cx), max(sy*cs, cy))
        hook = ring.intersection(clip)
        if hook.area > 0.5:
            material = material.union(hook)

    print(f"  Material: {material.area:.1f}mm^2")
    return material


def geom_to_patches(geom):
    """Shapely -> matplotlib PathPatch."""
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
             'Alu-Profil 40x40 | Art.Nr. 60800 | M 2:1 | AlMgSi0,5',
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
    hw = 20
    kw = dict(color=C_DIM, lw=LW_THIN)
    tkw = dict(fontsize=7.5, color=C_DIM,
               bbox=dict(facecolor='white', edgecolor='none', pad=0.5, alpha=0.85))

    def dim_h(x1, x2, y, off, txt):
        yo = y + off
        ax.plot([x1,x1],[y+.5*np.sign(off),yo+np.sign(off)], **kw)
        ax.plot([x2,x2],[y+.5*np.sign(off),yo+np.sign(off)], **kw)
        ax.annotate('', xy=(x2,yo), xytext=(x1,yo),
                     arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
        ax.text((x1+x2)/2, yo+.5*np.sign(off), txt,
                ha='center', va='bottom' if off>0 else 'top', **tkw)

    def dim_v(y1, y2, x, off, txt):
        xo = x + off
        ax.plot([x+.5*np.sign(off),xo+np.sign(off)],[y1,y1], **kw)
        ax.plot([x+.5*np.sign(off),xo+np.sign(off)],[y2,y2], **kw)
        ax.annotate('', xy=(xo,y2), xytext=(xo,y1),
                     arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
        ax.text(xo+.5*np.sign(off), (y1+y2)/2, txt,
                ha='left' if off>0 else 'right', va='center', rotation=90, **tkw)

    dim_h(-hw, hw, hw, 7, '40')
    dim_v(-hw, hw, hw, 7, '40')
    dim_h(-4, 4, -hw, -5, '8')
    dim_v(-hw, -hw+12.25, -hw, -7, '12,25')

    r = 3.4
    a = np.radians(45)
    ax.annotate('', xy=(r*np.cos(a),r*np.sin(a)), xytext=(-r*np.cos(a),-r*np.sin(a)),
                arrowprops=dict(arrowstyle='<->', mutation_scale=7, **kw))
    ax.plot([r*np.cos(a),13*np.cos(a)],[r*np.sin(a),13*np.sin(a)], **kw)
    ax.text(14*np.cos(a), 14*np.sin(a), '\u00D86,8', ha='left', va='bottom', **tkw)


if __name__ == '__main__':
    OUTPUT.mkdir(exist_ok=True)

    print("=== Kontur extrahieren ===")
    outer, inners = extract_contour()

    print("\n=== Profil bauen ===")
    material = build_profile(outer, inners)

    print("\n=== Zeichnungen ===")
    render(material, True, True, str(OUTPUT / 'alu_40x40_schnitt.png'))
    render(material, True, True, str(OUTPUT / 'alu_40x40_schnitt.svg'))
    render(material, False, True, str(OUTPUT / 'alu_40x40_kontur.png'))

    # Vergleich
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)
    axes[0].imshow(mpimg.imread(str(INPUT)))
    axes[0].set_title('Original (Datenblatt)', fontsize=12, fontweight='bold')
    axes[0].axis('off')
    axes[1].imshow(mpimg.imread(str(OUTPUT / 'alu_40x40_schnitt.png')))
    axes[1].set_title('Generiert (Image-Trace + make_valid)', fontsize=12, fontweight='bold')
    axes[1].axis('off')
    fig.tight_layout()
    fig.savefig(str(OUTPUT / 'vergleich_40x40.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print("  OK: vergleich_40x40.png")
