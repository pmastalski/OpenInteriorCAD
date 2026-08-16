OpenInteriorCAD — Materials 0.4 / Color Hover Preview

NEW VISUAL LANGUAGE

BLUE   = Carcass
GREEN  = Front
VIOLET = Back
ORANGE = Edge band

Material Library:
- rows are visually separated by material type
- Type combobox has a colored marker
- library row hover highlights the corresponding cabinet category

Selected Cabinet:
- Carcass / Front / Back / Edge rows have permanent color markers
- hover over the label OR material combobox highlights that category in 3D

Legend:
- top legend explains the color convention
- hovering the legend also previews that category

3D PREVIEW:
Carcass:
- highlights carcass boards

Front:
- highlights door / drawer-front geometry

Back:
- highlights back panels

Edge:
- reuses the stable Edge Assignment renderer and highlights currently
  assigned edge-band faces

The preview uses Coin3D only:
- no temporary FreeCAD document objects
- no Shape changes
- preview is removed when the pointer leaves the control or panel closes

Existing functionality retained:
- persistent materials
- presets
- Apply material thickness to geometry
- Cut List 1.0
- Hardware 0.1
- interactive Edge Assignment

No accepted cabinet or corner geometry was changed.
