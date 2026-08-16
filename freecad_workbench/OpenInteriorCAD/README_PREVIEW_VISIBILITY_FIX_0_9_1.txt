OpenInteriorCAD — Edge Assignment 0.9.1 Preview Visibility Fix

Problem:
Active/inactive edge faces sometimes disappeared while orbiting the 3D view.

Cause:
The Coin3D preview faces were almost coplanar with the real cabinet surfaces.
Depending on camera angle and OpenGL depth/back-face handling, they could be
hidden by the cabinet or culled.

Fix:
- preview group no longer participates in normal depth testing when
  SoDepthBuffer is available
- preview faces are explicitly double-sided (both vertex windings)
- shape hints no longer assume one visible face orientation
- preview offset increased from 0.35 mm to 0.75 mm as a fallback against
  z-fighting

Unchanged:
- cabinet geometry
- Edge Assignment data
- click-to-toggle behavior
- orange / grey / yellow state colors
- Cut List / CSV logic

Replace only OICEdgePreview.py if desired.
