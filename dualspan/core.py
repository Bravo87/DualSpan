"""Cross-platform orchestration and persistent restore data."""
import json
import os
from pathlib import Path
import tempfile
from dualspan.geometry import Rect, selection, union

class DualSpan:
    def __init__(self, backend=None, state_path=None):
        self.backend = backend or detect_backend()
        self.state_path = Path(state_path) if state_path else default_state_path()

    def _read_state(self):
        try:
            with self.state_path.open("r", encoding="utf-8") as f:
                content = json.load(f)
                return content if isinstance(content, dict) else {}
        except (FileNotFoundError, ValueError, OSError):
            return {}

    def _save_state(self, state):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".dualspan-", dir=self.state_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            os.replace(tmp, self.state_path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def _key(self, wid):
        return self.backend.key + ":" + str(wid).lower()

    def span(self, wid=None, indices=None, dry_run=False):
        if wid is None:
            wid = self.backend.active_id()
        window = self.backend.get_window(wid)
        monitors = self.backend.monitors()
        left, right = selection(monitors, window.rect, indices)
        target = union(left.rect, right.rect)
        key = self._key(window.id)
        state = self._read_state()
        if key in state:
            raise RuntimeError("This window is already spanned; restore it first")
        if not dry_run:
            previous = {"rect": window.rect.to_dict(), "window_title": window.title,
                        "original_state": self.backend.window_state(window.id)}
            self.backend.move(window.id, target)
            state[key] = previous
            self._save_state(state)
        return target, (left.name, right.name)

    def restore(self, wid=None, dry_run=False):
        if wid is None:
            wid = self.backend.active_id()
        window = self.backend.get_window(wid)
        key = self._key(window.id)
        state = self._read_state()
        if key not in state:
            raise RuntimeError("No saved pre-span position for this window")
        saved = state[key]
        rect = Rect(**saved["rect"])
        if not dry_run:
            self.backend.move(window.id, rect)
            self.backend.restore_state(window.id, saved["original_state"])
            del state[key]
            self._save_state(state)
        return rect

def detect_backend(environ=None, os_name=None):
    environ = os.environ if environ is None else environ
    os_name = os.name if os_name is None else os_name
    if os_name == "nt":
        from dualspan.backends.windows import WindowsBackend
        return WindowsBackend()
    if os_name == "posix":
        if environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            raise RuntimeError("Wayland needs compositor-specific integration. KDE Plasma 6: install KWin extension")
        from dualspan.backends.x11 import X11Backend
        return X11Backend()
    raise RuntimeError("Only Windows 10/11 and Linux X11 supported by launcher")

def default_state_path():
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    else:
        root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    return root / "DualSpan" / "windows.json"
