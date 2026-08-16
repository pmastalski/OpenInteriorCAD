OpenInteriorCAD — Blind Corner Base 0.3 / Corner Fit

This update changes the corner connection to match a practical kitchen
blind-corner installation.

1. CORNER SPACER / PERPENDICULAR FILLER

The existing perpendicular spacer is now:
- height = cabinet Height minus PlinthHeight
- bottom = exactly at PlinthHeight
- top = cabinet top
- recessed by PlinthSetback
- width/length remains fully adjustable with Corner Spacer Width

This means it no longer reaches the floor.

2. PLINTH / TOE-KICK RETURN

The new cabinet now has:
- the existing straight recessed front plinth
- an additional perpendicular Plinth Return under the corner spacer

The return:
- has the same PlinthHeight
- uses the same PlinthSetback line
- closes the visible bottom at the corner
- runs toward the neighbouring 90-degree cabinet
- follows Corner Spacer Width

3. SECOND ADJUSTABLE FILLER FOR DOOR CLEARANCE

New property:
    BlindDoorFillerWidth

UI label:
    Door Clearance Filler

Default:
    50 mm

This is a front-plane filler next to the corner. It shortens the usable
front/door width so the door has space to open without colliding with the
neighbouring cabinet.

Hidden Side = Left:
- clearance filler is on the LEFT side of the usable front

Hidden Side = Right:
- clearance filler is on the RIGHT side of the usable front

The front-opening hinge limits are moved with the shortened usable opening.

4. PRODUCTION

Board Parts / Cut List now include:
- Corner Spacer Filler
- Door Clearance Filler
- Plinth Return

Cut Layout / PDF / SVG use those parts automatically.

Existing accepted L-shaped Corner Base / Corner Wall geometry is unchanged.
