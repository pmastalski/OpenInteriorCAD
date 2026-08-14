OpenInteriorCAD — Cut List 0.2

Based on the working Cut List 0.1.

NEW:
- "Aggregate identical parts" option
- identical parts are combined by:
  role + length + width + thickness + material
- quantities are summed
- board area is calculated in m²
- summary shows:
  cabinets / parts / total board area
- "Export CSV" button
- CSV uses UTF-8 with BOM and semicolon delimiter for good Excel compatibility

IMPORTANT:
- cabinet geometry is not changed
- Board Parts metadata remains unchanged
- current accepted corner cabinet geometry remains untouched

CSV columns:
Cabinet
Part
Role
Qty
Length [mm]
Width [mm]
Thickness [mm]
Material
Area [m2]

Next recommended stage:
Cut List 0.3
- edging data
- board/material assignment
- separate totals by material and thickness
