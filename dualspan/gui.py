"""Tkinter GUI for DualSpan."""
from dualspan.core import DualSpan

def launch():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("Tkinter is missing. Install python3-tk.")
        return 1
    root = tk.Tk()
    root.title("DualSpan 0.2 — Two displays, one window")
    root.geometry("660x360")
    frame = ttk.Frame(root, padding=18)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="DualSpan", font=("TkDefaultFont", 18, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Select a window and two screens. Both displays must use Extend mode.").pack(anchor="w", pady=(0, 12))
    status = tk.StringVar(value="Ready")
    windows, monitors, app = [], [], None
    ttk.Label(frame, text="Window").pack(anchor="w")
    win = ttk.Combobox(frame, state="readonly", width=70)
    win.pack(fill="x", pady=(2, 10))
    ttk.Label(frame, text="Displays (Auto on both for nearest pair)").pack(anchor="w")
    line = ttk.Frame(frame); line.pack(fill="x", pady=(2, 10))
    a = ttk.Combobox(line, state="readonly", width=35); a.pack(side="left", fill="x", expand=True)
    b = ttk.Combobox(line, state="readonly", width=35); b.pack(side="left", fill="x", expand=True)

    def refresh():
        nonlocal windows, monitors, app
        try:
            app = DualSpan()
            windows, monitors = app.backend.windows(), app.backend.monitors()
            win["values"] = [f"{w.id}: {w.title[:95]}" for w in windows]
            if windows: win.current(0)
            labels = ["Auto"] + [f"{i}: {m.name} ({m.rect.width}x{m.rect.height})" for i, m in enumerate(monitors)]
            for c in (a, b):
                c["values"] = labels
                c.current(0)
            status.set(f"Found {len(windows)} windows and {len(monitors)} monitors")
        except (RuntimeError, OSError, ValueError) as e:
            status.set(str(e)); messagebox.showwarning("DualSpan", str(e))

    def run(action):
        try:
            if app is None or win.current() < 0: raise RuntimeError("Select a window")
            wid = windows[win.current()].id
            if action == "span":
                i, j = a.current(), b.current()
                if (i == 0) != (j == 0): raise ValueError("Choose two displays or Auto on both")
                pair = None if i == j == 0 else (i - 1, j - 1)
                rect, names = app.span(wid, pair)
                status.set(f"Spanned {rect.width}x{rect.height} across {names[0]} + {names[1]}")
            else:
                rect = app.restore(wid)
                status.set(f"Restored {rect.width}x{rect.height}")
        except (RuntimeError, OSError, ValueError) as e:
            status.set(str(e)); messagebox.showerror("DualSpan", str(e))
    buttons = ttk.Frame(frame); buttons.pack(fill="x", pady=12)
    ttk.Button(buttons, text="Refresh", command=refresh).pack(side="left", padx=8)
    ttk.Button(buttons, text="Span window", command=lambda:run("span")).pack(side="left", padx=8)
    ttk.Button(buttons, text="Restore window", command=lambda:run("restore")).pack(side="left", padx=8)
    ttk.Label(frame, textvariable=status, wraplength=610).pack(anchor="w", pady=10)
    ttk.Label(frame, text="Wayland KDE: use KWin script. Does not merge displays for games.", wraplength=610).pack(anchor="w")
    root.after(50, refresh)
    root.mainloop()
    return 0
