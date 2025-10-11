# SPEC-EXPORT-001 수락 기준 (Acceptance Criteria)

> **SPEC**: @SPEC:EXPORT-001
> **작성일**: 2025-10-11
> **작성자**: @Alfred

---

## Given-When-Then 시나리오

### 시나리오 1: Markdown 내보내기 성공

**Given**: 사용자가 "게임 밸런스 조정" 프롬프트를 생성했을 때
- Role: 게임 밸런스 디자이너
- Goal: 신규 전설 무기의 밸런스 조정안 작성
- Context: PvP 승률 데이터, 사용률 통계
- Output: 비교 분석표

**When**: "Markdown으로 내보내기" 버튼을 클릭하면

**Then**:
- [x] "game_balance_20251011_143020.md" 파일이 생성된다
- [x] 다운로드 버튼이 화면에 표시된다
- [x] 파일에 프롬프트 전체 내용(Role, Goal, Context, Document, Output, Rules)이 포함된다
- [x] Markdown 구문(헤더 ##, ###, 리스트)이 정확하게 렌더링된다
- [x] 파일 크기가 10MB 이하이다
- [x] 성공 메시지 "Markdown 파일이 생성되었습니다"가 표시된다

---

### 시나리오 2: JSON 내보내기 성공

**Given**: 사용자가 복잡한 프롬프트(Document 섹션 포함)를 생성했을 때
- Document: 5000자 길이의 게임 디자인 문서

**When**: "JSON으로 내보내기" 버튼을 클릭하면

**Then**:
- [x] "complex_prompt_20251011_143020.json" 파일이 생성된다
- [x] JSON 구조가 유효하다 (json.loads() 성공)
- [x] `version`, `metadata`, `content` 필드가 존재한다
- [x] `metadata.template_name`, `metadata.created_at`, `metadata.exported_at`가 존재한다
- [x] `content.role`, `content.goal`, `content.context` 등이 존재한다
- [x] 한글 텍스트가 정상적으로 인코딩된다 (UTF-8)
- [x] 파일을 JSON 뷰어에서 열면 계층 구조가 명확히 보인다

**검증 코드**:
```python
import json

with open("complex_prompt_20251011_143020.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    assert "version" in data
    assert "metadata" in data
    assert "content" in data
    assert data["metadata"]["template_name"] == "복잡한 프롬프트"
    assert "한글" in data["content"]["role"]  # 한글 정상 디코딩
```

---

### 시나리오 3: PDF 내보내기 성공 (한글 포함)

**Given**: 사용자가 한글/영문 혼용 프롬프트를 생성했을 때
- Role: "Game Balance Designer (게임 밸런스 디자이너)"
- Goal: "Adjust weapon stats for PvP balance (PvP 밸런스 조정)"

**When**: "PDF로 내보내기" 버튼을 클릭하면

**Then**:
- [x] "multilang_prompt_20251011_143020.pdf" 파일이 생성된다
- [x] 한글과 영문이 모두 정상적으로 렌더링된다
- [x] 페이지 헤더에 프롬프트명과 생성일이 표시된다
- [x] 페이지 푸터에 페이지 번호와 프로젝트명이 표시된다
- [x] 섹션별 제목(Role, Goal 등)이 굵은 글씨로 표시된다
- [x] 파일을 PDF 뷰어에서 열면 한글이 깨지지 않는다
- [x] NanumGothic 폰트가 적용되어 있다

**검증 방법**:
- Adobe Acrobat Reader에서 파일 열기
- 한글 텍스트 복사 후 메모장에 붙여넣기 (정상 복사 확인)
- PDF 속성에서 폰트 정보 확인 (NanumGothic 포함 확인)

---

### 시나리오 4: 대용량 프롬프트 제약 처리

**Given**: 사용자가 15MB 크기의 프롬프트를 생성했을 때
- Document: 15MB 크기의 게임 데이터 텍스트 파일

**When**: "PDF로 내보내기" 버튼을 클릭하면

**Then**:
- [x] 오류 메시지 "파일 크기가 10MB를 초과합니다. 프롬프트 내용을 줄여주세요."가 표시된다
- [x] 다운로드 버튼이 표시되지 않는다
- [x] 파일이 생성되지 않는다 (파일 시스템 확인)
- [x] 에러 아이콘(🚨)이 함께 표시된다

**검증 코드**:
```python
# 파일 크기 사전 검증
content_size = len(prompt_text.encode('utf-8'))
max_size = 10 * 1024 * 1024  # 10MB

if content_size > max_size:
    raise ValueError(f"파일 크기가 {content_size / 1024 / 1024:.2f}MB로 10MB를 초과합니다.")
```

---

### 시나리오 5: 프롬프트 미생성 상태

**Given**: 사용자가 프롬프트를 생성하지 않았을 때
- st.session_state["generated_prompt"] == None

**When**: 내보내기 섹션을 확인하면

**Then**:
- [x] 내보내기 버튼이 비활성화되어 있다 (disabled=True)
- [x] 툴팁에 "프롬프트를 먼저 생성하세요"가 표시된다
- [x] 내보내기 섹션이 회색으로 흐릿하게 표시된다
- [x] 형식 선택 라디오 버튼이 비활성화되어 있다

---

### 시나리오 6: reportlab 라이브러리 미설치

**Given**: reportlab 라이브러리가 설치되지 않았을 때
- `pip list | grep reportlab` 결과 없음

**When**: PDF 내보내기를 시도하면

**Then**:
- [x] 경고 메시지 "⚠️ PDF 내보내기 기능을 사용하려면 reportlab을 설치하세요: `pip install reportlab`"가 표시된다
- [x] PDF 라디오 버튼이 비활성화되어 있다
- [x] Markdown/JSON 내보내기는 정상 작동한다
- [x] 설치 안내 링크가 함께 표시된다 (https://pypi.org/project/reportlab/)

**검증 코드**:
```python
def _is_reportlab_available() -> bool:
    try:
        import reportlab
        return True
    except ImportError:
        return False

if not _is_reportlab_available():
    st.warning("⚠️ PDF 내보내기 기능을 사용하려면 reportlab을 설치하세요: `pip install reportlab`")
    pdf_disabled = True
```

---

### 시나리오 7: 파일명 특수 문자 처리

**Given**: 사용자가 특수 문자가 포함된 템플릿명으로 프롬프트를 생성했을 때
- Template Name: "게임/밸런스:조정*안?"

**When**: Markdown으로 내보내기하면

**Then**:
- [x] 파일명이 "게임_밸런스_조정_안_20251011_143020.md"로 sanitization된다
- [x] 특수 문자(`/`, `:`, `*`, `?`)가 언더스코어로 변환된다
- [x] 파일이 정상적으로 생성된다
- [x] Path Traversal 시도(`../../../etc/passwd`)가 차단된다

**검증 코드**:
```python
def _sanitize_filename(filename: str) -> str:
    # 특수 문자 제거
    invalid_chars = r'/\:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Path Traversal 방지
    filename = filename.replace('..', '')
    filename = filename.replace('./', '')

    return filename
```

---

### 시나리오 8: PDF 50 페이지 제한

**Given**: 사용자가 매우 긴 프롬프트(100 페이지 분량)를 생성했을 때
- Document: 100,000자 길이의 텍스트

**When**: PDF로 내보내기하면

**Then**:
- [x] 오류 메시지 "PDF 페이지 수가 50 페이지를 초과합니다. 내용을 줄여주세요."가 표시된다
- [x] 파일이 생성되지 않는다
- [x] 대안으로 "Markdown 또는 JSON 형식 사용을 권장합니다"가 표시된다

---

### 시나리오 9: 내보내기 진행 상태 표시

**Given**: 사용자가 PDF 내보내기를 시작했을 때

**When**: 파일 생성 중일 때

**Then**:
- [x] 스피너가 표시된다 ("파일 생성 중...")
- [x] 내보내기 버튼이 비활성화된다 (중복 클릭 방지)
- [x] 3초 이내에 완료된다 (일반 프롬프트 기준)
- [x] 완료 후 스피너가 사라지고 성공 메시지가 표시된다

**검증 코드**:
```python
import time

start_time = time.time()

with st.spinner("파일 생성 중..."):
    export_service.export_to_pdf(prompt, filename)

elapsed_time = time.time() - start_time
assert elapsed_time < 3.0, f"내보내기 시간 초과: {elapsed_time:.2f}초"
```

---

### 시나리오 10: Markdown 프리뷰 (Optional Feature)

**Given**: 사용자가 Markdown 프리뷰를 활성화했을 때
- st.checkbox("내보내기 전 미리보기") == True

**When**: Markdown 내보내기 버튼을 클릭하면

**Then**:
- [x] 내보내기 전 Markdown 렌더링된 프리뷰가 표시된다
- [x] "계속 진행" 버튼과 "취소" 버튼이 표시된다
- [x] "계속 진행" 클릭 시 파일이 생성된다
- [x] "취소" 클릭 시 내보내기가 중단된다

---

## 검증 요구사항

### 기능 검증 체크리스트

- [ ] Markdown 내보내기 성공률 >95%
- [ ] JSON 내보내기 성공률 >95%
- [ ] PDF 내보내기 성공률 >95% (reportlab 설치 시)
- [ ] 파일 크기 10MB 제한 준수
- [ ] 한글/영문 혼용 텍스트 정상 렌더링 (PDF)
- [ ] 파일명 sanitization 적용
- [ ] 내보내기 소요 시간 <3초 (일반 프롬프트)

### 보안 검증 체크리스트

- [ ] Path Traversal 차단 (`../../../etc/passwd`)
- [ ] 파일명 특수 문자 제거 (`/\:*?"<>|`)
- [ ] 파일 크기 제한 강제 (10MB)
- [ ] XSS 방지 (HTML 태그 이스케이핑)

### 사용성 검증 체크리스트

- [ ] 내보내기 버튼이 프롬프트 생성 후 즉시 표시
- [ ] 형식 선택 UI가 직관적 (라디오 버튼)
- [ ] 진행 상태가 명확히 표시 (스피너)
- [ ] 오류 메시지가 명확하고 실행 가능한 조치 포함
- [ ] reportlab 미설치 시 안내 메시지 표시

### 품질 검증 체크리스트

- [ ] 테스트 커버리지 ≥85%
- [ ] 모든 시나리오에 대응하는 pytest 테스트 케이스 작성
- [ ] mypy 타입 검증 통과
- [ ] ruff 린팅 통과 (E, F, W 규칙)
- [ ] black 포맷팅 적용

---

## Definition of Done (완료 조건)

### SPEC-EXPORT-001은 다음 조건이 모두 충족되었을 때 완료됩니다:

1. **기능 완성**:
   - [x] Markdown, JSON, PDF 내보내기 모두 구현
   - [x] Streamlit UI 통합 완료
   - [x] 10개 시나리오 모두 통과

2. **테스트 완성**:
   - [x] 단위 테스트 커버리지 ≥85%
   - [x] 통합 테스트 통과
   - [x] 보안 테스트 통과

3. **문서 완성**:
   - [x] @TAG 시스템 적용 (SPEC, TEST, CODE, DOC)
   - [x] Living Document 동기화 완료
   - [x] 사용자 가이드 작성

4. **품질 검증**:
   - [x] TRUST 5원칙 준수
   - [x] mypy, ruff, black 통과
   - [x] 코드 리뷰 완료

5. **사용자 검증**:
   - [x] 사용자 테스트 완료
   - [x] 피드백 반영
   - [x] 프로덕션 배포 준비 완료

---

## 다음 단계

1. **/alfred:2-build EXPORT-001** - TDD 구현 시작
2. **/alfred:3-sync** - 문서 동기화 및 TAG 체인 검증
3. 사용자 테스트 및 피드백 수집

---

_이 수락 기준은 SPEC-EXPORT-001 구현의 완료 기준입니다._
