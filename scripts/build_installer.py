"""Wrap a verified portable payload in a per-user Windows EXE installer."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_metadata import APP_NAME, VERSION
from scripts.setup_ffmpeg import sha256
from scripts.smoke_portable import extract_verified
from scripts.build_portable import package_files


def build(archive, output_dir, compiler):
    if os.name != "nt":
        raise RuntimeError("Windows is required")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{APP_NAME}-{VERSION}-windows-x64-setup.exe"
    if target.exists():
        raise FileExistsError(f"Preserving existing installer: {target}")
    parent = ROOT / "build/installer"
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="build-", dir=parent))
    extracted = work / "extracted"
    extracted.mkdir()
    payload = extract_verified(archive.resolve(), extracted)
    info = json.loads((payload / "build-info.json").read_text(encoding="utf-8"))
    if info["name"] != APP_NAME or info["version"] != VERSION or info["source_dirty"]:
        raise ValueError("Installer requires a clean portable build with the current identity")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if info["source_commit"] != commit:
        raise ValueError("Installer script and portable payload must use the same commit")
    shutil.copy2(compiler.parent / "license.txt", payload / "licenses/Inno-Setup.txt")
    (payload / "package-manifest.json").write_text(json.dumps(package_files(payload), indent=2), encoding="utf-8")
    with (work / "compiler.log").open("w", encoding="utf-8") as log:
        subprocess.run([str(compiler.resolve()), "/Qp", f"/DPayloadDir={payload}", f"/DAppVersion={VERSION}",
                        f"/DFileVersion={VERSION.split('-')[0]}.0",
                        f"/DOutputDir={work}", str(ROOT / "installer/Imadeoconvert.iss")],
                       check=True, stdout=log, stderr=subprocess.STDOUT, timeout=300)
    generated = work / target.name
    # Both directories are inside the workspace by default. Windows rename refuses an existing target.
    generated.rename(target)
    checksum = sha256(target)
    target.with_name(target.name + ".sha256").write_text(f"{checksum}  {target.name}\n", encoding="ascii")
    report = {"installer": str(target), "sha256": checksum, "size": target.stat().st_size,
              "source_commit": commit, "portable_sha256": sha256(archive), "compiler": "Inno Setup 6.7.3"}
    (output_dir / "installer-build.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--compiler", type=Path, default=ROOT / "tools/innosetup-6.7.3/ISCC.exe")
    args = parser.parse_args()
    build(args.archive, args.output_dir, args.compiler)
