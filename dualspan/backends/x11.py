"""X11 window backend using wmctrl + xrandr (no shell execution)."""
import os
import re
import shutil
import subprocess
from dualspan.geometry import Monitor, Rect, Window
OUTPUT_RE = re.compile(r"^([^\s]+) connected(?: primary)? (\d+)x(\d+)([+-]\d+)([+-]\d+)", re.M)
def parse_xrandr(content):
    return [Monitor(m.group(1), Rect(int(m.group(4)), int(m.group(5)), int(m.group(2)), int(m.group(3)))) for m in OUTPUT_RE.finditer(content)]
def parse_wmctrl(content):
    windows = []
    for line in content.splitlines():
        parts = line.split(maxsplit=8)
        if len(parts) < 9:
            continue
        wid, desktop, pid, x, y, width, height, host, title = parts
        try:
            int(wid, 16)
            rect = Rect(int(x), int(y), int(width), int(height))
        except ValueError:
            continue
        if desktop != "-1" and title.strip():
            windows.append(Window(wid.lower(), title, rect))
    return windows
class X11Backend:
    key = "x11"
    def __init__(self):
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            raise RuntimeError("Native X11 window control is unavailable on Wayland; use the KDE KWin script where supported")
        if not os.environ.get("DISPLAY"):
            raise RuntimeError("DISPLAY is unset. Log into an X11 graphical session")
        for executable in ("wmctrl", "xrandr", "xprop"):
            if not shutil.which(executable):
                raise RuntimeError(f"Missing {executable}; install wmctrl, xrandr, xprop")
    @staticmethod
    def run(*args):
        try:
            p = subprocess.run(args, text=True, capture_output=True, timeout=8, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise RuntimeError(f"Cannot run {args[0]}: {e}") from e
        if p.returncode:
            raise RuntimeError(f"{args[0]} failed: {(p.stderr or p.stdout).strip()}")
        return p.stdout
    def monitors(self):
        return parse_xrandr(self.run("xrandr", "--query"))
    def windows(self):
        return parse_wmctrl(self.run("wmctrl", "-lG", "-p"))
    def active_id(self):
        s = self.run("xprop", "-root", "_NET_ACTIVE_WINDOW")
        m = re.search(r"window id # (0x[0-9a-fA-F]+)", s)
        if not m or int(m.group(1), 16) == 0:
            raise RuntimeError("No active X11 window")
        return f"0x{int(m.group(1), 16):08x}"
    def get_window(self, wid):
        for w in self.windows():
            if int(w.id, 16) == int(wid, 16):
                return w
        raise RuntimeError("Window not found")
    def window_state(self, wid):
        s = self.run("xprop", "-id", wid, "_NET_WM_STATE")
        return {"max_vert": "_NET_WM_STATE_MAXIMIZED_VERT" in s, "max_horz": "_NET_WM_STATE_MAXIMIZED_HORZ" in s, "fullscreen": "_NET_WM_STATE_FULLSCREEN" in s}
    def move(self, wid, rect):
        self.run("wmctrl", "-i", "-r", wid, "-b", "remove,maximized_vert,maximized_horz")
        self.run("wmctrl", "-i", "-r", wid, "-b", "remove,fullscreen")
        self.run("wmctrl", "-i", "-r", wid, "-e", f"0,{rect.x},{rect.y},{rect.width},{rect.height}")
    def restore_state(self, wid, state):
        if state.get("max_vert") or state.get("max_horz"):
            atoms = [x for bit, x in (("max_vert", "maximized_vert"), ("max_horz", "maximized_horz")) if state.get(bit)]
            self.run("wmctrl", "-i", "-r", wid, "-b", "add," + ",".join(atoms))
        if state.get("fullscreen"):
            self.run("wmctrl", "-i", "-r", wid, "-b", "add,fullscreen")
