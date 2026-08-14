OpenInteriorCAD — Cut List 0.1

Adds a production Cut List panel to the OpenInteriorCAD workbench.

NEW:
- OICCutListPanel.py

UPDATED:
- OICFurniture.py
- OICBoardParts.py
- OICFurnitureCommands.py
- InitGui.py

Usage:
1. Select one or more cabinets and click "Cut List".
2. The panel shows:
   Cabinet / Part / Role / Qty / Length / Width / Thickness / Material
3. If no cabinet is selected, Cut List shows all cabinets in the active document.
4. Refresh recalculates the table from current cabinet parameters.

Important:
- no cabinet Shape geometry is modified by Cut List
- accepted corner cabinet geometry remains unchanged
- this is a read-only production view

Next planned step:
Cut List 0.2 — CSV export + totals/aggregation.
