# SPEC-EXPORT-001 구현 계획서

> **SPEC**: @SPEC:EXPORT-001
> **작성일**: 2025-10-11
> **작성자**: @Alfred

---

## 구현 전략

### TDD 사이클 기반 단계별 접근
1. **Phase 1**: Markdown 내보내기 (기본 기능)
2. **Phase 2**: JSON 내보내기 (구조화)
3. **Phase 3**: PDF 내보내기 (고급 기능)
4. **Phase 4**: UI 통합 및 사용성 개선

**중요**: 각 Phase는 RED-GREEN-REFACTOR 사이클을 완전히 완료한 후 다음 단계로 진행합니다.

---

## Phase 1: Markdown 내보내기

### 1.1 RED - 테스트 작성
- **파일**: `tests/ai_prompt_maker/test_export_service.py`
- **테스트 케이스**:
  - `test_export_markdown_success()`: 정상 내보내기
  - `test_export_markdown_sanitize_filename()`: 파일명 sanitization
  - `test_export_markdown_section_formatting()`: 섹션 포맷팅 검증
  - `test_export_markdown_empty_sections()`: 빈 섹션 처리
  - `test_export_markdown_special_characters()`: 특수 문자 이스케이핑

### 1.2 GREEN - 최소 구현
- **파일**: `ai_prompt_maker/export_service.py`
- **함수**:
  ```python
  class ExportService:
      def export_to_markdown(self, prompt: PromptComponent, filename: str) -> str:
          """프롬프트를 Markdown 형식으로 변환"""
          pass

      def _sanitize_filename(self, filename: str) -> str:
          """파일명 sanitization"""
          pass

      def _format_section(self, title: str, content: str) -> str:
          """섹션 Markdown 포맷팅"""
          pass
  ```

### 1.3 REFACTOR - 코드 품질 개선
- 중복 코드 제거
- 함수 분리 (SRP 준수)
- 타입 힌트 추가 (mypy 검증)
- 도큐멘테이션 작성

---

## Phase 2: JSON 내보내기

### 2.1 RED - 테스트 작성
- **테스트 케이스**:
  - `test_export_json_success()`: 정상 내보내기
  - `test_export_json_schema_validation()`: JSON 스키마 검증
  - `test_export_json_utf8_encoding()`: UTF-8 인코딩
  - `test_export_json_metadata()`: 메타데이터 포함 확인
  - `test_export_json_special_characters()`: 특수 문자 처리

### 2.2 GREEN - JSON 직렬화 구현
- **함수**:
  ```python
  def export_to_json(self, prompt: PromptComponent, filename: str) -> str:
      """프롬프트를 JSON 형식으로 변환"""
      pass

  def _to_dict(self, prompt: PromptComponent) -> dict:
      """PromptComponent를 dict로 변환"""
      pass

  def _generate_metadata(self, template_name: str) -> dict:
      """메타데이터 생성"""
      pass
  ```

### 2.3 REFACTOR - 스키마 최적화
- JSON 스키마 검증 로직 추가
- ISO-8601 날짜 포맷팅
- ensure_ascii=False 확인
- JSON 들여쓰기 최적화

---

## Phase 3: PDF 내보내기

### 3.1 RED - 테스트 작성
- **테스트 케이스**:
  - `test_export_pdf_success()`: 정상 내보내기
  - `test_export_pdf_korean_rendering()`: 한글 렌더링
  - `test_export_pdf_page_break()`: 페이지 분할
  - `test_export_pdf_50_page_limit()`: 50 페이지 제한
  - `test_export_pdf_header_footer()`: 헤더/푸터 렌더링
  - `test_export_pdf_reportlab_missing()`: reportlab 누락 처리

### 3.2 GREEN - PDF 생성 구현
- **함수**:
  ```python
  def export_to_pdf(self, prompt: PromptComponent, filename: str) -> Optional[str]:
      """프롬프트를 PDF 형식으로 변환"""
      if not self._is_reportlab_available():
          return None
      pass

  def _is_reportlab_available(self) -> bool:
      """reportlab 설치 여부 확인"""
      pass

  def _register_korean_font(self):
      """NanumGothic 폰트 등록"""
      pass

  def _create_pdf_canvas(self, filename: str) -> Canvas:
      """PDF Canvas 생성"""
      pass

  def _draw_header(self, canvas: Canvas, prompt_name: str, date: str):
      """페이지 헤더 그리기"""
      pass

  def _draw_footer(self, canvas: Canvas, page_num: int):
      """페이지 푸터 그리기"""
      pass

  def _draw_section(self, canvas: Canvas, title: str, content: str, y_position: int) -> int:
      """섹션 그리기, 새 y 위치 반환"""
      pass

  def _check_page_break(self, canvas: Canvas, y_position: int, threshold: int = 100) -> int:
      """페이지 넘김 필요 여부 확인"""
      pass
  ```

### 3.3 REFACTOR - 폰트 및 레이아웃 최적화
- 한글/영문 혼용 텍스트 렌더링 개선
- 페이지 여백 조정
- 헤더/푸터 디자인 개선
- 에러 핸들링 강화

---

