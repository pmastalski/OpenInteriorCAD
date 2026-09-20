OpenInteriorCAD – Tall cabinet independent zones 0.1

INSTALL: replace OICFurniture.py, OICBoardParts.py, OICFurnitureEditPanel.py and
ADD OICTallZones.py in the SAME FreeCAD Mod/OpenInteriorCAD directory.
Restart FreeCAD. Do not remove existing Editable Bodies / InitGui files.

Edit Furniture -> Cabinet Type: Tall -> Tall Cabinet - Independent Zones.
Each table row is one clear opening, bottom to top:
  Open | Oven | Microwave | Single Door | Double Door | Drawers | Lift-up
Clear height in mm: 0 = auto remaining space; only ONE auto row.
Drawers count matters only on Drawers rows.
Add / Remove / Up / Down reorder zones. Example button seeds:
  440-mm 3 drawer niche, 600-mm oven, 380-mm microwave,
  auto remaining height single door at top.
Tall height should be ~2200 mm for that example.

Zone types Oven and Microwave create empty slots bounded by structural
partitions, NOT 3D appliance objects or appliance-specific ventilation cuts.
Actual appliance installation dimensions and ventilation require the
manufacturer's own documentation.

The outer back is the accepted full-overlay glued-on back.
The model has full-height sides, top, bottom and one divider between zones.
The divider and all generated zone front panels enter Board Parts/Cut List.
Global shelf count is ignored while valid tall zones are enabled.
Empty TallZonesJSON preserves old Tall cabinet configuration.

Note: this is the first iteration. Front lift motion is not simulated in
this version. Oven/microwave slots are *nominal*, not appliance-ready.
If total fixed zone heights exceed available clear body height, the UI
indicates INVALID. Correct it before relying on the regenerated geometry.

When loading old FCStd documents, the new zone property is initialized empty.
Use the Example button or add zone rows to opt into the new layout.
