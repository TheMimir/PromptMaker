# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
Models 템플릿 및 예외 테스트

ai_prompt_maker.models 모듈의 데이터 모델을 테스트합니다.
- PromptTemplate: 프롬프트 템플릿
- PromptCategory: 카테고리 Enum
- 예외 클래스
"""

import pytest
import json
from datetime import datetime

from ai_prompt_maker.models import (
    PromptTemplate,
    PromptCategory,
    PromptValidationError,
    TemplateNotFoundError
)


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
