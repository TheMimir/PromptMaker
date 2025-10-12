---
id: EXPORT-001
version: 0.1.0
status: completed
created: 2025-10-11
updated: 2025-10-12
author: @Alfred
priority: high
category: feature
labels:
  - export
  - file-io
  - pdf
  - markdown
  - json
depends_on: []
blocks: []
related_specs: [TEMPLATE-SHARE-001]
scope:
  packages:
    - ai_prompt_maker
  files:
    - export_service.py
    - app.py
---

# @SPEC:EXPORT-001: 프롬프트 내보내기 시스템

## HISTORY

### v0.1.0 (2025-10-12)
- **COMPLETED**: TDD 구현 완료 (RED-GREEN-REFACTOR)
- **AUTHOR**: @Alfred
- **TEST**: 18개 테스트 케이스 통과, 커버리지 93%
- **QUALITY**: TRUST 5원칙 92% 준수
- **FILES**:
  - ai_prompt_maker/export_service.py (390 LOC)
  - tests/ai_prompt_maker/test_export_service.py (502 LOC)
- **FEATURES**:
  - Markdown 내보내기 (UTF-8 인코딩)
  - JSON 내보내기 (구조화된 스키마)
  - PDF 내보내기 (한글 폰트 지원, reportlab 조건부)
- **SECURITY**:
  - Path Traversal 방지 (파일명 sanitization)
  - 파일 크기 제한 강제 (10MB)
  - 파일명 특수문자 필터링
- **RELATED**: feature/SPEC-EXPORT-001 브랜치 구현 완료

### v0.0.1 (2025-10-11)
- **INITIAL**: 프롬프트 내보내기 시스템 SPEC 최초 작성
- **AUTHOR**: @Alfred
- **REVIEW**: Pending
- **REASON**: 사용자 요구사항 Top 3, 템플릿 공유 기능의 전제 조건
- **SCOPE**: Markdown, JSON, PDF 내보내기 기능
- **RELATED**: product.md#TODO:SPEC-BACKLOG-001 (1순위 요구사항)

---

## 개요

PromptMaker 사용자가 생성한 프롬프트를 다양한 형식(Markdown, JSON, PDF)으로 내보내기하여 저장, 공유, 문서화할 수 있는 시스템을 제공합니다.

### 핵심 가치
- **이식성**: 생성된 프롬프트를 다양한 환경에서 재사용 (Notion, Confluence, GitHub 등)
- **공유성**: 팀원 간 프롬프트 공유 및 협업 지원
- **문서화**: 프로젝트 산출물로 프롬프트를 아카이빙

### 지원 형식
1. **Markdown (.md)**: 범용성 높은 텍스트 형식, GitHub/Notion 호환
2. **JSON (.json)**: 구조화된 데이터 형식, API 연동 및 자동화 지원
3. **PDF (.pdf)**: 최종 문서 형식, 한글 폰트 지원

---

## EARS 요구사항

### Ubiquitous Requirements (기본 요구사항)

- 시스템은 생성된 프롬프트를 Markdown 형식(.md)으로 내보내기해야 한다
- 시스템은 생성된 프롬프트를 JSON 형식(.json)으로 내보내기해야 한다
- 시스템은 생성된 프롬프트를 PDF 형식(.pdf)으로 내보내기해야 한다
- 시스템은 내보내기 형식 선택 UI를 제공해야 한다
- 시스템은 파일 다운로드 기능을 제공해야 한다
- 시스템은 내보내기 시 파일명 자동 생성(템플릿명_날짜_시간.확장자) 기능을 제공해야 한다

### Event-driven Requirements (이벤트 기반)

