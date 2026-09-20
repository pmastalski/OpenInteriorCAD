OpenInteriorCAD: manual drawer front heights 0.5

Select Drawers -> Set individual heights... in Edit Furniture.
Tall cabinet: select a Drawers zone -> Drawer heights...
Heights from bottom to top. Set first n-1 heights, final front auto-fills.
Front Gap is subtracted before heights are divided; outer top/bottom remain
as already defined in 0.4. Same divisions used in Shape and Cut List.
If drawer count changes, obsolete manual division falls back to equal heights.
If cabinet/zone shrinks so custom heights no longer fit, geometry does not
build overlapping drawer fronts: update heights in the dialog.

Install all 5 .py files to FreeCAD v1-1/Mod/OpenInteriorCAD and restart.
No live FreeCAD runtime test performed.
