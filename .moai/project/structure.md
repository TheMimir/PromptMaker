---
id: STRUCTURE-001
version: 0.2.0
status: active
created: 2025-10-01
updated: 2025-10-11
authors: ["@architect", "@project-manager"]
---

# PromptMaker Structure Design

## HISTORY

### v0.2.0 (2025-10-11)
- **CHANGED**: 실제 프로젝트 구조 반영 (Streamlit 기반 웹 앱)
- **AUTHOR**: @project-manager
- **REVIEW**: 소스 코드 구조 분석 완료
- **SECTIONS**: Architecture, Modules, Integration 실제 정보로 갱신

### v0.1.0 (2025-10-01)
- **INITIAL**: 프로젝트 구조 설계 문서 작성
- **AUTHOR**: @architect
- **SECTIONS**: Architecture, Modules, Integration, Traceability

---

## @DOC:ARCHITECTURE-001 시스템 아키텍처

### 아키텍처 전략

**Streamlit 기반 계층형 웹 애플리케이션 아키텍처**

```
PromptMaker Architecture
├── Presentation Layer     # Streamlit UI 컴포넌트 (components/)
│   ├── 프롬프트 생성기 (game_dev, uiux 탭)
│   ├── 템플릿 관리자 (template_manager.py)
│   ├── 프롬프트 편집기 (prompt_editor.py)
│   └── 프롬프트 가이드 (prompt_guide.py)
│
├── Business Logic Layer   # 핵심 로직 (ai_prompt_maker/)
│   ├── Service (service.py) - 프롬프트 생성 오케스트레이션
│   ├── Generator (prompt_generator.py) - 프롬프트 조립 로직
│   └── Models (models.py) - 데이터 모델 및 검증
│
├── Data Access Layer      # 데이터 관리 (utils/)
│   ├── Template Storage (template_storage.py) - 템플릿 CRUD
│   └── Data Handler (data_handler.py) - JSON 설정 로드
│
└── Data Layer             # JSON 파일 저장소 (data/)
    ├── config.json - 도메인별 키워드 및 확장 규칙
    ├── output_formats.json - 출력 형식 정의
    └── prompt_guides.json - 가이드 콘텐츠
```

**선택 이유**:
- Streamlit의 리액티브 UI 패러다임을 활용한 빠른 프로토타이핑
- 로컬 파일 시스템 기반 데이터 저장으로 외부 의존성 최소화
- 도메인 주도 설계(DDD) 패턴으로 비즈니스 로직과 UI 분리
- 확장 가능한 구조: 새 도메인(domain) 추가 시 config.json만 수정

## @DOC:MODULES-001 모듈별 책임 구분

### 1. ai_prompt_maker (핵심 비즈니스 로직)

- **책임**: 프롬프트 생성 및 도메인 설정 관리
- **입력**: PromptComponent (role, goal, context, document, output, rule)
- **처리**:
  - Goal/Context/Rule expansion 적용
  - 템플릿 기반 프롬프트 조립
  - 도메인별 설정 로드 및 검증
- **출력**: 최종 프롬프트 텍스트

| 컴포넌트 | 역할 | 주요 기능 |
|----------|------|-----------|
| `service.py` | 프롬프트 생성 서비스 | `generate_prompt()`, `load_output_formats()`, `get_domain_config()` |
| `prompt_generator.py` | 프롬프트 조립 엔진 | 템플릿 기반 프롬프트 문자열 생성 |
| `models.py` | 데이터 모델 및 검증 | `PromptComponent`, `PromptTemplate`, `PromptCategory` |

### 2. components (Presentation Layer)

- **책임**: Streamlit 기반 UI 컴포넌트 렌더링
- **입력**: 사용자 상호작용 (폼 입력, 버튼 클릭, 선택)
- **처리**:
  - 도메인별 프롬프트 생성기 UI (`render_prompt_generator()`)
  - 템플릿 CRUD 인터페이스 (`render_template_manager()`)
  - 프롬프트 편집 및 버전 관리 (`render_prompt_editor()`)
  - 공식 AI 프롬프트 가이드 표시 (`render_prompt_guide()`)
- **출력**: Streamlit 위젯 및 세션 상태 업데이트

