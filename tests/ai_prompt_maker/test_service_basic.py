# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 기본 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 초기화
- 설정 관리
- 통계
- 정리
"""

import pytest

from ai_prompt_maker.service import PromptMakerService


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
