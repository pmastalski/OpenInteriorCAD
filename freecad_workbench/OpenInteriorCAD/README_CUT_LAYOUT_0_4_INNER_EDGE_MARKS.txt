OpenInteriorCAD — Cut Layout 0.4 / Inner Edge Marks

CHANGE:
Edge banding is no longer drawn directly on the board outline.

NEW VISUAL CONVENTION:
- a short orange line is drawn INSIDE the board
- the line is parallel to the edge that must be banded
- the line is centered along that edge
- the line is intentionally shorter than the edge
- the mark follows the part when the nesting algorithm rotates it 90 degrees

WHY:
This is clearer in production drawings because the board contour remains
unobstructed while the edge-banding instruction is still obvious.

PDF:
The PDF export uses the same scene, so the new inner edge marks are included.

SVG:
The same inner parallel marks are exported to SVG.

UNCHANGED:
- edge assignments
- materials
- Cut List
- packing algorithm
- cabinet geometry
- hardware
- costing
- front opening
