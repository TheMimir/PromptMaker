# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
Models 컴포넌트 및 버전 테스트

ai_prompt_maker.models 모듈의 데이터 모델을 테스트합니다.
- PromptComponent: 프롬프트 구성 요소
- PromptVersion: 프롬프트 버전
"""

import pytest
from datetime import datetime

from ai_prompt_maker.models import (
    PromptComponent,
    PromptVersion,
)


# ==================== PromptComponent 테스트 ====================

class TestPromptComponentCreation:
    """PromptComponent 생성 테스트"""

    @pytest.mark.unit
    def test_should_create_valid_component_with_goal(self):
        """유효한 goal이 있으면 컴포넌트를 생성할 수 있어야 한다"""
        # Given/When
        component = PromptComponent(goal="테스트 목표")

        # Then
        assert component.goal == "테스트 목표"

    @pytest.mark.unit
    def test_should_fail_creation_without_goal(self):
        """goal이 없으면 컴포넌트 생성에 실패해야 한다"""
        # Given/When/Then
        with pytest.raises(ValueError, match="Goal은 필수 항목입니다"):
            PromptComponent(goal="")

    @pytest.mark.unit
    def test_should_sanitize_string_fields(self):
        """문자열 필드는 자동으로 정제되어야 한다"""
        # Given/When
        component = PromptComponent(
            goal="  테스트  ",
            document="  문서  "
        )

        # Then
        assert component.goal == "테스트"
        assert component.document == "문서"


class TestPromptComponentValidation:
    """PromptComponent 유효성 검증 테스트"""

    @pytest.mark.unit
    def test_should_reject_goal_exceeding_max_length(self):
        """goal이 최대 길이를 초과하면 거부해야 한다"""
        # Given
        long_goal = "a" * 501  # MAX_GOAL_LENGTH = 500

        # When/Then
        with pytest.raises(ValueError, match="Input too long"):
            PromptComponent(goal=long_goal)

    @pytest.mark.unit
    def test_should_reject_too_many_list_items(self):
        """리스트 항목이 최대 개수를 초과하면 거부해야 한다"""
        # Given
        too_many_roles = ["role" + str(i) for i in range(11)]  # MAX_LIST_ITEMS = 10

        # When/Then
        with pytest.raises(ValueError, match="Too many items"):
            PromptComponent(goal="테스트", role=too_many_roles)

    @pytest.mark.unit
    def test_should_reject_malicious_script_tags(self):
        """악의적인 스크립트 태그를 거부해야 한다"""
        # Given
        malicious_goal = "<script>alert('xss')</script>테스트"

        # When/Then
        with pytest.raises(ValueError, match="malicious content"):
            PromptComponent(goal=malicious_goal)

    @pytest.mark.unit
    def test_should_reject_javascript_protocol(self):
        """javascript: 프로토콜을 거부해야 한다"""
        # Given
        malicious_goal = "javascript:alert('xss')"

        # When/Then
        with pytest.raises(ValueError, match="malicious content"):
            PromptComponent(goal=malicious_goal)


class TestPromptComponentMethods:
    """PromptComponent 메서드 테스트"""

    @pytest.mark.unit
    def test_should_convert_to_dict(self, sample_component):
        """딕셔너리로 변환할 수 있어야 한다"""
        # Given/When
        data = sample_component.to_dict()

        # Then
        assert isinstance(data, dict)
        assert "goal" in data
        assert "role" in data
        assert data["goal"] == sample_component.goal

    @pytest.mark.unit
    def test_should_create_from_dict(self):
        """딕셔너리로부터 객체를 생성할 수 있어야 한다"""
        # Given
        data = {
            "goal": "테스트 목표",
            "role": ["역할1"],
            "context": ["맥락1"],
            "output": "출력 형식"
        }

        # When
        component = PromptComponent.from_dict(data)

        # Then
        assert component.goal == "테스트 목표"
        assert component.role == ["역할1"]

    @pytest.mark.unit
    def test_should_validate_component(self):
        """컴포넌트 유효성을 검증할 수 있어야 한다"""
        # Given
        component = PromptComponent(goal="테스트")

        # When
        is_valid, error_msg = component.validate()

        # Then
        assert is_valid is True
        assert error_msg == ""

    @pytest.mark.unit
    def test_should_detect_empty_component(self):
        """빈 컴포넌트를 감지할 수 있어야 한다"""
        # Given
        empty_component = PromptComponent(goal="테스트")
        empty_component.goal = ""  # 강제로 비우기

        # When
        is_empty = empty_component.is_empty()

        # Then
        assert is_empty is True


# ==================== PromptVersion 테스트 ====================

class TestPromptVersionCreation:
    """PromptVersion 생성 테스트"""

    @pytest.mark.unit
    def test_should_create_version_with_component(self, sample_component):
        """컴포넌트로 버전을 생성할 수 있어야 한다"""
        # Given/When
        version = PromptVersion(
            version=1,
            created_at=datetime.now(),
            components=sample_component
        )

        # Then
        assert version.version == 1
        assert version.components == sample_component

    @pytest.mark.unit
    def test_should_auto_generate_prompt_if_not_provided(self, sample_component):
        """프롬프트가 제공되지 않으면 자동 생성해야 한다"""
        # Given/When
        version = PromptVersion(
            version=1,
            created_at=datetime.now(),
            components=sample_component,
            generated_prompt=""
        )

        # Then
        assert version.generated_prompt != ""
        assert "<Goal>" in version.generated_prompt


class TestPromptVersionMethods:
    """PromptVersion 메서드 테스트"""

    @pytest.mark.unit
    def test_should_convert_version_to_dict(self, sample_version):
        """버전을 딕셔너리로 변환할 수 있어야 한다"""
        # Given/When
        data = sample_version.to_dict()

        # Then
        assert "version" in data
        assert "created_at" in data
        assert "components" in data
        assert data["version"] == 1

    @pytest.mark.unit
    def test_should_create_version_from_dict(self):
        """딕셔너리로부터 버전을 생성할 수 있어야 한다"""
        # Given
        data = {
            "version": 2,
            "created_at": datetime.now().isoformat(),
            "components": {"goal": "테스트"},
            "generated_prompt": "프롬프트"
        }

        # When
        version = PromptVersion.from_dict(data)

        # Then
        assert version.version == 2
        assert isinstance(version.created_at, datetime)
