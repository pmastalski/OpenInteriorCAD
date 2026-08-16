OpenInteriorCAD — Hardware 0.1

NEW COMMAND:
Hardware

Select exactly one cabinet and open Hardware.

AUTOMATIC HARDWARE:
- Concealed Hinges
- Drawer Runner Sets
- Adjustable Legs
- Shelf Supports
- Lift-up Mechanism
- Handles

Automatic rules use:
- CabinetType
- FrontType
- Height
- Width / WidthB
- DrawerCount
- ShelfCount
- Plinth presence through cabinet type

HINGE DEFAULT:
<= 900 mm door height  -> 2 hinges / leaf
<= 1600 mm             -> 3 hinges / leaf
<= 2200 mm             -> 4 hinges / leaf
> 2200 mm               -> 5 hinges / leaf

These are generic defaults. Manufacturer-specific engineering rules can be
added later.

MANUAL OVERRIDES:
Each hardware row shows:
- Auto Qty
- Override checkbox
- Final Qty

Enable Override to set a custom quantity.
Quantity 0 is valid and disables that item.

Reset to Automatic removes all manual overrides.

PRODUCTION METADATA:
Furniture receives:
- HardwareOverridesJSON
- HardwareJSON
- HardwareItemCount

EXPORT:
Hardware CSV:
- UTF-8 BOM
- semicolon delimiter
- suitable for Excel in Polish/European locale

IMPORTANT:
No cabinet Shape geometry was changed.
No accepted corner-cabinet geometry was changed.
No front geometry was changed.
Hardware 0.1 is metadata/calculation only.

NEXT LOGICAL STEP:
Hardware 0.2 can add a persistent hardware library:
Blum / Hettich / Grass style manufacturers, codes, variants and prices.
