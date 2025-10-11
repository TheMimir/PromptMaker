# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
DataHandler 테스트

utils.data_handler 모듈의 DataHandler 클래스를 테스트합니다.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from utils.data_handler import DataHandler
from ai_prompt_maker.models import PromptTemplate, PromptCategory


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


class TestDataHandlerTemplateLoad:
    """DataHandler 템플릿 로드 테스트"""

    @pytest.mark.unit
    def test_should_load_template_from_filesystem(self, sample_template):
        """파일시스템에서 템플릿을 로드할 수 있어야 한다"""
        # Given
        template_id = "test-id-123"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.load_template(template_id)

            # Then
            assert result is not None
            assert result['source'] == 'file'
            mock_service.load_template.assert_called_with(template_id)

    @pytest.mark.unit
    def test_should_load_template_from_localstorage_if_not_in_filesystem(self):
        """파일시스템에 없으면 localStorage에서 로드해야 한다"""
        # Given
        template_id = "test-id-123"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = None  # 파일시스템에 없음

            with patch('utils.template_storage.TemplateStorageManager') as MockStorage:
                mock_template = Mock()
                mock_template.to_dict.return_value = {"name": "Test"}
                MockStorage.load_template.return_value = mock_template

                handler = DataHandler()
                handler.service = mock_service

                # When
                result = handler.load_template(template_id)

                # Then
                assert result is not None
                assert result['source'] == 'localStorage'

    @pytest.mark.unit
    def test_should_return_none_if_template_not_found(self):
        """템플릿을 찾을 수 없으면 None을 반환해야 한다"""
        # Given
        template_id = "nonexistent"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = None

            with patch('utils.template_storage.TemplateStorageManager') as MockStorage:
                MockStorage.load_template.return_value = None

                handler = DataHandler()
                handler.service = mock_service

                # When
                result = handler.load_template(template_id)

                # Then
                assert result is None


class TestDataHandlerTemplateDelete:
    """DataHandler 템플릿 삭제 테스트"""

    @pytest.mark.unit
    def test_should_delete_template_from_filesystem(self):
        """파일시스템에서 템플릿을 삭제할 수 있어야 한다"""
        # Given
        template_id = "test-id-123"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = Mock()
            mock_service.delete_template.return_value = True

            handler = DataHandler()
            handler.service = mock_service

            # Mock load_template to return file source
            with patch.object(handler, 'load_template', return_value={'source': 'file'}):
                # When
                result = handler.delete_template(template_id)

                # Then
                assert result is True
                mock_service.delete_template.assert_called_with(template_id)

    @pytest.mark.unit
    def test_should_return_false_if_template_not_found_for_deletion(self):
        """삭제할 템플릿을 찾을 수 없으면 False를 반환해야 한다"""
        # Given
        template_id = "nonexistent"

        handler = DataHandler()

        with patch.object(handler, 'load_template', return_value=None):
            # When
            result = handler.delete_template(template_id)

            # Then
            assert result is False


class TestDataHandlerTemplateDuplicate:
    """DataHandler 템플릿 복제 테스트"""

    @pytest.mark.unit
    def test_should_duplicate_template_successfully(self):
        """템플릿을 성공적으로 복제할 수 있어야 한다"""
        # Given
        template_id = "test-id-123"
        new_name = "복제본"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_template = Mock()
            mock_template.template_id = "new-id-456"
            mock_service.copy_template.return_value = mock_template

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.duplicate_template(template_id, new_name)

            # Then
            assert result == "new-id-456"
            mock_service.copy_template.assert_called_with(template_id, new_name)

    @pytest.mark.unit
    def test_should_return_none_if_duplicate_fails(self):
        """복제 실패 시 None을 반환해야 한다"""
        # Given
        template_id = "test-id-123"
        new_name = "복제본"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.copy_template.return_value = None

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.duplicate_template(template_id, new_name)

            # Then
            assert result is None

    @pytest.mark.unit
    def test_should_handle_exception_during_duplicate(self):
        """복제 중 예외 발생 시 None을 반환해야 한다"""
        # Given
        template_id = "test-id-123"
        new_name = "복제본"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.copy_template.side_effect = Exception("복제 실패")

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.duplicate_template(template_id, new_name)

            # Then
            assert result is None


class TestDataHandlerVersionHistory:
    """DataHandler 버전 히스토리 테스트"""

    @pytest.mark.unit
    def test_should_get_version_history(self, sample_template):
        """버전 히스토리를 조회할 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template

            handler = DataHandler()
            handler.service = mock_service

            # When
            history = handler.get_version_history(template_id)

            # Then
            assert isinstance(history, list)
            assert len(history) > 0

    @pytest.mark.unit
    def test_should_return_empty_list_if_template_not_found(self):
        """템플릿을 찾을 수 없으면 빈 리스트를 반환해야 한다"""
        # Given
        template_id = "nonexistent"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = None

            handler = DataHandler()
            handler.service = mock_service

            # When
            history = handler.get_version_history(template_id)

            # Then
            assert history == []


class TestDataHandlerVersionManagement:
    """DataHandler 버전 관리 테스트"""

    @pytest.mark.unit
    def test_should_set_current_version(self, sample_template):
        """현재 버전을 설정할 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            mock_service.save_template.return_value = True

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.set_current_version(template_id, version_number)

            # Then
            assert result is True

    @pytest.mark.unit
    def test_should_return_false_if_template_not_found_for_version_set(self):
        """템플릿을 찾을 수 없으면 False를 반환해야 한다"""
        # Given
        template_id = "nonexistent"
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = None

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.set_current_version(template_id, version_number)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_return_false_if_version_not_exists(self, sample_template):
        """버전이 존재하지 않으면 False를 반환해야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 999  # 존재하지 않는 버전

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            sample_template.get_version = Mock(return_value=None)

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.set_current_version(template_id, version_number)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_handle_exception_during_version_set(self, sample_template):
        """버전 설정 중 예외 발생 시 False를 반환해야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.side_effect = Exception("오류 발생")

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.set_current_version(template_id, version_number)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_delete_version_successfully(self, sample_template):
        """버전을 성공적으로 삭제할 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            mock_service.save_template.return_value = True
            sample_template.delete_version = Mock(return_value=True)

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.delete_version(template_id, version_number)

            # Then
            assert result is True

    @pytest.mark.unit
    def test_should_return_false_if_version_delete_fails(self, sample_template):
        """버전 삭제 실패 시 False를 반환해야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            sample_template.delete_version = Mock(return_value=False)

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.delete_version(template_id, version_number)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_handle_exception_during_version_delete(self):
        """버전 삭제 중 예외 발생 시 False를 반환해야 한다"""
        # Given
        template_id = "test-id"
        version_number = 1

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.side_effect = Exception("오류 발생")

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.delete_version(template_id, version_number)

            # Then
            assert result is False


