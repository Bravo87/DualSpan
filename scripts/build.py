"""Build Plasma 6 KWin script archive."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
out = root / "dist" / "DualSpan-KDE.kwinscript"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for filename in ("dualspan-kwin/metadata.json", "dualspan-kwin/contents/code/main.js"):
        z.write(root/filename, filename.removeprefix("dualspan-kwin/"))
print(out)
