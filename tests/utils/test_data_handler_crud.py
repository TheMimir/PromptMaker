# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
DataHandler CRUD 테스트

utils.data_handler 모듈의 DataHandler 클래스를 테스트합니다.
- 템플릿 로드
- 템플릿 삭제
- 템플릿 복제
"""

import pytest
from unittest.mock import Mock, patch

from utils.data_handler import DataHandler


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
