OpenInteriorCAD – Tall Zones 0.3: Auto Height / Always Snap

Changes from 0.2:

1. Tall Cabinet -> Auto Height:
- Fills the LAST zone Height spinbox with the actual remaining clear height.
- Formula: Cabinet Height - Plinth Height - 2 x Panel Thickness - (zone count - 1) x Panel Thickness - sum of preceding zone clear heights.
- Checks that at least 40 mm remains; otherwise shows an explanation.
- No longer just enters 0 mm, which previously meant an automatic sentinel and appeared to do nothing.
- The computed height is editable and saved as an explicit value.

2. Add Cabinet -> Pick Position:
- Always checks the clicked cabinet for side snapping, including Placement Height (Z) = 0 mm.
- Fallback to the cabinet selected before pressing Pick Position.
- Without a reference cabinet, free position at the entered Z.
- Left or right side is chosen from the click position; cabinet rotation is inherited from the reference.

Installation: replace OICFurnitureEditPanel.py, OICFurnitureCommands.py and OICFurniturePanel.py in FreeCAD Mod/OpenInteriorCAD; restart FreeCAD.

Full FreeCAD 1.1 GUI runtime test remains necessary.
