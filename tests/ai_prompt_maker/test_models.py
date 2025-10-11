# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
Models 테스트

ai_prompt_maker.models 모듈의 데이터 모델을 테스트합니다.
- PromptComponent: 프롬프트 구성 요소
- PromptVersion: 프롬프트 버전
- PromptTemplate: 프롬프트 템플릿
"""

import pytest
import json
from datetime import datetime

from ai_prompt_maker.models import (
    PromptComponent,
    PromptVersion,
    PromptTemplate,
    PromptCategory,
    PromptValidationError,
    TemplateNotFoundError
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


# ==================== PromptTemplate 테스트 ====================

class TestPromptTemplateCreation:
    """PromptTemplate 생성 테스트"""

    @pytest.mark.unit
    def test_should_create_template_with_name(self):
        """이름으로 템플릿을 생성할 수 있어야 한다"""
        # Given/When
        template = PromptTemplate(
            name="테스트 템플릿",
            category=PromptCategory.PLANNING
        )

        # Then
        assert template.name == "테스트 템플릿"
        assert template.category == PromptCategory.PLANNING

    @pytest.mark.unit
    def test_should_fail_creation_without_name(self):
        """이름 없이는 템플릿 생성에 실패해야 한다"""
        # Given/When/Then
        with pytest.raises(ValueError, match="템플릿 이름은 필수입니다"):
            PromptTemplate(name="", category=PromptCategory.ALL)

    @pytest.mark.unit
    def test_should_create_default_version_if_not_provided(self):
        """버전이 제공되지 않으면 기본 버전을 생성해야 한다"""
        # Given/When
        template = PromptTemplate(
            name="테스트",
            category=PromptCategory.ALL
        )

        # Then
        assert len(template.versions) == 1
        assert template.versions[0].version == 1


class TestPromptTemplateVersionManagement:
    """PromptTemplate 버전 관리 테스트"""

    @pytest.mark.unit
    def test_should_add_new_version(self, sample_template, sample_component):
        """새 버전을 추가할 수 있어야 한다"""
        # Given
        initial_count = len(sample_template.versions)

        # When
        new_version_number = sample_template.add_version(sample_component, "새 버전")

        # Then
        assert len(sample_template.versions) == initial_count + 1
        assert sample_template.current_version == new_version_number

    @pytest.mark.unit
    def test_should_get_current_version(self, sample_template):
        """현재 버전을 가져올 수 있어야 한다"""
        # Given/When
        current = sample_template.get_current_version()

        # Then
        assert current is not None
        assert current.version == sample_template.current_version

    @pytest.mark.unit
    def test_should_get_specific_version(self, sample_template):
        """특정 버전 번호로 버전을 가져올 수 있어야 한다"""
        # Given/When
        version = sample_template.get_version(1)

        # Then
        assert version is not None
        assert version.version == 1

    @pytest.mark.unit
    def test_should_update_current_version(self, sample_template, sample_component):
        """현재 버전을 업데이트할 수 있어야 한다"""
        # Given/When
        result = sample_template.update_current_version(sample_component, "업데이트")

        # Then
        assert result is True
        current = sample_template.get_current_version()
        assert current.description == "업데이트"

    @pytest.mark.unit
    def test_should_delete_version_but_keep_at_least_one(self, sample_template, sample_component):
        """버전을 삭제할 수 있지만 최소 1개는 유지해야 한다"""
        # Given
        sample_template.add_version(sample_component, "버전 2")

        # When
        result = sample_template.delete_version(1)

        # Then
        assert result is True
        assert len(sample_template.versions) >= 1

    @pytest.mark.unit
    def test_should_not_delete_last_version(self, sample_template):
        """마지막 버전은 삭제할 수 없어야 한다"""
        # Given/When
        result = sample_template.delete_version(1)

        # Then
        assert result is False


class TestPromptTemplateSerialization:
    """PromptTemplate 직렬화 테스트"""

    @pytest.mark.unit
    def test_should_convert_to_dict(self, sample_template):
        """딕셔너리로 변환할 수 있어야 한다"""
        # Given/When
        data = sample_template.to_dict()

        # Then
        assert isinstance(data, dict)
        assert "name" in data
        assert "category" in data
        assert "versions" in data

    @pytest.mark.unit
    def test_should_convert_to_json_string(self, sample_template):
        """JSON 문자열로 변환할 수 있어야 한다"""
        # Given/When
        json_str = sample_template.to_json()

        # Then
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == sample_template.name

    @pytest.mark.unit
    def test_should_create_from_dict(self):
        """딕셔너리로부터 템플릿을 생성할 수 있어야 한다"""
        # Given
        data = {
            "name": "테스트",
            "category": "기획",
            "versions": [{
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "components": {"goal": "테스트"}
            }]
        }

        # When
        template = PromptTemplate.from_dict(data)

        # Then
        assert template.name == "테스트"
        assert len(template.versions) == 1

    @pytest.mark.unit
    def test_should_create_from_json_string(self, sample_template):
        """JSON 문자열로부터 템플릿을 생성할 수 있어야 한다"""
        # Given
        json_str = sample_template.to_json()

        # When
        template = PromptTemplate.from_json(json_str)

        # Then
        assert template.name == sample_template.name
        assert template.category == sample_template.category

    @pytest.mark.unit
    def test_should_reject_oversized_json(self):
        """너무 큰 JSON은 거부해야 한다"""
        # Given
        oversized_json = '{"name": "' + 'a' * 1_000_001 + '"}'

        # When/Then
        with pytest.raises(ValueError, match="JSON payload too large"):
            PromptTemplate.from_json(oversized_json)

    @pytest.mark.unit
    def test_should_reject_invalid_json_format(self):
        """잘못된 JSON 형식은 거부해야 한다"""
        # Given
        invalid_json = "{ invalid json }"

        # When/Then
        with pytest.raises(ValueError, match="Invalid JSON format"):
            PromptTemplate.from_json(invalid_json)


class TestPromptTemplateSummary:
    """PromptTemplate 요약 정보 테스트"""

    @pytest.mark.unit
    def test_should_get_template_summary(self, sample_template):
        """템플릿 요약 정보를 가져올 수 있어야 한다"""
        # Given/When
        summary = sample_template.get_summary()

        # Then
        assert "template_id" in summary
        assert "name" in summary
        assert "version_count" in summary
        assert summary["name"] == sample_template.name

    @pytest.mark.unit
    def test_should_create_example_template(self):
        """예시 템플릿을 생성할 수 있어야 한다"""
        # Given/When
        template = PromptTemplate.create_example()

        # Then
        assert template is not None
        assert template.name == "캐릭터 시스템 분석"
        assert template.category == PromptCategory.PLANNING


# ==================== PromptCategory 테스트 ====================

class TestPromptCategory:
    """PromptCategory Enum 테스트"""

    @pytest.mark.unit
    def test_should_have_all_categories(self):
        """모든 카테고리가 정의되어 있어야 한다"""
        # Given/When/Then
        assert PromptCategory.PLANNING.value == "기획"
        assert PromptCategory.PROGRAMMING.value == "프로그램"
        assert PromptCategory.ART.value == "아트"
        assert PromptCategory.QA.value == "QA"
        assert PromptCategory.ALL.value == "전체"


# ==================== 예외 클래스 테스트 ====================

class TestExceptionClasses:
    """예외 클래스 테스트"""

    @pytest.mark.unit
    def test_should_raise_prompt_validation_error(self):
        """PromptValidationError를 발생시킬 수 있어야 한다"""
        # Given/When/Then
        with pytest.raises(PromptValidationError):
            raise PromptValidationError("검증 실패")

    @pytest.mark.unit
    def test_should_raise_template_not_found_error(self):
        """TemplateNotFoundError를 발생시킬 수 있어야 한다"""
        # Given/When/Then
        with pytest.raises(TemplateNotFoundError):
            raise TemplateNotFoundError("템플릿 없음")
