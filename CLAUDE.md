# CAD by AI — Projektdokumentation

## Überblick

Dieses Projekt entstand im Dialog zwischen einem PH-Dozenten (Pädagogische Hochschule, Österreich) und Claude Code (Anthropic). Ziel: Demonstration, wie KI Geometrie-Konstruktionen durchführen kann — für einen Workshop "KI im Geometrieunterricht" in Graz am 9. April 2026.

**Repository:** https://github.com/harubert/cad-by-ai
**GitHub Pages:** https://harubert.github.io/cad-by-ai/
**Landing Page:** output/index.html

## Projektstruktur

```
CAD_by_AI/
├── index.html                    # Redirect zu output/index.html
├── CLAUDE.md                     # Diese Datei (Projektdoku)
├── humanImput/                   # Vorlagen vom Benutzer
│   ├── C100_60800-STLS-0500-2.jpg    # Datenblatt Alu-Profil 40x40
│   ├── C100_60817-STLS-0500-2.jpg    # Datenblatt Alu-Profil 40x80
│   └── 81c98a7de9716dde44aba845415e83e6.webp  # Detailzeichnung mit Maßen
├── src/                          # Python-Quellcode
│   ├── aufgabe01.py              # Hauptprofil 40x40 (Shapely + SVG)
│   ├── aufgabe01_formal.py       # Technische Zeichnung A4 mit Bemaßung
│   ├── aufgabe01_stl.py          # STL-Export (parst SVG → trimesh)
│   ├── aufgabe02_tpu.py          # TPU-Fußkappe + Verbinder
│   ├── aufgabe03_risse.py        # Schrägriss + Dreitafel (manuell)
│   ├── aufgabe03_cadquery.py     # Schrägriss CadQuery Versuch 1
│   ├── aufgabe03_cadquery_v2.py  # Schrägriss CadQuery Versuch 2
│   ├── aufgabe04_pyramide.py     # Pyramide 50x50 h=70
│   ├── aufgabe05_verbinder.py    # TPU-Verbindungsstück
│   ├── aufgabe06_*.py            # Tool-Vergleiche
│   ├── gz_aufgaben.py            # 10 GZ-Aufgaben (Shapely)
│   ├── gz_cadquery.py            # 10 GZ-Aufgaben (CadQuery HLR)
│   ├── dg_aufgaben.py            # 10 DG-Aufgaben
│   ├── schritte*.py              # Schritt-für-Schritt SVG-Generatoren
│   └── ALT/                      # Verworfene Versionen (v1-v5)
└── output/                       # Alle generierten Dateien
    ├── index.html                # Landing Page (Haupteinstieg)
    ├── konstruktionsdoku.html    # Konstruktionsprotokoll (35+ Schritte)
    ├── schraegriss_protokoll.html # Schrägriss-Dokumentation
    ├── praesentation_notizen.html # Notizen fürs Referat
    ├── aufgabe01_path.svg        # ⭐ Profil-Kontur (die geometrische Basis)
    ├── aufgabe01_Final-Schnitt.svg # Profil mit Schraffur
    ├── aufgabe01_path_formal.svg # A4 technische Zeichnung
    ├── aufgabe01_overlay.svg     # Profil auf Originalbild
    ├── aufgabe01_profil_100mm.stl # 3D-Druck Profil
    ├── aufgabe02_abschlussTPU_5mm.stl # 3D-Druck TPU-Fuß
    ├── aufgabe05_verbinder_40mm.stl   # 3D-Druck TPU-Verbinder
    ├── aufgabe03_*.svg           # Schrägriss-Varianten
    ├── aufgabe04_*.svg           # Pyramide
    ├── gz/                       # 10 GZ-Aufgaben (Shapely SVGs)
    ├── gz_cadquery/              # 10 GZ-Aufgaben (CadQuery SVGs)
    ├── dg/                       # 10 DG-Aufgaben
    ├── aufgabe06/                # Tool-Vergleich
    ├── schritte/                 # Schritt-für-Schritt SVGs + Overlays
    └── *.png                     # Screenshots (3D-Druck, Fails etc.)
```

## Technische Basis

### Python-Umgebung
- **Interpreter:** `D:/Programme/python/scripts/python.bat` (Python 3.10.9)
- **ACHTUNG:** `python` im PATH ist Python 3.9.7 (Inkscape), die installierten Pakete liegen bei 3.10.9

