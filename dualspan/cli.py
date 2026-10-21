"""DualSpan command line launcher."""
import argparse
import sys
from dualspan import __version__
from dualspan.core import DualSpan

def main(argv=None):
    parser = argparse.ArgumentParser(prog="dualspan", description="Span a normal application window across two monitors")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("monitors", help="Show active monitors and zero-based indices")
    sub.add_parser("windows", help="Show resizable-window candidates and IDs")
    for action in ("span", "restore"):
        p = sub.add_parser(action, help="Span or restore selected window")
        p.add_argument("--window", help="Hex window ID (default foreground)")
        p.add_argument("--dry-run", action="store_true")
        if action == "span":
            p.add_argument("--screens", nargs=2, type=int, metavar=("FIRST","SECOND"))
    sub.add_parser("gui")
    args = parser.parse_args(argv)
    if args.action == "gui":
        from dualspan.gui import launch
        return launch()
    try:
        app = DualSpan()
        if args.action == "monitors":
            for i, m in enumerate(app.backend.monitors()):
                r = m.rect
                print(f"{i}: {m.name} ({r.width}x{r.height} at {r.x},{r.y})")
        elif args.action == "windows":
            for w in app.backend.windows(): print(f"{w.id}  {w.title}")
        elif args.action == "span":
            r, pair = app.span(args.window, tuple(args.screens) if args.screens else None, args.dry_run)
            print(f"{'Would span' if args.dry_run else 'Spanned'} over {pair[0]} + {pair[1]}: {r.width}x{r.height} at {r.x},{r.y}")
        elif args.action == "restore":
            r = app.restore(args.window, args.dry_run)
            print(f"{'Would restore' if args.dry_run else 'Restored'}: {r.width}x{r.height} at {r.x},{r.y}")
    except (RuntimeError, ValueError, OSError) as exc:
        print("DualSpan:", exc, file=sys.stderr)
        return 1
    return 0
