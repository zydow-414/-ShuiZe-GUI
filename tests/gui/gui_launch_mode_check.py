import os
import sys

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PySide6.QtWidgets import QApplication

from shuize_gui import should_use_internal_process


def main() -> int:
    app = QApplication(sys.argv)
    qt_qpa_platform = os.environ.get("QT_QPA_PLATFORM", "")
    internal_process = should_use_internal_process()
    print(f"qt_qpa_platform={qt_qpa_platform}")
    print(f"internal_process={internal_process}")
    app.quit()
    if sys.platform.startswith("win") and qt_qpa_platform.lower() != "offscreen":
        return 0 if not internal_process else 1
    if qt_qpa_platform.lower() == "offscreen":
        return 0 if internal_process else 1
    return 0 if internal_process else 1


if __name__ == "__main__":
    raise SystemExit(main())
