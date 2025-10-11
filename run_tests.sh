#!/bin/bash
# @CODE:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md | TEST: tests/

# pytest 테스트 실행 스크립트
# 사용법: ./run_tests.sh [옵션]

echo "========================================="
echo "PromptMaker pytest 테스트 실행"
echo "========================================="

# 가상 환경 확인
if [ ! -d "venv" ]; then
    echo ""
    echo "⚠️ 가상 환경이 없습니다. 다음 명령으로 생성하세요:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements-dev.txt"
    echo ""
    exit 1
fi

# 가상 환경 활성화
source venv/bin/activate

# pytest 설치 확인
if ! python -c "import pytest" 2>/dev/null; then
    echo ""
    echo "⚠️ pytest가 설치되어 있지 않습니다. 다음 명령으로 설치하세요:"
    echo "   pip install -r requirements-dev.txt"
    echo ""
    exit 1
fi

# 테스트 실행 (pytest.ini 설정 사용)
echo ""
echo "📋 테스트 실행 중..."
echo ""

# 기본 옵션: verbose, coverage
if [ "$1" == "--fast" ]; then
    # 빠른 테스트 (커버리지 없음)
    pytest -v
elif [ "$1" == "--coverage" ]; then
    # 커버리지 상세 보고서
    pytest -v --cov --cov-report=html --cov-report=term-missing
elif [ "$1" == "--unit" ]; then
    # 단위 테스트만
    pytest -v -m unit
elif [ "$1" == "--integration" ]; then
    # 통합 테스트만
    pytest -v -m integration
else
    # 기본: 모든 테스트 + 커버리지
    pytest -v --cov --cov-report=html --cov-report=term-missing
fi

echo ""
echo "========================================="
echo "테스트 완료!"
echo "========================================="
echo ""
echo "📊 HTML 커버리지 보고서: htmlcov/index.html"
echo ""
