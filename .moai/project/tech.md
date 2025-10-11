---
id: TECH-001
version: 0.2.0
status: active
created: 2025-10-01
updated: 2025-10-11
authors: ["@tech-lead", "@project-manager"]
---

# PromptMaker Technology Stack

## HISTORY

### v0.2.0 (2025-10-11)
- **CHANGED**: 실제 기술 스택 반영 (Python 3.8+, Streamlit 1.37.0+)
- **AUTHOR**: @project-manager
- **REVIEW**: requirements.txt 및 소스 코드 분석 완료
- **SECTIONS**: Stack, Framework, Quality, Security, Deploy 실제 정보로 갱신

### v0.1.0 (2025-10-01)
- **INITIAL**: 프로젝트 기술 스택 문서 작성
- **AUTHOR**: @tech-lead
- **SECTIONS**: Stack, Framework, Quality, Security, Deploy

---

## @DOC:STACK-001 언어 & 런타임

### 주 언어 선택

- **언어**: Python
- **버전**: 3.8 이상 (Python 3.13 테스트 완료)
- **선택 이유**:
  - Streamlit 프레임워크와의 완벽한 통합
  - 빠른 프로토타이핑 및 웹 앱 개발
  - 풍부한 데이터 처리 라이브러리 생태계
  - 크로스 플랫폼 지원 (Windows, macOS, Linux)
- **패키지 매니저**: pip (requirements.txt 기반)

### 멀티 플랫폼 지원

| 플랫폼 | 지원 상태 | 검증 도구 | 주요 제약 |
|--------|-----------|-----------|-----------|
| **Windows** | 완전 지원 | `run.py` (UTF-8 인코딩 자동 설정) | chcp 65001 필요 (자동 처리) |
| **macOS** | 완전 지원 | `python3 run.py` | Python 3.8+ 필수 |
| **Linux** | 완전 지원 | `python3 run.py` | Python 3.8+ 필수 |

**시스템 요구사항**:
- 최소 메모리: 2GB RAM
- 디스크 공간: 100MB 이상
- 네트워크: 로컬 실행 시 불필요 (Streamlit Cloud 배포 시 필요)

## @DOC:FRAMEWORK-001 핵심 프레임워크 & 라이브러리

### 1. 주요 의존성 (Production)

```ini
# Core dependencies
streamlit>=1.37.0,<2.0.0         # 웹 UI 프레임워크
python-dateutil>=2.9.0,<3.0.0    # 날짜/시간 처리

# Security dependencies
bleach>=6.0.0,<7.0.0             # HTML sanitization (XSS 방지)
jsonschema>=4.20.0,<5.0.0        # JSON 스키마 검증

# Timezone support
pytz>=2024.1                     # 시간대 처리
```

**주요 라이브러리 선택 이유**:
- **Streamlit 1.37.0+**: 리액티브 UI, 세션 상태 관리, 탭 위젯 지원
- **bleach 6.0.0+**: XSS 공격 방지를 위한 HTML sanitization (OWASP 권장)
- **jsonschema 4.20.0+**: config.json 및 output_formats.json 검증
- **pytz 2024.1**: 템플릿 생성/수정 시간 기록

### 2. 개발 도구 (Development)

```ini
# 권장 개발 도구 (requirements-dev.txt 생성 필요)
pytest>=7.4.0                    # 테스트 프레임워크
pytest-cov>=4.1.0                # 테스트 커버리지
mypy>=1.8.0                      # 정적 타입 검사
ruff>=0.1.0                      # 린터 + 포매터 (flake8 + black 대체)
black>=23.0.0                    # 코드 포매터 (백업용)
```

**개발 도구 선택 이유**:
- **pytest**: Python 표준 테스트 프레임워크, 픽스처 및 파라미터화 지원
- **mypy**: 타입 힌트 검증으로 런타임 오류 사전 방지
- **ruff**: 빠른 린팅 (Rust 기반), black + flake8 통합
- **pytest-cov**: 테스트 커버리지 85% 목표 달성 검증

### 3. 빌드 시스템

- **빌드 도구**: 없음 (인터프리터 언어, 컴파일 불필요)
- **번들링**: Streamlit 내장 번들링 (JavaScript + CSS 자동 처리)
- **타겟**: 웹 브라우저 (Chromium, Firefox, Safari 지원)
- **실행 방식**:
  ```bash
  # 로컬 개발
  streamlit run app.py

  # 또는 run.py 스크립트
  python run.py
  ```

