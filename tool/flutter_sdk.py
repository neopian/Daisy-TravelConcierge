#!/usr/bin/env python3
"""Resolve the pinned SDK without changing the user's global Flutter installation."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def revision(sdk):
    if not (sdk / "bin/flutter").is_file():
        return None
    result = subprocess.run(
        ["git", "-C", str(sdk), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def sdk_from_command(command):
    executable = shutil.which(command)
    return Path(executable).resolve().parent.parent if executable else None


def candidates(root, cache, version):
    yield root / ".tools/flutter"
    yield cache / version
    for filename, key in [
        (root / "android/local.properties", "flutter.sdk="),
        (root / "ios/Flutter/Generated.xcconfig", "FLUTTER_ROOT="),
    ]:
        if filename.is_file():
            for line in filename.read_text().splitlines():
                if line.startswith(key):
                    yield Path(line[len(key):])
    path_sdk = sdk_from_command("flutter")
    if path_sdk:
        yield path_sdk
    yield Path.home() / ".local/share/flutter" / version
    for cellar in [Path("/opt/homebrew/Caskroom/flutter"), Path("/usr/local/Caskroom/flutter")]:
        if cellar.is_dir():
            yield from sorted(cellar.glob("*/flutter"))


def install_sdk(spec, cache):
    destination = cache / spec["version"]
    if destination.exists():
        raise RuntimeError(f"SDK 캐시의 커밋이 다릅니다. 내용을 확인하거나 FLUTTER_SDK_CACHE를 바꾸세요: {destination}")
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".install-", dir=cache) as temporary:
        checkout = Path(temporary) / "flutter"
        print(f"Flutter {spec['version']} SDK를 준비합니다.", file=sys.stderr)
        subprocess.run([
            "git", "clone", "--depth", "1", "--single-branch", "--branch",
            spec["version"], spec["repository"], str(checkout),
        ], check=True, stdout=sys.stderr)
        if revision(checkout) != spec["revision"]:
            raise RuntimeError("다운로드한 Flutter SDK가 고정된 커밋과 일치하지 않습니다.")
        # A second setup may have finished while this one was downloading.
        if destination.exists():
            if revision(destination) != spec["revision"]:
                raise RuntimeError("다른 설치 작업이 만든 SDK의 커밋이 일치하지 않습니다.")
        else:
            checkout.rename(destination)
    return destination.resolve()


def resolve_sdk(root, spec, cache):
    explicit = os.environ.get("FLUTTER_BIN")
    if explicit:
        selected = sdk_from_command(explicit)
        if selected is None or revision(selected) != spec["revision"]:
            raise RuntimeError(f"FLUTTER_BIN은 Flutter {spec['version']} ({spec['revision'][:10]}) 실행 파일이어야 합니다.")
        return selected
    for candidate in candidates(root, cache, spec["version"]):
        if revision(candidate) == spec["revision"]:
            return candidate.resolve()
    if os.environ.get("CONCIERGE_OFFLINE") == "1":
        raise RuntimeError("고정된 Flutter SDK가 없습니다. 온라인에서 setup.sh를 실행하거나 FLUTTER_BIN을 지정하세요.")
    return install_sdk(spec, cache)


def link_sdk(root, sdk):
    tools = root / ".tools"
    tools.mkdir(exist_ok=True)
    link = tools / "flutter"
    if link.is_symlink():
        if link.resolve() == sdk:
            return
        link.unlink()
    elif link.exists():
        raise RuntimeError(f"SDK 연결 위치에 일반 파일 또는 폴더가 있습니다. 덮어쓰지 않았습니다: {link}")
    link.symlink_to(sdk, target_is_directory=True)


def main():
    if not shutil.which("git"):
        raise RuntimeError("먼저 Git을 설치하세요.")
    spec = json.loads((ROOT / "tool/flutter-sdk.json").read_text())
    cache = Path(os.environ.get(
        "FLUTTER_SDK_CACHE",
        str(Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "local-qa-concierge/flutter"),
    )).expanduser().resolve()
    sdk = resolve_sdk(ROOT, spec, cache)
    link_sdk(ROOT, sdk)
    print(sdk / "bin/flutter")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Flutter 준비 실패: {error}", file=sys.stderr)
        sys.exit(1)
