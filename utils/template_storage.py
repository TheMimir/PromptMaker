"""
Template Storage Manager for session state-based persistence with file system backup.

This module provides a storage abstraction layer that allows templates
to be saved to and loaded from both Streamlit session state and file system.
Templates persist across sessions and can be exported/imported.
"""

import json
import streamlit as st
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from pathlib import Path

from ai_prompt_maker.models import PromptTemplate, PromptCategory


class TemplateStorageManager:
    """Manages template storage in Streamlit session state with file system backup.

    Note: Uses st.session_state as primary storage with file system as persistent backup.
    Templates persist across sessions.
    """

    STORAGE_KEY = "ai_prompt_maker_templates"
    TEMPLATE_DIR = Path("ai_prompt_maker/templates")

    @classmethod
    def initialize(cls):
        """Initialize template storage. Call this once in app startup."""
        # Initialize session state storage if not exists
        if cls.STORAGE_KEY not in st.session_state:
            st.session_state[cls.STORAGE_KEY] = []

            # Load templates from file system
            cls._load_from_filesystem()

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

            # Save to file system
            cls._save_to_filesystem(template)

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

            # Delete from file system
            if len(templates) < original_count:
                cls._delete_from_filesystem(template_id)

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

    @classmethod
    def _load_from_filesystem(cls):
        """Load templates from file system into session state."""
        try:
            # Create directory if not exists
            cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

            # Load all JSON files
            templates = []
            for json_file in cls.TEMPLATE_DIR.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        template = PromptTemplate.from_dict(data)
                        templates.append(template)
                except Exception as e:
                    # Skip invalid files
                    print(f"Warning: Failed to load template from {json_file}: {e}")
                    continue

            # Update session state
            if templates:
                st.session_state[cls.STORAGE_KEY] = templates

        except Exception as e:
            # Silent fail on initialization - just log the error
            print(f"Warning: Failed to load templates from file system: {e}")

    @classmethod
    def _save_to_filesystem(cls, template: PromptTemplate):
        """Save a template to file system."""
        try:
            # Create directory if not exists
            cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

            # Save template as JSON file
            filename = f"{template.template_id}.json"
            filepath = cls.TEMPLATE_DIR / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)

        except Exception as e:
            # Silent fail - template is still in session state
            print(f"Warning: Failed to save template to file system: {e}")

    @classmethod
    def _delete_from_filesystem(cls, template_id: str):
        """Delete a template from file system."""
        try:
            filename = f"{template_id}.json"
            filepath = cls.TEMPLATE_DIR / filename

            if filepath.exists():
                filepath.unlink()

        except Exception as e:
            # Silent fail - template is already deleted from session state
            print(f"Warning: Failed to delete template from file system: {e}")
