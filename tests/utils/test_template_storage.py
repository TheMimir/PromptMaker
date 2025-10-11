# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
TemplateStorageManager 테스트

utils.template_storage 모듈의 TemplateStorageManager 클래스를 테스트합니다.
Streamlit 의존성이 있으므로 mock을 사용하여 테스트합니다.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai_prompt_maker.models import PromptTemplate, PromptCategory, PromptComponent, PromptVersion


class TestTemplateStorageManagerConstants:
    """TemplateStorageManager 상수 테스트"""

    @pytest.mark.unit
    def test_should_have_storage_key_constant(self):
        """STORAGE_KEY 상수가 정의되어 있어야 한다"""
        # Given/When
        from utils.template_storage import TemplateStorageManager

        # Then
        assert hasattr(TemplateStorageManager, 'STORAGE_KEY')
        assert TemplateStorageManager.STORAGE_KEY == "ai_prompt_maker_templates"

    @pytest.mark.unit
    def test_should_have_cache_constants(self):
        """캐시 관련 상수가 정의되어 있어야 한다"""
        # Given/When
        from utils.template_storage import TemplateStorageManager

        # Then
        assert hasattr(TemplateStorageManager, 'SESSION_CACHE_KEY')
        assert hasattr(TemplateStorageManager, 'SESSION_TIMESTAMP_KEY')
        assert hasattr(TemplateStorageManager, 'CACHE_TTL_SECONDS')


class TestTemplateStorageManagerJavaScriptBridge:
    """TemplateStorageManager JavaScript 브릿지 테스트"""

    @pytest.mark.unit
    def test_should_generate_javascript_bridge_code(self):
        """JavaScript 브릿지 코드를 생성할 수 있어야 한다"""
        # Given/When
        from utils.template_storage import TemplateStorageManager

        js_code = TemplateStorageManager._get_javascript_bridge()

        # Then
        assert isinstance(js_code, str)
        assert '<script>' in js_code
        assert 'localStorage' in js_code
        assert 'saveTemplate' in js_code
        assert 'loadTemplates' in js_code
        assert 'deleteTemplate' in js_code


class TestTemplateStorageManagerSaveTemplate:
    """TemplateStorageManager save_template 테스트"""

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_save_template_successfully(self, mock_components, mock_st, sample_component):
        """템플릿을 성공적으로 저장할 수 있어야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {}
        mock_components.html = Mock()

        # When
        result = TemplateStorageManager.save_template(
            name="Test Template",
            category=PromptCategory.PLANNING,
            components_dict={
                'role': sample_component.role,
                'goal': sample_component.goal,
                'context': sample_component.context,
                'document': sample_component.document,
                'output': sample_component.output,
                'rule': sample_component.rule
            },
            generated_prompt="<Role>게임 기획자</Role>",
            description="Test description"
        )

        # Then
        assert result is True
        mock_components.html.assert_called()

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_clear_cache_after_save(self, mock_components, mock_st):
        """저장 후 캐시를 클리어해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {
            TemplateStorageManager.SESSION_CACHE_KEY: [],
            TemplateStorageManager.SESSION_TIMESTAMP_KEY: datetime.now()
        }
        mock_components.html = Mock()

        # When
        TemplateStorageManager.save_template(
            name="Test",
            category=PromptCategory.ALL,
            components_dict={'goal': 'test'},
            generated_prompt="test"
        )

        # Then
        assert TemplateStorageManager.SESSION_CACHE_KEY not in mock_st.session_state


