OpenInteriorCAD — Cut List 0.9 / Interactive Edge Assignment

Major interaction upgrade:

WHEN EDGE ASSIGNMENT OPENS
- all candidate edge-band faces appear directly on the cabinet
- ORANGE = edge band enabled
- GREY TRANSPARENT = edge band disabled but available
- YELLOW = currently hovered edge

TABLE INTERACTION
- checking/unchecking Front / Back / Left / Right immediately updates the model
- no Apply is needed just to preview the change
- Apply still stores EdgeOverridesJSON

MODEL INTERACTION
- click an edge-band face directly in the 3D viewport
- the corresponding checkbox toggles automatically
- the model indicator updates immediately
- this allows edge assignment without returning to the table for every edge

TECHNICAL
- all indicators are Coin3D overlays
- no temporary FreeCAD document objects
- cabinet Shape is untouched
- overlays are removed when Edge Assignment closes

The model picker uses SoRayPickAction against named Coin3D edge-face nodes.
A small 0.35 mm preview offset is used to avoid z-fighting and improve picking.
