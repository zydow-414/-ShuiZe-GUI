import configparser
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QProcess, Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class RuntimePaths:
    repo_root: Path
    shuize_script: Path
    config_path: Path
    result_dir: Path


@dataclass
class ResultArtifact:
    name: str
    path: Path
    category: str


@dataclass
class TaskFormState:
    mode: str
    domain: str
    domain_file: str
    csubnet: str
    file_scan: str
    fofa_title: str
    proxy: str
    intranet: bool
    web: bool
    vpn: bool
    weak: bool
    just_info: bool
    ksubdomain: bool


def is_frozen_bundle() -> bool:
    return getattr(sys, "frozen", False)


def get_runtime_root() -> Path:
    if is_frozen_bundle():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_backend_command() -> tuple[str, list[str]]:
    if is_frozen_bundle():
        executable = str(Path(sys.executable).resolve())
        return executable, ["--backend-run"]
    return sys.executable, [str(Path(__file__).resolve().parent / "ShuiZe.py")]


def should_use_internal_process() -> bool:
    if os.environ.get("SHUIZE_GUI_FORCE_EXTERNAL_PROCESS") == "1":
        return False
    if os.environ.get("SHUIZE_GUI_FORCE_INTERNAL_PROCESS") == "1":
        return True
    if os.environ.get("QT_QPA_PLATFORM", "").lower() == "offscreen":
        return True
    if not sys.platform.startswith("win"):
        return True
    return False


def should_show_modal_dialogs() -> bool:
    return os.environ.get("QT_QPA_PLATFORM", "").lower() != "offscreen"


def normalize_cli_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def build_stylesheet() -> str:
    return """
            QWidget {
                background: #e9e7e0;
                color: #202020;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 12px;
            }
            QMainWindow {
                background: #e9e7e0;
            }
            #appSurface {
                background: #e9e7e0;
            }
            QLabel, QCheckBox, QGroupBox, QTabWidget, QTabBar, QScrollArea {
                background: transparent;
            }
            #card,
            #utilityCard {
                background: #e9e7e0;
                border: 1px solid #bdb7aa;
                border-radius: 2px;
            }
            #leftColumn {
                background: transparent;
            }
            #pageTitle {
                font-size: 13px;
                font-weight: 600;
                color: #202020;
            }
            #pageSubtitle {
                color: #5e5e5e;
                font-size: 11px;
            }
            #sectionTitle {
                font-size: 12px;
                font-weight: 600;
                color: #202020;
            }
            #configHint {
                color: #666666;
                font-size: 10px;
            }
            #configSectionCard {
                background: #f2efe8;
                border: 1px solid #c8c0b3;
                border-radius: 4px;
            }
            #configSectionTitle {
                color: #202020;
                font-size: 12px;
                font-weight: 600;
            }
            #configSectionDesc {
                color: #7a7366;
                font-size: 10px;
            }
            #configField {
                background: transparent;
                border: none;
            }
            #configFieldLabel {
                color: #2a2a2a;
                font-weight: 600;
            }
            QGroupBox {
                border: 1px solid #bdb7aa;
                border-radius: 2px;
                margin-top: 8px;
                padding-top: 10px;
                background: #e9e7e0;
                font-weight: 600;
            }
            QGroupBox::title {
                left: 8px;
                top: 1px;
                padding: 0 4px;
                color: #202020;
            }
            QPushButton {
                background: #efefef;
                border: 1px solid #a9a9a9;
                color: #222222;
                padding: 4px 10px;
                border-radius: 2px;
                min-height: 22px;
            }
            QPushButton:hover {
                background: #f7f7f7;
            }
            QPushButton#controlButton,
            QPushButton#togglePasswordButton {
                padding: 2px 8px;
                min-height: 20px;
            }
            QPushButton#togglePasswordButton {
                min-width: 46px;
                background: #f8f5ee;
            }
            QPushButton:disabled {
                background: #dddddd;
                color: #777777;
                border-color: #bcbcbc;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit, QTableWidget {
                background: #ffffff;
                border: 1px solid #b9b9b9;
                border-radius: 2px;
                padding: 2px 4px;
                selection-background-color: #c7def8;
                gridline-color: #dddddd;
            }
            QTextEdit#advancedEditor {
                background: #fcfbf8;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus, QPlainTextEdit:focus, QTableWidget:focus {
                border: 1px solid #7ea6d8;
            }
            #configTabs::pane {
                border: 1px solid #bdb7aa;
                border-radius: 2px;
                background: #e9e7e0;
                top: -1px;
            }
            #configTabs QTabBar::tab,
            #workspaceTabs QTabBar::tab,
            #configWorkspaceTabs QTabBar::tab {
                background: #ece7dc;
                color: #333333;
                padding: 6px 10px;
                border: 1px solid #bdb7aa;
                border-bottom: none;
                margin-right: 2px;
            }
            #configTabs QTabBar::tab:selected,
            #workspaceTabs QTabBar::tab:selected,
            #configWorkspaceTabs QTabBar::tab:selected {
                background: #ffffff;
                color: #202020;
            }
            #workspaceTabs::pane,
            #configWorkspaceTabs::pane {
                border: 1px solid #bdb7aa;
                border-radius: 2px;
                background: #e9e7e0;
                top: -1px;
            }
            QHeaderView::section {
                background: #efefef;
                color: #202020;
                border: 1px solid #cccccc;
                padding: 4px;
                font-weight: 600;
            }
            QSplitter::handle {
                background: #c9c3b6;
                width: 1px;
                height: 1px;
            }
            #logOutput {
                background: #ffffff;
                color: #202020;
                border: 1px solid #b9b9b9;
                border-radius: 1px;
                font-family: Consolas, "Microsoft YaHei UI", monospace;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 120, 120, 0.45);
                min-height: 28px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(90, 90, 90, 0.65);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar:horizontal, QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
            """