class TestDataHandlerVersionUpdate:
    """DataHandler 버전 업데이트 테스트"""

    @pytest.mark.unit
    def test_should_update_template_version(self, sample_template):
        """템플릿 버전을 업데이트할 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 1
        components = {
            'role': ['역할1'],
            'goal': '목표',
            'context': ['컨텍스트'],
            'output': '출력',
            'rule': ['규칙']
        }

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            mock_service.save_template.return_value = True
            sample_template.get_version = Mock(return_value=Mock())
            sample_template.current_version = 1

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.update_template_version(template_id, version_number, components)

            # Then
            assert result is True

    @pytest.mark.unit
    def test_should_return_false_if_version_not_found_for_update(self, sample_template):
        """업데이트할 버전을 찾을 수 없으면 False를 반환해야 한다"""
        # Given
        template_id = sample_template.template_id
        version_number = 999
        components = {'goal': '목표'}

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            sample_template.get_version = Mock(return_value=None)

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.update_template_version(template_id, version_number, components)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_handle_exception_during_version_update(self):
        """버전 업데이트 중 예외 발생 시 False를 반환해야 한다"""
        # Given
        template_id = "test-id"
        version_number = 1
        components = {'goal': '목표'}

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.side_effect = Exception("오류 발생")

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.update_template_version(template_id, version_number, components)

            # Then
            assert result is False

    @pytest.mark.unit
    def test_should_create_new_version_from_existing(self, sample_template):
        """기존 버전으로부터 새 버전을 생성할 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id
        base_version = 1
        components = {
            'role': ['역할'],
            'goal': '새 목표',
            'context': ['컨텍스트'],
            'output': '출력',
            'rule': ['규칙']
        }

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            mock_service.save_template.return_value = True
            sample_template.add_version = Mock(return_value=2)

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.create_new_version_from_existing(template_id, base_version, components)

            # Then
            assert result == 2

    @pytest.mark.unit
    def test_should_return_none_if_version_creation_fails(self, sample_template):
        """버전 생성 실패 시 None을 반환해야 한다"""
        # Given
        template_id = sample_template.template_id
        base_version = 1
        components = {'goal': '목표'}

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            mock_service.save_template.return_value = False

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.create_new_version_from_existing(template_id, base_version, components)

            # Then
            assert result is None

    @pytest.mark.unit
    def test_should_handle_exception_during_version_creation(self):
        """버전 생성 중 예외 발생 시 None을 반환해야 한다"""
        # Given
        template_id = "test-id"
        base_version = 1
        components = {'goal': '목표'}

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.side_effect = Exception("오류 발생")

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.create_new_version_from_existing(template_id, base_version, components)

            # Then
            assert result is None


class TestDataHandlerExport:
    """DataHandler 내보내기 테스트"""

    @pytest.mark.unit
    def test_should_export_template_to_text(self, sample_template):
        """템플릿을 텍스트로 내보낼 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.export_template_to_text(template_id)

            # Then
            assert result is not None
            assert isinstance(result, str)
            assert sample_template.name in result

    @pytest.mark.unit
    def test_should_export_all_versions_when_requested(self, sample_template):
        """요청 시 모든 버전을 내보낼 수 있어야 한다"""
        # Given
        template_id = sample_template.template_id

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.export_template_to_text(template_id, include_all_versions=True)

            # Then
            assert result is not None
            assert "버전" in result

    @pytest.mark.unit
    def test_should_return_none_if_export_template_not_found(self):
        """내보낼 템플릿을 찾을 수 없으면 None을 반환해야 한다"""
        # Given
        template_id = "nonexistent"

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = None

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.export_template_to_text(template_id)

            # Then
            assert result is None

    @pytest.mark.unit
    def test_should_handle_exception_during_export(self, sample_template):
        """내보내기 중 예외 발생 시 None을 반환해야 한다"""
        # Given
        template_id = sample_template.template_id

        with patch('ai_prompt_maker.service.PromptMakerService') as MockService:
            mock_service = MockService.return_value
            mock_service.load_template.return_value = sample_template
            # get_current_version이 예외를 발생시키도록 설정
            sample_template.get_current_version = Mock(side_effect=Exception("오류"))

            handler = DataHandler()
            handler.service = mock_service

            # When
            result = handler.export_template_to_text(template_id, include_all_versions=False)

            # Then
            assert result is None
