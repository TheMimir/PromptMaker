# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
DataHandler 기본 테스트

utils.data_handler 모듈의 DataHandler 클래스를 테스트합니다.
- 초기화
- 설정 관리
- 템플릿 목록 조회
- 템플릿 검색
"""

import pytest
from unittest.mock import patch

from utils.data_handler import DataHandler


class TestDataHandlerInitialization:
    """DataHandler 초기화 테스트"""

    @pytest.mark.unit
    def test_should_initialize_with_service(self):
        """DataHandler는 PromptMakerService를 포함해야 한다"""
        # Given/When
        handler = DataHandler()

        # Then
        assert handler.service is not None
        assert hasattr(handler.service, 'get_config')


class TestDataHandlerConfig:
    """DataHandler 설정 관련 테스트"""

    @pytest.mark.unit
    def test_should_load_config_from_service(self, config_file):
        """설정 파일을 로드할 수 있어야 한다"""
        # Given
        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.get_config.return_value = {"keywords": {}}

            handler = DataHandler()
            handler.service = mock_service

            # When
            config = handler.load_config()

            # Then
            mock_service.get_config.assert_called_once()
            assert config == {"keywords": {}}


class TestDataHandlerTemplateList:
    """DataHandler 템플릿 목록 조회 테스트"""

    @pytest.mark.unit
    def test_should_list_all_templates_without_category_filter(self):
        """카테고리 필터 없이 모든 템플릿을 조회할 수 있어야 한다"""
        # Given
        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.list_templates.return_value = [
                {"name": "Template 1", "category": "기획"},
                {"name": "Template 2", "category": "프로그램"}
            ]

            with patch('utils.template_storage.TemplateStorageManager') as MockStorage:
                MockStorage.load_templates.return_value = []

                handler = DataHandler()
                handler.service = mock_service

                # When
                templates = handler.list_templates()

                # Then
                assert len(templates) == 2
                assert all('source' in t for t in templates)

    @pytest.mark.unit
    def test_should_filter_templates_by_category(self):
        """카테고리별로 템플릿을 필터링할 수 있어야 한다"""
        # Given
        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.list_templates.return_value = [
                {"name": "Template 1", "category": "기획"}
            ]

            with patch('utils.template_storage.TemplateStorageManager') as MockStorage:
                MockStorage.load_templates.return_value = []

                handler = DataHandler()
                handler.service = mock_service

                # When
                templates = handler.list_templates(category="기획")

                # Then
                mock_service.list_templates.assert_called_with(category="기획")


class TestDataHandlerTemplateSearch:
    """DataHandler 템플릿 검색 테스트"""

    @pytest.mark.unit
    def test_should_search_templates_by_query(self):
        """검색어로 템플릿을 검색할 수 있어야 한다"""
        # Given
        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.search_templates.return_value = [
                {"name": "Character System", "tags": ["character"]}
            ]

            with patch('utils.template_storage.TemplateStorageManager') as MockStorage:
                MockStorage.load_templates.return_value = []

                handler = DataHandler()
                handler.service = mock_service

                # When
                results = handler.search_templates("character")

                # Then
                mock_service.search_templates.assert_called_with("character")
                assert len(results) == 1
