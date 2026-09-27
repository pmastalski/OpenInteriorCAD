OpenInteriorCAD - Simple Corner Base 0.5 - Reverse two perpendicular fillers

CORRECTION
Both 90-degree fillers now point OUT from the front into the room,
instead of pointing toward the back/wall. Only Simple Corner Base is changed.

Geometry, local coordinate system:
- Back/wall is at Y = 0; front body edge is at Y = Depth.
- Fixed left front and opening right door run Y=Depth..Depth+FrontThickness.
- Both fillers start at Y=Depth+FrontThickness (the OUTER front face)
  and end at Y=Depth+FrontThickness+BlindFillerWidth.
- X=0..FrontThickness for left starting filler;
  X=BlindBoxWidth-FrontThickness..BlindBoxWidth for inner corner filler.

They only touch front solids at a face; there is no volume overlap
with the fixed fascia / door in closed position.

UI text now calls the shared setting Both 90 degree Fillers Projection.
Board Parts no longer limits filler projection by the cabinet's internal depth.
The two filler production lengths and other carcass/door geometry stay as-is.

Install OICFurniture.py, OICFurnitureEditPanel.py, OICBoardParts.py
into the active OpenInteriorCAD Mod folder and restart FreeCAD.
