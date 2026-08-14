OpenInteriorCAD — Cut List 0.4

NEW:
- explicit edge-band assignment per rectangular part:
  Front / Back / Left / Right
- Cut List shows one column for each edge
- CSV exports exact edge assignment
- aggregation now also respects edge assignment

Edge convention:
- Front and Back edges have the part Length
- Left and Right edges have the part Width

Default production rules in 0.4:
- carcass sides: front edge
- bottom/top: front edge
- shelves: front edge
- fillers: front edge
- plinth: front edge
- fronts: all four edges
- backs: no edge band
- L-shaped corner boards/shelves remain marked as "Custom (L)"
  because their exposed edges do not map cleanly to a simple rectangle.

IMPORTANT:
- no cabinet Shape geometry changes
- stable corner geometry remains untouched
- this stage changes production metadata only

Recommended next step:
Cut List 0.5
- editable edge assignment panel per logical part
- presets such as Carcass / Shelf / Front / Filler
- ability to override automatic Front/Back/Left/Right edge rules
