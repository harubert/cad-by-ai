"""Vergleichsbild: Original vs. generierte Zeichnung."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)
fig.patch.set_facecolor('white')

# Original
orig = mpimg.imread(os.path.join(base, 'humanImput', 'C100_60800-STLS-0500-2.jpg'))
axes[0].imshow(orig)
axes[0].set_title('Original (Datenblatt)', fontsize=12, fontweight='bold')
axes[0].axis('off')

# Generiert
gen = mpimg.imread(os.path.join(base, 'output', 'alu_40x40_schnitt.png'))
axes[1].imshow(gen)
axes[1].set_title('Generiert (Python/Shapely)', fontsize=12, fontweight='bold')
axes[1].axis('off')

plt.tight_layout()
out = os.path.join(base, 'output', 'vergleich_40x40.png')
fig.savefig(out, bbox_inches='tight', facecolor='white', dpi=150)
print(f"OK: {out}")
plt.close()
