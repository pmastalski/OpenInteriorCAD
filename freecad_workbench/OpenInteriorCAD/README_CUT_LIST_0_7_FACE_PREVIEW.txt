OpenInteriorCAD — Cut List 0.7 / Face Preview

Changes requested after 0.6 testing:

1. Highlight is now a FILLED TRANSLUCENT SURFACE STRIP instead of a thin line.
   The highlighted strip runs along the selected Front / Back / Left / Right
   board edge and is much easier to see in 3D.

2. Hover reliability improved.
   Qt cellEntered does not fire consistently over checkbox widgets.
   0.7 gives each checkbox cell its own enter-event handler, so hovering the
   checkbox area triggers the preview directly.

3. Hover over Part / Role / Qty still previews all edge strips of that board.

4. Preview remains a temporary Coin3D overlay:
   - no document object
   - no Shape changes
   - no geometry changes

Only preview/UI code changed.
All cabinet geometry and Cut List data remain as in 0.6.