## Phase 4: UI 통합

### 4.1 Streamlit UI 통합
- **파일**: `ai_prompt_maker/app.py`
- **위치**: "프롬프트 편집기" 탭 또는 새로운 "내보내기" 탭
- **UI 컴포넌트**:
  ```python
  # 내보내기 버튼 활성화 조건
  if st.session_state.get("generated_prompt"):
      st.subheader("📤 프롬프트 내보내기")

      export_format = st.radio(
          "내보내기 형식 선택",
          ["Markdown (.md)", "JSON (.json)", "PDF (.pdf)"],
          horizontal=True
      )

      if st.button("내보내기", type="primary"):
          with st.spinner("파일 생성 중..."):
              # 내보내기 로직
              pass
  ```

### 4.2 사용성 개선
- 진행 상태 표시 (st.spinner, st.progress)
- 성공/실패 메시지 표시 (st.success, st.error)
- 다운로드 버튼 제공 (st.download_button)
- reportlab 미설치 시 안내 메시지

### 4.3 에러 핸들링
- 파일 크기 검증 (10MB 제한)
- 페이지 수 검증 (50 페이지 제한)
- 인코딩 오류 처리
- 폰트 로드 실패 처리

---

## 기술적 의존성

### 필수 라이브러리
```python
# requirements.txt
reportlab>=4.0.0
```

### 폰트 번들링
- **경로**: `data/fonts/NanumGothic.ttf`
- **다운로드**: https://hangeul.naver.com/font
- **라이선스**: OFL (Open Font License)

### 개발 도구
- pytest (테스트)
- pytest-cov (커버리지)
- mypy (타입 검증)
- black (포맷팅)
- ruff (린팅)

---

## 보안 고려사항

### 1. 파일명 Sanitization
- **위협**: Path Traversal 공격 (../../../etc/passwd)
- **대응**:
  - 화이트리스트 기반 문자 필터링 (영문, 숫자, 언더스코어, 하이픈만 허용)
  - 특수 문자 제거 (`/\:*?"<>|`)
  - 경로 구분자 제거 (`../`, `./`)

### 2. 파일 크기 제한
- **위협**: 메모리 부족, DoS 공격
- **대응**:
  - 10MB 파일 크기 제한
  - 사전 검증 (파일 생성 전 크기 계산)

### 3. 입력 검증
- **위협**: XSS, 인젝션 공격
- **대응**:
  - HTML 태그 이스케이핑 (Markdown/PDF)
  - JSON 직렬화 시 ensure_ascii=False 사용

---

## 테스트 전략

### 단위 테스트 (Unit Test)
- ExportService 각 함수별 독립 테스트
- 모킹: reportlab Canvas, 파일 시스템

### 통합 테스트 (Integration Test)
- Streamlit UI + ExportService 통합
- 실제 파일 생성 및 검증

### 보안 테스트 (Security Test)
- Path Traversal 시뮬레이션
- 파일명 특수 문자 테스트
- 대용량 파일 생성 시도

### 성능 테스트 (Performance Test)
- 일반 프롬프트 내보내기 시간 <3초
- 대용량 프롬프트 (5MB) 내보내기 시간 <10초

---

## 우선순위별 구현 순서

### 1차 목표 (MVP)
- [x] Phase 1: Markdown 내보내기
- [x] Phase 2: JSON 내보내기
- [x] Phase 4.1: Streamlit UI 통합 (Markdown/JSON만)

### 2차 목표 (Enhanced)
- [ ] Phase 3: PDF 내보내기
- [ ] Phase 4.2: 사용성 개선 (진행 상태, 미리보기)

### 3차 목표 (Advanced)
- [ ] 파일명 커스터마이징
- [ ] 내보내기 히스토리 로깅
- [ ] 배치 내보내기 (여러 프롬프트 한 번에)

**중요**: 시간 예측은 제공하지 않습니다. 각 Phase는 완료 후 다음 단계로 진행합니다.

---

## 품질 게이트

### Code Quality
- [ ] 테스트 커버리지 ≥85%
- [ ] mypy 타입 검증 통과
- [ ] ruff 린팅 통과
- [ ] black 포맷팅 적용

### TRUST 5원칙 준수
- [ ] **T**est First: 모든 함수에 테스트 케이스 존재
- [ ] **R**eadable: 의도 드러내는 함수/변수명 사용
- [ ] **U**nified: 타입 힌트 100% 적용
- [ ] **S**ecured: 보안 테스트 통과
- [ ] **T**rackable: @TAG 시스템 적용 완료

### SPEC 정합성
- [ ] 모든 EARS 요구사항에 대응하는 구현 존재
- [ ] Success Criteria 모두 충족
- [ ] Risk Mitigation 전략 구현 완료

---

## 다음 단계

1. **git-manager**: 브랜치 생성 및 Draft PR 생성 (Personal 모드는 선택)
2. **/alfred:2-build EXPORT-001**: TDD 구현 시작
3. **SPEC 검토**: 사용자 피드백 반영 후 SPEC 업데이트

---

_이 계획서는 SPEC-EXPORT-001 구현의 로드맵입니다._
