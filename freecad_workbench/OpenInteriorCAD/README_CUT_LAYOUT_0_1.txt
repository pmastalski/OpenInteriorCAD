OpenInteriorCAD — Cut Layout 0.1

NEW COMMAND:
Cut Layout

PURPOSE:
Visualize the cutting layout of board parts generated from the existing
OpenInteriorCAD Board Parts / Cut List data.

SOURCE:
- if one or more cabinets are selected -> selected cabinets only
- if nothing is selected -> all cabinets in the document

GROUPING:
Separate sheets are created automatically for every:
- Material
- Thickness

DEFAULT SHEET:
2800 x 2070 mm

USER SETTINGS:
- sheet width
- sheet height
- saw kerf
- outer margin
- allow / disable 90-degree rotation

DISPLAY:
- sheet outline
- usable margin
- placed parts
- part name
- part dimensions
- R marker for 90-degree rotated pieces
- material
- thickness
- sheet number
- reserved-area utilization
- zoom with mouse wheel
- pan with mouse drag
- Fit button

EXPORT:
Current sheet can be exported as SVG.

ALGORITHM 0.1:
First-fit decreasing shelf packing.

IMPORTANT:
- This is a visualization / planning tool.
- It does NOT modify cabinet geometry.
- It does NOT change Board Parts, Cut List, materials, edge data or costing.
- Rectangular parts are optimized with optional 90-degree rotation.
- L-shaped corner parts are DISPLAYED as L shapes but their full bounding
  rectangle is reserved for packing in version 0.1.
- Therefore Cut Layout 0.1 is conservative for L-shaped parts and does not
  yet place other parts inside their cut-outs.

NEXT POSSIBLE VERSIONS:
- true 2D nesting into L-shaped waste areas
- grain direction / rotation restrictions
- stock-sheet library by material
- offcut/remnant reuse
- cut sequence / guillotine cutting plan
- labels / barcode export
