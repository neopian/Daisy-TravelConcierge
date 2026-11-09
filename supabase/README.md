# 개발용 Supabase 준비

기존 개발용 프로젝트에 연결할 때는 `config/dev.json`에 URL과 공개 클라이언트
키를 입력합니다. 아래 초기화 SQL을 기존 DB에 다시 실행할 필요는 없습니다.

## 새 프로젝트의 필수 스키마

새 Supabase 프로젝트를 만든 뒤 SQL Editor에서 다음 파일을 **순서대로** 실행합니다.
SQL에는 Supabase의 `auth`, `storage`, `supabase_realtime` 구성이 필요하므로 일반
PostgreSQL 빈 DB만으로는 실행할 수 없습니다.

1. [기본 테이블·함수·RLS·이미지 Storage](migrations/202607040001_initial_mvp.sql)
2. [스페인 지도 좌표와 질문 등록 함수](migrations/202607070001_spain_map_coordinates.sql)
3. [댓글 테이블·정책](migrations/202607070002_question_comments.sql)
4. [질문·답변·댓글·이미지 Realtime](migrations/202607120001_enable_question_realtime.sql)

댓글 테이블은 Realtime 설정과 앱의 질문 조회에서 사용하므로 3번을 생략하면 안 됩니다.
현재 앱은 질문을 등록할 때 좌표를 전달하므로 2번도 필수입니다.
일부 SQL은 정책을 처음 만드는 방식이므로 전체 목록을 반복 실행하지 않습니다.
기존 DB에 누락된 기능을 추가할 때는 해당 마이그레이션 적용 여부를 먼저 확인합니다.

설치 후 SQL Editor에서 아래 결과를 확인합니다.

```sql
select to_regclass('public.questions') as questions,
       to_regclass('public.question_comments') as question_comments;
select id from storage.buckets where id = 'question-images';
select tablename from pg_publication_tables
where pubname = 'supabase_realtime' and schemaname = 'public'
order by tablename;
```

두 테이블 이름과 `question-images` 버킷이 조회되고, Realtime 목록에는
`questions`, `answers`, `question_comments`, `question_images`가 포함돼야 합니다.

## 관리자와 선택적인 테스트 계정

직접 가입한 계정을 관리자로 지정하려면 실제 개발 계정의 이메일로 실행합니다.

```sql
update public.users set is_admin = true where email = 'admin@example.com';
```

앱의 디버그 로그인 바로가기를 사용할 개발용 DB에서만 아래 파일을 실행합니다.

1. [개발 계정 5개 준비](migrations/202607080001_dev_login_shortcuts.sql)
2. [테스트 답변자 승인·지역 설정](migrations/202607100001_approve_temp_answerers.sql)

개발 계정 비밀번호는 `daisy-dev-1234`입니다. 첫 파일은 정해진 테스트 계정의
기존 인증 계정을 삭제·재생성하므로 실제 사용자가 있는 운영 DB의 일반 초기화
명령으로 사용하지 않습니다. 두 번째 파일은 테스트 답변자의 지역 설정을 갱신합니다.
현재 초기화 방식은 SQL Editor를 이용하며, Supabase CLI의 로컬 환경이나 기존
DB 데이터·Storage 파일의 백업 복원은 이 저장소에 포함되지 않습니다.
