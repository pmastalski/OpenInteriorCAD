OpenInteriorCAD — Blind Corner Set 0.8 / Clean Joints

SOURCE
The exported model:
    Unnamed(1).step
was analysed geometrically.

RESULT
The two vertical fillers were NOT actually intersecting in volume.

Measured vertical filler solids:
- Corner Spacer:
    18 x 50 x 750 mm
- Door Clearance Filler:
    50 x 18 x 750 mm

They meet at the intended 90-degree butt joint.

REAL COLLISION FOUND
The only true solid collision between the Blind Corner cabinet and the
linked Corner Mate was:

    Plinth Return x Corner Mate Plinth

Overlap:
    18 x 18 x 100 mm

This is exactly one panel thickness in both horizontal directions.

ROOT CAUSE
Plinth Return length was calculated as:

    distance_to_mate + PanelThickness

The extra PanelThickness made the short plinth enter the neighbour plinth.

FIX
Plinth Return now ends exactly on the mate-plinth face:

    return_len = abs(mate_face - parent_plinth_start)

The + PanelThickness overlap has been removed.

PRODUCTION DATA
Board Parts now uses the matching physical cut length:

    Plinth Return =
        Corner Spacer Width
        + Plinth Setback
        + Panel Thickness

Example:
    Corner Spacer Width = 50
    Plinth Setback = 50
    Panel Thickness = 18

    Plinth Return = 118 mm

The previous geometry was 136 mm and physically overlapped the mate plinth
by 18 mm.

UNCHANGED
- vertical Corner Spacer geometry
- Door Clearance Filler geometry
- physical spacer gap
- Left / Right STEP fix
- linked 90-degree cabinet
- existing standard and L-shaped corner cabinets