## @DOC:QUALITY-001 품질 게이트 & 정책

### 테스트 커버리지

- **목표**: 85% 이상
- **측정 도구**: pytest-cov
- **실패 시 대응**: PR 머지 차단 (Team 모드), 경고 표시 (Personal 모드)
- **현재 상태**: 0% (테스트 코드 없음 - 우선 개선 필요)

### 정적 분석

| 도구 | 역할 | 설정 파일 | 실패 시 조치 |
|------|------|-----------|--------------|
| **ruff** | 린터 + 포매터 | `ruff.toml` (생성 필요) | PR 차단 (Team 모드) |
| **black** | 코드 포매터 | `pyproject.toml` (생성 필요) | 자동 포맷 적용 |
| **mypy** | 타입 체커 | `mypy.ini` (생성 필요) | 경고 표시 (점진적 도입) |

### 자동화 스크립트 (생성 필요)

```bash
# 품질 검사 파이프라인 (Makefile 또는 scripts/ 추천)
pytest tests/ --cov=ai_prompt_maker --cov=components --cov=utils --cov-report=html
ruff check .
ruff format .
mypy ai_prompt_maker/ components/ utils/
```

**현재 상태**:
- 테스트 파일 없음 → `tests/` 디렉토리 생성 및 TDD 사이클 도입 필요
- 린터 설정 없음 → `ruff.toml` 생성 필요
- 타입 힌트 부분 적용 → mypy strict 모드 점진적 도입

## @DOC:SECURITY-001 보안 정책 & 운영

### 비밀 관리

- **정책**: 비밀 정보 없음 (로컬 파일 시스템 기반, API 키 불필요)
- **도구**: 환경변수 없음 (Streamlit secrets 미사용)
- **검증**: 코드 리뷰 시 하드코딩된 비밀 정보 확인

### 의존성 보안

```json
{
  "security": {
    "audit_tool": "pip-audit (권장)",
    "update_policy": "Minor 버전 자동 업데이트 (patch), Major 버전 수동 검토",
    "vulnerability_threshold": "Critical/High 취약점 발견 시 즉시 업데이트"
  }
}
```

**보안 점검 명령어**:
```bash
# 의존성 취약점 스캔
pip-audit

# 의존성 업데이트 확인
pip list --outdated
```

### XSS 방지 (bleach)

- **적용 위치**: `app.py` 내 `sanitize_html()` 함수
- **허용 태그**: `div, span, h1-h3, p, br, style`
- **허용 속성**: `style, class`
- **허용 스타일**: `color, background, font-*, margin, padding, border, display` 등 화이트리스트

### 로깅 정책

- **로그 수준**: INFO (개발), WARNING (프로덕션)
- **민감정보 마스킹**: 사용자 생성 프롬프트 내용은 로그에 기록 안함
- **보존 정책**: Streamlit Cloud 기본 정책 따름 (7일)

## @DOC:DEPLOY-001 배포 채널 & 전략

### 1. 배포 채널

- **주 채널**: Streamlit Cloud (권장), Render, 로컬 실행
- **릴리스 절차**:
  1. GitHub main 브랜치에 푸시
  2. Streamlit Cloud 자동 배포 (Webhook 연동)
  3. 배포 후 smoke test (주요 기능 동작 확인)
- **버전 정책**: Semantic Versioning (v2.3.0)
- **rollback 전략**: GitHub 이전 커밋으로 revert 후 재배포

### 2. 개발 설치

```bash
# 개발자 모드 설정
git clone https://github.com/TheMimir/PromptMaker.git
cd PromptMaker

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 도구 설치 (선택사항)
pip install -r requirements-dev.txt  # 생성 필요

# 애플리케이션 실행
python run.py
# 또는
streamlit run app.py
```

### 3. CI/CD 파이프라인 (구축 예정)

| 단계 | 목적 | 사용 도구 | 성공 조건 |
|------|------|-----------|-----------|
| **Lint** | 코드 품질 검사 | ruff | 린트 오류 0개 |
| **Type Check** | 타입 안전성 검증 | mypy | 타입 오류 0개 (점진적) |
| **Test** | 자동 테스트 실행 | pytest | 모든 테스트 통과, 커버리지 85%+ |
| **Deploy** | Streamlit Cloud 배포 | GitHub Actions | 배포 성공, smoke test 통과 |

**현재 상태**: CI/CD 파이프라인 없음 → `.github/workflows/ci.yml` 생성 필요

