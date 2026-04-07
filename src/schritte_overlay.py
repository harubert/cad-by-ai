"""
Fuegt allen Schritt-SVGs das Originalbild als Hintergrund hinzu.
Erzeugt _overlay Versionen.
"""

import base64
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SCHRITTE = BASE / 'output' / 'schritte'
IMG_PATH = BASE / 'humanImput' / 'C100_60800-STLS-0500-2.jpg'

# Bild laden und als base64
b64 = base64.b64encode(IMG_PATH.read_bytes()).decode('ascii')

# Bild-Positionierung (aus frueherer Analyse)
scale = 40.0 / 223.0  # mm/px
img_x = -20 - 35 * scale
img_y = -20 - 52 * scale  # SVG y ist invertiert, aber Bild ist schon richtig
img_w = 300 * scale
img_h = 300 * scale

bg_element = (
    f'<image href="data:image/jpeg;base64,{b64}" '
    f'x="{img_x:.2f}" y="{img_y:.2f}" '
    f'width="{img_w:.2f}" height="{img_h:.2f}" '
    f'opacity="0.2"/>'
)

count = 0
for svg_file in sorted(SCHRITTE.glob('*.svg')):
    if '_overlay' in svg_file.name:
        continue

    svg_text = svg_file.read_text(encoding='utf-8')

    # Fuege Hintergrundbild direkt nach dem oeffnenden <svg...> Tag ein
    # Finde das Ende des <svg ...> Tags
    match = re.search(r'(<svg[^>]*>)', svg_text)
    if not match:
        continue

    insert_pos = match.end()
    overlay_svg = svg_text[:insert_pos] + '\n' + bg_element + '\n' + svg_text[insert_pos:]

    overlay_name = svg_file.stem + '_overlay.svg'
    (SCHRITTE / overlay_name).write_text(overlay_svg, encoding='utf-8')
    count += 1

print(f"OK: {count} Overlay-SVGs erzeugt")
