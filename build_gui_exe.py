import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"
SPEC_PATH = REPO_ROOT / "ShuiZeDesktop.spec"


def format_data_arg(path: Path) -> str:
    return f"{path};{path.name}"


def main() -> int:
    if shutil.which("pyinstaller") is None:
        print("PyInstaller 未安装，请先执行: python -m pip install pyinstaller")
        return 1

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "ShuiZeDesktop",
        "--add-data",
        format_data_arg(REPO_ROOT / "iniFile"),
        "--add-data",
        format_data_arg(REPO_ROOT / "Plugins"),
        "--add-data",
        format_data_arg(REPO_ROOT / "result"),
        "--collect-submodules",
        "PySide6",
        "--collect-data",
        "PySide6",
        "ShuiZe.py",
    ]

    result = subprocess.run(command, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        return result.returncode

    exe_path = DIST_DIR / "ShuiZeDesktop" / "ShuiZeDesktop.exe"
    print(f"exe_path={exe_path}")
    print(f"spec_path={SPEC_PATH}")
    print(f"build_dir={BUILD_DIR}")
    return 0 if exe_path.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
