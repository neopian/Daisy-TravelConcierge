#!/usr/bin/env bash
set -euo pipefail

# Resolve the project before changing directories; the checkout name is unrestricted.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
if ! command -v python3 >/dev/null || ! command -v git >/dev/null; then
  printf '먼저 Python 3와 Git을 설치하세요.\n' >&2
  exit 1
fi
for argument in "$@"; do
  [[ "$argument" != --offline ]] || export CONCIERGE_OFFLINE=1
done
FLUTTER_EXECUTABLE="$(python3 "$PROJECT_ROOT/tool/flutter_sdk.py")"
export PATH="$(dirname -- "$FLUTTER_EXECUTABLE"):$PATH"
cd -- "$PROJECT_ROOT"

LOCATION_FILE=.dart_tool/project-location
CURRENT_LOCATION="$(printf '%s\n%s' "$PROJECT_ROOT" "$FLUTTER_EXECUTABLE")"

prepare_project() {
  # Flutter-generated paths and native build caches belong to the previous location.
  # Keep pubspec.lock and all application/source configuration intact.
  "$FLUTTER_EXECUTABLE" clean
  "$FLUTTER_EXECUTABLE" pub get --enforce-lockfile "$@"
  mkdir -p .dart_tool
  printf '%s\n' "$CURRENT_LOCATION" > "$LOCATION_FILE"
}

case "${1:-}" in
  prepare)
    shift
    prepare_project "$@"
    exit 0
    ;;
  run|build|test|analyze|drive|attach|install|gen-l10n)
    if [[ ! -f .dart_tool/package_config.json || ! -f "$LOCATION_FILE" ]] ||
       [[ "$(cat "$LOCATION_FILE")" != "$CURRENT_LOCATION" ]]; then
      printf '현재 프로젝트 위치에 맞게 Flutter 빌드 환경을 준비합니다.\n'
      prepare_project
    fi
    ;;
  "")
    printf '사용법: %s prepare [pub get 옵션] | <Flutter 명령과 옵션>\n' "$0"
    exit 0
    ;;
esac

exec "$FLUTTER_EXECUTABLE" "$@"
