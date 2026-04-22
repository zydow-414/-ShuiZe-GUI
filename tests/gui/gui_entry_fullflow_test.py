import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER = REPO_ROOT / ".gui_fullflow_marker"
RESULT_DIR = REPO_ROOT / "result"


def latest_result_dir() -> Path | None:
    if not RESULT_DIR.exists():
        return None
    run_dirs = [item for item in RESULT_DIR.iterdir() if item.is_dir()]
    if not run_dirs:
        return None
    return max(run_dirs, key=lambda item: item.stat().st_mtime)


def main() -> int:
    before_dir = latest_result_dir()
    MARKER.unlink(missing_ok=True)

    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["SHUIZE_GUI_TEST_DOMAIN"] = "example.com"
    env["SHUIZE_GUI_FULLFLOW_MARKER"] = str(MARKER)

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "ShuiZe.py"), "--gui"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        text=True,
        errors="replace",
    )

    after_dir = latest_result_dir()
    marker_text = MARKER.read_text(encoding="utf-8") if MARKER.exists() else ""
    marker_ok = (
        "status=已完成" in marker_text
        and after_dir is not None
        and f"current_folder={after_dir}" in marker_text
        and f"first_result_path={after_dir}\\example.com.xlsx" in marker_text
        and "window_title=ShuiZe Desktop Console" in marker_text
        and "pages=3" in marker_text
        and "nav=3" in marker_text
    )
    new_dir_created = after_dir is not None and (before_dir is None or after_dir != before_dir)
    xlsx_exists = after_dir is not None and (after_dir / "example.com.xlsx").exists()

    print(f"returncode={result.returncode}")
    print(f"marker_exists={MARKER.exists()}")
    print(f"marker_ok={marker_ok}")
    print(f"new_result_dir_created={new_dir_created}")
    print(f"xlsx_exists={xlsx_exists}")
    return 0 if result.returncode == 0 and MARKER.exists() and marker_ok and new_dir_created and xlsx_exists else 1


if __name__ == "__main__":
    raise SystemExit(main())
