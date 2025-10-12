"""
Template Storage Manager for session state-based persistence.

This module provides a storage abstraction layer that allows templates
to be saved to and loaded from Streamlit session state.
Templates persist during the session and can be exported/imported for long-term storage.
"""

import json
import streamlit as st
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from ai_prompt_maker.models import PromptTemplate, PromptCategory


class TemplateStorageManager:
    """Manages template storage in Streamlit session state.

    Note: Uses st.session_state as primary storage. Templates persist during the session
    and can be exported/imported for long-term storage.
    """

    STORAGE_KEY = "ai_prompt_maker_templates"

    @classmethod
    def initialize(cls):
        """Initialize template storage. Call this once in app startup."""
        # Initialize session state storage if not exists
        if cls.STORAGE_KEY not in st.session_state:
            st.session_state[cls.STORAGE_KEY] = []

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
        Save a template to session state.

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
                current_version=1,
                versions=[
                    PromptVersion(
                        version=1,
                        components=component,
                        generated_prompt=generated_prompt,
                        description=description,
                        created_at=datetime.now()
                    )
                ]
            )

            # Initialize storage if needed
            cls.initialize()

            # Save to session state
            templates = st.session_state[cls.STORAGE_KEY]

            # Check if template with same ID exists (update)
            existing_index = next(
                (i for i, t in enumerate(templates) if t.template_id == template_id),
                None
            )

            if existing_index is not None:
                templates[existing_index] = template
            else:
                templates.append(template)

            st.session_state[cls.STORAGE_KEY] = templates

            return True

        except Exception as e:
            st.error(f"템플릿 저장 실패: {e}")
            import traceback
            st.error(traceback.format_exc())
            return False

    @classmethod
    def load_templates(cls, use_cache: bool = True) -> List[PromptTemplate]:
        """
        Load all templates from session state.

        Args:
            use_cache: Not used, kept for API compatibility

        Returns:
            List of PromptTemplate objects
        """
        try:
            # Initialize storage if needed
            cls.initialize()

            # Return templates from session state
            templates = st.session_state.get(cls.STORAGE_KEY, [])
            return templates

        except Exception as e:
            st.error(f"템플릿 로딩 실패: {e}")
            import traceback
            st.error(traceback.format_exc())
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
        Delete a template from session state.

        Args:
            template_id: Template ID to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            # Initialize storage if needed
            cls.initialize()

            # Get templates from session state
            templates = st.session_state[cls.STORAGE_KEY]

            # Filter out the template to delete
            original_count = len(templates)
            templates = [t for t in templates if t.template_id != template_id]

            # Update session state
            st.session_state[cls.STORAGE_KEY] = templates

            # Return True if template was found and deleted
            return len(templates) < original_count

        except Exception as e:
            st.error(f"템플릿 삭제 실패: {e}")
            import traceback
            st.error(traceback.format_exc())
            return False

    @classmethod
    def get_storage_stats(cls) -> Dict[str, Any]:
        """
        Get session state storage statistics.

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
            'total_size_kb': round(total_size / 1024, 2)
        }
