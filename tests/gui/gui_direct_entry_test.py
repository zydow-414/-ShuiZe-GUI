import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / ".gui_direct_started_marker"


def main() -> int:
    MARKER.unlink(missing_ok=True)
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["SHUIZE_GUI_AUTO_EXIT_MS"] = "1000"
    env["SHUIZE_GUI_STARTUP_MARKER"] = str(MARKER)

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "shuize_gui.py")],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        text=True,
        errors="replace",
    )

    marker_text = MARKER.read_text(encoding="utf-8") if MARKER.exists() else ""
    marker_ok = (
        "title=ShuiZe Desktop Console" in marker_text
        and "pages=3" in marker_text
        and "nav=3" in marker_text
    )

    print(f"returncode={result.returncode}")
    print(f"marker_exists={MARKER.exists()}")
    print(f"marker_ok={marker_ok}")
    return 0 if result.returncode == 0 and MARKER.exists() and marker_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
