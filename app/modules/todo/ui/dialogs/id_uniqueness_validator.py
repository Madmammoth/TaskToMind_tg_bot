import logging
from collections import defaultdict
from typing import Tuple, Any

logger = logging.getLogger(__name__)

CHILD_CONTAINERS = (
    "buttons", "children", "widgets", "items", "rows", "columns", "inputs"
)


class DuplicateWidgetIdError(RuntimeError):
    pass


class DialogsValidationError(RuntimeError):
    pass


def _get_widget_id(widget) -> str | None:
    for attribute in ("widget_id", "id", "name", "widget_name"):
        value = getattr(widget, attribute, None)
        if value is not None:
            logger.info("return value=%r", value)
            return value

    for method in ("get_widget_id", "get_id"):
        current_function = getattr(widget, method, None)
        if callable(current_function):
            try:
                value = current_function()
            except TypeError:
                continue
            if value is not None:
                logger.info("return value=%r", value)
                return value

    return None


def iter_widgets_with_ui_path(widget, path: Tuple[str, ...] = ()):
    if widget is None:
        return

    class_name = type(widget).__name__
    if class_name in ("Const", "Format"):
        return

    if class_name in ("CombinedInput", "Row", "Column", "Group"):
        path = path + (class_name,)

    yield widget, path

    for attribute_name in CHILD_CONTAINERS:
        children = getattr(widget, attribute_name, None)

        if not children:
            continue

        for child in children:
            if isinstance(child, tuple) and len(child) == 2:
                child = child[1]
            yield from iter_widgets_with_ui_path(child, path)

    keyboard = getattr(widget, "keyboard", None)
    if keyboard:
        for row in keyboard:
            for child in row:
                yield from iter_widgets_with_ui_path(child, path)


def collect_window_widget_ids(
        window,
) -> dict[str, list[Tuple[Any, Any, Tuple[str, ...]]]]:
    seen = defaultdict(list)
    roots = []
    for attribute in (
            "text", "keyboard", "on_message", "media", "link_preview"
    ):
        root = getattr(window, attribute, None)
        if root is not None:
            roots.append(root)
    if hasattr(window, "widgets"):
        roots.extend(window.widgets)

    for root in roots:
        if root is None:
            continue
        for widget, path in iter_widgets_with_ui_path(root):
            widget_id = getattr(widget, "widget_id", None)
            if not isinstance(widget_id, str) or not widget_id:
                continue
            seen[widget_id].append(path + (widget_id,))

    return seen


def validate_unique_ids_in_window(window):
    duplicates = {
        widget_id: paths
        for widget_id, paths in collect_window_widget_ids(window).items()
        if len(paths) > 1
    }
    if not duplicates:
        return

    lines = []
    for widget_id, paths in duplicates.items():
        lines.append(
            f"widget_id '{widget_id}' duplicated in window {window.state}:"
        )
        for path in paths:
            lines.append("  " + " > ".join(path))
    raise DuplicateWidgetIdError("\n".join(lines))


def validate_dialog(dialog):
    windows = getattr(dialog, "windows", {})

    for state, window in windows.items():
        validate_unique_ids_in_window(window)

    return None


def validate_dialogs(all_dialogs):
    logger.debug(
        "Starting validation of unique widget IDs within windows of dialogs"
    )
    errors = []
    for dialog in all_dialogs:
        try:
            validate_dialog(dialog)
        except DuplicateWidgetIdError as e:
            logger.error("%s", e)
            errors.append(str(e))

    if errors:
        raise DialogsValidationError("\n\n".join(errors))

    logger.debug(
        "Completed validation: "
        "unique widget IDs confirmed within dialog windows"
    )
