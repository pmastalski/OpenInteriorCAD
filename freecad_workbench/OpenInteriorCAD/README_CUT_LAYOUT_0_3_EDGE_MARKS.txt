OpenInteriorCAD — Cut Layout 0.3 / Edge Banding Marks

NEW:
The board cut layout now displays which edges must be edge-banded.

VISUAL CONVENTION:
Orange thick line = edge to be banded / ABS edge.

SOURCE:
The markings come directly from the existing Board Parts edge metadata:
- edge_front
- edge_back
- edge_left
- edge_right
- EdgeMaterial
- EdgeThickness

ROTATED PARTS:
When a part is rotated 90 degrees by the nesting algorithm, its edge-band
markings rotate with it.

TOOLTIPS:
Hovering a part or orange edge shows:
- cabinet
- part name
- dimensions
- material
- edge material / thickness
- logical edge names

LABELS:
Parts with edge banding receive an additional "EDGE" marker.

SHOW / HIDE:
New checkbox:
    Show edge banding

EXPORT:
- PDF automatically contains the same orange edge-band marks because it is
  rendered from the Cut Layout scene.
- SVG now also contains the orange edge-band marks and legend.

L-SHAPED CORNER PARTS:
Current Board Parts data stores these as "Custom (L)" instead of exact
individual edge segments. Cut Layout therefore displays:
    EDGE: Custom (L)
rather than inventing potentially incorrect segment markings.

UNCHANGED:
- packing algorithm
- cabinet geometry
- Board Parts calculations
- Cut List
- Edge Assignment
- materials
- hardware
- costing
- Front Opening
