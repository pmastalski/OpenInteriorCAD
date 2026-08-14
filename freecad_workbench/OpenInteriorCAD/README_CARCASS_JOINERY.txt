OpenInteriorCAD — Carcass Joinery 0.1

Goal:
Remove avoidable intersections between cabinet boards and establish
production-oriented carcass geometry before front-opening mechanics.

Rules introduced / consolidated:
- vertical side/end panels remain full height
- horizontal bottom/top/shelf parts are intended to terminate at inner faces
  of side panels rather than pass through them
- Corner Cabinet 0.5 opening logic is preserved
- corner carcass remains the current L-shaped baseline
- back-panel construction is intentionally unchanged in this step

Next planned stages:
1. validate Base / Wall / Tall and Corner Base / Corner Wall visually
2. separate logical board identities for BOM/cut-list output
3. add back style: overlay / inset-groove
4. Front Operation 0.1

Install by replacing the included files in:
freecad_workbench/OpenInteriorCAD/
