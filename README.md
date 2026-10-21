# DualSpan v0.2

Free and open-source (MIT) prototype for spanning a **normal resizable application window** across two extended monitors. Does **not** create a single virtual display, change EDID, or reliably merge exclusive-fullscreen games.

## Platform targets
- Windows 10 / 11: native Win32 backend (experimental)
- Debian / Ubuntu / Arch and derivatives: X11 backend (experimental; requires wmctrl, xrandr, xprop)
- KDE Plasma 6 Wayland: separate experimental KWin extension
- GNOME and other Wayland compositors: not currently supported

**Not yet tested on physical multi-monitor hardware.**

This repository includes the v0.2 Python GUI, CLI, native Windows and Linux X11 backends, experimental KDE KWin script, tests, and build instructions. Generate the KDE KWin package with `python3 scripts/build.py`. See LICENSE for terms.

## Using the complete source package

**Windows:** install Python 3.9+, connect two monitors in Extend mode, double-click `DualSpan-Windows.bat`.

**Debian/Ubuntu X11:** `sudo apt install python3 python3-tk wmctrl x11-xserver-utils x11-utils`, then `python3 dualspan.py gui`.

**Arch X11:** `sudo pacman -S python tk wmctrl xorg-xrandr xorg-xprop`, then `python dualspan.py gui`.

**KDE Plasma 6 Wayland:** install `DualSpan-KDE.kwinscript` via System Settings > KWin Scripts (experimental).

For project status and collaboration, open a GitHub issue.
