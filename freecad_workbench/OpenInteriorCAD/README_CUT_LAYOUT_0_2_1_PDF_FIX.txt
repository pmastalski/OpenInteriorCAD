OpenInteriorCAD - Cut Layout 0.2.1 / PDF Fix

FIX:
FreeCAD 1.1 on macOS does not expose QtPrintSupport through:
    from PySide import QtPrintSupport

This caused OpenInteriorCAD to fail during workbench startup.

The PDF exporter now uses:
    QtGui.QPdfWriter

This is part of QtGui and is compatible with FreeCAD's PySide environment.

PDF FEATURES RETAINED:
- Export PDF button
- all calculated sheets in one PDF
- one stock sheet per page
- A3 landscape
- vector output
- sheet layout, labels, dimensions and header
- SVG export remains unchanged

No cabinet geometry, Cut List, Board Parts, materials, hardware,
edge assignments or front-opening behavior is changed.