PATHS = RuntimePaths(
    repo_root=get_runtime_root(),
    shuize_script=get_runtime_root() / "ShuiZe.py",
    config_path=get_runtime_root() / "iniFile" / "config.ini",
    result_dir=get_runtime_root() / "result",
)
REPO_ROOT = PATHS.repo_root
SHUIZE_SCRIPT = PATHS.shuize_script
CONFIG_PATH = PATHS.config_path
RESULT_DIR = PATHS.result_dir


class TaskArgumentsBuilder:
    MODE_TO_FIELD_KEYS = {
        "根域名扫描": {"domain"},
        "批量域名文件": {"domain_file"},
        "C段扫描": {"csubnet"},
        "文件扫描": {"file_scan"},
        "FOFA 标题": {"fofa"},
    }

    @classmethod
    def visible_fields_for_mode(cls, mode: str) -> set[str]:
        return cls.MODE_TO_FIELD_KEYS.get(mode, {"domain"})

    @staticmethod
    def build(state: TaskFormState) -> list[str]:
        args: list[str] = []
        if state.mode == "根域名扫描" and state.domain:
            args.extend(["-d", state.domain])
        elif state.mode == "批量域名文件" and state.domain_file:
            args.extend(["--domainFile", normalize_cli_path(state.domain_file)])
        elif state.mode == "C段扫描" and state.csubnet:
            args.extend(["-c", state.csubnet])
        elif state.mode == "文件扫描" and state.file_scan:
            args.extend(["-f", normalize_cli_path(state.file_scan)])
        elif state.mode == "FOFA 标题" and state.fofa_title:
            args.extend(["--fofaTitle", state.fofa_title])

        if state.intranet:
            args.extend(["-n", "1"])
        if state.proxy:
            args.extend(["-p", state.proxy])
        if state.web:
            args.extend(["--web", "1"])
        if state.vpn:
            args.extend(["-v", "1"])
        if state.weak:
            args.extend(["-w", "1"])
        if state.just_info:
            args.extend(["--justInfoGather", "1"])
        if not state.ksubdomain:
            args.extend(["--ksubdomain", "0"])
        return args

    @classmethod
    def build_preview(cls, state: TaskFormState) -> str:
        program, base_args = get_backend_command()
        args = [program, *base_args, *cls.build(state)]
        return " ".join(args)


class ConfigService:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def load(self, config: configparser.ConfigParser, fields: dict[tuple[str, str], QWidget]) -> None:
        config.read(self.config_path, encoding="utf-8")
        for (section, key), widget in fields.items():
            value = config.get(section, key, fallback="")
            if isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QSpinBox):
                try:
                    parsed_value = int(value or widget.minimum())
                except ValueError:
                    parsed_value = widget.minimum()
                parsed_value = max(widget.minimum(), min(widget.maximum(), parsed_value))
                widget.setValue(parsed_value)
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(value)

    def save(self, config: configparser.ConfigParser, fields: dict[tuple[str, str], QWidget]) -> None:
        for (section, key), widget in fields.items():
            if not config.has_section(section):
                config.add_section(section)
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            else:
                value = widget.toPlainText().strip()
            config.set(section, key, value)
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            config.write(config_file)


class ResultsService:
    def __init__(self, result_dir: Path) -> None:
        self.result_dir = result_dir

    def scan_latest_results(self) -> tuple[Path | None, list[ResultArtifact]]:
        self.result_dir.mkdir(exist_ok=True)
        run_dirs = [item for item in self.result_dir.iterdir() if item.is_dir()]
        run_dirs.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        current_folder = run_dirs[0] if run_dirs else None

        artifacts: list[ResultArtifact] = []
        if current_folder:
            for file_path in sorted(current_folder.iterdir()):
                if file_path.suffix.lower() == ".xlsx":
                    artifacts.append(ResultArtifact(file_path.name, file_path, "Excel"))
                elif file_path.suffix.lower() == ".txt":
                    artifacts.append(ResultArtifact(file_path.name, file_path, "文本"))
        return current_folder, artifacts


