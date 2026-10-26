"""Install, exercise and uninstall the EXE in a fresh workspace directory."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import winreg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.setup_ffmpeg import sha256

UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{D9FB8823-266B-4DC7-942B-D838D0E9550A}_is1"


def registration():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY, 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            return winreg.QueryValueEx(key, "InstallLocation")[0]
    except FileNotFoundError:
        return None


def run(installer, report_path):
    installer = installer.resolve()
    expected = installer.with_name(installer.name + ".sha256").read_text().split()[0]
    if sha256(installer) != expected:
        raise ValueError("Installer checksum mismatch")
    if registration() is not None:
        raise RuntimeError("An Imadeoconvert installation exists; preserving it. Run this test in a fresh Windows user account.")
    parent = ROOT / "test-results/installer"
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="安装 installer (test)-", dir=parent)).resolve()
    app = work / "installed app"
    # The only uninstall target is a new directory strictly inside this test workspace.
    if not app.resolve().is_relative_to(parent.resolve()) or app.exists():
        raise ValueError("Unsafe installer smoke directory")
    settings = [Path.home() / name for name in (".imadeoconvert_settings.json", ".imadeocovert_settings.json",
                                               ".formatix_image_converter_settings.json")]
    before = {str(path): sha256(path) if path.exists() else None for path in settings}
    report = {"installer_sha256": expected, "installation": str(app), "success": False, "checks": []}

    def check(name, passed):
        report["checks"].append({"name": name, "passed": bool(passed)})
        if not passed:
            raise AssertionError(name)

    def execute(arguments, timeout=150, **kwargs):
        process = subprocess.run(arguments, timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        if process.returncode != 0:
            raise RuntimeError(f"Process exited {process.returncode}; logs: {work}")

    try:
        execute([str(installer), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/NOICONS",
                 "/TASKS=", "/NOCLOSEAPPLICATIONS", "/NORESTARTAPPLICATIONS", f"/DIR={app}", f"/LOG={work / 'install.log'}"])
        check("per_user_registration", Path(registration() or "").resolve() == app)
        manifest = json.loads((app / "package-manifest.json").read_text(encoding="utf-8"))
        check("installed_payload_integrity", all((app / name).stat().st_size == data["size"]
              and sha256(app / name) == data["sha256"] for name, data in manifest.items()))
        sentinel = app / "user-kept.txt"
        sentinel.write_text("preserve user-created files", encoding="utf-8")
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith(("CONDA", "PYTHON")) and key.upper() not in {"TCL_LIBRARY", "TK_LIBRARY"}}
        windows = Path(env.get("SystemRoot", r"C:\Windows"))
        env["PATH"] = os.pathsep.join(map(str, (windows / "System32", windows)))
        execute([str(app / "Imadeoconvert.exe"), "--self-test", str(work / "self-test")], cwd=work, env=env)
        app_report = json.loads((work / "self-test/report.json").read_text(encoding="utf-8"))
        check("installed_app_self_test", app_report["success"] and app_report["frozen"])
        report["app_checks"] = app_report["checks"]
        report["version"] = app_report["version"]
    finally:
        uninstaller = app / "unins000.exe"
        if uninstaller.exists():
            if Path(registration() or "").resolve() != app:
                raise RuntimeError("Uninstall registration does not match this test directory; preserving files")
            execute([str(uninstaller), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", f"/LOG={work / 'uninstall.log'}"])
            deadline = time.monotonic() + 20
            while (app / "Imadeoconvert.exe").exists() and time.monotonic() < deadline:
                time.sleep(0.1)
        check("uninstalled_application", not (app / "Imadeoconvert.exe").exists())
        check("removed_registration", registration() is None)
        check("preserved_user_file", (app / "user-kept.txt").read_text(encoding="utf-8") == "preserve user-created files")
        check("preserved_settings", before == {str(path): sha256(path) if path.exists() else None for path in settings})
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["success"] = True
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Installer passed {len(report['checks'])} lifecycle checks and {len(report['app_checks'])} app checks: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("installer", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "test-results/installer-smoke.json")
    args = parser.parse_args()
    run(args.installer, args.report)