## 환경별 설정

### 개발 환경 (`dev`)

```bash
# 로컬 개발 모드
export STREAMLIT_ENV=development
export LOG_LEVEL=debug

# Streamlit 실행 (핫 리로드 활성화)
streamlit run app.py --server.runOnSave true
```

### 테스트 환경 (`test`)

```bash
# 테스트 환경 (단위 테스트용)
export STREAMLIT_ENV=test
export LOG_LEVEL=info

# pytest 실행
pytest tests/ -v
```

### 프로덕션 환경 (`production`)

```bash
# Streamlit Cloud 환경 (자동 설정)
export STREAMLIT_ENV=production
export LOG_LEVEL=warning

# Streamlit Cloud에서 자동 실행
```

## @CODE:TECH-DEBT-001 기술 부채 관리

### 현재 기술 부채

1. **테스트 코드 부재** (Critical)
   - **설명**: 전체 프로젝트에 단위 테스트 없음, 커버리지 0%
   - **우선순위**: P0 (최우선)
   - **해결 방안**: `/alfred:1-spec` → `/alfred:2-build` TDD 사이클 도입
   - **예상 공수**: 4주 (핵심 모듈 우선, 커버리지 85% 목표)

2. **타입 힌트 불완전** (High)
   - **설명**: 일부 함수에만 타입 힌트 적용, mypy 검증 없음
   - **우선순위**: P1
   - **해결 방안**: mypy strict 모드 점진적 도입, 신규 코드부터 강제
   - **예상 공수**: 2주

3. **개발 도구 설정 부재** (Medium)
   - **설명**: ruff.toml, mypy.ini, pytest.ini 없음
   - **우선순위**: P2
   - **해결 방안**: 표준 설정 파일 생성, pre-commit hook 도입
   - **예상 공수**: 1주

4. **CI/CD 파이프라인 없음** (Medium)
   - **설명**: 수동 배포, 품질 게이트 자동화 없음
   - **우선순위**: P2
   - **해결 방안**: GitHub Actions 워크플로우 구축
   - **예상 공수**: 1주

### 개선 계획

- **단기 (1개월)**: 테스트 코드 추가 (P0), 개발 도구 설정 (P2)
- **중기 (3개월)**: 타입 힌트 완성 (P1), CI/CD 구축 (P2)
- **장기 (6개월+)**: 테스트 커버리지 85% 달성, mypy strict 모드 전체 적용

## EARS 기술 요구사항 작성법

### 기술 스택에서의 EARS 활용

기술적 의사결정과 품질 게이트 설정 시 EARS 구문을 활용하여 명확한 기술 요구사항을 정의하세요:

#### 기술 스택 EARS 예시
```markdown
### Ubiquitous Requirements (기본 기술 요구사항)
- 시스템은 Python 3.8 이상을 지원해야 한다
- 시스템은 Streamlit 1.37.0 이상을 사용해야 한다
- 시스템은 크로스 플랫폼 호환성을 제공해야 한다 (Windows, macOS, Linux)

### Event-driven Requirements (이벤트 기반 기술)
- WHEN 의존성 취약점이 발견되면, 시스템은 Critical/High 취약점을 즉시 패치해야 한다
- WHEN 테스트가 실행되면, 시스템은 커버리지 보고서를 생성해야 한다
- WHEN bleach 라이브러리가 없으면, 시스템은 경고 로그를 출력하고 계속 실행해야 한다

### State-driven Requirements (상태 기반 기술)
- WHILE 개발 모드일 때, 시스템은 핫 리로드를 제공해야 한다
- WHILE 프로덕션 모드일 때, 시스템은 디버그 정보를 숨겨야 한다

### Optional Features (선택적 기술)
- WHERE pytest-cov가 설치되면, 시스템은 커버리지 측정을 활성화할 수 있다
- WHERE mypy가 설치되면, 시스템은 타입 검사를 수행할 수 있다

### Constraints (기술적 제약사항)
- IF 테스트 커버리지가 85% 미만이면, PR 머지를 차단해야 한다 (Team 모드)
- Python 파일은 300 LOC를 초과하지 않아야 한다
- 함수는 50 LOC를 초과하지 않아야 한다
- 매개변수는 5개를 초과하지 않아야 한다
```

---

_이 기술 스택은 `/alfred:2-build` 실행 시 TDD 도구 선택과 품질 게이트 적용의 기준이 됩니다._
