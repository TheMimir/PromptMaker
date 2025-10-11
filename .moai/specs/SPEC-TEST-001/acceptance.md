# SPEC-TEST-001 Acceptance Criteria

## AC1: pytest 기본 실행

**Given**: 테스트 디렉토리(`tests/`)가 구성되어 있고
**When**: `pytest` 명령을 실행하면
**Then**:
- 모든 테스트가 실행되어야 한다
- 테스트 결과(PASSED/FAILED)가 터미널에 출력되어야 한다
- 실패한 테스트가 있으면 exit code 1을 반환해야 한다

**검증 방법**:
```bash
pytest -v
echo $?  # exit code 확인
```

**예상 출력**:
```
tests/ai_prompt_maker/test_service.py::test_generate_prompt_success PASSED
tests/utils/test_data_handler.py::test_load_config PASSED

======================== 2 passed in 0.15s ========================
```

---

## AC2: 커버리지 측정 및 보고서 생성

**Given**: pytest-cov가 설치되어 있고, pytest.ini에 커버리지 설정이 있고
**When**: `pytest --cov` 명령을 실행하면
**Then**:
- 테스트 커버리지가 측정되어야 한다
- HTML 보고서가 `htmlcov/index.html`에 생성되어야 한다
- 터미널에 커버리지 요약이 출력되어야 한다
- 누락된 라인(missing lines)이 표시되어야 한다

**검증 방법**:
```bash
pytest --cov --cov-report=html --cov-report=term-missing
ls htmlcov/index.html  # HTML 보고서 존재 확인
open htmlcov/index.html  # 브라우저에서 열기
```

**예상 출력**:
```
---------- coverage: platform darwin, python 3.13 -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
ai_prompt_maker/__init__.py                   2      0   100%
ai_prompt_maker/service.py                   50      5    90%   45-49
ai_prompt_maker/models.py                    30      2    93%   28-29
utils/data_handler.py                        25      3    88%   15-17
utils/template_storage.py                   40      6    85%   30-35
components/template_manager.py               60     15    75%   40-54
-----------------------------------------------------------------------
TOTAL                                       207     31    85%
```

---

## AC3: 커버리지 임계값 검증

**Given**: pytest.ini에 `--cov-fail-under=85` 설정이 있고
**When**: 커버리지가 85% 미만이면
**Then**:
- pytest가 실패해야 한다 (exit code 1)
- "FAIL Required test coverage of 85% not reached" 메시지가 출력되어야 한다

**검증 방법**:
```bash
pytest --cov --cov-fail-under=85
echo $?  # 커버리지 < 85%이면 1, >= 85%이면 0
```

**예상 출력 (실패 케이스)**:
```
---------- coverage: platform darwin, python 3.13 -----------
TOTAL                                       207     50    76%

FAIL Required test coverage of 85% not reached. Total coverage: 76.00%
```

**예상 출력 (성공 케이스)**:
```
---------- coverage: platform darwin, python 3.13 -----------
TOTAL                                       207     31    85%

Required test coverage of 85% reached. Total coverage: 85.00%
```

---

## AC4: 테스트 마커 필터링

**Given**: 테스트에 마커(`@pytest.mark.unit`)가 설정되어 있고
**When**: `pytest -m unit` 명령을 실행하면
**Then**:
- unit 마커가 있는 테스트만 실행되어야 한다
- 다른 마커의 테스트는 실행되지 않아야 한다

**검증 방법**:
```python
# tests/ai_prompt_maker/test_service.py
import pytest

@pytest.mark.unit
def test_generate_prompt_success():
    """단위 테스트: 프롬프트 생성 성공"""
    pass

@pytest.mark.integration
def test_generate_prompt_with_external_api():
    """통합 테스트: 외부 API 연동"""
    pass

@pytest.mark.slow
def test_heavy_processing():
    """느린 테스트: 대량 데이터 처리"""
    pass
```

