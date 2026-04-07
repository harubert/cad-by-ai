"""
Analysiert die einzelnen Material-Regionen im Profil
(ohne Morphologie, um Kammern sichtbar zu machen).
"""

import cv2
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
OUTPUT = BASE / 'output'


def analyze():
    img = cv2.imread(str(INPUT))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

    filled = binary.copy()
    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    for s in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(0,h//2),(w-1,h//2),(w//2,h-1)]:
        if filled[s[1], s[0]] == 255:
            cv2.floodFill(filled, mask, s, 128)

    # Material = weisse Pixel (255) die nicht vom Exterior-Fill erreicht wurden
    material_raw = np.where(filled == 255, 255, 0).astype(np.uint8)

    # Connected Components auf dem Rohmaterial
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        material_raw, connectivity=4)

    # Skalierung (aus dem Profil-BB des vorherigen Laufs)
    # Profil BB: ca 221x222px, Mitte ca (146, 164)
    scale = 40.0 / 222.0  # mm/px
    cx_px, cy_px = 146, 164

    print(f"Material-Regionen: {n_labels - 1}")  # -1 fuer Hintergrund

    # Sortiere nach Flaeche
    regions = []
    for i in range(1, n_labels):
        area_px = stats[i, cv2.CC_STAT_AREA]
        area_mm2 = area_px * scale * scale
        cx = (centroids[i][0] - cx_px) * scale
        cy = -(centroids[i][1] - cy_px) * scale
        bw = stats[i, cv2.CC_STAT_WIDTH] * scale
        bh = stats[i, cv2.CC_STAT_HEIGHT] * scale
        regions.append({
            'label': i, 'area_mm2': area_mm2,
            'center': (cx, cy), 'size': (bw, bh),
            'area_px': area_px,
        })

    regions.sort(key=lambda r: r['area_mm2'], reverse=True)

    print(f"\nAlle Regionen (> 1mm^2):")
    for r in regions:
        if r['area_mm2'] < 1:
            continue
        cx, cy = r['center']
        bw, bh = r['size']
        print(f"  Label {r['label']:3d}: A={r['area_mm2']:7.1f}mm^2, "
              f"Gr={bw:.1f}x{bh:.1f}mm, Mitte=({cx:6.1f},{cy:6.1f})")

    # Visualisierung: farbkodierte Regionen
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Farbkarte fuer Regionen
    color_img = np.zeros((h, w, 3), dtype=np.uint8)
    color_img[:] = 40  # dunkelgrauer Hintergrund

    # Grosse Regionen = Material (gruen), kleine = evtl. Kammern (rot)
    for r in regions:
        mask_r = (labels == r['label'])
        if r['area_mm2'] > 5:
            color_img[mask_r] = [0, 200, 0]  # gruen = Material
        elif r['area_mm2'] > 0.5:
            color_img[mask_r] = [200, 0, 0]  # rot = kleine Region

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=150)

    axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0].set_title('Original')
    axes[0].axis('off')

    axes[1].imshow(filled, cmap='gray')
    axes[1].set_title('Nach Flood-Fill\n(128=Aussen, 255=Material, 0=Linie)')
    axes[1].axis('off')

    axes[2].imshow(color_img)
    axes[2].set_title(f'Material-Regionen ({len([r for r in regions if r["area_mm2"]>1])} Stueck)\n'
                      f'Gruen=Material, Rot=Klein')
    axes[2].axis('off')

    fig.tight_layout()
    fig.savefig(str(OUTPUT / 'region_analysis.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print(f"\nBild: {OUTPUT / 'region_analysis.png'}")

    # Zusammenfassung
    material_total = sum(r['area_mm2'] for r in regions if r['area_mm2'] > 5)
    print(f"\nMaterial gesamt (Regionen > 5mm^2): {material_total:.1f}mm^2")
    print(f"Soll (Item 40x40 Katalog): ~534mm^2")


if __name__ == '__main__':
    OUTPUT.mkdir(exist_ok=True)
    analyze()