### Installierte Pakete
- **shapely** — 2D-Geometrie (Boolean-Ops, Buffer-Verrundung)
- **numpy** 1.26.4 — Numerik
- **matplotlib** — PNG-Export (wird kaum noch genutzt)
- **opencv-python** — Bildanalyse (Flood-Fill Konturextraktion)
- **trimesh + mapbox-earcut** — STL-Extrusion aus Shapely-Polygonen
- **cadquery** 2.7.0 — 3D-CAD mit OpenCASCADE-Kernel, HLR
- **build123d** — Modernere CadQuery-Alternative
- **solidpython2** — OpenSCAD Code-Generator

## Hauptprojekt: Alu-Profil 40×40

### Geometrie (aufgabe01.py)

Das Profil wird in drei Phasen aufgebaut:

**Phase 1: Shapely-Geometrie (gerade Linien)**
1. Quadrat 40×40 mit R4.5 Ecken (`buffer(-4.5).buffer(4.5)`)
2. Einfacher Schlitz 8mm breit, Tiefe bis cd_y (`box`)
3. R2 Verrundung an Eintrittskanten (`buffer(-2).buffer(2)`)
4. Hinterschnitt als Polygon mit Punkten P, Q, R, S, T, U + Bogen G⌢F
5. Bohrung Ø6.8 + 4 Eckpockets 6.5mm

**Phase 2: SVG-Arc-Replacement (coords_to_svg_path)**
Beim Export erkennt die Funktion bestimmte Punktpaare und ersetzt `L` durch `A`:
- D↔A: Großer Kreisbogen (Mittelpunkt M, Radius r_AD ≈ 7.3mm)
- P↔Q: R1-Verrundung bei C
- R↔S: R0.5-Verrundung bei E  
- T↔U: R0.5-Verrundung bei F (Gerade→Bogen-Übergang)
- G⌢F: Viertelkreis R2.5 (als Shapely-Punktliste, nicht Arc-Replacement)

**Phase 3: SVG-Ausgabe**
- Schraffur via SVG `<pattern>` (45°, Abstand 0.75mm)
- Hintergrundbild (base64-encoded JPEG) für Overlay-Variante
- Verschiedene Ausgaben: mit/ohne Schraffur, mit/ohne Punkte, mit/ohne Hintergrund

### Wichtige Parameter
```python
SLOT_W = 8; SLOT_DEPTH = 12.5; CD_DEPTH = 4.5; E_EXT = 3
sw = 4; sb = 7.5; cd_y = 15.5; e_x = 7
A = (4, 7.5); B = (4, 20); C = (4, 15.5)
E = (7, 15.5); F = (7, 18); G = (9.5, 15.5)
D_x = 9.5; D_y = 7.5 + sqrt(64 - 5.5²) ≈ 13.31
P = (4, 16.5); Q = (5, 15.5)  # R1 bei C
R = (7, 16); S = (6.5, 15.5)  # R0.5 bei E
T = (7, 17.5); U auf dem G⌢F-Bogen  # R0.5 bei F
```

### Kreisbogen A⌢D (Dreieckskonstruktion)
- Basis m = Strecke AD, |AD| = 8mm
- Mittelpunkt S der Basis
- M = S + h·n (h=6, n = Normale auf AD nach links)
- Radius r = |MA| = |MD|
- Im SVG: `A r,r 0 0,sweep x,y`

### STL-Export (aufgabe01_stl.py)
- Parst aufgabe01_path.svg direkt
- SVG Arc-Befehle → Punktlisten (sweep invertiert wegen Y-Achse: `1 - sweep`)
- Sub-Pfad 0 = Außenkontur, 1 = Bohrung, 2-5 = Pockets
- Extrusion via `trimesh.creation.extrude_polygon`
- MultiPolygon: Teile einzeln extrudieren, dann concatenate

### TPU-Teile (aufgabe02_tpu.py, aufgabe05_verbinder.py)
- Laden das Profil aus aufgabe01_path.svg (gleicher Parser)
- Fußkappe: Außen 46×46 (3mm Rand), Basis 2mm + Verzahnung 3mm
- Verbinder: Außen 46×46, 40mm hoch, Profil-Durchbruch ohne Bohrung/Pockets

