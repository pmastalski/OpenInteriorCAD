OpenInteriorCAD — Cut List 0.5

NEW:
- "Edge Assignment" command
- select one cabinet and open Edge Assignment
- edit edge banding per logical part:
  Front / Back / Left / Right
- Apply stores overrides in the cabinet
- Reset to Automatic returns to production defaults
- Cut List and CSV automatically use the saved overrides

NEW Production property:
- EdgeOverridesJSON
  hidden/read-only metadata used internally by the panel

IMPORTANT:
- this changes production metadata only
- cabinet Shape geometry is untouched
- stable corner cabinet geometry remains unchanged

Workflow:
1. Select a cabinet.
2. Open OpenInteriorCAD > Edge Assignment.
3. Tick desired edges for each logical part.
4. Click Apply.
5. Open Cut List to see the result.

Next recommended stage:
Cut List 0.6:
- material library / presets
- Egger / Kronospan-style board names
- separate board, front, back and edge-band presets
