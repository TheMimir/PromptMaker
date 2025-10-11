# @DOC:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

# PromptMaker pytest 테스트 가이드

## 개요

이 디렉토리는 **SPEC-TEST-001** 기반 pytest 테스트 프레임워크를 포함합니다.

- **TDD 원칙**: RED → GREEN → REFACTOR 사이클 준수
- **테스트 커버리지 목표**: 85% 이상
- **테스트 독립성**: 각 테스트는 독립적이고 결정적으로 실행
- **@TAG 추적성**: 모든 테스트에 @TEST:TEST-001 TAG 적용

---

## 디렉토리 구조

```
tests/
├── __init__.py                          # 테스트 패키지 초기화
├── conftest.py                          # pytest 공통 픽스처
├── README.md                            # 이 파일
├── ai_prompt_maker/                     # 핵심 로직 테스트
│   ├── __init__.py
│   ├── test_models.py                   # PromptComponent, PromptTemplate 테스트 (82개 테스트)
│   ├── test_prompt_generator.py         # PromptGenerator 테스트 (30개 테스트)
│   └── test_service.py                  # PromptMakerService 테스트 (60개 테스트)
├── components/                          # UI 컴포넌트 테스트
│   └── __init__.py
└── utils/                               # 유틸리티 테스트
    ├── __init__.py
    ├── test_data_handler.py             # DataHandler 테스트 (16개 테스트)
    └── test_template_storage.py         # TemplateStorageManager 테스트 (18개 테스트)
```

**총 테스트 수**: 약 206개 테스트
**총 코드 라인**: 2,250 LOC

---

## 테스트 실행 방법

### 1. 가상 환경 설정 (필수)

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements-dev.txt
```

### 2. 테스트 실행

#### 기본 실행 (모든 테스트 + 커버리지)
```bash
./run_tests.sh
```

#### 빠른 실행 (커버리지 없음)
```bash
./run_tests.sh --fast
```

#### 단위 테스트만 실행
```bash
./run_tests.sh --unit
```

#### 커버리지 상세 보고서
```bash
./run_tests.sh --coverage
```

#### 직접 pytest 사용
```bash
# 모든 테스트 실행
pytest -v

# 특정 모듈만 테스트
pytest tests/ai_prompt_maker/test_models.py -v

# 특정 테스트 함수만 실행
pytest tests/ai_prompt_maker/test_models.py::TestPromptComponentCreation::test_should_create_valid_component_with_goal -v

# 커버리지 측정
pytest --cov=ai_prompt_maker --cov=components --cov=utils --cov-report=html
```

---

## 테스트 마커 (Markers)

pytest.ini에 정의된 커스텀 마커:

- `@pytest.mark.unit`: 독립적인 단위 테스트
- `@pytest.mark.integration`: 통합 테스트
- `@pytest.mark.slow`: 실행 시간이 긴 테스트
- `@pytest.mark.ui`: Streamlit UI 테스트

사용 예시:
```python
@pytest.mark.unit
def test_should_create_component():
    # 단위 테스트
    pass

@pytest.mark.integration
def test_should_integrate_with_service():
    # 통합 테스트
    pass
```

---

## 픽스처 (Fixtures)

`conftest.py`에서 제공하는 공통 픽스처:

### 파일 시스템 픽스처
- `temp_dir`: 임시 디렉토리 (자동 정리)
- `test_data_dir`: 테스트 데이터 디렉토리
- `test_templates_dir`: 템플릿 저장 디렉토리

### 설정 픽스처
- `sample_config`: 샘플 설정 데이터
- `config_file`: 임시 config.json 파일

### 모델 픽스처
- `sample_component`: 유효한 PromptComponent 객체
- `sample_version`: 유효한 PromptVersion 객체
- `sample_template`: 유효한 PromptTemplate 객체

### 서비스 픽스처
- `prompt_generator`: PromptGenerator 인스턴스
- `service`: PromptMakerService 인스턴스 (임시 디렉토리 사용)

### 유틸리티 픽스처
- `assert_valid_json`: JSON 유효성 검증 함수
- `assert_file_exists`: 파일 존재 검증 함수

---

## 테스트 작성 가이드

### Given/When/Then 패턴 사용

```python
def test_should_create_component(self):
    # Given - 테스트 준비
    goal = "테스트 목표"

    # When - 테스트 실행
    component = PromptComponent(goal=goal)

    # Then - 검증
    assert component.goal == goal
```

### 명확한 테스트 함수명

- `test_should_[동작]_when_[조건]`
- `test_should_[동작]_with_[입력]`
- `test_should_fail_[동작]_when_[조건]`

예시:
```python
def test_should_reject_goal_exceeding_max_length(self):
    # 최대 길이 초과 시 거부해야 함
    pass

def test_should_return_none_if_template_not_found(self):
    # 템플릿이 없으면 None 반환해야 함
    pass
```

### 테스트 제약사항 준수

- **파일 크기**: 각 테스트 파일 ≤ 300 LOC
- **함수 크기**: 각 테스트 함수 ≤ 50 LOC
- **독립성**: 테스트 간 의존성 없음
- **결정성**: 항상 동일한 결과 반환

---

## 보안 테스트

**중요**: `test_service.py`에 Path Traversal 방어 테스트 포함

```python
def test_should_reject_template_id_with_path_traversal(self, service):
    """Path Traversal 시도를 거부해야 한다"""
    malicious_id = "../../../etc/passwd"

    with pytest.raises(ValueError, match="Invalid template ID"):
        service._sanitize_template_id(malicious_id)
```

이 테스트는 **SPEC-TEST-001 제약사항**을 검증합니다.

---

## 커버리지 보고서

### 터미널 출력
```bash
pytest --cov --cov-report=term-missing
```

### HTML 보고서
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

### 커버리지 목표
- **전체 커버리지**: ≥ 85%
- **핵심 모듈 (ai_prompt_maker)**: ≥ 90%
- **유틸리티 (utils)**: ≥ 80%

---

## 문제 해결

### pytest를 찾을 수 없음
```bash
# 가상 환경이 활성화되었는지 확인
which python
# 출력: .../venv/bin/python (가상 환경 경로)

# pytest 재설치
pip install pytest pytest-cov
```

### 테스트 실행 시간이 너무 길 때
```bash
# 병렬 실행 (pytest-xdist 필요)
pytest -n auto
```

### 캐시 문제
```bash
# pytest 캐시 삭제
rm -rf .pytest_cache
pytest --cache-clear
```

---

## CI/CD 통합

### GitHub Actions 예시
```yaml
- name: Run pytest
  run: |
    pip install -r requirements-dev.txt
    pytest --cov --cov-report=xml --cov-fail-under=85
```

### 로컬에서 CI 검증
```bash
# CI 환경 시뮬레이션
pytest --cov --cov-fail-under=85 --strict-markers
```

---

## 관련 문서

- **SPEC 문서**: `.moai/specs/SPEC-TEST-001/spec.md`
- **개발 가이드**: `.moai/memory/development-guide.md`
- **CLAUDE.md**: 프로젝트 개요 및 워크플로우

---

## 라이센스

MIT License - PromptMaker Project
