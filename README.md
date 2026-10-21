# DualSpan — two monitors, one wide application window

**Version 0.2.0 | Free and open source | MIT licensed | Experimental**

DualSpan attempts to move and resize an ordinary, resizable application window across **two extended monitors**, with a way to restore its previous size. This prototype is **not** a virtual-display driver and does not make the OS or fullscreen games detect one physical ultrawide monitor.

> These are implementation targets, not confirmed compatibility certifications. The code has passed synthetic tests, but it still needs real hardware testing.

## Supported implementations

| Platform | Method | Current status |
| --- | --- | --- |
| Windows 10, Windows 11 | Native Win32 window-management API | Implemented; needs hardware testing |
| Debian, Ubuntu and derivatives running X11 | `wmctrl`, `xrandr`, `xprop` | Implemented; needs hardware testing |
| Arch, CachyOS, Manjaro and derivatives running X11 | Same X11 backend | Implemented; needs hardware testing |
| KDE Plasma 6 on Wayland | Separate KWin script | Experimental |
| GNOME, XFCE, Cinnamon, MATE and other X11 desktops | EWMH/X11 backend | Best-effort |
| GNOME and other non-KDE Wayland desktops | No generic cross-compositor API for moving other apps' windows | Not yet supported |

## Install & run

Connect two monitors and enable **Extend**, not Mirror.

**Windows 10 / 11**: Install Python 3.9+ (with Tkinter), download the repository as ZIP from GitHub, extract it, and double-click `DualSpan-Windows.bat`. Alternatively, run `py -3 dualspan.py gui`.

**Debian / Ubuntu (X11):**

```bash
sudo apt update
sudo apt install python3 python3-tk wmctrl x11-xserver-utils x11-utils
python3 dualspan.py gui
```

**Arch / CachyOS / Manjaro (X11):**

```bash
sudo pacman -S python tk wmctrl xorg-xrandr xorg-xprop
python dualspan.py gui
```

**KDE Plasma 6 (Wayland):** Build the experimental KWin extension from source:

```bash
python3 scripts/build.py
```

Install `dist/DualSpan-KDE.kwinscript` in **System Settings → Window Management → KWin Scripts**, enable it, and try **Meta+Alt+S** (span focused window) / **Meta+Alt+R** (restore). Shortcut registration and KWin APIs can vary by version.

For Windows and Linux X11, choose an application in the GUI and use **Span window** or **Restore window**. The CLI is also available:

```bash
python3 dualspan.py monitors
python3 dualspan.py windows
python3 dualspan.py span --window 0x01234567 --screens 0 1
python3 dualspan.py restore --window 0x01234567
```

## Important limitations

- Does not merge hardware displays, EDID, or fullscreen games.
- Some apps cannot be resized, and some window managers may reject or modify geometry requests.
- Mixed DPI scaling, decorations, monitor rotation, and unusual layouts need testing.
- Generic window control is deliberately unavailable across most Wayland compositors.
- A signed Windows executable or platform installers are **not** included yet.
- No telemetry, sign-in, subscription, or remote service is required.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q dualspan dualspan.py
python3 scripts/build.py
```

These tests check geometry, X11 parsing, and restore-state logic, **not actual display functionality**. GitHub Actions is configured to run source/tests on Linux and Windows.

## Open source and contributing

We welcome **bug reports, new desktop/Wayland integrations, platform compatibility test results, documentation improvements, and pull requests**. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. Report bugs or propose features in [Issues](https://github.com/Bravo87/DualSpan/issues). Contributions are reviewed before being merged; no automatic merging is promised.

Licensed under the [MIT License](LICENSE).
