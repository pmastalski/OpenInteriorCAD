OpenInteriorCAD — Cut List 0.3

Adds production material and edge-band information without changing cabinet geometry.

NEW furniture properties under Production:
- BoardMaterial
- FrontMaterial
- BackMaterial
- EdgeMaterial
- EdgeThickness

Cut List columns now include:
- Material
- Edge
- Edge thickness
- Edge length

Summary includes:
- total board area
- total edge-band length
- totals grouped by material and thickness

CSV export includes all new production fields.

Important:
- no Shape geometry changes
- stable corner cabinet geometry remains untouched
- all production data is metadata only

Recommended next stage:
Cut List 0.4:
- per-edge control (Front / Back / Left / Right)
- user-editable edge assignment panel
- material library/presets