```bash
# unit 테스트만 실행
pytest -m unit -v

# integration 테스트만 실행
pytest -m integration -v

# slow 테스트 제외
pytest -m "not slow" -v

# unit 또는 integration 테스트 실행
pytest -m "unit or integration" -v
```

**예상 출력**:
```
pytest -m unit -v
======================== test session starts ========================
collected 3 items / 2 deselected / 1 selected

tests/ai_prompt_maker/test_service.py::test_generate_prompt_success PASSED

==================== 1 passed, 2 deselected in 0.05s ====================
```

---

## AC5: 독립적이고 결정적인 테스트

**Given**: 여러 테스트가 작성되어 있고
**When**: 테스트를 여러 번 실행하거나 순서를Energy 바꿔 실행하면
**Then**:
- 모든 테스트가 항상 같은 결과를 반환해야 한다
- 테스트 순서에 관계없이 모든 테스트가 통과해야 한다
- 테스트 간 상태 공유가 없어야 한다

**검증 방법**:
```bash
# 10번 반복 실행
for i in {1..10}; do
  echo "Run $i"
  pytest -q || break
done

# 랜덤 순서 실행 (pytest-randomly 필요)
pytest --randomly-seed=42
pytest --randomly-seed=12345
```

**안티패턴 (피해야 할 코드)**:
```python
# ❌ 나쁜 예: 전역 상태 공유
global_counter = 0

def test_increment_counter():
    global global_counter
    global_counter += 1
    assert global_counter == 1  # 두 번째 실행 시 실패!

# ❌ 나쁜 예: 파일 시스템 상태 공유
def test_create_file():
    with open("test.txt", "w") as f:
        f.write("test")
    assert os.path.exists("test.txt")

def test_read_file():
    # test_create_file 실행 순서에 의존
    with open("test.txt", "r") as f:
        content = f.read()
    assert content == "test"
```

**좋은 예 (독립적인 테스트)**:
```python
# ✅ 좋은 예: 픽스처로 상태 격리
@pytest.fixture
def temp_counter():
    """각 테스트마다 독립적인 카운터"""
    return 0

def test_increment_counter(temp_counter):
    temp_counter += 1
    assert temp_counter == 1

# ✅ 좋은 예: 임시 파일 시스템 사용
@pytest.fixture
def temp_file(tmp_path):
    """임시 디렉토리에 파일 생성"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test")
    return file_path

def test_read_file(temp_file):
    content = temp_file.read_text()
    assert content == "test"
```

---

## AC6: 병렬 테스트 실행 (선택적)

**Given**: pytest-xdist가 설치되어 있고
**When**: `pytest -n auto` 명령을 실행하면
**Then**:
- CPU 코어 수만큼 병렬로 테스트가 실행되어야 한다
- 총 실행 시간이 단일 실행보다 짧아야 한다
- 모든 테스트가 정상적으로 통과해야 한다

**검증 방법**:
```bash
# 단일 실행 시간 측정
time pytest

# 병렬 실행 시간 측정
time pytest -n auto

# 병렬 실행 시간이 더 짧아야 함
```

**예상 출력**:
```bash
# 단일 실행
pytest  3.45s user 0.32s system 99% cpu 3.789 total

# 병렬 실행 (8코어)
pytest -n auto  4.23s user 0.45s system 680% cpu 0.687 total
```

**병렬 실행 주의사항**:
- 테스트는 완전히 독립적이어야 함 (상태 공유 없음)
- 파일 시스템 접근 시 충돌 방지 (tmp_path 사용)
- 데이터베이스 사용 시 각 워커별 독립 DB

---

## AC7: 테스트 실행 시간 제약

**Given**: 전체 테스트 스위트가 작성되어 있고
**When**: `pytest` 명령을 실행하면
**Then**:
- 전체 테스트 실행 시간이 5분을 초과하지 않아야 한다
- 느린 테스트는 `@pytest.mark.slow` 마커로 표시되어야 한다
- 각 단위 테스트는 100ms 이내에 완료되어야 한다

