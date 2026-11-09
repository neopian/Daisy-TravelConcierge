# 지역 기반 1:1 유료 Q&A 컨시어지 MVP

Flutter, Riverpod, GoRouter, Supabase로 만든 모바일 우선 MVP입니다.

## 포함된 범위

- 이메일 회원가입/로그인, 사용자 프로필과 개발용 mock 포인트
- 질문 등록·목록·상세·댓글과 Supabase Storage 이미지 업로드
- 답변자 신청, 관리자 승인·거절과 승인 답변자의 1:1 질문 수락
- 근거 URL이 포함된 답변, 질문자의 답변 채택과 mock 포인트 보상
- 포인트 거래 내역과 질문·답변·댓글의 실시간 갱신

## clone 후 개발 환경 준비

준비 스크립트는 macOS 또는 Linux의 Bash, Python 3.9 이상, Git, curl, unzip과
인터넷 연결을 사용합니다. Flutter는 다른 프로젝트의 전역 설정을 바꾸지 않고
준비합니다. 실제 복구 검증은 macOS에서 수행했습니다.

```bash
git clone https://github.com/neopian/DaisyOne-Malaga.git local-qa-concierge
cd local-qa-concierge
./tool/setup.sh
```

clone 대상 폴더명은 자유롭게 정할 수 있습니다. 스크립트는 자신의 위치에서
프로젝트를 찾으며, 준비 명령을 다시 실행해도 기존 `config/dev.json`을 보존합니다.

1. [SDK 고정 파일](tool/flutter-sdk.json)의 **Flutter 3.32.8 / Dart 3.8.1**을 찾습니다.
   설치된 SDK의 실제 Git 커밋까지 확인하고, PATH에 다른 버전이 있어도 선택하지 않습니다.
2. 맞는 SDK가 없으면 Flutter 공식 Git 저장소의 고정 태그를 내려받아 커밋을 확인합니다.
   기본 설치 위치는 `~/.cache/local-qa-concierge/flutter/3.32.8`이며,
   `FLUTTER_SDK_CACHE`로 캐시 상위 경로를 지정할 수 있습니다.
3. `flutter clean`과 `flutter pub get --enforce-lockfile`로 생성 설정을 준비합니다.
   앱 의존성은 `pubspec.lock`의 버전을 유지합니다.
4. `config/dev.example.json`에서 Git에 포함되지 않는 `config/dev.json`을 만듭니다.

설치된 SDK를 직접 지정하려면 `FLUTTER_BIN`에 해당 SDK의 `bin/flutter` 경로를
전달합니다. 고정 커밋과 다르면 중단합니다. `./tool/setup.sh --offline`은 이미
고정 SDK와 모든 의존성이 준비된 환경에서만 사용할 수 있습니다.