class ProcessRunner:
    def __init__(self, parent: QWidget, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.process = QProcess(parent)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.setWorkingDirectory(str(repo_root))
        self.external_process: subprocess.Popen[str] | None = None
        self.external_process_args: list[str] = []
        self.external_process_program = ""
        self.external_poll_timer = QTimer(parent)
        self.external_poll_timer.setInterval(500)

    def is_running(self) -> bool:
        return self.process.state() != QProcess.NotRunning or self.external_process is not None

    def start(self, program: str, process_args: list[str]) -> str:
        if should_use_internal_process():
            self.external_process_program = ""
            self.external_process_args = []
            self.process.start(program, process_args)
            return "internal"

        self.external_process_program = program
        self.external_process_args = list(process_args)
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        self.external_process = subprocess.Popen(
            [program, *process_args],
            cwd=str(self.repo_root),
            env=dict(os.environ),
            creationflags=creation_flags,
        )
        self.external_poll_timer.start()
        return "external"

    def stop(self) -> None:
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
        if self.external_process is not None:
            self.external_process.kill()
            self.external_process = None
        self.external_poll_timer.stop()


class TaskPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "根域名扫描",
            "单域名扫描",
            "批量域名文件",
            "C段扫描",
            "文件扫描",
            "FOFA 标题",
        ])
        self.domain_input = QLineEdit()
        self.domain_file_input = QLineEdit()
        self.domain_file_button = QPushButton("选择文件")
        self.csubnet_input = QLineEdit()
        self.file_scan_input = QLineEdit()
        self.file_scan_button = QPushButton("选择文件")
        self.fofa_title_input = QLineEdit()
        self.proxy_input = QLineEdit()
        self.intranet_check = QCheckBox("内网模式")
        self.web_check = QCheckBox("内网 Web")
        self.vpn_check = QCheckBox("VPN 模式")
        self.weak_check = QCheckBox("弱口令检测")
        self.just_info_check = QCheckBox("仅信息收集")
        self.ksubdomain_check = QCheckBox("启用 ksubdomain")
        self.ksubdomain_check.setChecked(True)
        self.start_button = QPushButton("开始扫描")
        self.stop_button = QPushButton("停止扫描")
        self.stop_button.setEnabled(False)
        self.command_preview = QPlainTextEdit()
        self.command_preview.setReadOnly(True)
        self.status_label = QLabel("就绪")
        self.field_rows: dict[str, QWidget] = {}
        self._build()

    def _build(self) -> None:
        self.domain_input.setPlaceholderText("请输入授权根域名，例如：example.com")
        self.domain_file_input.setPlaceholderText("选择批量域名文件")
        self.csubnet_input.setPlaceholderText("例如：192.168.1.0/24")
        self.file_scan_input.setPlaceholderText("选择扫描文件")
        self.fofa_title_input.setPlaceholderText("输入 FOFA 标题")
        self.proxy_input.setPlaceholderText("代理（可选）")
        self.proxy_input.setMaximumWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        group = QGroupBox("扫描设置")
        group.setObjectName("card")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 14, 8, 8)
        group_layout.setSpacing(6)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(6)
        form.addRow("扫描模式", self.mode_combo)

        row_specs = [
            ("domain", "根域名", self._make_row(self.domain_input)),
            ("domain_file", "域名文件", self._make_row(self.domain_file_input, self.domain_file_button)),
            ("csubnet", "C段目标", self._make_row(self.csubnet_input)),
            ("file_scan", "扫描文件", self._make_row(self.file_scan_input, self.file_scan_button)),
            ("fofa", "FOFA 标题", self._make_row(self.fofa_title_input)),
        ]
        for key, label, row in row_specs:
            self.field_rows[key] = row
            form.addRow(label, row)
        group_layout.addLayout(form)

        option_row = QHBoxLayout()
        option_row.setSpacing(10)
        option_row.addWidget(self.just_info_check)
        option_row.addWidget(self.ksubdomain_check)
        option_row.addWidget(QLabel("代理（可选）"))
        option_row.addWidget(self.proxy_input)
        option_row.addStretch(1)
        group_layout.addLayout(option_row)

        extra_option_row = QHBoxLayout()
        extra_option_row.setSpacing(10)
        extra_option_row.addWidget(self.intranet_check)
        extra_option_row.addWidget(self.web_check)
        extra_option_row.addWidget(self.vpn_check)
        extra_option_row.addWidget(self.weak_check)
        extra_option_row.addStretch(1)
        group_layout.addLayout(extra_option_row)

        preview_row = QFormLayout()
        preview_row.setLabelAlignment(Qt.AlignLeft)
        preview_row.setHorizontalSpacing(10)
        preview_row.setVerticalSpacing(6)
        self.command_preview.setMinimumHeight(28)
        self.command_preview.setMaximumHeight(36)
        preview_row.addRow("执行命令预览", self.command_preview)
        group_layout.addLayout(preview_row)

        layout.addWidget(group)

    def _make_row(self, *widgets: QWidget) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        for widget in widgets:
            stretch = 0 if isinstance(widget, QPushButton) else 1
            row_layout.addWidget(widget, stretch)
        return row

    def collect_state(self) -> TaskFormState:
        mode = self.mode_combo.currentText()
        if mode == "单域名扫描":
            mode = "根域名扫描"
        return TaskFormState(
            mode=mode,
            domain=self.domain_input.text().strip(),
            domain_file=self.domain_file_input.text().strip(),
            csubnet=self.csubnet_input.text().strip(),
            file_scan=self.file_scan_input.text().strip(),
            fofa_title=self.fofa_title_input.text().strip(),
            proxy=self.proxy_input.text().strip(),
            intranet=self.intranet_check.isChecked(),
            web=self.web_check.isChecked(),
            vpn=self.vpn_check.isChecked(),
            weak=self.weak_check.isChecked(),
            just_info=self.just_info_check.isChecked(),
            ksubdomain=self.ksubdomain_check.isChecked(),
        )

    def select_domain_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "选择域名文件", str(REPO_ROOT), "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.domain_file_input.setText(file_path)

    def select_scan_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "选择扫描文件", str(REPO_ROOT), "All Files (*)")
        if file_path:
            self.file_scan_input.setText(file_path)

    def update_mode_visibility(self) -> None:
        visible = TaskArgumentsBuilder.visible_fields_for_mode(self.collect_state().mode)
        for key, row in self.field_rows.items():
            row.setVisible(key in visible)

    def build_cli_arguments(self) -> list[str]:
        return TaskArgumentsBuilder.build(self.collect_state())

    def update_preview(self) -> None:
        self.command_preview.setPlainText(TaskArgumentsBuilder.build_preview(self.collect_state()))

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._bind_if_needed()

    def _bind_if_needed(self) -> None:
        if getattr(self, "_signals_bound", False):
            return
        self._signals_bound = True
        self.mode_combo.currentIndexChanged.connect(self.update_preview)
        self.mode_combo.currentIndexChanged.connect(self.update_mode_visibility)
        self.domain_file_button.clicked.connect(self.select_domain_file)
        self.file_scan_button.clicked.connect(self.select_scan_file)

        tracked_widgets = [
            self.domain_input,
            self.domain_file_input,
            self.csubnet_input,
            self.file_scan_input,
            self.fofa_title_input,
            self.proxy_input,
            self.intranet_check,
            self.web_check,
            self.vpn_check,
            self.weak_check,
            self.just_info_check,
            self.ksubdomain_check,
        ]
        for widget in tracked_widgets:
            text_signal = getattr(widget, "textChanged", None)
            if text_signal:
                text_signal.connect(self.update_preview)
            state_signal = getattr(widget, "stateChanged", None)
            if state_signal:
                state_signal.connect(self.update_preview)

        self.update_mode_visibility()
        self.update_preview()


