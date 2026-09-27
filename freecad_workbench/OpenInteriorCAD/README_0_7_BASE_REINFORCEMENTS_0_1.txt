OpenInteriorCAD 0.7 - Base Reinforcements 0.1

Changes

1. BASE CABINET TOP
Normal Base cabinets no longer use one complete top board.

They use two reinforcement rails:
- Front reinforcement
- Back reinforcement

Top Reinforcements:
- Horizontal
  Two flat rails at the top, front and back.
  Reinforcement Size = rail depth.

- Vertical
  Two upright rails at the top, front and back.
  Reinforcement Size = rail height.
  Intended especially for sink cabinets where the centre of the cabinet
  must stay open for the sink bowl and plumbing.

Default:
  Horizontal
  Reinforcement Size = 100 mm

Wall and Tall cabinets keep their complete top panel.

2. LOWER PLINTH / BOTTOM FILLER
New property:
  ShowLowerPlinth

The edit panel shows:
  Lower Plinth -> Generate lower plinth / bottom filler

Turning it off removes the lower front plinth strip while preserving:
- cabinet overall height
- plinth clearance / carcass Z level
- side panel geometry
- fronts

This lets the user omit the lower filler/plinth when needed.

3. BOARD PARTS
Cut List / Board Parts now reports:
- Top Reinforcement Front
- Top Reinforcement Back

instead of Top for Base cabinets.

The production dimensions follow Horizontal / Vertical mode.

4. DUPLICATION
Duplicate Furniture preserves:
- Top Reinforcement mode
- Reinforcement size
- Lower Plinth on/off

This package starts the OpenInteriorCAD 0.7 development line.
