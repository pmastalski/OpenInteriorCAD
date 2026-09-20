OpenInteriorCAD Custom Drawer Heights 0.6 — any drawer may be Auto

The manual drawer-height dialog now displays an Auto radio button alongside
EVERY front (bottom to top). Select whichever front is to fill the remainder.
All other fields are directly editable and the automatic field recalculates
immediately when any value or Auto selection changes.

Storage now uses a JSON list with one null at the selected Auto position, e.g.
[120.0, null, 200.0] means the MIDDLE drawer is automatic. This persists in
DrawerHeightsJSON and tall-zone drawer_heights. Existing data from 0.5 with
n-1 entries still works; the last/top front remains Auto until changed.

The same resolver is used by UI, 3D geometry and Board Parts/Cut List.
The total sum of front heights + internal Front Gaps must equal the available
front envelope. Invalid divisions cannot be confirmed in the dialog.

Replace all five .py files in the current FreeCAD Workbench directory, then
restart FreeCAD and create/re-edit a drawer cabinet or tall-cabinet zone.
