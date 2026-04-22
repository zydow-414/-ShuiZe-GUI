# ShuiZe 水泽 GUI 桌面版

郑重声明：本文档中涉及的技术、思路和工具仅限于合法授权的安全测试、学习研究与防御场景，严禁用于任何非法用途，使用者需自行承担合规与法律责任。

原始项目地址：<https://github.com/zydow-414/-ShuiZe-GUI>

本仓库在原项目基础上补充了 PySide6 图形化桌面界面，用于降低命令参数记忆成本，并将常用运行流程、配置编辑与结果查看整合到同一窗口中。

## 项目概览

当前仓库的核心入口与目录如下：

- `ShuiZe.py`：主入口，支持 `--gui` 启动桌面界面，也保留后端命令行执行能力
- `shuize_gui.py`：PySide6 GUI 主程序
- `Plugins/`：信息收集、资产发现与扫描相关插件
- `iniFile/`：配置文件、字典、规则与辅助资源
- `result/`：任务输出目录
- `tests/gui/`：GUI 回归与联调验证脚本
- `build_gui_exe.py`：Windows GUI 打包脚本
- `scripts/build.sh`：Linux 环境初始化脚本
- `docs/imgs/`：文档图片与界面截图资源

## 当前 GUI 结构

当前桌面界面采用左侧工作台 + 右侧工作区的布局：

### 左侧工作台

1. **扫描设置**
   - 支持以下模式：
     - 根域名扫描
     - 单域名扫描
     - 批量域名文件
     - C 段扫描
     - 文件扫描
     - FOFA 标题
   - 支持常用选项：
     - 内网模式
     - 内网 Web
     - VPN 模式
     - 弱口令检测
     - 仅信息收集
     - 启用 `ksubdomain`
   - 支持代理输入与执行命令预览

2. **运行控制**
   - 开始扫描
   - 停止扫描
   - 清空日志
   - 打开结果根目录
   - 打开最近结果目录
   - 打开最近结果文件

3. **运行日志**
   - 实时展示后端执行输出
   - 任务结束后自动更新状态与结果区

### 右侧工作区

1. **配置管理**
   - 配置项按两个页签分组：
     - `常用配置`
     - `高级参数`
   - 常用配置继续拆分为：
     - `资产 API`
     - `配额与并发`
   - 高级参数用于维护端口、服务映射、关键词等低频项
   - 保存后直接写回 `iniFile/config.ini`

2. **结果列表**
   - 自动扫描 `result/` 下最新任务目录
   - 展示 `.xlsx` 与 `.txt` 产物
   - 支持双击打开结果文件

## 环境准备

建议在项目根目录下安装依赖：

```bash
pip install -r requirements.txt
```

如果需要打包 Windows 可执行文件，还需要安装 `PyInstaller`：

```bash
python -m pip install pyinstaller
```

## 启动方式

### 1. 启动桌面 GUI

在项目根目录执行：

```bash
python ShuiZe.py --gui
```

也可以直接运行：

```bash
python shuize_gui.py
```

### 2. GUI 后端执行说明

GUI 会根据当前运行环境自动选择任务执行方式：

- 非 Windows 或离屏测试环境：优先使用内部进程执行
- 常规 Windows 桌面环境：优先使用外部命令行窗口执行

这样可以同时兼顾桌面使用体验与自动化测试稳定性。

## 常见使用流程

1. 先打开 **配置管理**，填写常用 API 凭证与并发/配额参数
2. 回到 **扫描设置**，选择扫描模式并补充目标参数
3. 按需勾选附加选项，例如仅信息收集、内网模式或弱口令检测
4. 点击 **开始扫描**，在日志区观察执行过程
5. 扫描结束后，在 **结果列表** 中查看最新 `.xlsx` / `.txt` 文件

## 配置文件说明

GUI 读取并写入以下配置文件：

```text
iniFile/config.ini
```

当前 GUI 已覆盖常见配置项，包括但不限于：

- FOFA
- Shodan
- Github
- Quake
- Qianxin
- VirusTotal
- SecurityTrails
- Censys
- C 扫描并发与结果上限
- Web 端口
- 服务端口映射
- Github 关键词

## 结果目录说明

默认结果位于：

```text
result/
```

每次任务通常会生成一个新的子目录，GUI 会自动定位最新目录并刷新表格。

## Windows 打包

执行以下命令：

```bash
python build_gui_exe.py
```

打包完成后，输出目录为：

```text
dist/ShuiZeDesktop/ShuiZeDesktop.exe
```

注意：这是目录打包结果，实际分发时请保留整个 `dist/ShuiZeDesktop/` 目录，不要只单独复制 exe。

## Linux 环境初始化

如需在 Linux 环境快速准备依赖，可执行：

```bash
bash scripts/build.sh
```

该脚本会安装 Python、pip、tmux、项目依赖，并处理 `ksubdomain_linux` 可执行权限。

## GUI 回归测试

当前仓库已经提供多组 GUI 验证脚本，可直接在项目根目录执行：

```bash
python tests/gui/gui_entry_test.py
python tests/gui/gui_direct_entry_test.py
python tests/gui/gui_smoke_test.py
python tests/gui/gui_external_process_test.py
python tests/gui/gui_style_evidence.py
python tests/gui/gui_entry_fullflow_test.py
python tests/gui/gui_launch_mode_check.py
```

各脚本用途如下：

- `tests/gui/gui_entry_test.py`：验证 `python ShuiZe.py --gui` 启动入口
- `tests/gui/gui_direct_entry_test.py`：验证直接运行 `shuize_gui.py`
- `tests/gui/gui_smoke_test.py`：验证 GUI 结构、配置读写、结果刷新与完整执行链路
- `tests/gui/gui_external_process_test.py`：验证外部命令行执行分支
- `tests/gui/gui_style_evidence.py`：验证关键样式与兼容结构未被破坏
- `tests/gui/gui_entry_fullflow_test.py`：验证主入口完整工作流
- `tests/gui/gui_launch_mode_check.py`：验证内部/外部进程模式选择逻辑

## 打包与运行注意事项

- 请尽量从项目根目录启动 GUI，避免相对路径资源加载异常
- 首次运行前建议先检查 `iniFile/config.ini` 中的 API 配置是否完整
- 若结果区为空，先确认任务是否执行完成，以及 `result/` 下是否已生成新目录
- 若在自动化环境下运行 GUI，请设置离屏平台，例如 `QT_QPA_PLATFORM=offscreen`

## 说明

本 README 主要描述当前仓库的桌面 GUI 结构、启动方式、配置管理、结果查看、测试与打包流程；底层扫描逻辑仍由原有命令行主程序与插件体系负责。