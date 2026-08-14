OpenInteriorCAD — Cut List 0.8 / Exact Edge Faces

Requested improvement:
Instead of highlighting a line or a strip on the large board surface,
Edge Assignment now highlights the actual narrow physical face where
the edge band is applied.

Examples:
- shelf Front -> front vertical face of the shelf, height = panel thickness
- side Front -> narrow vertical face at the exposed front edge
- front Left -> left narrow side face of the front panel
- plinth Front -> actual exposed plinth edge face

The preview uses the real:
- PanelThickness
- FrontThickness
- BackThickness
where applicable.

Reliability:
- retains the explicit hover handlers from 0.7
- checkbox cells continue to trigger preview directly
- preview is cleared when leaving the panel/table

Safety:
- no FreeCAD document object is created
- cabinet Shape is unchanged
- Cut List and Edge Assignment data are unchanged

Only preview/UI code changed.
