# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 보안 및 검증 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 보안 검증 (Path Traversal 방어)
- 템플릿 데이터 검증
"""

import pytest

from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import PromptValidationError


# ==================== 보안 테스트 (중요) ====================

class TestPromptMakerServiceSecurity:
    """PromptMakerService 보안 테스트"""

    @pytest.mark.unit
    def test_should_sanitize_template_id_with_valid_id(self, service):
        """유효한 template ID는 정제를 통과해야 한다"""
        # Given
        valid_id = "abc123-def456"

        # When
        sanitized = service._sanitize_template_id(valid_id)

        # Then
        assert sanitized == valid_id

    @pytest.mark.unit
    def test_should_reject_template_id_with_path_traversal(self, service):
        """Path Traversal 시도를 거부해야 한다"""
        # Given
        malicious_id = "../../../etc/passwd"

        # When/Then
        with pytest.raises(ValueError, match="Invalid template ID"):
            service._sanitize_template_id(malicious_id)

    @pytest.mark.unit
    def test_should_reject_template_id_with_special_characters(self, service):
        """특수 문자가 포함된 ID를 거부해야 한다"""
        # Given
        malicious_id = "template@#$%.json"

        # When/Then
        with pytest.raises(ValueError, match="Invalid template ID"):
            service._sanitize_template_id(malicious_id)

    @pytest.mark.unit
    def test_should_reject_empty_template_id(self, service):
        """빈 template ID를 거부해야 한다"""
        # Given/When/Then
        with pytest.raises(ValueError):
            service._sanitize_template_id("")

    @pytest.mark.unit
    def test_should_reject_oversized_template_id(self, service):
        """너무 긴 template ID를 거부해야 한다"""
        # Given
        long_id = "a" * 101  # MAX = 100

        # When/Then
        with pytest.raises(ValueError, match="Template ID too long"):
            service._sanitize_template_id(long_id)

    @pytest.mark.unit
    def test_should_validate_template_path_within_directory(self, service):
        """템플릿 디렉토리 내부 경로는 허용해야 한다"""
        # Given
        valid_path = service.templates_dir / "template.json"

        # When/Then
        try:
            service._validate_template_path(valid_path)
        except ValueError:
            pytest.fail("Valid path should not raise ValueError")

    @pytest.mark.unit
    def test_should_reject_path_traversal_attempts(self, service):
        """Path Traversal 경로를 거부해야 한다"""
        # Given
        malicious_path = service.templates_dir / ".." / ".." / "etc" / "passwd"

        # When/Then
        with pytest.raises(ValueError, match="Path traversal detected"):
            service._validate_template_path(malicious_path)


# ==================== 템플릿 데이터 검증 테스트 ====================

class TestPromptMakerServiceValidation:
    """PromptMakerService 템플릿 데이터 검증 테스트"""

    @pytest.mark.unit
    def test_should_validate_complete_template_data(self, service):
        """완전한 템플릿 데이터는 검증을 통과해야 한다"""
        # Given
        template_data = {
            "name": "테스트 템플릿",
            "category": "기획",
            "versions": [
                {
                    "components": {
                        "goal": "목표",
                        "role": ["역할"],
                        "context": [],
                        "output": "",
                        "rule": []
                    }
                }
            ]
        }

        # When
        is_valid, errors = service.validate_template_data(template_data)

        # Then
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_should_reject_template_without_name(self, service):
        """이름 없는 템플릿은 거부해야 한다"""
        # Given
        template_data = {
            "name": "",
            "category": "기획",
            "versions": [{"components": {"goal": "목표"}}]
        }

        # When
        is_valid, errors = service.validate_template_data(template_data)

        # Then
        assert is_valid is False
        assert any("이름" in error for error in errors)

    @pytest.mark.unit
    def test_should_reject_template_without_category(self, service):
        """카테고리 없는 템플릿은 거부해야 한다"""
        # Given
        template_data = {
            "name": "테스트",
            "category": "",
            "versions": [{"components": {"goal": "목표"}}]
        }

        # When
        is_valid, errors = service.validate_template_data(template_data)

        # Then
        assert is_valid is False
        assert any("카테고리" in error for error in errors)

    @pytest.mark.unit
    def test_should_reject_template_without_versions(self, service):
        """버전 없는 템플릿은 거부해야 한다"""
        # Given
        template_data = {
            "name": "테스트",
            "category": "기획",
            "versions": []
        }

        # When
        is_valid, errors = service.validate_template_data(template_data)

        # Then
        assert is_valid is False
        assert any("버전" in error for error in errors)

    @pytest.mark.unit
    def test_should_reject_version_without_goal(self, service):
        """Goal 없는 버전은 거부해야 한다"""
        # Given
        template_data = {
            "name": "테스트",
            "category": "기획",
            "versions": [
                {
                    "components": {
                        "goal": "",
                        "role": []
                    }
                }
            ]
        }

        # When
        is_valid, errors = service.validate_template_data(template_data)

        # Then
        assert is_valid is False
        assert any("Goal" in error for error in errors)

    @pytest.mark.unit
    def test_should_handle_validation_exception(self, service):
        """검증 중 예외 발생 시 처리해야 한다"""
        # Given
        invalid_data = None  # None은 get() 메서드 없음

        # When
        is_valid, errors = service.validate_template_data(invalid_data)

        # Then
        assert is_valid is False
        assert len(errors) > 0
