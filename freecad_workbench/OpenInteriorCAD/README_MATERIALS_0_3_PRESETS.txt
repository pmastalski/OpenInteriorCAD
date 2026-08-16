OpenInteriorCAD — Materials 0.3 / Material Presets

NEW:
Material Presets.

A preset stores one complete material set:
- Carcass material
- Front material
- Back material
- Edge-band material

Functions:
- Load Preset
- Save Current as Preset
- Delete Preset
- Reset Presets

Presets are persistent across FreeCAD sessions and projects.

Typical workflow:
1. Create materials in Material Library.
2. Choose Carcass / Front / Back / Edge.
3. Save Current as Preset, e.g.:
   "White kitchen 18"
   "Oak carcass + matte front"
4. For another cabinet choose the preset and click Load Preset.
5. Click Apply to Cabinet.

Materials 0.2 functionality is retained:
- optional Apply material thickness to geometry
- validation before PanelThickness / FrontThickness / BackThickness changes

No cabinet geometry algorithms were rewritten.
