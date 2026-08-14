OpenInteriorCAD — Corner Cabinet 0.5

Major corner geometry revision.

CornerOpeningWidth now defines the carcass opening itself, not only the fronts.

Changes:
- opening and folding fronts use the exact same clamped dimension
- two opening-boundary stiles are generated at the ends of the opening
- no front return panel is placed inside the doorway
- plinth starts after the opening, removing the former central plinth leg
- Width A / Width B remain total cabinet dimensions
- Depth A / Depth B remain cabinet leg depths
- Corner Folding Doors are generated inside the same opening

Recommended first test:
Width A: 1100 mm
Depth A: 600 mm
Width B: 1100 mm
Depth B: 600 mm
Corner Opening: 450 mm
Front Gap: 2 mm

Files:
OICFurniture.py
OICFurnitureEditPanel.py
OICFurnitureDuplicate.py

Only OICFurniture.py contains the 0.5 geometry change; the other files are
included to keep the package version consistent.