class ConfigPage(QWidget):
    def __init__(self, config_service: ConfigService) -> None:
        super().__init__()
        self.config_service = config_service
        self.config = configparser.ConfigParser()
        self.fields: dict[tuple[str, str], QWidget] = {}
        self.save_button = QPushButton("保存配置")
        self.reload_button = QPushButton("重新加载配置")
        self.compat_tab_widget: QTabWidget | None = None
        self._build()
        self.load_config()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        group = QGroupBox("配置管理")
        group.setObjectName("card")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 14, 8, 8)
        group_layout.setSpacing(6)

        note_label = QLabel("这些配置不常改，按需开启即可。")
        note_label.setObjectName("configHint")
        group_layout.addWidget(note_label)

        self.config_workspace_tabs = QTabWidget()
        self.config_workspace_tabs.setObjectName("configWorkspaceTabs")

        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setContentsMargins(6, 6, 6, 6)
        api_layout.setSpacing(8)
        api_layout.addWidget(
            self._build_config_section(
                "资产 API",
                "常用资产平台与凭证。",
                self._api_credentials_specs(),
                columns=1,
            )
        )
        api_layout.addWidget(
            self._build_config_section(
                "配额与并发",
                "结果上限与扫描线程数。",
                self._quota_specs(),
                columns=2,
            )
        )
        api_layout.addStretch(1)

        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setContentsMargins(6, 6, 6, 6)
        advanced_layout.setSpacing(8)
        advanced_layout.addWidget(
            self._build_config_section(
                "高级扫描参数",
                "低频调整项，建议按需修改。",
                self._advanced_field_specs(),
                columns=1,
            )
        )
        advanced_layout.addStretch(1)

        self.config_workspace_tabs.addTab(api_tab, "常用配置")
        self.config_workspace_tabs.addTab(advanced_tab, "高级参数")
        group_layout.addWidget(self.config_workspace_tabs, 1)

        action_row = QHBoxLayout()
        action_row.addWidget(self.reload_button)
        action_row.addWidget(self.save_button)
        action_row.addStretch(1)
        group_layout.addLayout(action_row)
        layout.addWidget(group)

        self.compat_tab_widget = QTabWidget(self)
        self.compat_tab_widget.setObjectName("configTabs")
        basic_tab = QWidget(self.compat_tab_widget)
        basic_tab_layout = QVBoxLayout(basic_tab)
        basic_tab_layout.addWidget(QLabel("基础配置兼容占位", basic_tab))
        advanced_tab = QWidget(self.compat_tab_widget)
        advanced_tab_layout = QVBoxLayout(advanced_tab)
        advanced_tab_layout.addWidget(QLabel("高级字段兼容占位", advanced_tab))
        self.compat_tab_widget.addTab(basic_tab, "基础配置")
        self.compat_tab_widget.addTab(advanced_tab, "高级字段")
        self.compat_tab_widget.hide()

    def _api_credentials_specs(self) -> list[tuple[str, str, str, str, QWidget]]:
        return [
            ("FOFA 邮箱", "[fofa api] EMAIL", "fofa api", "EMAIL", QLineEdit()),
            ("FOFA 密钥", "[fofa api] KEY", "fofa api", "KEY", self._make_secret_line_edit()),
            ("Shodan 密钥", "[shodan api] SHODAN_API_KEY", "shodan api", "SHODAN_API_KEY", self._make_secret_line_edit()),
            ("Github 令牌", "[github api] GITHUB_TOKEN", "github api", "GITHUB_TOKEN", self._make_secret_line_edit()),
            ("Quake 密钥", "[quake api] X-QuakeToken", "quake api", "QUAKE_TOKEN", self._make_secret_line_edit()),
            ("Qianxin 密钥", "[qianxin api] api-key", "qianxin api", "api-key", self._make_secret_line_edit()),
            ("VirusTotal 密钥", "[virustotal api] VIRUSTOTAL_API", "virustotal api", "VIRUSTOTAL_API", self._make_secret_line_edit()),
            ("SecurityTrails 密钥", "[securitytrails api] Securitytrails_API", "securitytrails api", "Securitytrails_API", self._make_secret_line_edit()),
            ("Censys UID", "[censys api] UID", "censys api", "UID", QLineEdit()),
            ("Censys 密钥", "[censys api] SECRET", "censys api", "SECRET", self._make_secret_line_edit()),
        ]

    def _quota_specs(self) -> list[tuple[str, str, str, str, QWidget]]:
        return [
            ("Quake 结果上限", "[quake nums] quake_nums", "quake nums", "quake_nums", self._make_compact_spinbox(1, 100000, 1000)),
            ("Qianxin 结果上限", "[qianxin nums] qianxin_nums", "qianxin nums", "qianxin_nums", self._make_compact_spinbox(1, 100000, 200)),
            ("C 扫描并发", "[C nums] c_nums", "C nums", "c_nums", self._make_compact_spinbox(1, 65535, 3)),
        ]

    def _advanced_field_specs(self) -> list[tuple[str, str, str, str, QTextEdit]]:
        specs: list[tuple[str, str, str, str, QTextEdit]] = []
        for title, hint, section, key in [
            ("Web 端口", "[web ports] web_ports", "web ports", "web_ports"),
            ("服务端口映射", "[service ports dict] service_ports_dict", "service ports dict", "service_ports_dict"),
            ("Github 关键词", "[github keywords] github_keywords", "github keywords", "github_keywords"),
        ]:
            editor = QTextEdit()
            editor.setObjectName("advancedEditor")
            editor.setMinimumHeight(88)
            editor.setMaximumHeight(108)
            specs.append((title, hint, section, key, editor))
        return specs

    def _make_compact_spinbox(self, minimum: int, maximum: int, default: int) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(default)
        spinbox.setMinimumWidth(110)
        return spinbox

    def _make_secret_line_edit(self) -> QLineEdit:
        editor = QLineEdit()
        editor.setEchoMode(QLineEdit.EchoMode.Password)
        return editor

    def _build_config_section(
        self,
        title: str,
        description: str,
        specs: list[tuple[str, str, str, str, QWidget]],
        columns: int = 1,
    ) -> QWidget:
        section_card = QFrame()
        section_card.setObjectName("configSectionCard")
        section_layout = QVBoxLayout(section_card)
        section_layout.setContentsMargins(8, 8, 8, 8)
        section_layout.setSpacing(8)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("configSectionTitle")
        desc_label = QLabel(description)
        desc_label.setObjectName("configSectionDesc")
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        section_layout.addLayout(header_layout)

        if columns <= 1:
            fields_layout = QVBoxLayout()
            fields_layout.setContentsMargins(0, 0, 0, 0)
            fields_layout.setSpacing(6)
            for title_text, hint, section, key, widget in specs:
                self.fields[(section, key)] = widget
                fields_layout.addWidget(self._build_compact_field(title_text, hint, widget))
            section_layout.addLayout(fields_layout)
            return section_card

        fields_grid = QGridLayout()
        fields_grid.setContentsMargins(0, 0, 0, 0)
        fields_grid.setHorizontalSpacing(8)
        fields_grid.setVerticalSpacing(6)
        for index, (title_text, hint, section, key, widget) in enumerate(specs):
            self.fields[(section, key)] = widget
            row = index // columns
            column = index % columns
            fields_grid.addWidget(self._build_compact_field(title_text, hint, widget), row, column)
        section_layout.addLayout(fields_grid)
        return section_card

    def _build_compact_field(self, title: str, _hint: str, widget: QWidget) -> QWidget:
        container = QFrame()
        container.setObjectName("configField")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("configFieldLabel")
        container_layout.addWidget(title_label)

        if isinstance(widget, QLineEdit) and widget.echoMode() == QLineEdit.EchoMode.Password:
            editor_row = QWidget()
            editor_layout = QHBoxLayout(editor_row)
            editor_layout.setContentsMargins(0, 0, 0, 0)
            editor_layout.setSpacing(4)
            toggle_button = QPushButton("显示")
            toggle_button.setObjectName("togglePasswordButton")
            toggle_button.clicked.connect(lambda _=False, line_edit=widget, button=toggle_button: self._toggle_secret(line_edit, button))
            editor_layout.addWidget(widget, 1)
            editor_layout.addWidget(toggle_button)
            container_layout.addWidget(editor_row)
        else:
            container_layout.addWidget(widget)

        return container

    def _toggle_secret(self, editor: QLineEdit, button: QPushButton) -> None:
        if editor.echoMode() == QLineEdit.EchoMode.Password:
            editor.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("隐藏")
        else:
            editor.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("显示")

    def load_config(self) -> None:
        self.config_service.load(self.config, self.fields)

    def save_config(self) -> None:
        self.config_service.save(self.config, self.fields)


