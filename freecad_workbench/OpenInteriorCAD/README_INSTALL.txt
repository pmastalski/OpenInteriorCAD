OpenInteriorCAD - Snap Run to Wall update

Copy with:
unzip -o ~/Downloads/OpenInteriorCAD_snap_run_wall_update.zip -d freecad_workbench/OpenInteriorCAD/

Then fully restart FreeCAD.

Test:
1. Select Cabinet Run.
2. Snap Run to Wall.
3. Wall Offset = 0 mm.
4. Pick Wall and click the desired physical wall face.
5. Repeat with Wall Offset = 50 mm.

The wall-face geometry is reused from OICFurnitureSnapWall.py.
