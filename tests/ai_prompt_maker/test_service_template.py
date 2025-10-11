# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 템플릿 관리 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 템플릿 생성
- 템플릿 저장/로드
- 템플릿 목록 조회
- 템플릿 삭제
- 템플릿 복사
"""

import pytest

from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import (
    PromptCategory,
    PromptValidationError,
    TemplateNotFoundError
)


# ==================== 템플릿 생성 테스트 ====================

class TestPromptMakerServiceTemplateCreation:
    """PromptMakerService 템플릿 생성 테스트"""

    @pytest.mark.unit
    def test_should_create_new_template(self, service, sample_component):
        """새 템플릿을 생성할 수 있어야 한다"""
        # Given/When
        template = service.create_template(
            name="테스트 템플릿",
            category="기획",
            components=sample_component,
            description="테스트용 템플릿"
        )

        # Then
        assert template is not None
        assert template.name == "테스트 템플릿"
        assert template.category == PromptCategory.PLANNING
        assert service.stats["templates_created"] > 0

    @pytest.mark.unit
    def test_should_create_template_with_tags(self, service, sample_component):
        """태그와 함께 템플릿을 생성할 수 있어야 한다"""
        # Given/When
        template = service.create_template(
            name="태그 테스트",
            category="전체",
            components=sample_component,
            tags=["태그1", "태그2"]
        )

        # Then
        assert len(template.tags) == 2
        assert "태그1" in template.tags


# ==================== 템플릿 저장/로드 테스트 ====================

class TestPromptMakerServiceTemplateSaveLoad:
    """PromptMakerService 템플릿 저장/로드 테스트"""

    @pytest.mark.unit
    def test_should_save_template_to_file(self, service, sample_template):
        """템플릿을 파일로 저장할 수 있어야 한다"""
        # Given/When
        result = service.save_template(sample_template)

        # Then
        assert result is True
        template_path = service.templates_dir / f"{sample_template.template_id}.json"
        assert template_path.exists()

    @pytest.mark.unit
    def test_should_load_template_from_file(self, service, sample_template):
        """파일에서 템플릿을 로드할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        loaded_template = service.load_template(sample_template.template_id)

        # Then
        assert loaded_template is not None
        assert loaded_template.name == sample_template.name
        assert service.stats["templates_loaded"] > 0

    @pytest.mark.unit
    def test_should_return_none_for_nonexistent_template(self, service):
        """존재하지 않는 템플릿은 None을 반환해야 한다"""
        # Given/When
        template = service.load_template("nonexistent-id-12345")

        # Then
        assert template is None

    @pytest.mark.unit
    def test_should_cache_loaded_templates(self, service, sample_template):
        """로드된 템플릿을 캐시해야 한다"""
        # Given
        service.save_template(sample_template)
        template1 = service.load_template(sample_template.template_id)

        # When
        template2 = service.load_template(sample_template.template_id)

        # Then
        assert template1 is template2  # 같은 객체 (캐시됨)

    @pytest.mark.unit
    def test_should_prevent_overwrite_when_flag_is_false(self, service, sample_template):
        """overwrite=False면 기존 파일 덮어쓰기를 방지해야 한다"""
        # Given
        service.save_template(sample_template, overwrite=True)

        # When/Then
        with pytest.raises(PromptValidationError, match="이미 존재합니다"):
            service.save_template(sample_template, overwrite=False)


# ==================== 템플릿 목록 조회 테스트 ====================

class TestPromptMakerServiceTemplateList:
    """PromptMakerService 템플릿 목록 조회 테스트"""

    @pytest.mark.unit
    def test_should_list_all_templates(self, service, sample_template):
        """모든 템플릿을 조회할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        templates = service.list_templates()

        # Then
        assert len(templates) > 0
        assert any(t['template_id'] == sample_template.template_id for t in templates)

    @pytest.mark.unit
    def test_should_filter_templates_by_category(self, service, sample_template):
        """카테고리로 템플릿을 필터링할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        templates = service.list_templates(category=sample_template.category.value)

        # Then
        assert all(t['category'] == sample_template.category.value for t in templates)

    @pytest.mark.unit
    def test_should_filter_templates_by_tags(self, service, sample_template):
        """태그로 템플릿을 필터링할 수 있어야 한다"""
        # Given
        sample_template.tags = ["테스트태그"]
        service.save_template(sample_template)

        # When
        templates = service.list_templates(tags=["테스트태그"])

        # Then
        assert len(templates) > 0


# ==================== 템플릿 삭제 테스트 ====================

class TestPromptMakerServiceTemplateDelete:
    """PromptMakerService 템플릿 삭제 테스트"""

    @pytest.mark.unit
    def test_should_delete_template_successfully(self, service, sample_template):
        """템플릿을 성공적으로 삭제할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)
        template_path = service.templates_dir / f"{sample_template.template_id}.json"
        assert template_path.exists()

        # When
        result = service.delete_template(sample_template.template_id)

        # Then
        assert result is True
        assert not template_path.exists()
        assert service.stats["templates_deleted"] > 0

    @pytest.mark.unit
    def test_should_backup_before_deletion(self, service, sample_template):
        """삭제 전에 백업을 생성해야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        service.delete_template(sample_template.template_id)

        # Then
        backup_dir = service.templates_dir / "backup"
        assert backup_dir.exists()
        backup_files = list(backup_dir.glob(f"{sample_template.template_id}_*.json"))
        assert len(backup_files) > 0

    @pytest.mark.unit
    def test_should_return_false_for_nonexistent_template_deletion(self, service):
        """존재하지 않는 템플릿 삭제는 False를 반환해야 한다"""
        # Given/When
        result = service.delete_template("nonexistent-id-12345")

        # Then
        assert result is False


# ==================== 템플릿 복사 테스트 ====================

class TestPromptMakerServiceTemplateCopy:
    """PromptMakerService 템플릿 복사 테스트"""

    @pytest.mark.unit
    def test_should_copy_template_successfully(self, service, sample_template):
        """템플릿을 성공적으로 복사할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        new_template = service.copy_template(
            sample_template.template_id,
            "복사본 템플릿"
        )

        # Then
        assert new_template is not None
        assert new_template.name == "복사본 템플릿"
        assert new_template.template_id != sample_template.template_id

    @pytest.mark.unit
    def test_should_fail_copy_for_nonexistent_template(self, service):
        """존재하지 않는 템플릿 복사는 실패해야 한다"""
        # Given/When/Then
        with pytest.raises(TemplateNotFoundError):
            service.copy_template("nonexistent-id", "새 이름")
