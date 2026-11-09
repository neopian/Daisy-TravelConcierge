# 개발 환경 복구 검증

## 고정 환경

- Flutter 3.32.8 / Dart 3.8.1, SDK 커밋은 `tool/flutter-sdk.json`에 고정합니다.
- Dart 패키지는 `pubspec.lock`, iOS Pods는 `ios/Podfile.lock`으로 관리합니다.
- Android는 Gradle 8.12 / AGP 8.7.3 / NDK 27.0.12077973을 사용합니다.
- iOS 앱과 Pods의 최소 배포 대상은 15.0입니다.
- 새 clone의 준비 진입점은 `./tool/setup.sh`입니다.

## 2026-11-09 검증 결과

macOS 27.2 / Apple Silicon / Xcode 27.2 / CocoaPods 1.16.2 / JDK 21에서 확인했습니다.
Android SDK와 Apple 도구는 이미 설치된 환경을 사용했습니다. Gradle 및 CocoaPods의
공용 캐시는 재사용했으므로 운영체제 전체를 새로 설치한 검증은 아닙니다.

커밋된 저장소를 `git clone --no-hardlinks`로 임시 폴더에 복제했습니다. 처음에는
`.tools/`, `.dart_tool/`, `build/`, `android/local.properties`,
`ios/Flutter/Generated.xcconfig`, `config/dev.json`이 없는 것을 확인했습니다.
검증용 폴더 이름에는 한글과 공백을 포함했습니다.

| 확인 항목 | 결과 |
| --- | --- |
| SDK가 이미 있는 환경 | 고정 커밋의 SDK를 선택하고 오프라인 준비 성공 |
| SDK 첫 설치 | 설치 함수로 공식 저장소의 3.32.8 태그를 새 캐시에 내려받고 정확한 커밋 확인 |
| 새 SDK의 초기 실행 | 새 clone에서 새 SDK를 지정해 Dart·엔진 아티팩트 다운로드와 준비 성공 |
| Dart 패키지 복구 | 빈 `PUB_CACHE`에서 `--enforce-lockfile` 설치 성공, `pubspec.lock` 변경 없음 |
| SDK 복구 테스트 | 7개 통과: 잘못된 SDK 거부, 오프라인 처리, 설치 커밋 검증, 기존 경로 보호, 폴더 이동 |
| 정적 분석 | 문제 없음 |
| Flutter 테스트 | 6개 통과 |
| 웹 빌드 | `build web --no-pub` 성공 |
| iOS 시뮬레이터 | `build ios --simulator --debug --no-pub` 성공 |
| Android 개발 APK | NDK 요구 버전을 명시한 뒤 `build apk --debug --no-pub` 성공, NDK 불일치 경고 해소 |
| 준비 재실행 | 기존 `config/dev.json`의 바이트가 그대로 보존됨 |
| 폴더 이동 | 폴더 이름 변경 후 `analyze --no-pub` 실행 시 생성 경로 자동 복구 및 분석 성공 |
| Git 상태 | 복구·빌드·이동 후 추적 파일 변경 없음. 키 파일과 생성 설정은 Git에서 제외됨 |

iOS 15 설정으로 배포 대상 불일치를 해결했고, Debug 시뮬레이터를 현재 Mac의
아키텍처로 빌드하도록 지정해 Xcode 27의 다중 아키텍처 검사 문제를 피했습니다.
iOS와 Android에서 앱의 최소 지원 버전이나 서명 설정을 바꿀 때는 별도 검증이 필요합니다.

## 별도 준비·확인이 필요한 범위

- Supabase URL과 공개 클라이언트 키는 직접 입력해야 합니다. 실제 로그인, DB 접근,
  Storage 업로드와 Realtime 동작은 이번 복구 검증에서 확인하지 않았습니다.
- 새 Supabase의 초기화 순서는 [DB 준비 안내](../supabase/README.md)에 정리했습니다.
  외부 DB 변경과 테스트 계정 생성은 실행하지 않았습니다.
- iOS 실기기 설치·서명·배포와 Android 스토어 배포 서명은 검증하지 않았습니다.
- Linux, Windows, macOS 데스크톱 앱 빌드 및 기존 수동 GitHub Actions 워크플로는
  이번 로컬 복구 검증에 포함하지 않았습니다.
