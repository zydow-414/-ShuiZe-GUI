import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from shuize_gui import ShuiZeGUI


OUTPUT_PATH = REPO_ROOT / "docs" / "imgs" / "gui_current_review.png"


def main() -> int:
    app = QApplication(sys.argv)
    window = ShuiZeGUI()
    window.show()

    def capture() -> None:
        pixmap = window.grab()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(str(OUTPUT_PATH), "PNG")
        print(f"screenshot_path={OUTPUT_PATH}")
        print(f"exists={OUTPUT_PATH.exists()}")
        app.quit()

    QTimer.singleShot(400, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
