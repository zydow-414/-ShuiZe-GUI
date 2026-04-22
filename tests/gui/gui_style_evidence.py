import os
import sys

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTabWidget

from shuize_gui import ShuiZeGUI


def main() -> int:
    app = QApplication(sys.argv)
    window = ShuiZeGUI()
    stylesheet = window.styleSheet()
    config_tabs = window.config_page.findChild(QTabWidget, "configTabs")

    checks = {
        "has_transparent_label_rule": "QLabel, QCheckBox, QGroupBox, QTabWidget, QTabBar, QScrollArea {" in stylesheet,
        "has_config_tab_rule": "#configTabs::pane" in stylesheet,
        "has_scrollbar_rule": "QScrollBar:vertical" in stylesheet and "QScrollBar::handle:vertical" in stylesheet,
        "has_tab_widget": config_tabs is not None,
        "tab_count_is_two": config_tabs.count() == 2 if config_tabs else False,
        "tab_names_ok": [config_tabs.tabText(i) for i in range(config_tabs.count())] == ["基础配置", "高级字段"] if config_tabs else False,
        "nav_count_is_three": window.sidebar.count() == 3,
        "stack_count_is_three": window.stack.count() == 3,
    }

    for key, value in checks.items():
        print(f"{key}={value}")

    app.quit()
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