**검증 방법**:
```bash
# 실행 시간 측정
time pytest

# 느린 테스트만 표시
pytest --durations=10

# 느린 테스트 제외 실행
pytest -m "not slow"
```

**예상 출력**:
```
======================== slowest 10 durations ========================
2.50s call     tests/integration/test_api_client.py::test_external_api
0.85s call     tests/integration/test_database.py::test_bulk_insert
0.45s call     tests/ai_prompt_maker/test_service.py::test_complex_prompt
0.12s call     tests/utils/test_data_handler.py::test_load_large_file
0.08s call     tests/ai_prompt_maker/test_models.py::test_validation
...
======================== 50 passed in 4.85s ========================
```

**느린 테스트 분리**:
```python
import pytest
import time

@pytest.mark.slow
def test_heavy_processing():
    """느린 테스트: 대량 데이터 처리"""
    time.sleep(2)  # 시뮬레이션
    assert True

# 빠른 테스트만 실행
pytest -m "not slow"  # 0.15s

# 전체 테스트 실행
pytest  # 2.15s
```

---

## AC8: conftest.py 픽스처 재사용

**Given**: `tests/conftest.py`에 공통 픽스처가 정의되어 있고
**When**: 여러 테스트에서 같은 픽스처를 사용하면
**Then**:
- 픽스처가 자동으로 주입되어야 한다
- 테스트마다 픽스처가 독립적으로 실행되어야 한다
- 픽스처 스코프(function, class, module, session)가 올바르게 동작해야 한다

**검증 방법**:
```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_prompt_component():
    """함수 스코프: 각 테스트마다 새로 생성"""
    return {
        "role": "게임 디자이너",
        "goal": "밸런스 조정",
        "context": "레벨 60 전설 무기"
    }

@pytest.fixture(scope="module")
def shared_config():
    """모듈 스코프: 같은 파일의 테스트들이 공유"""
    print("\n🔧 Setting up shared config")
    config = {"version": "0.1.0"}
    yield config
    print("\n🧹 Tearing down shared config")

@pytest.fixture(scope="session")
def database_connection():
    """세션 스코프: 전체 테스트 실행 중 1번만 생성"""
    print("\n🗄️ Connecting to database")
    db = {"connected": True}
    yield db
    print("\n🗄️ Closing database connection")
```

```python
# tests/ai_prompt_maker/test_service.py
def test_generate_prompt(sample_prompt_component):
    """픽스처 자동 주입"""
    assert sample_prompt_component["role"] == "게임 디자이너"

def test_modify_prompt(sample_prompt_component):
    """각 테스트는 독립적인 픽스처 인스턴스를 받음"""
    sample_prompt_component["role"] = "프로그래머"
    assert sample_prompt_component["role"] == "프로그래머"

def test_original_prompt(sample_prompt_component):
    """이전 테스트의 수정이 영향을 주지 않음"""
    assert sample_prompt_component["role"] == "게임 디자이너"  # ✅ 통과!

def test_with_config(shared_config):
    """모듈 스코프 픽스처 사용"""
    assert shared_config["version"] == "0.1.0"

def test_with_database(database_connection):
    """세션 스코프 픽스처 사용"""
    assert database_connection["connected"] is True
```

**예상 출력**:
```
======================== test session starts ========================
🗄️ Connecting to database
🔧 Setting up shared config

tests/ai_prompt_maker/test_service.py::test_generate_prompt PASSED
tests/ai_prompt_maker/test_service.py::test_modify_prompt PASSED
tests/ai_prompt_maker/test_service.py::test_original_prompt PASSED
tests/ai_prompt_maker/test_service.py::test_with_config PASSED
tests/ai_prompt_maker/test_service.py::test_with_database PASSED

🧹 Tearing down shared config
🗄️ Closing database connection
======================== 5 passed in 0.25s ========================
```

