OpenInteriorCAD — Blind Corner Set 0.6 / STEP Geometry Fix

SOURCE OF FIX
The exported models were analysed directly:

    szafka_right.step
    szafka_left.step

MEASURED RESULT IN VERSION 0.5

RIGHT (correct reference):
- parent front approximately Y = 591 mm
- linked 90° cabinet begins approximately Y = 591 mm
- linked cabinet extends outward to approximately Y = 1191 mm

LEFT (incorrect):
- linked cabinet ended approximately Y = 391 mm
- linked cabinet extended inward to approximately Y = -209 mm
- parent itself occupied approximately Y = -9 ... 591 mm

Therefore the Left companion cabinet physically entered / overlapped the
parent cabinet instead of extending outward from the corner.

ROOT CAUSE
The Left branch incorrectly mirrored the DEPTH direction (-Y).

A true left/right corner mirror should:
- mirror the side in X
- reverse cabinet rotation (+90 / -90)
- but keep BOTH return cabinets extending outward from the parent front

FIX

1. CORNER SPACER
Both Left and Right now run from the same recessed corner line toward +Y.
Their X position is mirrored.

2. LINKED 90° CABINET
Right:
- rotation +90°
- Width naturally extends toward +Y

Left:
- rotation -90°
- because Width points toward -Y at -90°, the origin Y is shifted by
  +BlindMateWidth
- final physical Y span is therefore the same outward span as Right

3. PLINTH RETURN
The short perpendicular toe-kick now has:
- the same Y geometry for Left and Right
- mirrored X location
- the same cut length in production data

4. EXISTING 50 mm RECESS
The v0.5 wall-direction recess remains:
- Corner Spacer uses Depth - 2 * PlinthSetback
- Door Clearance Filler uses Depth - PlinthSetback

No accepted standard / L-corner cabinet geometry was changed.