## GZ/DG Aufgaben

### GZ (Geometrisches Zeichnen, Sek I)
10 Aufgaben in `gz_aufgaben.py`:
1. Dreitafelprojektion Quader 80×50×30
2. Schrägriss Quader (Kavalier 45°)
3. Normalriss Pyramide 60×60 h=80
4. Abwicklung Würfel 40mm
5. Abwicklung Zylinder d=40 h=60
6. Parallelprojektion Prisma
7. Durchdringung Quader-Quader
8. Ebenenschnitt Würfel
9. Kreis im Schrägriss (Ellipse)
10. Zusammengesetzter Körper (Quader + Pyramide)

CadQuery-Versionen in `gz_cadquery.py` mit automatischem HLR.

### DG (Darstellende Geometrie, Oberstufe)
10 Aufgaben in `dg_aufgaben.py`:
1. Zweitafelprojektion Gerade
2. Ebene durch 3 Punkte (Spurgeraden)
3. Ellipse als Zylinderschnitt
4. Parabel als Kegelschnitt
5. Schattenkonstruktion Quader
6. Durchdringung Zylinder-Zylinder
7. Isometrie L-Profil
8. Zentralprojektion Quader
9. Torus im Aufriss
10. Schraublinie

## Bekannte Probleme und Workarounds

### SVG-Arc sweep-flag
- Bei 8-facher Spiegelung (4 Nuten × 2 Seiten) gibt es 32 Kombinationen
- Lösung: `arc_pairs` Liste mit (from_pt, to_pt, radius, sweep) für jede Kombination
- Bei STL-Export: sweep invertieren wegen Y-Achsen-Inversion

### Shapely kann keine Kreisbögen
- Workaround 1: Polygon-Approximation (Punktliste, n=12-32 Punkte)
- Workaround 2: SVG-Arc-Replacement beim Export (L→A ersetzen)
- Problem: Shapely-Geometrie hat gerade Linien, SVG zeigt Bögen

### CadQuery HLR SVG-Export
- CadQuery's eingebauter SVG-Exporter schneidet ab / zentriert nicht
- Eigener SVG-Export: HLR-Edges extrahieren, Start/Endpunkt, als `<path>` schreiben
- Problem: Jeder Polygon-Punkt wird eine Edge → zu viele Kanten bei komplexen Profilen
- Lösung: Profil vereinfachen (weniger Punkte) oder nur Start/Endpunkt pro Edge

### Selektive Verrundung
- `buffer(-r).buffer(r)` rundet ALLE konvexen Ecken
- Lösung: Zweistufig — erst Schlitz + R2, dann Hinterschnitt (C bleibt scharf)

## Erkenntnisse für den Unterricht

1. **KI ersetzt nicht geometrisches Denken — sie verstärkt es**
2. **Punkt-für-Punkt-Konstruktion** ist der robusteste Kommunikationsweg
3. **Werkzeugwahl entscheidend**: Shapely für 2D OK, CadQuery für 3D/HLR nötig
4. **47% Erfolgsrate** beim ersten Versuch, 17 Rückschritte in 35+ Schritten
5. **Sichtbarkeitsanalyse** (Hidden Line Removal) ist KI-Schwäche bei manuellem Ansatz
6. **Präzise Fachsprache** ist Kernkompetenz der Zukunft (nicht weniger, sondern mehr)
7. **Iteratives Verfeinern** (h: 15→10→6) ist typisches CAD-Verhalten
8. **Snapshots bei jedem Schritt speichern** — sonst sind Zwischenstände verloren

## User-Kontext

- PH-Dozent in Österreich, Experte für Darstellende Geometrie / Geometrisches Zeichnen
- Spielt E-Gitarre (Fender Stratocaster), Rock, 20+ Gitarren, tüftelt gern daran
- Bambu Lab X1 Carbon 3D-Drucker
- Bevorzugt SVG über PNG (Vektorgrafik für technische Zeichnungen)
- Will immer Overlays (Vorlage im Hintergrund) zum Vergleich
- Alle Bilder sollen klickbar sein (Lightbox → Vollbild, weißer Hintergrund)
- Maßeinheiten mit Leerzeichen: "40 x 40" nicht "40x40"
- Punkte = Großbuchstaben, Kanten = Kleinbuchstaben (Norm)
