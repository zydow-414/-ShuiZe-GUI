import os
import sys
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("SHUIZE_FAST_TEST", "1")

from PySide6.QtCore import QEventLoop, QProcess, QTimer
from PySide6.QtWidgets import QApplication, QTabWidget

from shuize_gui import CONFIG_PATH, RESULT_DIR, ShuiZeGUI


def latest_result_dir() -> Path | None:
    if not RESULT_DIR.exists():
        return None
    run_dirs = [item for item in RESULT_DIR.iterdir() if item.is_dir()]
    if not run_dirs:
        return None
    return max(run_dirs, key=lambda item: item.stat().st_mtime)


def main() -> int:
    app = QApplication(sys.argv)
    window = ShuiZeGUI()

    print(window.windowTitle())
    print(f"nav={window.sidebar.count()} pages={window.stack.count()} modes={window.task_page.mode_combo.count()}")

    original_config = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        email_field = window.config_page.fields[("fofa api", "EMAIL")]
        email_field.setText("gui-test@example.com")
        c_nums_field = window.config_page.fields[("C nums", "c_nums")]
        c_nums_field.setValue(1234)
        window.config_page.save_config()
        window.config_page.load_config()
        print(f"config_email={window.config_page.fields[('fofa api', 'EMAIL')].text()}")
        print(f"config_c_nums={window.config_page.fields[('C nums', 'c_nums')].value()}")
    finally:
        CONFIG_PATH.write_text(original_config, encoding="utf-8")
        window.config_page.load_config()

    window.results_page.refresh_results()
    latest = window.results_page.current_folder
    print(f"latest_result_dir={latest if latest else 'NONE'}")

    fake_result_dir = Path(window.results_page.current_folder or window.results_page.current_folder or Path(""))
    created_fake_dir = False
    if not latest:
        fake_result_dir = Path("result") / "gui_test_artifacts"
        fake_result_dir.mkdir(parents=True, exist_ok=True)
        (fake_result_dir / "demo.xlsx").write_text("demo", encoding="utf-8")
        (fake_result_dir / "demo_github.txt").write_text("demo", encoding="utf-8")
        created_fake_dir = True
        window.results_page.refresh_results()
    print(f"results_rows={window.results_page.result_table.rowCount()}")

    print(f"config_tabs={window.config_page.findChild(QTabWidget, 'configTabs') is not None}")

    window.task_page.domain_input.setText("example.com")
    window.task_page.just_info_check.setChecked(True)
    window.task_page.update_preview()
    before_dir = latest_result_dir()
    window.start_task()

    loop = QEventLoop()
    timeout_triggered = {"value": False}

    def on_timeout() -> None:
        timeout_triggered["value"] = True
        loop.quit()

    def poll_finished() -> None:
        internal_done = window.process.state() == QProcess.ProcessState.NotRunning
        external_done = window.external_process is None
        if internal_done and external_done:
            loop.quit()
            return
        QTimer.singleShot(400, poll_finished)

    QTimer.singleShot(400, poll_finished)
    QTimer.singleShot(600000, on_timeout)
    loop.exec()

    if window.process.state() != QProcess.ProcessState.NotRunning:
        window.stop_task()
        wait_loop = QEventLoop()
        window.process.finished.connect(wait_loop.quit)
        QTimer.singleShot(2000, wait_loop.quit)
        wait_loop.exec()
    elif window.external_process is not None:
        window.stop_task()

    preview_text = window.task_page.command_preview.toPlainText()
    after_dir = latest_result_dir()
    new_dir_created = after_dir is not None and (before_dir is None or after_dir != before_dir)
    result_files = []
    if after_dir and after_dir.exists() and not any(after_dir.iterdir()):
        settle_loop = QEventLoop()

        def finish_settle_wait() -> None:
            settle_loop.quit()

        def poll_result_files() -> None:
            if after_dir and any(after_dir.iterdir()):
                settle_loop.quit()
                return
            QTimer.singleShot(300, poll_result_files)

        QTimer.singleShot(300, poll_result_files)
        QTimer.singleShot(10000, finish_settle_wait)
        settle_loop.exec()

    if after_dir and after_dir.exists():
        result_files = sorted(p.name for p in after_dir.iterdir() if p.is_file())
    window.results_page.refresh_results()
    gui_current_folder = window.results_page.current_folder
    first_result_path = "NONE"
    if window.results_page.result_table.rowCount() > 0:
        first_item = window.results_page.result_table.item(0, 2)
        if first_item:
            first_result_path = first_item.text()
    gui_folder_matches_new = str(gui_current_folder) == str(after_dir) if gui_current_folder and after_dir else False
    gui_first_path_matches_new = str(after_dir) in first_result_path if after_dir else False
    print(f"preview_has_domain={'example.com' in preview_text}")
    print(f"status_label={window.task_page.status_label.text().encode('unicode_escape').decode('ascii')}")
    print(f"domain_run_timed_out={timeout_triggered['value']}")
    print(f"domain_run_completed={window.task_page.status_label.text() == '已完成'}")
    print(f"result_dir_before={before_dir if before_dir else 'NONE'}")
    print(f"result_dir_after={after_dir if after_dir else 'NONE'}")
    print(f"new_result_dir_created={new_dir_created}")
    print(f"result_file_count={len(result_files)}")
    print(f"has_xlsx_artifact={any(name.endswith('.xlsx') for name in result_files)}")
    print(f"gui_current_folder={gui_current_folder if gui_current_folder else 'NONE'}")
    print(f"gui_folder_matches_new={gui_folder_matches_new}")
    print(f"gui_first_result_path={first_result_path}")
    print(f"gui_first_path_matches_new={gui_first_path_matches_new}")
    if created_fake_dir:
        shutil.rmtree(fake_result_dir, ignore_errors=True)
    success = (
        not timeout_triggered["value"]
        and window.task_page.status_label.text() == "已完成"
        and new_dir_created
        and any(name.endswith('.xlsx') for name in result_files)
        and gui_folder_matches_new
    )
    print(f"success={success}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