| 컴포넌트 | 역할 | 주요 기능 |
|----------|------|-----------|
| `app.py` | 메인 애플리케이션 | 5개 탭 구성, CSS 적용, 라우팅 |
| `template_manager.py` | 템플릿 관리 UI | 저장/로드/삭제/검색 |
| `prompt_editor.py` | 프롬프트 편집 UI | 직접 편집, 버전 관리 |
| `prompt_guide.py` | 가이드 콘텐츠 | 공식 AI 프롬프트 작성법 |

### 3. utils (Data Access Layer)

- **책임**: 데이터 저장/로드 및 영속성 관리
- **입력**: 템플릿 객체, 파일 경로
- **처리**:
  - localStorage 브릿지를 통한 템플릿 영속화
  - JSON 파일 읽기/쓰기
  - HTML sanitization (XSS 방지)
- **출력**: 템플릿 객체, 설정 딕셔너리

| 컴포넌트 | 역할 | 주요 기능 |
|----------|------|-----------|
| `template_storage.py` | 템플릿 CRUD | `save_template()`, `load_templates()`, localStorage 브릿지 |
| `data_handler.py` | JSON 설정 로더 | `config.json`, `output_formats.json` 읽기 |

### 4. data (Data Layer)

- **책임**: JSON 기반 설정 및 콘텐츠 저장
- **파일 구조**:
  - `config.json` (187 LOC): 도메인별 keywords, goal_expansions, context_expansions, rule_expansions
  - `output_formats.json`: 20가지 출력 형식 정의 (categories, formats)
  - `prompt_guides.json`: 프롬프트 가이드 콘텐츠

## @DOC:INTEGRATION-001 외부 시스템 통합

### Streamlit Cloud / Render 배포

- **인증 방식**: 없음 (공개 웹 앱)
- **데이터 교환**: 정적 파일 시스템 기반 (no API)
- **장애 시 대체**: 로컬 실행 모드 (`python run.py`)
- **위험도**: 낮음 (외부 의존성 없음)

### 로컬 파일 시스템 (templates/)

- **용도**: 사용자 생성 템플릿 영속화
- **의존성 수준**: 중간 (localStorage 브릿지 실패 시 세션 내 휘발)
- **성능 요구사항**: 파일 읽기/쓰기 < 100ms

### bleach 라이브러리 (HTML Sanitization)

- **용도**: XSS 공격 방지 (HTML 콘텐츠 정화)
- **의존성 수준**: 선택적 (없으면 경고 로그, 기능 동작)
- **보안 정책**: 허용 태그/속성/스타일 화이트리스트

## @DOC:TRACEABILITY-001 추적성 전략

### TAG 체계 적용

**TDD 완벽 정렬**: SPEC → 테스트 → 구현 → 문서
- `@SPEC:ID` (.moai/specs/) → `@TEST:ID` (tests/) → `@CODE:ID` (src/) → `@DOC:ID` (docs/)

**구현 세부사항**: @CODE:ID 내부 주석 레벨
- `@CODE:ID:API` - REST API, GraphQL 엔드포인트
- `@CODE:ID:UI` - 컴포넌트, 뷰, 화면
- `@CODE:ID:DATA` - 데이터 모델, 스키마, 타입
- `@CODE:ID:DOMAIN` - 비즈니스 로직, 도메인 규칙
- `@CODE:ID:INFRA` - 인프라, 데이터베이스, 외부 연동

### TAG 추적성 관리 (코드 스캔 방식)

- **검증 방법**: `/alfred:3-sync` 실행 시 `rg '@(SPEC|TEST|CODE|DOC):' -n`으로 코드 전체 스캔
- **추적 범위**: 프로젝트 전체 소스코드 (.moai/specs/, tests/, src/, docs/)
- **유지 주기**: 코드 변경 시점마다 실시간 검증
- **CODE-FIRST 원칙**: TAG의 진실은 코드 자체에만 존재

## Legacy Context

### 기존 시스템 현황

**Production Ready 상태의 Streamlit 웹 애플리케이션**

