OpenInteriorCAD — Carcass Joinery 0.3

Focus:
Clean up the remaining vertical overlaps in Corner Base / Corner Wall.

Changes:
- opening boundary stiles are constrained to their own panel-sized volumes
- stiles are clamped before outer end panels
- back panels no longer overlap each other in the rear corner
- plinth segments stop before outer end panels
- Carcass Joinery 0.2 single-solid L plates are preserved
- Corner Opening and folding-front logic are preserved

Recommended validation:
1. Corner Base -> Front Type = Open.
2. Inspect both vertical edges at the corner opening.
3. Inspect the rear corner.
4. Inspect plinth/end-panel joints.
5. Enable Corner Folding Doors and confirm fronts remain aligned.

Next milestone after validation:
Board Parts 0.1 — logical Left Side / Right Side / Bottom / Top /
Shelf / Back identities for Cut List and BOM.
