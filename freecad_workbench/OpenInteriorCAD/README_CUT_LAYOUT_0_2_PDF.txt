OpenInteriorCAD — Cut Layout 0.2 / PDF Export

NEW:
Export PDF button in Board Cut Layout.

PDF BEHAVIOR:
- exports ALL calculated sheets
- one stock sheet per PDF page
- one multi-page PDF file
- vector rendering through Qt / QPrinter
- A3 landscape page
- includes the same visual content as Cut Layout:
  sheet outline
  usable margin
  placed parts
  part labels and dimensions
  material / thickness / sheet number header

EXISTING EXPORT:
- Export SVG still exports the currently displayed sheet only

UNCHANGED:
- Cut Layout packing algorithm
- Board Parts
- Cut List
- cabinet geometry
- materials
- edge assignments
- hardware
- costing
- front opening

DEFAULT SHEET:
2800 x 2070 mm

The PDF is intended as a readable production/print visualization.
The stock-sheet dimensions shown in the drawing remain the real millimetre
dimensions from the layout; the whole drawing is scaled to fit an A3
landscape PDF page.
