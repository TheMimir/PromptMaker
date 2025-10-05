"""
Template Storage Manager for localStorage-based persistence.

This module provides a storage abstraction layer that allows templates
to be saved to and loaded from browser localStorage via JavaScript bridge.
This is necessary for Streamlit Cloud deployment where filesystem is ephemeral.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from ai_prompt_maker.models import PromptTemplate, PromptCategory


class TemplateStorageManager:
    """Manages template storage in browser localStorage."""

    STORAGE_KEY = "ai_prompt_maker_templates"
    SESSION_CACHE_KEY = "localstorage_templates_cache"
    SESSION_TIMESTAMP_KEY = "localstorage_cache_timestamp"
    CACHE_TTL_SECONDS = 60  # Cache for 60 seconds

    @staticmethod
    def _get_javascript_bridge() -> str:
        """Generate JavaScript code for localStorage operations."""
        return """
        <script>
        // localStorage Bridge for Streamlit
        const STORAGE_KEY = 'ai_prompt_maker_templates';

        // Save template to localStorage
        function saveTemplate(templateData) {
            try {
                let templates = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

                // Check if template already exists (by template_id)
                const existingIndex = templates.findIndex(t => t.template_id === templateData.template_id);

                if (existingIndex >= 0) {
                    // Update existing template
                    templates[existingIndex] = templateData;
                } else {
                    // Add new template
                    templates.push(templateData);
                }

                localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
                return { success: true, message: '템플릿이 저장되었습니다.' };
            } catch (error) {
                return { success: false, message: '저장 실패: ' + error.message };
            }
        }

        // Load all templates from localStorage
        function loadTemplates() {
            try {
                const templates = localStorage.getItem(STORAGE_KEY);
                return templates ? JSON.parse(templates) : [];
            } catch (error) {
                console.error('Template load error:', error);
                return [];
            }
        }

        // Delete template from localStorage
        function deleteTemplate(templateId) {
            try {
                let templates = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
                templates = templates.filter(t => t.template_id !== templateId);
                localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
                return { success: true, message: '템플릿이 삭제되었습니다.' };
            } catch (error) {
                return { success: false, message: '삭제 실패: ' + error.message };
            }
        }

        // Expose functions to Streamlit
        window.templateStorage = {
            save: saveTemplate,
            load: loadTemplates,
            delete: deleteTemplate
        };

        // Send loaded templates to Streamlit via session state
        window.addEventListener('load', function() {
            const templates = loadTemplates();
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                key: 'localstorage_templates',
                value: templates
            }, '*');
        });
        </script>
        """

    @classmethod
    def initialize(cls):
        """Initialize localStorage bridge. Call this once in app startup."""
        # Inject JavaScript bridge
        components.html(cls._get_javascript_bridge(), height=0, width=0)

    @classmethod
    def save_template(
        cls,
        name: str,
        category: PromptCategory,
        components_dict: Dict[str, Any],
        generated_prompt: str,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Save a template to localStorage.

        Args:
            name: Template name
            category: Template category
            components_dict: Dict with role, goal, context, document, output, rule
            generated_prompt: Generated prompt text
            description: Template description
            tags: Optional list of tags

        Returns:
            bool: True if saved successfully
        """
        try:
            # Create PromptTemplate object
            from ai_prompt_maker.models import PromptComponent, PromptVersion

            # Create component object
            component = PromptComponent(
                role=components_dict.get('role', []),
                goal=components_dict.get('goal', ''),
                context=components_dict.get('context', []),
                document=components_dict.get('document', ''),
                output=components_dict.get('output', ''),
                rule=components_dict.get('rule', [])
            )

            # Generate template ID
            template_id = str(uuid.uuid4())

            # Create template
            template = PromptTemplate(
                template_id=template_id,
                name=name,
                category=category,
                tags=tags or [],
                description=description,
                current_version=1,
                versions=[
                    PromptVersion(
                        version=1,
                        components=component,
                        generated_prompt=generated_prompt,
                        description=description,
                        created_at=datetime.now()
                    )
                ],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Convert to dict
            template_dict = template.to_dict()

            # Save to localStorage via JavaScript
            js_code = f"""
            <script>
            (function() {{
                const templateData = {json.dumps(template_dict)};
                const result = window.templateStorage.save(templateData);

                // Send result back to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    key: 'template_save_result',
                    value: result
                }}, '*');
            }})();
            </script>
            """

            components.html(js_code, height=0, width=0)

            # Clear cache
            if cls.SESSION_CACHE_KEY in st.session_state:
                del st.session_state[cls.SESSION_CACHE_KEY]
            if cls.SESSION_TIMESTAMP_KEY in st.session_state:
                del st.session_state[cls.SESSION_TIMESTAMP_KEY]

            return True

        except Exception as e:
            st.error(f"템플릿 저장 실패: {e}")
            return False

    @classmethod
    def load_templates(cls, use_cache: bool = True) -> List[PromptTemplate]:
        """
        Load all templates from localStorage.

        Args:
            use_cache: Whether to use session state cache

        Returns:
            List of PromptTemplate objects
        """
        # Check cache first
        if use_cache:
            now = datetime.now()
            cache_timestamp = st.session_state.get(cls.SESSION_TIMESTAMP_KEY)

            if cache_timestamp:
                age = (now - cache_timestamp).total_seconds()
                if age < cls.CACHE_TTL_SECONDS:
                    cached_templates = st.session_state.get(cls.SESSION_CACHE_KEY)
                    if cached_templates is not None:
                        return cached_templates

        try:
            # Load from localStorage via JavaScript
            js_code = """
            <script>
            (function() {
                const templates = window.templateStorage ? window.templateStorage.load() : [];

                // Send templates back to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'localstorage_templates',
                    value: templates
                }, '*');
            })();
            </script>
            """

            components.html(js_code, height=0, width=0)

            # Get templates from component value
            templates_data = st.session_state.get('localstorage_templates', [])

            # Convert to PromptTemplate objects
            templates = []
            for template_dict in templates_data:
                try:
                    template = PromptTemplate.from_dict(template_dict)
                    templates.append(template)
                except Exception as e:
                    st.warning(f"템플릿 로딩 실패 (ID: {template_dict.get('template_id', 'unknown')}): {e}")
                    continue

            # Update cache
            st.session_state[cls.SESSION_CACHE_KEY] = templates
            st.session_state[cls.SESSION_TIMESTAMP_KEY] = datetime.now()

            return templates

        except Exception as e:
            st.error(f"템플릿 로딩 실패: {e}")
            return []

    @classmethod
    def load_template(cls, template_id: str) -> Optional[PromptTemplate]:
        """
        Load a specific template by ID.

        Args:
            template_id: Template ID to load

        Returns:
            PromptTemplate object or None if not found
        """
        templates = cls.load_templates()

        for template in templates:
            if template.template_id == template_id:
                return template

        return None

    @classmethod
    def delete_template(cls, template_id: str) -> bool:
        """
        Delete a template from localStorage.

        Args:
            template_id: Template ID to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            js_code = f"""
            <script>
            (function() {{
                const result = window.templateStorage.delete('{template_id}');

                // Send result back to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    key: 'template_delete_result',
                    value: result
                }}, '*');
            }})();
            </script>
            """

            components.html(js_code, height=0, width=0)

            # Clear cache
            if cls.SESSION_CACHE_KEY in st.session_state:
                del st.session_state[cls.SESSION_CACHE_KEY]
            if cls.SESSION_TIMESTAMP_KEY in st.session_state:
                del st.session_state[cls.SESSION_TIMESTAMP_KEY]

            return True

        except Exception as e:
            st.error(f"템플릿 삭제 실패: {e}")
            return False

    @classmethod
    def get_storage_stats(cls) -> Dict[str, Any]:
        """
        Get localStorage usage statistics.

        Returns:
            Dict with storage statistics
        """
        templates = cls.load_templates()

        total_size = 0
        for template in templates:
            template_json = json.dumps(template.to_dict())
            total_size += len(template_json.encode('utf-8'))

        return {
            'template_count': len(templates),
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'estimated_capacity_mb': 5,  # Most browsers support 5-10MB
            'usage_percent': round((total_size / (5 * 1024 * 1024)) * 100, 2)
        }