```
PromptMaker/
├── app.py                      # 메인 애플리케이션 (695 LOC)
├── run.py                      # 실행 스크립트 (37 LOC)
├── ai_prompt_maker/            # 핵심 로직
│   ├── __init__.py
│   ├── service.py              # 프롬프트 생성 서비스
│   ├── prompt_generator.py     # 프롬프트 조립 엔진
│   └── models.py               # 데이터 모델
├── components/                 # UI 컴포넌트
│   ├── __init__.py
│   ├── template_manager.py     # 템플릿 관리 UI
│   ├── prompt_editor.py        # 프롬프트 편집 UI
│   └── prompt_guide.py         # 가이드 콘텐츠
├── utils/                      # 유틸리티
│   ├── __init__.py
│   ├── template_storage.py     # 템플릿 영속화
│   └── data_handler.py         # JSON 로더
├── data/                       # JSON 설정
│   ├── config.json             # 도메인 설정 (187 LOC)
│   ├── output_formats.json     # 출력 형식 정의
│   └── prompt_guides.json      # 가이드 콘텐츠
├── .streamlit/                 # Streamlit 설정
│   └── config.toml
└── templates/                  # 사용자 템플릿 저장소
```

### 디렉토리 구조 특징

- **ai_prompt_maker/**: 도메인 로직 캡슐화, 순수 Python 모듈 (Streamlit 의존성 없음)
- **components/**: Streamlit 전용 UI 컴포넌트, 프레젠테이션 로직만 포함
- **utils/**: 데이터 액세스 및 공통 유틸리티
- **data/**: 버전 관리되는 JSON 설정 파일

### 마이그레이션 고려사항

1. **테스트 추가** - 현재 테스트 코드 없음, TDD 사이클 도입 필요 (SPEC → TEST → CODE)
2. **타입 힌트 강화** - 일부 함수에만 타입 힌트 적용, mypy 검증 체계 구축 필요
3. **에러 핸들링 표준화** - try-except 블록 일관성 부족, 중앙화된 예외 처리 필요

## TODO:STRUCTURE-001 구조 개선 계획

1. **모듈 간 인터페이스 정의** - PromptMakerService 추상 인터페이스 정의, 테스트 가능성 향상
2. **의존성 관리 전략** - requirements.txt를 pyproject.toml로 마이그레이션, Poetry 도입 검토
3. **확장성 확보 방안** - 플러그인 아키텍처 도입, 새 도메인 추가 시 코드 수정 최소화

## EARS 아키텍처 요구사항 작성법

### 구조 설계에서의 EARS 활용

아키텍처와 모듈 설계 시 EARS 구문을 활용하여 명확한 요구사항을 정의하세요:

#### 시스템 아키텍처 EARS 예시
```markdown
### Ubiquitous Requirements (아키텍처 기본 요구사항)
- 시스템은 계층형 아키텍처를 채택해야 한다
- 시스템은 프레젠테이션 레이어와 비즈니스 로직을 분리해야 한다
- 시스템은 JSON 파일 기반 설정 관리를 제공해야 한다

### Event-driven Requirements (이벤트 기반 구조)
- WHEN 사용자가 출력 형식을 선택하면, 시스템은 해당 형식 정보를 세션 상태에 저장해야 한다
- WHEN config.json 로드가 실패하면, 시스템은 기본 설정으로 fallback해야 한다
- WHEN 템플릿 저장이 완료되면, 시스템은 템플릿 목록을 새로고침해야 한다

### State-driven Requirements (상태 기반 구조)
- WHILE 개발 모드일 때, 시스템은 상세한 에러 메시지를 표시해야 한다
- WHILE 템플릿 편집 중일 때, 시스템은 자동 저장 기능을 비활성화해야 한다

### Optional Features (선택적 구조)
- WHERE bleach 라이브러리가 설치되면, 시스템은 HTML sanitization을 활성화할 수 있다
- WHERE Streamlit Cloud 환경이면, 시스템은 외부 스토리지를 활용할 수 있다

### Constraints (구조적 제약사항)
- IF 파일 크기가 300 LOC를 초과하면, 시스템은 경고를 표시해야 한다
- 각 모듈은 단일 책임 원칙(SRP)을 준수해야 한다
- 프레젠테이션 레이어는 비즈니스 로직을 직접 호출하지 않아야 한다
```

---

_이 구조는 `/alfred:2-build` 실행 시 TDD 구현의 가이드라인이 됩니다._
