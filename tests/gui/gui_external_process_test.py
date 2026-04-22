import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from shuize_gui import RESULT_DIR, ShuiZeGUI


def latest_result_dir() -> Path | None:
    if not RESULT_DIR.exists():
        return None
    run_dirs = [item for item in RESULT_DIR.iterdir() if item.is_dir()]
    if not run_dirs:
        return None
    return max(run_dirs, key=lambda item: item.stat().st_mtime)


def main() -> int:
    os.environ["SHUIZE_GUI_FORCE_EXTERNAL_PROCESS"] = "1"
    app = QApplication(sys.argv)
    window = ShuiZeGUI()

    before_dir = latest_result_dir()
    window.task_page.mode_combo.setCurrentText("根域名扫描")
    window.task_page.domain_input.setText("example.com")
    window.task_page.just_info_check.setChecked(True)
    window.task_page.update_preview()
    window.start_task()

    loop = QEventLoop()
    timeout = {"value": False}

    def stop_waiting() -> None:
        timeout["value"] = True
        loop.quit()

    def poll_finished() -> None:
        if window.external_process is None:
            loop.quit()
            return
        QTimer.singleShot(400, poll_finished)

    QTimer.singleShot(400, poll_finished)
    QTimer.singleShot(900000, stop_waiting)
    loop.exec()

    after_dir = latest_result_dir()
    new_dir_created = after_dir is not None and (before_dir is None or after_dir != before_dir)
    xlsx_exists = after_dir is not None and (after_dir / "example.com.xlsx").exists()
    status_text = window.task_page.status_label.text()
    gui_folder = window.results_page.current_folder
    preview_text = window.task_page.command_preview.toPlainText()

    print(f"timeout={timeout['value']}")
    print(f"status={status_text.encode('unicode_escape').decode('ascii')}")
    print(f"new_result_dir_created={new_dir_created}")
    print(f"xlsx_exists={xlsx_exists}")
    print(f"gui_folder_matches_new={str(gui_folder) == str(after_dir) if gui_folder and after_dir else False}")
    print(f"external_program_set={bool(window.external_process_program)}")
    print(f"external_args_present={len(window.external_process_args) > 0}")
    print(f"preview_has_domain={'example.com' in preview_text}")
    app.quit()
    return 0 if not timeout["value"] and status_text == "已完成" and new_dir_created and xlsx_exists and bool(window.external_process_program) and len(window.external_process_args) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
