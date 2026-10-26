"""Check a release tag and verified corresponding-source assets before publication."""

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_metadata import VERSION
from scripts.setup_ffmpeg import sha256


def validate(tag, version, policy, assets, *, preview=False):
    if tag != f"v{version}" or not re.fullmatch(r"\d+\.\d+\.\d+(?:-rc\.\d+)?", version):
        raise ValueError("Release tag must match a stable or rc application version; dev builds cannot publish")
    permitted_preview = (preview and "-rc." in version and tag in policy.get("preview_tags", [])
                         and bool(policy.get("preview_notes", "").strip()))
    if preview and not permitted_preview:
        raise ValueError("Preview publication requires an explicitly recorded rc tag")
    if (policy.get("schema_version") != 1 or not policy.get("review_notes", "").strip()
            or policy.get("status") not in ({"reviewed", "pending"} if permitted_preview else {"reviewed"})):
        raise ValueError("Corresponding-source and third-party license review is pending; see tools/release-policy.json")
    required = set(policy["required_components"])
    covered = set()
    archives = policy.get("source_archives", [])
    if not archives and not permitted_preview:
        raise ValueError("No corresponding-source archives supplied")
    for item in archives:
        name = item["file"]
        if Path(name).name != name or "/" in name or "\\" in name or not name.endswith((".zip", ".tar.gz", ".tar.xz")):
            raise ValueError("Source asset must be an archive basename")
        path = assets / name
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(f"Source archive missing or checksum mismatch: {name}")
        covered.update(item["components"])
    if not required or (not permitted_preview and not required <= covered):
        raise ValueError(f"Missing source coverage: {sorted(required - covered)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--assets", type=Path, default=ROOT / "release-sources")
    parser.add_argument("--download-sources", action="store_true")
    parser.add_argument("--preview", action="store_true", help="Publish only an explicitly recorded rc preview; keep audit status unchanged")
    args = parser.parse_args()
    policy = json.loads((ROOT / "tools/release-policy.json").read_text(encoding="utf-8"))
    # Fail before downloading anything when the version or review is incomplete.
    if (args.tag != f"v{VERSION}" or "-dev" in VERSION
            or (policy.get("status") != "reviewed" and not args.preview)):
        raise ValueError("Release version/source review is not ready; see tools/release-policy.json")
    if args.download_sources:
        args.assets.mkdir(parents=True, exist_ok=True)
        for item in policy.get("source_archives", []):
            name, url = item["file"], item["url"]
            parsed = urllib.parse.urlsplit(url)
            if Path(name).name != name or "/" in name or "\\" in name or parsed.scheme != "https" or parsed.username or parsed.password:
                raise ValueError("Source assets require a basename and a public HTTPS URL")
            target = args.assets / name
            if target.exists():
                continue  # validate() will check the existing bytes, never overwrite them.
            with tempfile.NamedTemporaryFile(dir=args.assets, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    with urllib.request.urlopen(url, timeout=60) as response:
                        import shutil
                        shutil.copyfileobj(response, stream)
                except BaseException:
                    stream.close()
                    temporary.unlink(missing_ok=True)
                    raise
            try:
                if sha256(temporary) != item["sha256"]:
                    raise ValueError(f"Downloaded source checksum failed: {name}")
                temporary.rename(target)
            finally:
                temporary.unlink(missing_ok=True)
    validate(args.tag, VERSION, policy, args.assets, preview=args.preview)
    print("Release identity and listed source assets verified; source review status: " + policy["status"])


if __name__ == "__main__":
    main()
