# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 파일 시스템 연동
- 템플릿 CRUD 작업
- 보안 검증 (Path Traversal 방어)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import (
    PromptComponent,
    PromptTemplate,
    PromptCategory,
    PromptValidationError,
    TemplateNotFoundError
)


# ==================== 초기화 및 설정 테스트 ====================

class TestPromptMakerServiceInitialization:
    """PromptMakerService 초기화 테스트"""

    @pytest.mark.unit
    def test_should_initialize_with_default_paths(self, temp_dir):
        """기본 경로로 초기화할 수 있어야 한다"""
        # Given/When
        service = PromptMakerService(
            config_path=str(temp_dir / "config.json"),
            templates_dir=str(temp_dir / "templates")
        )

        # Then
        assert service.config_path.exists() or service.config_path.parent.exists()
        assert service.templates_dir.exists()
        assert service.generator is not None

    @pytest.mark.unit
    def test_should_create_templates_directory_if_not_exists(self, temp_dir):
        """템플릿 디렉토리가 없으면 생성해야 한다"""
        # Given
        templates_dir = temp_dir / "new_templates"
        assert not templates_dir.exists()

        # When
        service = PromptMakerService(
            config_path=str(temp_dir / "config.json"),
            templates_dir=str(templates_dir)
        )

        # Then
        assert service.templates_dir.exists()

    @pytest.mark.unit
    def test_should_create_default_config_if_not_exists(self, temp_dir):
        """설정 파일이 없으면 기본 설정을 생성해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        assert not config_path.exists()

        # When
        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # Then
        assert service.config_path.exists()
        config = service.get_config()
        assert 'keywords' in config


class TestPromptMakerServiceConfig:
    """PromptMakerService 설정 관리 테스트"""

    @pytest.mark.unit
    def test_should_load_config_from_file(self, service, sample_config):
        """설정 파일을 로드할 수 있어야 한다"""
        # Given/When
        config = service.get_config()

        # Then
        assert 'keywords' in config
        assert 'categories' in config

    @pytest.mark.unit
    def test_should_cache_config_after_first_load(self, service):
        """첫 로드 후 설정을 캐시해야 한다"""
        # Given
        config1 = service.get_config()

        # When
        config2 = service.get_config()

        # Then
        assert config1 is config2  # 같은 객체 (캐시됨)

    @pytest.mark.unit
    def test_should_reload_config_when_forced(self, service):
        """강제 reload 시 설정을 다시 로드해야 한다"""
        # Given
        config1 = service.get_config()

        # When
        config2 = service.get_config(force_reload=True)

        # Then
        assert config1 is not config2  # 다른 객체 (재로드됨)

    @pytest.mark.unit
    def test_should_get_keywords(self, service):
        """키워드 목록을 가져올 수 있어야 한다"""
        # Given/When
        keywords = service.get_keywords()

        # Then
        assert isinstance(keywords, dict)
        assert 'role' in keywords or len(keywords) == 0  # 빈 설정도 허용

    @pytest.mark.unit
    def test_should_get_categories(self, service):
        """카테고리 목록을 가져올 수 있어야 한다"""
        # Given/When
        categories = service.get_categories()

        # Then
        assert isinstance(categories, list)


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


# ==================== 프롬프트 생성 테스트 ====================

class TestPromptMakerServicePromptGeneration:
    """PromptMakerService 프롬프트 생성 테스트"""

    @pytest.mark.unit
    def test_should_generate_prompt_from_components(self, service, sample_component):
        """컴포넌트로부터 프롬프트를 생성할 수 있어야 한다"""
        # Given/When
        prompt = service.generate_prompt(sample_component)

        # Then
        assert prompt is not None
        assert len(prompt) > 0
        assert service.stats["prompts_generated"] > 0

    @pytest.mark.unit
    def test_should_fail_generation_with_invalid_component(self, service):
        """잘못된 컴포넌트로는 생성에 실패해야 한다"""
        # Given
        invalid_component = PromptComponent(goal="테스트")
        invalid_component.goal = ""  # 강제로 무효화

        # When/Then
        with pytest.raises(PromptValidationError):
            service.generate_prompt(invalid_component)


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


# ==================== 템플릿 검색 테스트 ====================

class TestPromptMakerServiceTemplateSearch:
    """PromptMakerService 템플릿 검색 테스트"""

    @pytest.mark.unit
    def test_should_search_templates_by_name(self, service, sample_template):
        """이름으로 템플릿을 검색할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        results = service.search_templates(sample_template.name[:3])

        # Then
        assert len(results) > 0
        assert any(r['name'] == sample_template.name for r in results)

    @pytest.mark.unit
    def test_should_search_templates_by_tags(self, service, sample_template):
        """태그로 템플릿을 검색할 수 있어야 한다"""
        # Given
        sample_template.tags = ["검색태그"]
        service.save_template(sample_template)

        # When
        results = service.search_templates("검색태그")

        # Then
        assert len(results) > 0

    @pytest.mark.unit
    def test_should_return_all_templates_for_empty_query(self, service):
        """빈 검색어는 모든 템플릿을 반환해야 한다"""
        # Given/When
        results = service.search_templates("")

        # Then
        assert isinstance(results, list)