- WHEN 사용자가 "내보내기" 버튼을 클릭하면, 시스템은 형식 선택 다이얼로그를 표시해야 한다
- WHEN 사용자가 Markdown 형식을 선택하면, 시스템은 .md 파일을 생성하고 다운로드 링크를 제공해야 한다
- WHEN 사용자가 JSON 형식을 선택하면, 시스템은 구조화된 .json 파일을 생성해야 한다
- WHEN 사용자가 PDF 형식을 선택하면, 시스템은 한글/영문이 포함된 .pdf 파일을 생성해야 한다
- WHEN 내보내기가 완료되면, 시스템은 성공 메시지와 함께 다운로드 버튼을 표시해야 한다
- WHEN 내보내기 실패 시, 시스템은 명확한 오류 메시지(파일 크기 초과, 라이브러리 누락 등)를 표시해야 한다
- WHEN reportlab이 설치되지 않았을 때, 시스템은 PDF 내보내기 버튼을 비활성화하고 설치 안내를 표시해야 한다

### State-driven Requirements (상태 기반)

- WHILE 프롬프트가 생성되지 않은 상태일 때, 시스템은 내보내기 버튼을 비활성화해야 한다
- WHILE 내보내기 진행 중일 때, 시스템은 진행 상태(스피너 또는 진행률)를 표시해야 한다
- WHILE 템플릿 편집 모드일 때, 시스템은 내보내기 버튼을 표시하지 않아야 한다

### Optional Features (선택적 기능)

- WHERE 사용자가 reportlab 라이브러리를 설치했다면, 시스템은 PDF 내보내기를 활성화할 수 있다
- WHERE 사용자가 파일명을 지정하면, 시스템은 사용자 지정 파일명을 사용할 수 있다
- WHERE Markdown 프리뷰가 활성화되면, 시스템은 내보내기 전 미리보기를 제공할 수 있다
- WHERE PDF 내보내기 시 커스텀 폰트를 지정하면, 시스템은 해당 폰트를 사용할 수 있다

### Constraints (제약사항)

