import json
from pathlib import Path

from app.config_data.config import DEV_MODE

SNAPSHOT_FILE = Path(__file__).parent.parent / "snapshots/task_creation.json"


class SnapshotContext:
    def __init__(self):
        self.prev_state = None
        self.prev_dialog_data = None


def start_snapshot(dialog_manager) -> SnapshotContext | None:
    if not DEV_MODE:
        return None
    snap_ctx = SnapshotContext()
    snap_ctx.prev_state = dialog_manager.current_context().state
    snap_ctx.prev_dialog_data = dialog_manager.dialog_data.copy()
    return snap_ctx


def end_snapshot(snap_ctx: SnapshotContext, action: str, widget_id: str, dialog_manager):
    if not DEV_MODE or snap_ctx is None:
        return
    snapshot = {
        "action": action,
        "widget_id": widget_id,
        "dialog_state_before": snap_ctx.prev_state,
        "dialog_data_before": snap_ctx.prev_dialog_data,
        "dialog_state_after": dialog_manager.current_context().state,
        "dialog_data_after": dialog_manager.dialog_data.copy(),
        "dialog_start_data": dialog_manager.start_data.copy(),
    }

    try:
        with SNAPSHOT_FILE.open("w", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(snapshot)
    with SNAPSHOT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)  # noqa
