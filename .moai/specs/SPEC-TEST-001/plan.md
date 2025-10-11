# SPEC-TEST-001 구현 계획

## TDD 단계별 접근

### Phase 1: RED (실패하는 테스트 작성)

**목표**: pytest 환경 구축 및 기본 테스트 프레임워크 작성

#### 1.1 디렉토리 구조 생성
- [ ] `tests/` 디렉토리 생성
- [ ] `tests/__init__.py` 생성
- [ ] `tests/conftest.py` 생성 (픽스처 정의)
- [ ] 모듈별 테스트 디렉토리 생성 (ai_prompt_maker, components, utils)

#### 1.2 pytest.ini 설정
- [ ] `pytest.ini` 파일 생성
- [ ] testpaths, python_files 설정
- [ ] addopts (커버리지, verbose 등) 설정
- [ ] 테스트 마커 정의 (unit, integration, slow)

#### 1.3 기본 테스트 케이스 작성 (실패 예정)
- [ ] `tests/ai_prompt_maker/test_service.py` 작성
  - `test_generate_prompt_success()` - 프롬프트 생성 성공 케이스
  - `test_generate_prompt_with_invalid_input()` - 유효하지 않은 입력 처리
- [ ] `tests/utils/test_data_handler.py` 작성
  - `test_load_config()` - config.json 로드 테스트
  - `test_load_output_formats()` - output_formats.json 로드 테스트

#### 1.4 pytest 실행 확인
```bash
pytest -v
# 예상 결과: 테스트 실패 (구현 코드 없음)
```

### Phase 2: GREEN (테스트 통과하는 최소 코드 작성)

**목표**: 모든 테스트가 통과하도록 최소 구현

#### 2.1 핵심 모듈 테스트 구현
- [ ] `ai_prompt_maker/service.py` 테스트 통과 코드
- [ ] `utils/data_handler.py` 테스트 통과 코드
- [ ] pytest 재실행 및 통과 확인

#### 2.2 커버리지 측정
```bash
pytest --cov --cov-report=html
# 목표: 커버리지 85% 이상
```

### Phase 3: REFACTOR (코드 품질 개선)

**목표**: 코드 품질 향상, 중복 제거, 가독성 개선

#### 3.1 테스트 코드 리팩토링
- [ ] 공통 픽스처를 `conftest.py`로 추출
- [ ] 테스트 헬퍼 함수 작성
- [ ] 테스트 데이터 분리 (fixtures/)

#### 3.2 프로덕션 코드 리팩토링
- [ ] 중복 코드 제거
- [ ] 함수 분리 (50 LOC 이하)
- [ ] 타입 힌트 추가

#### 3.3 최종 검증
```bash
pytest --cov --cov-report=html --cov-fail-under=85
# 예상 결과: 모든 테스트 통과, 커버리지 85% 이상
```

## 우선순위별 테스트 모듈

### P0 (Critical) - 즉시 구현
1. **ai_prompt_maker/service.py** - 프롬프트 생성 서비스
2. **utils/data_handler.py** - JSON 설정 로더

### P1 (High) - 1주 내
3. **utils/template_storage.py** - 템플릿 CRUD
4. **ai_prompt_maker/models.py** - 데이터 모델

### P2 (Medium) - 2주 내
5. **components/template_manager.py** - UI 컴포넌트

## 예상 일정

- **Day 1**: Phase 1 (RED) - 환경 구축 및 실패 테스트 작성
- **Day 2**: Phase 2 (GREEN) - 테스트 통과 코드 작성
- **Day 3**: Phase 3 (REFACTOR) - 리팩토링 및 커버리지 85% 달성

## 리스크 및 대응

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| Streamlit UI 테스트 어려움 | High | Streamlit 테스트 대신 비즈니스 로직만 테스트 |
| 커버리지 85% 미달 | High | 핵심 모듈 우선 커버리지 확보 |
| 테스트 실행 시간 초과 | Medium | pytest-xdist 병렬 실행 도입 |

## 기술적 접근 방법

### 1. 테스트 전략