VS Code는 저장소의 `.vscode/settings.json`을 통해 준비된 `.tools/flutter`를
사용합니다. 다른 IDE도 이 SDK 경로를 선택하면 같은 버전으로 분석·빌드합니다.
설치 기준은 [Flutter SDK 아카이브](https://docs.flutter.dev/install/archive)를 참고하세요.

## 플랫폼별 사전 준비

아래 운영체제 도구와 계정은 `setup.sh`가 설치하거나 변경하지 않습니다.

| 대상 | 필요한 도구와 설정 |
| --- | --- |
| 웹 | 웹 빌드는 고정 Flutter SDK로 가능. 브라우저 실행에는 Chrome 또는 지원 브라우저 필요 |
| Android | Android Studio/SDK, JDK 17 또는 21, Android SDK Platform 35, Build Tools, NDK 27.0.12077973, SDK 라이선스 동의 |
| iOS | macOS, Xcode와 iOS Simulator, CocoaPods 1.16.2. 앱 최소 지원 버전은 iOS 15 |
| iPhone 실기기 | Xcode의 Signing & Capabilities에서 사용할 개발 팀과 기기 서명 설정 필요 |

iOS 시뮬레이터는 현재 Mac의 CPU 아키텍처로 빌드합니다. 이는 고정 Flutter와
Xcode 27의 [다중 아키텍처 검사 문제](https://github.com/flutter/flutter/issues/188461)를
피하는 프로젝트 설정이며 iPhone 실기기 빌드에는 적용되지 않습니다.

Android는 Gradle 8.12와 AGP 8.7.3을 저장소에서 지정합니다. Gradle wrapper와
로컬 SDK 경로는 Flutter가 생성하므로 Git에 넣지 않습니다. JDK 조건은
[AGP 8.7 호환성 안내](https://developer.android.com/build/releases/agp-8-7-0-release-notes)를 따릅니다.
앱의 Java 소스 대상 버전과 Gradle을 실행하는 JDK 버전은 별개입니다.

```bash
./tool/flutter.sh doctor -v
# Android 개발 환경에서 SDK 라이선스 확인
./tool/flutter.sh doctor --android-licenses
```

macOS에서 Xcode를 처음 설치했다면 Xcode를 한 번 열어 초기 설치와 라이선스
설정을 완료합니다. CocoaPods는 Ruby 환경에 `gem install cocoapods -v 1.16.2`로
준비할 수 있습니다. iOS/macOS에서 `pod install`을 직접 실행하려면 먼저
`./tool/setup.sh`를 완료하고 해당 플랫폼 폴더에서 실행합니다.

## Supabase 연결과 앱 실행

`config/dev.json`의 두 값을 개발용 Supabase 프로젝트에 맞게 입력합니다.

- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_ANON_KEY`: publishable 키 또는 기존 anon 키. 서버용 secret/service_role 키를 넣지 않습니다.

기존 개발용 Supabase를 연결하면 기존 DB와 Storage를 그대로 사용합니다.
새 Supabase 프로젝트를 만드는 경우 [DB 준비 순서](supabase/README.md)를 먼저
따릅니다. Git clone은 Supabase 프로젝트, 실제 데이터, 업로드 파일이나 계정을
복사하지 않습니다. `setup.sh`도 외부 DB를 변경하지 않습니다.

```bash
./tool/flutter.sh run --dart-define-from-file=config/dev.json

# Android 개발용 APK
./tool/flutter.sh build apk --debug --dart-define-from-file=config/dev.json

# 서명 없는 iOS 시뮬레이터 빌드
./tool/flutter.sh build ios --simulator --debug --dart-define-from-file=config/dev.json

# 웹 빌드
./tool/flutter.sh build web --dart-define-from-file=config/dev.json
```

Supabase 설정 없이도 정적 분석·테스트·컴파일은 가능합니다. 이 경우 앱을 실행하면
설정 안내 화면이 표시되며 로그인·질문 기능을 사용할 수 없습니다.
Android release 빌드에는 현재 개발용 debug 서명 설정이 사용되므로 스토어 배포
서명 준비는 별도입니다.

## 폴더 이름 변경·이동

실행 중인 디버깅과 빌드를 종료하고 폴더를 이동한 뒤 위 명령을 그대로 사용합니다.
`tool/flutter.sh`는 프로젝트나 SDK 위치가 바뀌면 생성 설정과 캐시를 재생성합니다.
같은 위치에서는 매번 정리하지 않습니다. `build/`는 정리 대상이므로 보관할
APK·IPA·아카이브는 이동 전에 프로젝트 밖으로 내보냅니다.

IDE에서 직접 빌드할 때는 이동 후 `./tool/setup.sh`를 실행하고 새 위치의
프로젝트를 엽니다. `Generated.xcconfig`, `flutter_export_environment.sh`,
`local.properties`, `.dart_tool/`, `.tools/`, 플랫폼별 `ephemeral/`은 로컬
생성 파일입니다. 절대 경로가 들어 있어도 직접 수정하거나 Git에 추가하지 않습니다.
폴더명과 별개인 `local_qa_concierge` 패키지명과 앱 식별자는 유지합니다.

## 검증

```bash
python3 -B -m unittest discover -s tool/tests -v
./tool/flutter.sh analyze
./tool/flutter.sh test
```

새 clone 검증에서는 로컬 SDK 설정, 생성 파일과 `config/dev.json`이 없는 상태에서
`setup.sh`를 실행합니다. 검증 결과와 실제 서비스·기기 확인 범위는
[개발 환경 복구 검증](docs/DEVELOPMENT_RECOVERY.md)에 기록합니다.
