OpenInteriorCAD — Cut List 0.6 / Edge Hover Preview

NEW:
- Edge Assignment now previews board edges in the FreeCAD 3D viewport.
- Hover Front / Back / Left / Right -> highlights that edge.
- Hover Part / Role / Qty -> highlights the whole board perimeter.
- Shelf preview highlights all shelves represented by that logical row.
- Corner Bottom / Top / Shelf use an L-shaped outline preview.

Technical:
- preview is a temporary Coin3D overlay
- no document object is created
- document is not marked dirty by preview
- cabinet Shape is not changed
- preview is cleared when the mouse leaves the table or the panel closes

New file:
- OICEdgePreview.py

Updated:
- OICEdgeAssignmentPanel.py

All Cut List 0.5 functionality is retained.