---

## AC9: HTML 커버리지 보고서 상세 정보

**Given**: pytest-cov가 HTML 보고서를 생성했고
**When**: `htmlcov/index.html`을 브라우저에서 열면
**Then**:
- 전체 커버리지 요약이 표시되어야 한다
- 파일별 커버리지 비율이 표시되어야 한다
- 클릭 시 소스 코드와 누락된 라인이 하이라이트되어야 한다

**검증 방법**:
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

**보고서 구조**:
```
htmlcov/
├── index.html              # 전체 요약
├── status.json             # 커버리지 데이터
├── ai_prompt_maker_service_py.html   # 개별 파일 상세
├── utils_data_handler_py.html
└── ...
```

**확인 항목**:
- [ ] 전체 커버리지 퍼센트 표시
- [ ] 파일별 커버리지 목록
- [ ] 커버된 라인 (초록색 하이라이트)
- [ ] 누락된 라인 (빨간색 하이라이트)
- [ ] 부분 커버리지 라인 (노란색 - 분기 일부만 실행)

---

## AC10: 테스트 실패 시 상세 정보 출력

**Given**: 테스트가 실패했고
**When**: pytest가 결과를 출력하면
**Then**:
- 실패한 테스트의 파일/함수명이 표시되어야 한다
- 예상 값과 실제 값이 비교되어야 한다
- 실패 지점의 코드 컨텍스트가 표시되어야 한다
- 스택 트레이스가 포함되어야 한다

**검증 방법**:
```python
# tests/ai_prompt_maker/test_service.py
def test_generate_prompt_failure():
    """의도적으로 실패하는 테스트"""
    result = generate_prompt({"role": "게임 디자이너"})
    assert result == "Expected output"  # 실패 예정
```

```bash
pytest -v
```

**예상 출력**:
```
======================== FAILURES ========================
____________ test_generate_prompt_failure ____________

    def test_generate_prompt_failure():
        """의도적으로 실패하는 테스트"""
        result = generate_prompt({"role": "게임 디자이너"})
>       assert result == "Expected output"
E       AssertionError: assert 'Actual output' == 'Expected output'
E         - Expected output
E         + Actual output

tests/ai_prompt_maker/test_service.py:15: AssertionError
======================== short test summary info ========================
FAILED tests/ai_prompt_maker/test_service.py::test_generate_prompt_failure
======================== 1 failed in 0.12s ========================
```

---

## 전체 검증 체크리스트

### 기본 기능
- [ ] AC1: pytest 기본 실행 성공
- [ ] AC2: 커버리지 보고서 생성 (HTML + 터미널)
- [ ] AC3: 커버리지 85% 이상 달성
- [ ] AC10: 테스트 실패 시 상세 정보 출력

### 고급 기능
- [ ] AC4: 테스트 마커 필터링 동작
- [ ] AC5: 독립적이고 결정적인 테스트
- [ ] AC6: 병렬 테스트 실행 (선택적)
- [ ] AC7: 실행 시간 5분 이내
- [ ] AC8: conftest.py 픽스처 재사용
- [ ] AC9: HTML 커버리지 보고서 상세 정보

### 최종 검증 명령

```bash
# 전체 품질 검증 (한 번에 실행)
pytest \
  --cov \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=85 \
  -v \
  --durations=10

# 예상 결과: ✅ 모든 테스트 통과, 커버리지 85% 이상
```

### 성공 기준 요약

**필수 요구사항** (모두 충족 필요):
1. ✅ 전체 커버리지 ≥ 85%
2. ✅ 모든 테스트 통과
3. ✅ 실행 시간 ≤ 5분
4. ✅ 독립적/결정적 테스트

**권장 요구사항** (선택적):
1. 병렬 실행 지원
2. HTML 보고서 생성
3. 테스트 마커 활용
4. 느린 테스트 분리
