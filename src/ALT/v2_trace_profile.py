"""
Profilkontur-Extraktion aus Datenblatt-Bild.
Strategie: Flood-Fill zur Segmentierung, dann Konturfindung.
"""

import cv2
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'
OUTPUT = BASE / 'output'


def extract_profile(image_path):
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    print(f"Bild: {w}x{h}px")

    # 1) Schwellwert: Linien = schwarz (< 160), Hintergrund = weiss
    _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

    # 2) Flood-Fill von allen 4 Ecken: markiert den Aussenbereich
    filled = binary.copy()
    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    # Von jeder Ecke und Kantenmitte aus fuellen
    fill_seeds = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1),
                  (w//2, 0), (0, h//2), (w-1, h//2), (w//2, h-1)]
    for seed in fill_seeds:
        if filled[seed[1], seed[0]] == 255:  # nur weisse Pixel
            cv2.floodFill(filled, mask, seed, 128)

    # 3) Jetzt: 128=Aussen, 255=Innen (Material+Hohlraeume), 0=Linien
    # Erstelle Maske: alles was NICHT aussen ist = Profil-Region
    profile_mask = np.where(filled != 128, 255, 0).astype(np.uint8)

    # 4) Morphologie: Linien verdicken um geschlossene Bereiche zu fuellen
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    profile_filled = cv2.morphologyEx(profile_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 5) Konturen auf der gefuellten Maske finden
    contours, hierarchy = cv2.findContours(profile_filled, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if not contours:
        print("Keine Konturen!")
        return

    # Sortiere nach Flaeche
    indexed = [(i, cv2.contourArea(contours[i])) for i in range(len(contours))]
    indexed.sort(key=lambda x: x[1], reverse=True)

    print(f"\nTop-10 Konturen:")
    for rank, (idx, area) in enumerate(indexed[:15]):
        M = cv2.moments(contours[idx])
        cx = M['m10'] / max(M['m00'], 1)
        cy = M['m01'] / max(M['m00'], 1)
        x, y, bw, bh = cv2.boundingRect(contours[idx])
        parent = hierarchy[0][idx][3]
        circ = 4 * np.pi * area / (cv2.arcLength(contours[idx], True) ** 2 + 1e-6)
        print(f"  #{rank}: idx={idx}, A={area:.0f}px^2, "
              f"BB={bw}x{bh}px, Mitte=({cx:.0f},{cy:.0f}), "
              f"Parent={parent}, Circ={circ:.2f}")

    # Die groesste Kontur = Aussenkontur des Profils
    profile_idx = indexed[0][0]
    profile_c = contours[profile_idx]
    x_bb, y_bb, w_bb, h_bb = cv2.boundingRect(profile_c)

    # Skalierung
    scale = 40.0 / max(w_bb, h_bb)  # Profil = 40mm
    cx_px = x_bb + w_bb / 2
    cy_px = y_bb + h_bb / 2

    def to_mm(c):
        pts = c.reshape(-1, 2).astype(float)
        mm = np.zeros_like(pts)
        mm[:, 0] = (pts[:, 0] - cx_px) * scale
        mm[:, 1] = -(pts[:, 1] - cy_px) * scale
        return mm

    print(f"\nProfil: BB=({x_bb},{y_bb}) {w_bb}x{h_bb}px, scale={scale:.4f}mm/px")

    # Kind-Konturen des Profils = Hohlraeume
    # Finde alle Konturen die INNERHALB der Profilkontur liegen
    holes = []
    for rank, (idx, area) in enumerate(indexed[1:], 1):
        if area < 20:  # zu klein
            continue
        area_mm2 = area * scale * scale
        if area_mm2 > 500:  # zu gross (Duplikat der Aussenkontur)
            continue
        # Pruefen ob Schwerpunkt innerhalb der Profilkontur liegt
        M = cv2.moments(contours[idx])
        if M['m00'] == 0:
            continue
        cx_test = int(M['m10'] / M['m00'])
        cy_test = int(M['m01'] / M['m00'])
        dist = cv2.pointPolygonTest(profile_c, (cx_test, cy_test), False)
        if dist >= 0:  # innerhalb oder auf dem Rand
            c_mm = to_mm(contours[idx])
            cx_mm = np.mean(c_mm[:, 0])
            cy_mm = np.mean(c_mm[:, 1])
            bw_mm = (np.max(c_mm[:, 0]) - np.min(c_mm[:, 0]))
            bh_mm = (np.max(c_mm[:, 1]) - np.min(c_mm[:, 1]))
            circ = 4 * np.pi * area / (cv2.arcLength(contours[idx], True) ** 2 + 1e-6)
            holes.append({
                'idx': idx,
                'contour': contours[idx],
                'mm': c_mm,
                'area_mm2': area_mm2,
                'center_mm': (cx_mm, cy_mm),
                'size_mm': (bw_mm, bh_mm),
                'circularity': circ,
            })

    print(f"\nHohlraeume im Profil: {len(holes)}")
    for h_data in holes:
        cx_mm, cy_mm = h_data['center_mm']
        bw, bh = h_data['size_mm']
        print(f"  A={h_data['area_mm2']:.1f}mm^2, "
              f"Gr={bw:.1f}x{bh:.1f}mm, "
              f"Mitte=({cx_mm:.1f},{cy_mm:.1f})mm, "
              f"Circ={h_data['circularity']:.2f}")

    # Approximiere Konturen fuer saubere Ausgabe
    eps = 0.003 * cv2.arcLength(profile_c, True)
    outer_approx = to_mm(cv2.approxPolyDP(profile_c, eps, True))

    hole_approx = []
    for h_data in holes:
        eps_h = 0.005 * cv2.arcLength(h_data['contour'], True)
        approx = cv2.approxPolyDP(h_data['contour'], eps_h, True)
        hole_approx.append(to_mm(approx))

    # === Visualisierung ===
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(20, 7), dpi=150)

    # 1) Binaerbild nach Flood-Fill
    axes[0].imshow(filled, cmap='gray')
    axes[0].set_title('Nach Flood-Fill\n(128=Aussen, 255=Innen, 0=Linien)')
    axes[0].axis('off')

    # 2) Erkannte Konturen auf Original
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ax2 = axes[1]
    ax2.imshow(img_rgb)
    pts = profile_c.reshape(-1, 2)
    ax2.plot(pts[:, 0], pts[:, 1], 'b-', lw=2, alpha=0.7)
    colors = ['red', 'green', 'orange', 'purple', 'cyan']
    for i, h_data in enumerate(holes):
        pts = h_data['contour'].reshape(-1, 2)
        ax2.plot(pts[:, 0], pts[:, 1], '-', color=colors[i % len(colors)], lw=1.5)
    ax2.set_title('Erkannte Konturen')
    ax2.axis('off')

    # 3) Profil in mm (Material = grau, Hohlraeume = weiss)
    ax3 = axes[2]
    pts = outer_approx
    ax3.fill(pts[:, 0], pts[:, 1], facecolor='#D0D0D0', edgecolor='black', lw=1.5, zorder=2)
    for ha in hole_approx:
        ax3.fill(ha[:, 0], ha[:, 1], facecolor='white', edgecolor='red', lw=1.0, zorder=3)
    ax3.set_aspect('equal')
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Profil in mm\n(Material=grau)')
    ax3.set_xlim(-25, 25)
    ax3.set_ylim(-25, 25)

    fig.tight_layout()
    out_path = OUTPUT / 'trace_analysis.png'
    fig.savefig(str(out_path), bbox_inches='tight', dpi=150)
    plt.close()
    print(f"\nBild: {out_path}")

    # SVG
    write_svg(outer_approx, hole_approx, OUTPUT / 'traced_profile.svg')

    # Koordinaten-Dump fuer weitere Analyse
    print("\n=== AUSSENKONTUR (mm, approx) ===")
    for p in outer_approx:
        print(f"  ({p[0]:7.2f}, {p[1]:7.2f})")

    return outer_approx, hole_approx


def write_svg(outer, holes, path):
    margin = 5
    s = 40 + 2 * margin
    lo = -20 - margin

    def d(pts):
        r = f'M{pts[0,0]:.2f},{pts[0,1]:.2f}'
        for p in pts[1:]:
            r += f'L{p[0]:.2f},{p[1]:.2f}'
        return r + 'Z'

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{lo} {lo} {s} {s}" width="600" height="600">',
        '<g transform="scale(1,-1)">',
        f'<path d="{d(outer)}" fill="#E0E0E0" stroke="#000" stroke-width="0.3"/>',
    ]
    for h in holes:
        lines.append(f'<path d="{d(h)}" fill="#fff" stroke="red" stroke-width="0.2"/>')
    lines.append('</g></svg>')
    Path(path).write_text('\n'.join(lines))
    print(f"SVG: {path}")


if __name__ == '__main__':
    OUTPUT.mkdir(exist_ok=True)
    extract_profile(INPUT)
