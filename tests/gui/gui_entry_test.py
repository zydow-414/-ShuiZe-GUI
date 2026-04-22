import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / ".gui_started_marker"


def main() -> int:
    MARKER.unlink(missing_ok=True)
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["SHUIZE_GUI_AUTO_EXIT_MS"] = "1000"
    env["SHUIZE_GUI_STARTUP_MARKER"] = str(MARKER)

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "ShuiZe.py"), "--gui"],
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
    stdout_ok = "Start example.com information collection" not in result.stdout and "author:ske" not in result.stdout

    print(f"returncode={result.returncode}")
    print(f"marker_exists={MARKER.exists()}")
    print(f"marker_ok={marker_ok}")
    print(f"stdout_ok={stdout_ok}")
    if result.stderr.strip():
        print(result.stderr[:800].replace("\n", " | "))
    return 0 if result.returncode == 0 and MARKER.exists() and marker_ok and stdout_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
