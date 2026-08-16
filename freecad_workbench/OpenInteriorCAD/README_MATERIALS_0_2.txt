OpenInteriorCAD — Materials 0.2

NEW:
"Apply material thickness to geometry" checkbox in Material Library.

Default behavior remains SAFE:
- checkbox OFF -> only production metadata changes
- cabinet geometry remains untouched

When checkbox is ON:
- Board material thickness -> PanelThickness
- Front material thickness -> FrontThickness
- Back material thickness -> BackThickness

Safety validation:
- rejects zero/negative or unrealistic thicknesses
- standard cabinet must keep usable internal width/depth
- corner cabinet must keep valid Width A/B versus Depth A/B leg geometry
- geometry update is wrapped in one FreeCAD transaction
- failed update can abort without leaving a partial thickness change

Important:
Edge material thickness remains production metadata only and does NOT change
board dimensions.

No corner-cabinet geometry algorithms were rewritten.
This feature only changes existing thickness properties when explicitly enabled.
