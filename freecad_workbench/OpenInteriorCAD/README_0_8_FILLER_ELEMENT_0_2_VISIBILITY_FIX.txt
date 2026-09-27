OpenInteriorCAD 0.8 - Filler Element 0.2 Visibility Fix

PROBLEM
New filler objects appeared in the Model tree with a crossed-out eye and
could not be made visible.

CAUSE
The standalone filler was created as:
    PartDesign::FeaturePython

That object type is intended for Part Design features living inside a Body.
A standalone filler is not a Part Design feature and therefore could end up
with an invalid/non-toggleable display state.

FIX
The filler is now created as:
    Part::FeaturePython

This is the correct FreeCAD object type for an independent parametric shape.

Additionally the object is explicitly set visible after its first recompute.

RESULT
Newly inserted fillers should:
- appear immediately in the 3D view,
- have a normal visibility eye in the Model tree,
- allow Space / eye toggling normally,
- remain fully parametric and editable through OpenInteriorCAD.
