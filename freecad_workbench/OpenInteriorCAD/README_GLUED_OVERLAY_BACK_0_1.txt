OpenInteriorCAD — Full-overlay glued MDF back 0.1

Scope: Standard Base/Wall/Tall and Blind Corner Base. The accepted L-shaped
Corner Base/Corner Wall generator is deliberately unchanged.

Depth remains the OUTER dimension including the 3 mm rear MDF.
Back: full cabinet width x full carcass height, from Z=plinth to Z=height,
      positioned on the rear face (Y=0 .. back_thickness).
Sides, top, bottom, shelves: all stop at the rear back face, run from
      Y=back_thickness to Y=depth; no sideboard is deeper than a shelf.

For example (Base, W=600, D=560, H=850, plinth=100, T=18, BT=3):
Back 600 x 750 x 3 mm; both sides 750 x 557 x 18 mm;
Top/bottom 564 x 557 x 18 mm; shelf 564 x 557 x 18 mm.
External dimensions stay W=600, D=560 and H=850 (including plinth).

OICBoardParts.py is updated to match actual cut dimensions. For Blind Corner
Base its effective carcass depth still deducts Corner Spacer Width.

Existing FreeCAD furniture shapes need document recompute; conversion to
native Body should be repeated for existing converted objects.

Syntax checked. Not runtime tested inside FreeCAD 1.1.