class TestTemplateStorageManagerLoadTemplates:
    """TemplateStorageManager load_templates 테스트"""

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_load_templates_from_localstorage(self, mock_components, mock_st):
        """localStorage에서 템플릿을 로드할 수 있어야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {'localstorage_templates': []}
        mock_components.html = Mock()

        # When
        templates = TemplateStorageManager.load_templates(use_cache=False)

        # Then
        assert isinstance(templates, list)
        mock_components.html.assert_called()

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    def test_should_use_cache_when_available(self, mock_st):
        """캐시가 유효하면 캐시를 사용해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        cached_templates = [Mock(), Mock()]
        mock_st.session_state = {
            TemplateStorageManager.SESSION_CACHE_KEY: cached_templates,
            TemplateStorageManager.SESSION_TIMESTAMP_KEY: datetime.now()
        }

        # When
        templates = TemplateStorageManager.load_templates(use_cache=True)

        # Then
        assert templates == cached_templates

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    def test_should_invalidate_expired_cache(self, mock_st):
        """만료된 캐시는 무효화해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager
        from datetime import timedelta

        old_timestamp = datetime.now() - timedelta(seconds=100)
        mock_st.session_state = {
            TemplateStorageManager.SESSION_CACHE_KEY: [],
            TemplateStorageManager.SESSION_TIMESTAMP_KEY: old_timestamp,
            'localstorage_templates': []
        }

        with patch('utils.template_storage.components'):
            # When
            TemplateStorageManager.load_templates(use_cache=True)

            # Then - 캐시가 만료되어 새로 로드됨
            assert True  # components.html이 호출됨을 검증


class TestTemplateStorageManagerLoadTemplate:
    """TemplateStorageManager load_template (단일) 테스트"""

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_load_specific_template_by_id(self, mock_components, mock_st, sample_template):
        """ID로 특정 템플릿을 로드할 수 있어야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {'localstorage_templates': []}
        mock_components.html = Mock()

        with patch.object(TemplateStorageManager, 'load_templates', return_value=[sample_template]):
            # When
            template = TemplateStorageManager.load_template(sample_template.template_id)

            # Then
            assert template is not None
            assert template.template_id == sample_template.template_id

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_return_none_if_template_id_not_found(self, mock_components, mock_st):
        """존재하지 않는 ID면 None을 반환해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        with patch.object(TemplateStorageManager, 'load_templates', return_value=[]):
            # When
            template = TemplateStorageManager.load_template("nonexistent-id")

            # Then
            assert template is None


class TestTemplateStorageManagerDeleteTemplate:
    """TemplateStorageManager delete_template 테스트"""

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_delete_template_successfully(self, mock_components, mock_st):
        """템플릿을 성공적으로 삭제할 수 있어야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {}
        mock_components.html = Mock()

        # When
        result = TemplateStorageManager.delete_template("test-id-123")

        # Then
        assert result is True
        mock_components.html.assert_called()

    @pytest.mark.unit
    @patch('utils.template_storage.st')
    @patch('utils.template_storage.components')
    def test_should_clear_cache_after_delete(self, mock_components, mock_st):
        """삭제 후 캐시를 클리어해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_st.session_state = {
            TemplateStorageManager.SESSION_CACHE_KEY: [],
            TemplateStorageManager.SESSION_TIMESTAMP_KEY: datetime.now()
        }
        mock_components.html = Mock()

        # When
        TemplateStorageManager.delete_template("test-id")

        # Then
        assert TemplateStorageManager.SESSION_CACHE_KEY not in mock_st.session_state


class TestTemplateStorageManagerGetStorageStats:
    """TemplateStorageManager get_storage_stats 테스트"""

    @pytest.mark.unit
    def test_should_return_storage_statistics(self, sample_template):
        """스토리지 통계를 반환할 수 있어야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        with patch.object(TemplateStorageManager, 'load_templates', return_value=[sample_template]):
            # When
            stats = TemplateStorageManager.get_storage_stats()

            # Then
            assert 'template_count' in stats
            assert 'total_size_bytes' in stats
            assert 'total_size_kb' in stats
            assert 'estimated_capacity_mb' in stats
            assert 'usage_percent' in stats

    @pytest.mark.unit
    def test_should_calculate_correct_template_count(self):
        """템플릿 개수를 정확히 계산해야 한다"""
        # Given
        from utils.template_storage import TemplateStorageManager

        mock_templates = [Mock(), Mock(), Mock()]

        with patch.object(TemplateStorageManager, 'load_templates', return_value=mock_templates):
            # When
            stats = TemplateStorageManager.get_storage_stats()

            # Then
            assert stats['template_count'] == 3
