# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptMakerService 검색 및 도메인 테스트

ai_prompt_maker.service 모듈의 PromptMakerService 클래스를 테스트합니다.
- 템플릿 검색
- 도메인 설정 관리
"""

import pytest
import json
from pathlib import Path

from ai_prompt_maker.service import PromptMakerService


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