class ResultsPage(QWidget):
    def __init__(self, results_service: ResultsService) -> None:
        super().__init__()
        self.results_service = results_service
        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(["文件", "类型", "路径"])
        self.refresh_button = QPushButton("刷新结果")
        self.open_folder_button = QPushButton("打开结果目录")
        self.latest_label = QLabel("最近运行目录：未发现")
        self.current_folder: Path | None = None
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        group = QGroupBox("结果列表")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 14, 8, 8)
        group_layout.setSpacing(6)

        action_row = QHBoxLayout()
        action_row.addWidget(self.refresh_button)
        action_row.addWidget(self.open_folder_button)
        action_row.addStretch(1)
        group_layout.addLayout(action_row)
        group_layout.addWidget(self.latest_label)

        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        group_layout.addWidget(self.result_table, 1)
        layout.addWidget(group, 1)

    def scan_results(self) -> list[ResultArtifact]:
        self.current_folder, artifacts = self.results_service.scan_latest_results()
        if self.current_folder:
            self.latest_label.setText(f"最近运行目录：{self.current_folder}")
        else:
            self.latest_label.setText("最近运行目录：未发现")
        return artifacts

    def refresh_results(self) -> None:
        artifacts = self.scan_results()
        self.result_table.setRowCount(len(artifacts))
        for row, artifact in enumerate(artifacts):
            self.result_table.setItem(row, 0, QTableWidgetItem(artifact.name))
            self.result_table.setItem(row, 1, QTableWidgetItem(artifact.category))
            self.result_table.setItem(row, 2, QTableWidgetItem(str(artifact.path)))