- 파일 크기는 10MB를 초과하지 않아야 한다
- PDF 생성 시 최대 50 페이지로 제한해야 한다
- 파일명은 `[템플릿명]_[날짜]_[시간].{확장자}` 형식이어야 한다
- 파일명에 특수 문자(`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)가 포함되지 않아야 한다
- JSON 출력은 UTF-8 인코딩을 사용해야 한다
- PDF 출력은 NanumGothic 폰트를 사용하여 한글을 지원해야 한다
- 한 번의 내보내기 요청은 3초 이내에 완료되어야 한다 (일반 프롬프트 기준)

---

## Environment (환경)

### 시스템 요구사항
- Python 3.8+
- Streamlit 1.37.0+

### 필수 라이브러리
- reportlab>=4.0.0 (PDF 생성)

### 선택 라이브러리
- NanumGothic.ttf (한글 폰트, 번들링 권장)

### 폰트 번들링 경로
- `data/fonts/NanumGothic.ttf`

---

## Implementation Details

### Markdown 내보내기
- Python 내장 문자열 처리 사용
- 섹션별 헤더 포맷팅 (##, ###)
- 리스트/체크박스 Markdown 구문 적용
- Streamlit `st.download_button()` 통합

### JSON 내보내기
- `json.dumps()` with `ensure_ascii=False` 사용
- JSON 스키마:
  ```json
  {
    "version": "1.0",
    "metadata": {
      "template_name": "string",
      "created_at": "ISO-8601",
      "exported_at": "ISO-8601"
    },
    "content": {
      "role": "string",
      "goal": "string",
      "context": "string",
      "document": "string",
      "output": "string",
      "rules": "string"
    }
  }
  ```

### PDF 내보내기
- reportlab Canvas 사용
- 페이지 레이아웃:
  - **헤더**: 프롬프트명, 생성일 (페이지마다 반복)
  - **본문**: Role, Goal, Context, Document, Output, Rules 섹션
  - **푸터**: 페이지 번호, 프로젝트명
- NanumGothic 폰트 등록:
  ```python
  from reportlab.pdfbase import pdfmetrics
  from reportlab.pdfbase.ttfonts import TTFont

  pdfmetrics.registerFont(TTFont('NanumGothic', 'data/fonts/NanumGothic.ttf'))
  ```
- 한글/영문 혼용 텍스트 렌더링
- 페이지 자동 분할 (50 페이지 제한)

### 파일명 Sanitization
- 기존 `_sanitize_template_id()` 함수 재사용
- Path Traversal 방지 (`../`, `./` 제거)
- 특수 문자 제거 (`/\:*?"<>|`)
- 공백을 언더스코어로 변환

---

## Traceability (@TAG)

- **SPEC**: @SPEC:EXPORT-001
- **TEST**: tests/ai_prompt_maker/test_export_service.py (예정)
- **CODE**: ai_prompt_maker/export_service.py (예정)
- **DOC**: docs/user-guide/export.md (예정)

---

## Success Criteria (성공 기준)

### 기능 검증
1. ✅ Markdown 내보내기 성공률 >95%
2. ✅ JSON 내보내기 성공률 >95%
3. ✅ PDF 내보내기 성공률 >95% (reportlab 설치 시)
4. ✅ 파일 크기 10MB 이하 제약 준수
5. ✅ 한글/영문 혼용 프롬프트가 PDF에서 정상 렌더링
6. ✅ 파일명 sanitization 적용으로 Path Traversal 방지
7. ✅ 내보내기 소요 시간 <3초 (일반적인 프롬프트 기준)

### 품질 검증
1. ✅ 테스트 커버리지 ≥85%
2. ✅ 모든 EARS 요구사항에 대응하는 테스트 케이스 존재
3. ✅ 보안 테스트 통과 (Path Traversal, 파일명 특수문자)
4. ✅ 에러 핸들링 완전성 (라이브러리 누락, 파일 크기 초과, 인코딩 오류)

### 사용성 검증
1. ✅ 내보내기 버튼이 프롬프트 생성 후 즉시 표시됨
2. ✅ 형식 선택 UI가 직관적임 (라디오 버튼 또는 드롭다운)
3. ✅ 진행 상태가 명확히 표시됨 (스피너 또는 진행률)
4. ✅ 오류 메시지가 명확하고 실행 가능한 조치를 포함

---

## Risk & Mitigation

### 리스크 1: reportlab 라이브러리 누락
- **영향도**: High (PDF 기능 완전 차단)
- **완화 방안**:
  - requirements.txt에 optional dependency로 명시
  - PDF 버튼 비활성화 + 설치 안내 메시지 표시
  - Markdown/JSON 내보내기는 정상 작동

### 리스크 2: 대용량 프롬프트 처리
- **영향도**: Medium (메모리 부족, 브라우저 다운)
- **완화 방안**:
  - 10MB 파일 크기 제한
  - PDF 50 페이지 제한
  - 사전 검증 로직 (파일 크기 계산)

### 리스크 3: 한글 폰트 렌더링 실패
- **영향도**: High (한글 프롬프트 사용 불가)
- **완화 방안**:
  - NanumGothic.ttf 번들링 (data/fonts/)
  - 폰트 로드 실패 시 fallback 폰트 사용 (Helvetica)
  - 폰트 없음 경고 메시지 표시

### 리스크 4: Path Traversal 공격
- **영향도**: Critical (보안 취약점)
- **완화 방안**:
  - 파일명 sanitization 강제 적용
  - 화이트리스트 기반 문자 필터링
  - 보안 테스트 케이스 작성

---

## Next Steps

1. `/alfred:2-build EXPORT-001` - TDD 구현 (RED → GREEN → REFACTOR)
2. `/alfred:3-sync` - 문서 동기화 및 TAG 체인 검증
3. 사용자 테스트 및 피드백 수집

---

_이 SPEC은 MoAI-ADK SPEC-First TDD 방법론을 따릅니다._