**단위 테스트 (Unit Tests)**:
- 각 함수/메서드를 독립적으로 테스트
- Mock/Stub을 활용한 의존성 격리
- 빠른 실행 속도 유지 (각 테스트 < 100ms)

**통합 테스트 (Integration Tests)**:
- JSON 파일 로드 및 파싱 검증
- 여러 컴포넌트 간 상호작용 검증
- 실제 파일 시스템 사용

### 2. 테스트 픽스처 설계

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_prompt_component():
    """프롬프트 생성 테스트용 샘플 데이터"""
    return {
        "role": "게임 디자이너",
        "goal": "밸런스 조정",
        "context": "레벨 60 전설 무기"
    }

@pytest.fixture
def mock_config():
    """설정 파일 Mock 데이터"""
    return {
        "app": {
            "title": "AI Prompt Maker",
            "version": "0.1.0"
        }
    }

@pytest.fixture
def temp_template_file(tmp_path):
    """임시 템플릿 파일 생성"""
    template = tmp_path / "template.json"
    template.write_text('{"name": "test"}')
    return template
```

### 3. 커버리지 전략

**우선순위별 커버리지 목표**:
- **P0 (Critical)**: 95% 이상 (핵심 비즈니스 로직)
- **P1 (High)**: 85% 이상 (중요 기능)
- **P2 (Medium)**: 70% 이상 (보조 기능)

**커버리지 제외 대상**:
```python
# pragma: no cover - 테스트 제외
if __name__ == "__main__":  # pragma: no cover
    main()
```

### 4. 아키텍처 설계 방향

**계층 분리**:
```
┌─────────────────────────────┐
│  Streamlit UI (components)  │  ← 최소한의 테스트 (P2)
├─────────────────────────────┤
│  Service Layer              │  ← 핵심 테스트 (P0)
│  (ai_prompt_maker/service)  │
├─────────────────────────────┤
│  Domain Layer               │  ← 핵심 테스트 (P0)
│  (models, prompt_generator) │
├─────────────────────────────┤
│  Infrastructure Layer       │  ← 통합 테스트 (P1)
│  (utils/data_handler)       │
└─────────────────────────────┘
```

**테스트 가능한 설계**:
- 의존성 주입 (Dependency Injection) 활용
- 인터페이스 기반 설계
- 순수 함수 우선 사용

## 성능 최적화

### 테스트 실행 시간 단축

1. **병렬 실행** (pytest-xdist):
```bash
pytest -n auto  # CPU 코어 수만큼 병렬 실행
```

2. **테스트 캐싱** (pytest-cache):
```bash
pytest --lf  # 마지막 실패한 테스트만 실행
pytest --ff  # 실패 테스트 우선 실행
```

3. **느린 테스트 분리**:
```python
@pytest.mark.slow
def test_heavy_processing():
    pass

# 빠른 테스트만 실행
pytest -m "not slow"
```

## 품질 게이트

### 자동화된 검증 항목

```bash
# .moai/scripts/test-quality-gate.sh
#!/bin/bash

echo "🔍 Running quality gate checks..."

# 1. 테스트 실행 및 커버리지 검증
pytest --cov --cov-report=term-missing --cov-fail-under=85 || exit 1

# 2. 타입 체크 (mypy)
mypy ai_prompt_maker/ components/ utils/ || exit 1

# 3. 코드 스타일 (black)
black --check . || exit 1

# 4. Lint (ruff)
ruff check . || exit 1

echo "✅ All quality gates passed!"
```

### CI/CD 통합 준비

```yaml
# .github/workflows/test.yml (예시)
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## 다음 단계

1. `/alfred:2-build TEST-001` 실행 → TDD 구현 시작
2. Phase 1 (RED) 완료 후 git 체크포인트
3. Phase 2 (GREEN) 완료 후 git 체크포인트
4. Phase 3 (REFACTOR) 완료 후 `/alfred:3-sync` 실행

## 참고 자료

- **pytest 공식 문서**: https://docs.pytest.org/
- **pytest-cov 문서**: https://pytest-cov.readthedocs.io/
- **Python Testing Best Practices**: https://docs.python-guide.org/writing/tests/
- **TDD with pytest**: https://testdriven.io/blog/python-test-driven-development/