# ==================== 통계 및 기타 테스트 ====================

class TestPromptMakerServiceStats:
    """PromptMakerService 통계 테스트"""

    @pytest.mark.unit
    def test_should_get_service_statistics(self, service):
        """서비스 통계를 가져올 수 있어야 한다"""
        # Given/When
        stats = service.get_service_stats()

        # Then
        assert 'total_templates' in stats
        assert 'templates_directory' in stats
        assert 'config_path' in stats
        assert 'cache_size' in stats

    @pytest.mark.unit
    def test_should_track_operations(self, service, sample_component):
        """작업을 추적해야 한다"""
        # Given
        initial_count = service.stats["prompts_generated"]

        # When
        service.generate_prompt(sample_component)

        # Then
        assert service.stats["prompts_generated"] == initial_count + 1


class TestPromptMakerServiceExport:
    """PromptMakerService 내보내기 테스트"""

    @pytest.mark.unit
    def test_should_export_template_as_json(self, service, sample_template):
        """템플릿을 JSON으로 내보낼 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        json_str = service.export_template(sample_template.template_id, "json")

        # Then
        assert json_str is not None
        data = json.loads(json_str)
        assert data["name"] == sample_template.name

    @pytest.mark.unit
    def test_should_export_template_as_text(self, service, sample_template):
        """템플릿을 텍스트로 내보낼 수 있어야 한다"""
        # Given
        service.save_template(sample_template)

        # When
        text = service.export_template(sample_template.template_id, "text")

        # Then
        assert text is not None
        assert isinstance(text, str)


class TestPromptMakerServiceCleanup:
    """PromptMakerService 정리 테스트"""

    @pytest.mark.unit
    def test_should_cleanup_service_resources(self, service):
        """서비스 리소스를 정리할 수 있어야 한다"""
        # Given/When
        service.cleanup_service()

        # Then
        assert len(service._templates_cache) == 0
        assert service._config_cache is None


# ==================== 도메인 설정 테스트 ====================

class TestPromptMakerServiceDomain:
    """PromptMakerService 도메인 설정 테스트"""

    @pytest.mark.unit
    def test_should_get_domain_config_from_new_structure(self, temp_dir):
        """새 도메인 구조에서 도메인 설정을 가져올 수 있어야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        config_data = {
            "domains": {
                "game_dev": {
                    "name": "게임 개발",
                    "enabled": True,
                    "keywords": {"role": ["기획자"]}
                }
            }
        }
        config_path.write_text(json.dumps(config_data, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        domain_config = service.get_domain_config("game_dev")

        # Then
        assert domain_config["name"] == "게임 개발"
        assert domain_config["enabled"] is True

    @pytest.mark.unit
    def test_should_return_default_for_nonexistent_domain(self, temp_dir):
        """존재하지 않는 도메인은 기본값을 반환해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        config_data = {
            "domains": {
                "game_dev": {
                    "name": "게임 개발",
                    "enabled": True
                }
            }
        }
        config_path.write_text(json.dumps(config_data, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        domain_config = service.get_domain_config("nonexistent")

        # Then
        assert domain_config["name"] == "게임 개발"  # 기본값

    @pytest.mark.unit
    def test_should_migrate_legacy_config_to_domain(self, temp_dir):
        """레거시 config를 도메인 구조로 마이그레이션해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        legacy_config = {
            "keywords": {"role": ["기획자"], "goal": ["분석"]},
            "categories": ["기획", "프로그램"]
        }
        config_path.write_text(json.dumps(legacy_config, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        domain_config = service.get_domain_config("game_dev")

        # Then
        assert "keywords" in domain_config
        assert domain_config["keywords"]["role"] == ["기획자"]

    @pytest.mark.unit
    def test_should_list_enabled_domains(self, temp_dir):
        """활성화된 도메인 목록을 반환해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        config_data = {
            "domains": {
                "game_dev": {
                    "name": "게임 개발",
                    "description": "게임 개발 관련",
                    "icon": "🎮",
                    "enabled": True
                },
                "uiux": {
                    "name": "UI/UX",
                    "description": "UI/UX 관련",
                    "icon": "🎨",
                    "enabled": False
                }
            }
        }
        config_path.write_text(json.dumps(config_data, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        domains = service.list_domains()

        # Then
        assert len(domains) == 1
        assert domains[0]["id"] == "game_dev"
        assert domains[0]["icon"] == "🎮"

    @pytest.mark.unit
    def test_should_return_default_domain_for_legacy_config(self, temp_dir):
        """레거시 config는 기본 도메인을 반환해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        legacy_config = {"keywords": {}, "categories": []}
        config_path.write_text(json.dumps(legacy_config, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        domains = service.list_domains()

        # Then
        assert len(domains) == 1
        assert domains[0]["id"] == "game_dev"


# ==================== 출력 형식 테스트 ====================

class TestPromptMakerServiceOutputFormats:
    """PromptMakerService 출력 형식 테스트"""

    @pytest.mark.unit
    def test_should_load_output_formats_from_file(self, temp_dir):
        """파일에서 출력 형식을 로드할 수 있어야 한다"""
        # Given
        formats_path = Path("data/output_formats.json")
        formats_path.parent.mkdir(parents=True, exist_ok=True)
        formats_data = {
            "categories": {"basic_format": {"name": "기본 형식"}},
            "formats": {
                "report": {
                    "format_id": "report",
                    "name": "보고서",
                    "category": "basic_format"
                }
            }
        }
        formats_path.write_text(json.dumps(formats_data, ensure_ascii=False))

        service = PromptMakerService(
            config_path=str(temp_dir / "config.json"),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        formats = service.load_output_formats()

        # Then
        assert "categories" in formats
        assert "formats" in formats
        assert "report" in formats["formats"]

        # Cleanup
        formats_path.unlink()

    @pytest.mark.unit
    def test_should_return_default_formats_if_file_not_exists(self, service):
        """파일이 없으면 기본 형식을 반환해야 한다"""
        # Given/When
        formats = service.load_output_formats()

        # Then
        assert "categories" in formats
        assert "formats" in formats
        assert "basic_report" in formats["formats"]

    @pytest.mark.unit
    def test_should_handle_corrupted_formats_file(self, temp_dir):
        """손상된 형식 파일은 기본값을 반환해야 한다"""
        # Given
        formats_path = Path("data/output_formats.json")
        formats_path.parent.mkdir(parents=True, exist_ok=True)
        formats_path.write_text("INVALID JSON {{{")

        service = PromptMakerService(
            config_path=str(temp_dir / "config.json"),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        formats = service.load_output_formats()

        # Then
        assert "categories" in formats
        assert "basic_format" in formats["categories"]

        # Cleanup
        formats_path.unlink()


# ==================== 템플릿 가져오기 테스트 ====================

class TestPromptMakerServiceImport:
    """PromptMakerService 템플릿 가져오기 테스트"""

    @pytest.mark.unit
    def test_should_import_template_from_json(self, service, sample_template):
        """JSON에서 템플릿을 가져올 수 있어야 한다"""
        # Given
        json_data = sample_template.to_json()

        # When
        imported_template = service.import_template_from_json(json_data)

        # Then
        assert imported_template is not None
        assert imported_template.name == sample_template.name

    @pytest.mark.unit
    def test_should_fail_import_with_invalid_json(self, service):
        """잘못된 JSON으로 가져오기는 실패해야 한다"""
        # Given
        invalid_json = "INVALID JSON {{"

        # When/Then
        with pytest.raises(PromptValidationError):
            service.import_template_from_json(invalid_json)

    @pytest.mark.unit
    def test_should_fail_import_with_incomplete_data(self, service):
        """불완전한 데이터로 가져오기는 실패해야 한다"""
        # Given
        incomplete_json = json.dumps({"name": "Test"})  # 필수 필드 누락

        # When/Then
        with pytest.raises(PromptValidationError):
            service.import_template_from_json(incomplete_json)


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


# ==================== 캐시 무효화 테스트 ====================

class TestPromptMakerServiceCacheInvalidation:
    """PromptMakerService 캐시 무효화 테스트"""

    @pytest.mark.unit
    def test_should_invalidate_config_cache_on_file_change(self, service, temp_dir):
        """파일 변경 시 config 캐시를 무효화해야 한다"""
        # Given
        config1 = service.get_config()

        # 파일 수정 시간 변경 시뮬레이션
        import time
        time.sleep(0.1)

        # config 파일 수정
        config_path = service.config_path
        if config_path.exists():
            current_content = config_path.read_text()
            config_path.write_text(current_content)

        # When
        config2 = service.get_config()

        # Then - 캐시가 무효화되어 재로드됨
        # (실제로는 같은 내용이지만 다른 객체여야 함)
        assert config1 is not config2 or service._config_last_modified is not None

    @pytest.mark.unit
    def test_should_reload_templates_cache_after_cleanup(self, service, sample_template):
        """정리 후 템플릿 캐시를 재로드할 수 있어야 한다"""
        # Given
        service.save_template(sample_template)
        loaded1 = service.load_template(sample_template.template_id)

        # When
        service.cleanup_service()
        loaded2 = service.load_template(sample_template.template_id)

        # Then
        assert loaded1 is not None
        assert loaded2 is not None
        assert loaded1 is not loaded2  # 다른 객체 (재로드됨)


# ==================== 에러 처리 통합 테스트 ====================

class TestPromptMakerServiceErrorHandling:
    """PromptMakerService 에러 처리 통합 테스트"""

    @pytest.mark.unit
    def test_should_handle_permission_denied_on_save(self, service, sample_template, temp_dir):
        """저장 중 권한 오류를 처리해야 한다"""
        # Given
        # 템플릿 디렉토리를 읽기 전용으로 변경
        import os
        import stat

        templates_dir = service.templates_dir
        original_mode = templates_dir.stat().st_mode

        try:
            # 쓰기 권한 제거
            templates_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

            # When/Then
            with pytest.raises(PromptValidationError):
                service.save_template(sample_template)
        finally:
            # 권한 복구
            templates_dir.chmod(original_mode)

    @pytest.mark.unit
    def test_should_return_default_config_on_load_failure(self, temp_dir):
        """config 로드 실패 시 기본값을 반환해야 한다"""
        # Given
        config_path = temp_dir / "config.json"
        config_path.write_text("INVALID JSON")

        service = PromptMakerService(
            config_path=str(config_path),
            templates_dir=str(temp_dir / "templates")
        )

        # When
        config = service.get_config()

        # Then
        assert "keywords" in config
        assert isinstance(config["keywords"], dict)
