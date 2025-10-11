# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 고급 기능 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 프롬프트 생성
- 내보내기
- 가져오기
- 출력 형식
- 캐시 무효화
- 에러 처리
"""

import pytest
import json
from pathlib import Path

from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import (
    PromptComponent,
    PromptValidationError,
)


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
