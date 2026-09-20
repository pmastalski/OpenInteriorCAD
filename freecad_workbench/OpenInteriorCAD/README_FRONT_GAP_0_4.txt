OpenInteriorCAD - Global Front Gap 0.4

For FrontGap = 2 mm:
- 1 mm at cabinet LEFT outside edge
- 1 mm at cabinet RIGHT outside edge
- 2 mm between adjacent door leaves, drawer fronts and stacked zones
- 2 mm at bottom and top of Base / Tall body front area
- Wall front drop is preserved.
- The value is unchanged (FrontGap property); existing cabinets update on recompute.
- Matching BoardParts dimensions are updated.
- Previously accepted L-corner folding front geometry is not changed.

Example: Cabinet width 600, FrontGap 2:
  single front width 598 mm
  double front leaves (598 - 2)/2 = 298 mm each
  x of fronts 1 mm and 301 mm; middle gap 2 mm.
  drawer front width 598 mm, 2 mm between drawers.

To install, copy .py files to the ACTIVE FreeCAD Mod/OpenInteriorCAD
folder and fully restart FreeCAD. Re-convert already-independent
PartDesign Bodies if you need them to reflect these production dimensions.

Syntax checked only; runtime in FreeCAD 1.1 Windows not available here.
