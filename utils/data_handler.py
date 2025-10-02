"""
Data Handler - Wrapper around PromptMakerService for UI components
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import PromptTemplate, PromptComponent, PromptCategory


class DataHandler:
    """데이터 핸들러 - UI 컴포넌트를 위한 서비스 래퍼"""

    def __init__(self):
        """데이터 핸들러 초기화"""
        self.service = PromptMakerService()

    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        return self.service.get_config()

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """템플릿 목록 조회"""
        return self.service.list_templates(category=category)

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """템플릿 검색"""
        return self.service.search_templates(query)

    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """템플릿 로드"""
        template = self.service.load_template(template_id)
        if template:
            return template.to_dict()
        return None

    def delete_template(self, template_id: str) -> bool:
        """템플릿 삭제"""
        return self.service.delete_template(template_id)

    def duplicate_template(self, template_id: str, new_name: str) -> Optional[str]:
        """템플릿 복제"""
        try:
            new_template = self.service.copy_template(template_id, new_name)
            if new_template:
                return new_template.template_id
            return None
        except Exception as e:
            print(f"템플릿 복제 실패: {e}")
            return None

    def get_version_history(self, template_id: str) -> List[Dict[str, Any]]:
        """버전 히스토리 조회"""
        template = self.service.load_template(template_id)
        if not template:
            return []

        version_history = []
        for version in template.versions:
            version_info = {
                'version': version.version,
                'created_at': version.created_at,
                'description': version.description,
                'is_current': version.version == template.current_version,
                'components_summary': {
                    'role_count': len(version.components.role),
                    'has_goal': bool(version.components.goal),
                    'context_count': len(version.components.context),
                    'has_output': bool(version.components.output),
                    'rule_count': len(version.components.rule)
                }
            }
            version_history.append(version_info)

        return version_history

    def set_current_version(self, template_id: str, version_number: int) -> bool:
        """현재 버전 설정"""
        try:
            template = self.service.load_template(template_id)
            if not template:
                return False

            # 버전이 존재하는지 확인
            if not template.get_version(version_number):
                return False

            template.current_version = version_number
            return self.service.save_template(template)
        except Exception as e:
            print(f"버전 설정 실패: {e}")
            return False

    def delete_version(self, template_id: str, version_number: int) -> bool:
        """버전 삭제"""
        try:
            template = self.service.load_template(template_id)
            if not template:
                return False

            if template.delete_version(version_number):
                return self.service.save_template(template)
            return False
        except Exception as e:
            print(f"버전 삭제 실패: {e}")
            return False

    def update_template_version(self, template_id: str, version_number: int,
                               components: Dict[str, Any], description: str = "") -> bool:
        """템플릿 버전 업데이트"""
        try:
            template = self.service.load_template(template_id)
            if not template:
                return False

            # 버전 찾기
            version = template.get_version(version_number)
            if not version:
                return False

            # 컴포넌트 생성
            prompt_component = PromptComponent(
                role=components.get('role', []),
                goal=components.get('goal', ''),
                context=components.get('context', []),
                document=components.get('document', ''),
                output=components.get('output', ''),
                rule=components.get('rule', [])
            )

            # 버전 업데이트
            if version_number == template.current_version:
                template.update_current_version(prompt_component, description)
            else:
                version.components = prompt_component
                version.description = description
                # 프롬프트 재생성
                from ai_prompt_maker.prompt_generator import PromptGenerator
                generator = PromptGenerator()
                version.generated_prompt = generator.generate_prompt(prompt_component)

            return self.service.save_template(template)
        except Exception as e:
            print(f"버전 업데이트 실패: {e}")
            return False

    def create_new_version_from_existing(self, template_id: str, base_version: int,
                                        components: Dict[str, Any], description: str = "") -> Optional[int]:
        """기존 버전으로부터 새 버전 생성"""
        try:
            template = self.service.load_template(template_id)
            if not template:
                return None

            # 컴포넌트 생성
            prompt_component = PromptComponent(
                role=components.get('role', []),
                goal=components.get('goal', ''),
                context=components.get('context', []),
                document=components.get('document', ''),
                output=components.get('output', ''),
                rule=components.get('rule', [])
            )

            # 새 버전 추가
            new_version_number = template.add_version(prompt_component, description)

            if self.service.save_template(template):
                return new_version_number
            return None
        except Exception as e:
            print(f"새 버전 생성 실패: {e}")
            return None

    def export_template_to_text(self, template_id: str, include_all_versions: bool = False) -> Optional[str]:
        """템플릿을 텍스트로 내보내기"""
        try:
            template = self.service.load_template(template_id)
            if not template:
                return None

            export_lines = []
            export_lines.append(f"템플릿 이름: {template.name}")
            export_lines.append(f"카테고리: {template.category.value}")
            export_lines.append(f"태그: {', '.join(template.tags)}")
            export_lines.append("=" * 80)
            export_lines.append("")

            if include_all_versions:
                # 모든 버전 포함
                for version in template.versions:
                    export_lines.append(f"버전 {version.version}")
                    if version.description:
                        export_lines.append(f"설명: {version.description}")
                    export_lines.append(f"생성일: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    export_lines.append("-" * 80)
                    export_lines.append(version.generated_prompt)
                    export_lines.append("")
                    export_lines.append("=" * 80)
                    export_lines.append("")
            else:
                # 현재 버전만
                current_version = template.get_current_version()
                if current_version:
                    export_lines.append(f"버전 {current_version.version} (현재)")
                    if current_version.description:
                        export_lines.append(f"설명: {current_version.description}")
                    export_lines.append(f"생성일: {current_version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    export_lines.append("-" * 80)
                    export_lines.append(current_version.generated_prompt)

            return "\n".join(export_lines)
        except Exception as e:
            print(f"텍스트 내보내기 실패: {e}")
            return None
