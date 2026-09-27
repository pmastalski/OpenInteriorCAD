OpenInteriorCAD 0.8 - Standalone Filler Element 0.1

NEW COMMANDS
- Add Filler
- Edit Filler

FILLER
The filler is a standalone parametric board element, independent of a cabinet.

Editable:
- Width
- Height
- Thickness
- X / Y / Z placement
- Rotation around Z
- Board Material
- Edge Material
- Edge Thickness

EDGE BANDING
Each physical edge can be selected independently:
- Top
- Bottom
- Left
- Right

The filler is generated vertically by default:
- X = Width
- Y = Thickness
- Z = Height

LIVE EDITING
All changes are applied immediately.
The editor stays open and can switch to another filler by selecting it in
the 3D view or Model tree.

PRODUCTION
Standalone fillers are included in:
- Production Cut List
- Cut Layout (through the shared cut-list source)

Their selected edge banding is included in production metadata.

The new element is intentionally generic so it can later be reused for:
- wall fillers,
- end fillers,
- cover strips,
- decorative vertical boards,
- custom cabinet finishing panels.
