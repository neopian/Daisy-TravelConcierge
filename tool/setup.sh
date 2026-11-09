#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd -- "$PROJECT_ROOT"
./tool/flutter.sh prepare "$@"
if [[ ! -e config/dev.json ]]; then
  cp config/dev.example.json config/dev.json
  printf '\nconfig/dev.json을 만들었습니다. Supabase URL과 공개 클라이언트 키를 입력하세요.\n'
else
  printf '\n기존 config/dev.json을 유지했습니다.\n'
fi
printf '\n준비 완료. 플랫폼 도구 확인: ./tool/flutter.sh doctor -v\n'
printf '앱 실행: ./tool/flutter.sh run --dart-define-from-file=config/dev.json\n'
