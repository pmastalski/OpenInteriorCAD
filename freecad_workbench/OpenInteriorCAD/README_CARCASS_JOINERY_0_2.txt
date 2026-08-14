OpenInteriorCAD — Carcass Joinery 0.2

Purpose:
Clean the horizontal L-shaped boards used by corner cabinets.

Change:
- Top / Bottom / Shelf L-plates are no longer returned as two overlapping boxes.
- The two legs are fused into one solid.
- removeSplitter() is used when available to remove internal coplanar seams.
- External cabinet dimensions and Corner Cabinet 0.5 opening logic are unchanged.
- Front geometry is unchanged.

Why:
This gives a much better basis for:
- production board geometry
- board identification
- cut lists / BOM
- later CNC export

Test:
1. Corner Base, Front Type = Open.
2. Inspect top plate from above.
3. Inspect shelf and bottom around the inside corner.
4. Then enable Corner Folding Doors and confirm front geometry is unchanged.
