# @CODE:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md | TEST: tests/

"""
pytest 설정 및 공통 픽스처

이 파일은 모든 테스트에서 사용할 수 있는 공통 픽스처와 설정을 제공합니다.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# 프로젝트 모듈 import
from ai_prompt_maker.models import (
    PromptComponent,
    PromptVersion,
    PromptTemplate,
    PromptCategory
)
from ai_prompt_maker.prompt_generator import PromptGenerator
from ai_prompt_maker.service import PromptMakerService


# ==================== 파일 시스템 픽스처 ====================

@pytest.fixture
def temp_dir(tmp_path):
    """임시 디렉토리 픽스처

    각 테스트마다 독립적인 임시 디렉토리를 제공합니다.
    테스트 종료 후 자동으로 정리됩니다.

    Args:
        tmp_path: pytest 기본 제공 임시 경로

    Returns:
        Path: 임시 디렉토리 경로
    """
    return tmp_path


@pytest.fixture
def test_data_dir(temp_dir):
    """테스트 데이터 디렉토리 픽스처

    config.json과 템플릿 저장용 디렉토리를 생성합니다.

    Args:
        temp_dir: 임시 디렉토리

    Returns:
        Path: 데이터 디렉토리 경로
    """
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def test_templates_dir(temp_dir):
    """테스트 템플릿 디렉토리 픽스처

    템플릿 JSON 파일 저장용 디렉토리를 생성합니다.

    Args:
        temp_dir: 임시 디렉토리

    Returns:
        Path: 템플릿 디렉토리 경로
    """
    templates_dir = temp_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


# ==================== 설정 픽스처 ====================

@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """샘플 설정 데이터 픽스처

    테스트용 기본 설정 데이터를 제공합니다.

    Returns:
        Dict: 설정 데이터
    """
    return {
        "keywords": {
            "role": ["게임 기획자", "게임 프로그래머", "QA 엔지니어"],
            "goal": ["기능 분석", "시스템 설계", "버그 해결"],
            "context": ["신규 기능 개발", "TestCase 제작 요청"],
            "output": ["보고서", "TestCase", "분석 결과"],
            "rule": ["상세 분석 필수", "단계별 접근"]
        },
        "categories": ["기획", "프로그램", "아트", "QA", "전체"]
    }


@pytest.fixture
def config_file(test_data_dir, sample_config):
    """설정 파일 픽스처

    임시 디렉토리에 config.json 파일을 생성합니다.

    Args:
        test_data_dir: 테스트 데이터 디렉토리
        sample_config: 샘플 설정 데이터

    Returns:
        Path: 생성된 config.json 파일 경로
    """
    config_path = test_data_dir / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=2)
    return config_path


# ==================== 모델 픽스처 ====================

@pytest.fixture
def sample_component() -> PromptComponent:
    """샘플 프롬프트 컴포넌트 픽스처

    테스트용 유효한 PromptComponent 객체를 제공합니다.

    Returns:
        PromptComponent: 샘플 컴포넌트
    """
    return PromptComponent(
        role=["게임 기획자", "QA 엔지니어"],
        goal="캐릭터 시스템 기능 분석",
        context=["신규 기능 개발", "TestCase 제작 요청"],
        document="캐릭터 레벨업 시스템에 대한 상세 분석이 필요합니다.",
        output="분석 보고서",
        rule=["상세 분석 필수", "단계별 접근"]
    )


@pytest.fixture
def sample_version(sample_component) -> PromptVersion:
    """샘플 프롬프트 버전 픽스처

    Args:
        sample_component: 샘플 컴포넌트

    Returns:
        PromptVersion: 샘플 버전
    """
    return PromptVersion(
        version=1,
        created_at=datetime.now(),
        components=sample_component,
        description="초기 버전"
    )


@pytest.fixture
def sample_template(sample_version) -> PromptTemplate:
    """샘플 프롬프트 템플릿 픽스처

    Args:
        sample_version: 샘플 버전

    Returns:
        PromptTemplate: 샘플 템플릿
    """
    return PromptTemplate(
        name="캐릭터 시스템 분석",
        category=PromptCategory.PLANNING,
        versions=[sample_version],
        tags=["캐릭터", "시스템 분석", "기획"]
    )


# ==================== 서비스 픽스처 ====================

@pytest.fixture
def prompt_generator() -> PromptGenerator:
    """프롬프트 생성기 픽스처

    Returns:
        PromptGenerator: 프롬프트 생성기 인스턴스
    """
    return PromptGenerator()


@pytest.fixture
def service(config_file, test_templates_dir) -> PromptMakerService:
    """프롬프트 메이커 서비스 픽스처

    임시 디렉토리를 사용하는 서비스 인스턴스를 제공합니다.

    Args:
        config_file: 설정 파일 경로
        test_templates_dir: 템플릿 디렉토리 경로

    Returns:
        PromptMakerService: 서비스 인스턴스
    """
    return PromptMakerService(
        config_path=str(config_file),
        templates_dir=str(test_templates_dir)
    )


# ==================== 테스트 유틸리티 ====================

@pytest.fixture
def assert_valid_json():
    """JSON 유효성 검증 헬퍼 함수

    Returns:
        Callable: JSON 검증 함수
    """
    def _assert_valid_json(json_string: str) -> Dict:
        """JSON 문자열이 유효한지 검증"""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")
    return _assert_valid_json


@pytest.fixture
def assert_file_exists():
    """파일 존재 검증 헬퍼 함수

    Returns:
        Callable: 파일 존재 검증 함수
    """
    def _assert_file_exists(file_path: Path, should_exist: bool = True):
        """파일이 존재하는지 검증"""
        if should_exist:
            assert file_path.exists(), f"File should exist: {file_path}"
        else:
            assert not file_path.exists(), f"File should not exist: {file_path}"
    return _assert_file_exists