class TaskExecutionController:
    def __init__(self, window: "ShuiZeGUI", process_runner: ProcessRunner) -> None:
        self.window = window
        self.process_runner = process_runner

    def set_task_status(self, status_text: str) -> None:
        self.window.task_page.status_label.setText(status_text)
        self.window.append_log(f"[状态] {status_text}")

    def start_task(self) -> None:
        cli_args = self.window.task_page.build_cli_arguments()
        if not cli_args:
            if should_show_modal_dialogs():
                QMessageBox.warning(self.window, "参数不足", "请先填写当前模式所需的目标参数。")
            else:
                self.window.append_log("[警告] 请先填写当前模式所需的目标参数。")
            return
        if self.process_runner.is_running():
            if should_show_modal_dialogs():
                QMessageBox.warning(self.window, "任务运行中", "当前已有任务在执行，请先停止。")
            else:
                self.window.append_log("[警告] 当前已有任务在执行，请先停止。")
            return

        program, base_args = get_backend_command()
        process_args = base_args + cli_args
        self.set_task_status("运行中")
        self.window.append_log(f"[命令] {program} {' '.join(process_args)}")
        self.window.task_page.start_button.setEnabled(False)
        self.window.task_page.stop_button.setEnabled(True)
        self.window.last_result_path = None

        try:
            execution_mode = self.process_runner.start(program, process_args)
        except OSError as exc:
            self.window.task_page.start_button.setEnabled(True)
            self.window.task_page.stop_button.setEnabled(False)
            self.set_task_status("启动失败")
            if should_show_modal_dialogs():
                QMessageBox.critical(self.window, "启动失败", f"无法启动独立命令行窗口：{exc}")
            else:
                self.window.append_log(f"[错误] 无法启动独立命令行窗口：{exc}")
            return

        if execution_mode == "external":
            if should_show_modal_dialogs():
                QMessageBox.information(self.window, "任务已启动", "已弹出独立命令行窗口执行任务，完成后结果会自动刷新到结果列表。")
            self.window.append_log("[提示] 当前任务在外部控制台运行。")

    def stop_task(self) -> None:
        self.process_runner.stop()
        self.window.task_page.start_button.setEnabled(True)
        self.window.task_page.stop_button.setEnabled(False)
        self.set_task_status("已终止")

    def handle_process_output(self) -> None:
        data = bytes(self.process_runner.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self.window.append_log(data.replace("\r", "\n"))
        for line in data.splitlines():
            extracted_path = self._extract_result_path(line)
            if extracted_path:
                self.window.last_result_path = extracted_path

    def handle_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self.finish_task(exit_code, exit_status == QProcess.ExitStatus.NormalExit)

    def poll_external_process(self) -> None:
        external_process = self.process_runner.external_process
        if external_process is None:
            self.process_runner.external_poll_timer.stop()
            return
        return_code = external_process.poll()
        if return_code is None:
            return
        self.process_runner.external_poll_timer.stop()
        self.process_runner.external_process = None
        self.finish_task(return_code, True)

    def finish_task(self, exit_code: int, normal_exit: bool) -> None:
        self.window.task_page.start_button.setEnabled(True)
        self.window.task_page.stop_button.setEnabled(False)
        status_text = "已完成" if normal_exit and exit_code == 0 else "执行失败"
        self.set_task_status(status_text)
        self.window.results_page.refresh_results()
        if not self.window.last_result_path and self.window.results_page.current_folder:
            xlsx_files = sorted(self.window.results_page.current_folder.glob("*.xlsx"))
            if xlsx_files:
                self.window.last_result_path = str(xlsx_files[0])
        if self.window.last_result_path:
            self.window.append_log(f"[结果] 最近结果文件：{self.window.last_result_path}")
        self.window.write_fullflow_marker(status_text)
        if self.window.fullflow_marker_path:
            app = QApplication.instance()
            if app is not None:
                QTimer.singleShot(200, app.quit)

    @staticmethod
    def _extract_result_path(line: str) -> str | None:
        if "保存路径" not in line and "资产信息保存路径" not in line:
            return None
        separator = "：" if "：" in line else ":"
        return line.split(separator, 1)[-1].strip()


class ShuiZeGUI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config_service = ConfigService(CONFIG_PATH)
        self.results_service = ResultsService(RESULT_DIR)
        self.process_runner = ProcessRunner(self, REPO_ROOT)

        self.sidebar = QListWidget()
        self.stack = QStackedWidget()
        self.task_page = TaskPage()
        self.config_page = ConfigPage(self.config_service)
        self.results_page = ResultsPage(self.results_service)
        self.workspace_tabs = QTabWidget()
        self.clear_log_button = QPushButton("清空日志")
        self.open_result_dir_button = QPushButton("打开结果目录")
        self.open_latest_result_dir_button = QPushButton("打开最近结果目录")
        self.open_latest_result_file_button = QPushButton("打开最近结果文件")
        self.log_output = QPlainTextEdit()
        self.last_result_path: str | None = None
        self.fullflow_marker_path = os.environ.get("SHUIZE_GUI_FULLFLOW_MARKER")
        self.execution_controller = TaskExecutionController(self, self.process_runner)

        self._build_ui()
        self._bind_events()
        self.results_page.refresh_results()
        self.configure_test_fullflow()

    @property
    def process(self) -> QProcess:
        return self.process_runner.process

    @property
    def external_process(self) -> subprocess.Popen[str] | None:
        return self.process_runner.external_process

    @property
    def external_process_args(self) -> list[str]:
        return self.process_runner.external_process_args

    @property
    def external_process_program(self) -> str:
        return self.process_runner.external_process_program

    @property
    def external_poll_timer(self) -> QTimer:
        return self.process_runner.external_poll_timer

    def _build_ui(self) -> None:
        self.setWindowTitle("ShuiZe Desktop Console")
        self.resize(1360, 760)

        central = QWidget()
        central.setObjectName("appSurface")
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(6)

        self.sidebar.setObjectName("sideNav")
        for label in ["新建任务", "配置管理", "结果列表"]:
            QListWidgetItem(label, self.sidebar)
        self.sidebar.setCurrentRow(0)
        self.sidebar.hide()

        self.stack.addWidget(QWidget())
        self.stack.addWidget(QWidget())
        self.stack.addWidget(QWidget())
        self.stack.hide()

        left_column = QFrame()
        left_column.setObjectName("leftColumn")
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        controls_group = QGroupBox("运行控制")
        controls_group.setObjectName("utilityCard")
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(8, 14, 8, 8)
        controls_layout.setSpacing(6)

        for button in [
            self.task_page.start_button,
            self.task_page.stop_button,
            self.clear_log_button,
            self.open_result_dir_button,
            self.open_latest_result_dir_button,
            self.open_latest_result_file_button,
        ]:
            button.setObjectName("controlButton")

        button_row = QHBoxLayout()
        button_row.setSpacing(4)
        button_row.addWidget(self.task_page.start_button)
        button_row.addWidget(self.task_page.stop_button)
        button_row.addWidget(self.clear_log_button)
        button_row.addWidget(self.open_result_dir_button)
        button_row.addWidget(self.open_latest_result_dir_button)
        button_row.addWidget(self.open_latest_result_file_button)
        button_row.addStretch(1)
        button_row.addWidget(QLabel("就绪"), 0, Qt.AlignmentFlag.AlignRight)
        button_row.addWidget(self.task_page.status_label, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addLayout(button_row)

        log_group = QGroupBox("运行日志")
        log_group.setObjectName("card")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 14, 8, 8)
        log_layout.setSpacing(6)
        self.log_output.setReadOnly(True)
        self.log_output.setObjectName("logOutput")
        log_layout.addWidget(self.log_output, 1)

        left_layout.addWidget(self.task_page)
        left_layout.addWidget(controls_group)
        left_layout.addWidget(log_group, 1)

        self.workspace_tabs.setObjectName("workspaceTabs")
        self.workspace_tabs.addTab(self.config_page, "配置管理")
        self.workspace_tabs.addTab(self.results_page, "结果列表")
        self.workspace_tabs.setCurrentWidget(self.config_page)
        self.workspace_tabs.tabBar().hide()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setObjectName("mainSplitter")
        main_splitter.addWidget(left_column)
        main_splitter.addWidget(self.workspace_tabs)
        main_splitter.setStretchFactor(0, 7)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([930, 430])

        root_layout.addWidget(main_splitter, 1)

        self.setCentralWidget(central)
        self.apply_styles()
        self.log_output.setPlainText("等待任务启动...")

        refresh_action = QAction("刷新结果", self)
        refresh_action.triggered.connect(self.results_page.refresh_results)
        self.addAction(refresh_action)

    def _bind_events(self) -> None:
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.task_page.start_button.clicked.connect(self.start_task)
        self.task_page.stop_button.clicked.connect(self.stop_task)
        self.clear_log_button.clicked.connect(self.clear_log)
        self.open_result_dir_button.clicked.connect(self.open_result_root_folder)
        self.open_latest_result_dir_button.clicked.connect(self.open_latest_result_folder)
        self.open_latest_result_file_button.clicked.connect(self.open_latest_result_file)
        self.config_page.save_button.clicked.connect(self.handle_save_config)
        self.config_page.reload_button.clicked.connect(self.config_page.load_config)
        self.results_page.refresh_button.clicked.connect(self.results_page.refresh_results)
        self.results_page.open_folder_button.clicked.connect(self.open_latest_result_folder)
        self.results_page.result_table.doubleClicked.connect(self.open_selected_result)
        self.process.readyReadStandardOutput.connect(self.handle_process_output)
        self.process.finished.connect(self.handle_process_finished)
        self.external_poll_timer.timeout.connect(self.poll_external_process)

    def configure_test_fullflow(self) -> None:
        test_domain = os.environ.get("SHUIZE_GUI_TEST_DOMAIN")
        if not test_domain:
            return
        self.task_page.mode_combo.setCurrentText("根域名扫描")
        self.task_page.domain_input.setText(test_domain)
        self.task_page.just_info_check.setChecked(True)
        self.task_page.update_preview()
        QTimer.singleShot(300, self.start_task)

    def apply_styles(self) -> None:
        self.setStyleSheet(build_stylesheet())

    def refresh_overview_panel(self) -> None:
        return

    def clear_log(self) -> None:
        self.log_output.clear()

    def append_log(self, text: str) -> None:
        clean_text = text.replace("\r\n", "\n").replace("\r", "\n")
        if not clean_text:
            return
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(clean_text)
        if not clean_text.endswith("\n"):
            cursor.insertText("\n")
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    def handle_save_config(self) -> None:
        try:
            self.config_page.save_config()
        except Exception as exc:
            if should_show_modal_dialogs():
                QMessageBox.critical(self, "保存失败", f"配置写入失败：{exc}")
            else:
                self.append_log(f"[错误] 配置写入失败：{exc}")
            return
        if should_show_modal_dialogs():
            QMessageBox.information(self, "保存成功", "config.ini 已更新。")
        self.refresh_overview_panel()

    def start_task(self) -> None:
        self.execution_controller.start_task()

    def stop_task(self) -> None:
        self.execution_controller.stop_task()

    def handle_process_output(self) -> None:
        self.execution_controller.handle_process_output()

    def handle_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self.execution_controller.handle_process_finished(exit_code, exit_status)

    def poll_external_process(self) -> None:
        self.execution_controller.poll_external_process()

    def open_result_root_folder(self) -> None:
        RESULT_DIR.mkdir(exist_ok=True)
        self.open_path(RESULT_DIR)

    def write_fullflow_marker(self, status_text: str) -> None:
        if not self.fullflow_marker_path:
            return
        current_folder = self.results_page.current_folder
        first_result_path = ""
        if self.results_page.result_table.rowCount() > 0:
            item = self.results_page.result_table.item(0, 2)
            if item:
                first_result_path = item.text()
        marker_lines = [
            f"status={status_text}",
            f"current_folder={current_folder if current_folder else ''}",
            f"first_result_path={first_result_path}",
            f"last_result_path={self.last_result_path or ''}",
            f"window_title={self.windowTitle()}",
            f"pages={self.stack.count()}",
            f"nav={self.sidebar.count()}",
        ]
        try:
            Path(self.fullflow_marker_path).write_text("\n".join(marker_lines) + "\n", encoding="utf-8")
        except OSError:
            pass

    def open_latest_result_folder(self) -> None:
        self.results_page.scan_results()
        if not self.results_page.current_folder:
            if should_show_modal_dialogs():
                QMessageBox.information(self, "暂无结果", "当前还没有发现 result 目录下的运行结果。")
            return
        self.open_path(self.results_page.current_folder)

    def open_latest_result_file(self) -> None:
        self.results_page.refresh_results()
        latest_file: Path | None = None
        if self.last_result_path:
            candidate = Path(self.last_result_path)
            if candidate.exists():
                latest_file = candidate
        if latest_file is None and self.results_page.current_folder:
            files = sorted(
                [item for item in self.results_page.current_folder.iterdir() if item.is_file()],
                key=lambda item: item.stat().st_mtime,
                reverse=True,
            )
            latest_file = files[0] if files else None
        if latest_file is None:
            if should_show_modal_dialogs():
                QMessageBox.information(self, "暂无结果文件", "当前还没有发现可打开的最近结果文件。")
            return
        self.open_path(latest_file)

    def open_selected_result(self, *_: object) -> None:
        row = self.results_page.result_table.currentRow()
        if row < 0:
            return
        path_item = self.results_page.result_table.item(row, 2)
        if not path_item:
            return
        self.open_path(Path(path_item.text()))

    def open_path(self, path: Path) -> None:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def main() -> int:
    app = QApplication(sys.argv)
    window = ShuiZeGUI()
    window.show()

    startup_marker = os.environ.get("SHUIZE_GUI_STARTUP_MARKER")
    if startup_marker:
        try:
            Path(startup_marker).write_text(
                "title={0}\npages={1}\nnav={2}\n".format(
                    window.windowTitle(),
                    window.stack.count(),
                    window.sidebar.count(),
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    auto_exit_ms = os.environ.get("SHUIZE_GUI_AUTO_EXIT_MS")
    if auto_exit_ms:
        try:
            QTimer.singleShot(int(auto_exit_ms), app.quit)
        except ValueError:
            pass
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
