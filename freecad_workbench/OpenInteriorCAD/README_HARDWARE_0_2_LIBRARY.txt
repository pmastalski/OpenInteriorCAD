OpenInteriorCAD — Hardware 0.2 / Library + Prices + Presets

NEW HARDWARE LIBRARY:
- Type
- Manufacturer
- Code
- Name
- Unit
- Unit Price
- Notes

Hardware types:
- Hinge
- Drawer Runner
- Leg
- Shelf Support
- Lift-up
- Handle

LIBRARY:
The hardware library is persistent in FreeCAD preferences and available
across projects.

CABINET HARDWARE:
Automatic quantity calculation from Hardware 0.1 remains active.

Each automatic row can now be linked to a specific hardware-library item.

Example:
Auto:
Concealed Hinge -> Qty 4

Selected library item:
Blum | 71B3550 | CLIP top BLUMOTION

The production row then contains:
- manufacturer
- code
- exact hardware name
- unit price
- total row cost

QUANTITY OVERRIDE:
Still available independently from product selection.

HARDWARE PRESETS:
A preset stores one selected item for every hardware type:
- hinge
- drawer runner
- leg
- shelf support
- lift-up
- handle

This allows e.g.:
- Generic
- BLUM kitchen
- Hettich kitchen
- Economy
- Premium

COST:
Hardware panel shows total hardware cost for the selected cabinet.
CSV now includes unit price and total price.

NEW FURNITURE PRODUCTION METADATA:
HardwareSelectionJSON

Existing metadata retained:
- HardwareOverridesJSON
- HardwareJSON
- HardwareItemCount

IMPORTANT:
No cabinet Shape geometry was changed.
No corner geometry was changed.
No front geometry was changed.
Hardware 0.2 is production metadata, selection and costing only.
