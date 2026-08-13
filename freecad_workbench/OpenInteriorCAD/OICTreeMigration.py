"""One-time helper to translate existing OpenInteriorCAD Model tree labels."""

import FreeCAD as App


def migrate_model_tree_labels(document=None):
    """Translate existing Polish OpenInteriorCAD labels to English."""
    doc = document or App.ActiveDocument

    if doc is None:
        return 0

    changed = 0

    exact = {
        "Pomieszczenie": "Room",
        "Drzwi": "Door",
        "Okno": "Window",
        "Podłoga": "Floor",
        "Szafka": "Cabinet",
        "Wymiary": "Dimensions",
    }

    prefixes = (
        ("Ściana", "Wall"),
        ("Drzwi", "Door"),
        ("Okno", "Window"),
        ("Podłoga", "Floor"),
        ("Szafka", "Cabinet"),
        ("Wymiar ", "Dimension "),
    )

    for obj in doc.Objects:
        old_label = obj.Label
        new_label = exact.get(old_label)

        if new_label is None:
            for old_prefix, new_prefix in prefixes:
                if old_label.startswith(old_prefix):
                    new_label = (
                        new_prefix
                        + old_label[len(old_prefix):]
                    )
                    break

        if new_label and new_label != old_label:
            obj.Label = new_label
            changed += 1

    doc.recompute()

    App.Console.PrintMessage(
        f"OpenInteriorCAD: translated {changed} model tree labels.\n"
    )

    return changed
