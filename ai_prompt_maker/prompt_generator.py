"""
Prompt Generator

키워드 조합으로 구조화된 프롬프트를 생성하는 엔진
"""
from typing import Dict, List
from .models import PromptComponent, OutputFormat


class PromptGenerator:
    """프롬프트 생성 엔진"""

    def __init__(self, output_format: OutputFormat = OutputFormat.XML):
        self.output_format = output_format

    def generate_prompt(self, components: PromptComponent, output_format: OutputFormat = None) -> str:
        """컴포넌트로부터 프롬프트 생성

        Args:
            components: 프롬프트 컴포넌트
            output_format: 출력 포맷 (None이면 인스턴스 기본값 사용)
        """
        fmt = output_format or self.output_format

        if fmt == OutputFormat.MARKDOWN:
            return self._generate_markdown_prompt(components)
        else:
            return self._generate_xml_prompt(components)

    def _generate_xml_prompt(self, components: PromptComponent) -> str:
        """XML 형식 프롬프트 생성"""
        try:
            # Document가 있으면 Goal에 참조 문구 추가
            enhanced_goal = components.goal
            if components.document and components.document.strip():
                enhanced_goal = f"{components.goal}\n\n**중요: 아래 제공된 Document를 반드시 참고하세요.**"

            # 각 섹션 생성
            role_section = self._generate_role_section(components.role)
            goal_section = self._generate_goal_section(enhanced_goal)
            document_section = self._generate_document_section(components.document)
            context_section = self._generate_context_section(components.context)
            output_section = self._generate_output_section(components.output)
            rule_section = self._generate_rule_section(components.rule)

            # 전체 프롬프트 조합
            prompt_parts = []

            if role_section:
                prompt_parts.append(f"<Role>\n{role_section}\n</Role>")

            if goal_section:
                prompt_parts.append(f"<Goal>\n{goal_section}\n</Goal>")

            if document_section:
                prompt_parts.append(f"<Document>\n{document_section}\n</Document>")

            if context_section:
                prompt_parts.append(f"<Context>\n{context_section}\n</Context>")

            if output_section:
                prompt_parts.append(f"<Output>\n{output_section}\n</Output>")

            if rule_section:
                prompt_parts.append(f"<Rule>\n{rule_section}\n</Rule>")

            return "\n\n".join(prompt_parts)

        except Exception as e:
            return f"프롬프트 생성 중 오류 발생: {str(e)}"

    def _generate_markdown_prompt(self, components: PromptComponent) -> str:
        """Markdown 형식 프롬프트 생성"""
        try:
            # Document가 있으면 Goal에 참조 문구 추가
            enhanced_goal = components.goal
            if components.document and components.document.strip():
                enhanced_goal = f"{components.goal}\n\n**중요: 아래 제공된 Document를 반드시 참고하세요.**"

            # 각 섹션 생성
            role_section = self._generate_role_section(components.role)
            goal_section = self._generate_goal_section(enhanced_goal)
            document_section = self._generate_document_section(components.document)
            context_section = self._generate_context_section(components.context)
            output_section = self._generate_output_section(components.output)
            rule_section = self._generate_rule_section(components.rule)

            # 전체 프롬프트 조합 (Markdown 형식)
            prompt_parts = []

            if role_section:
                prompt_parts.append(f"# Role\n\n{role_section}")

            if goal_section:
                prompt_parts.append(f"# Goal\n\n{goal_section}")

            if document_section:
                prompt_parts.append(f"# Document\n\n{document_section}")

            if context_section:
                prompt_parts.append(f"# Context\n\n{context_section}")

            if output_section:
                prompt_parts.append(f"# Output\n\n{output_section}")

            if rule_section:
                prompt_parts.append(f"# Rule\n\n{rule_section}")

            return "\n\n".join(prompt_parts)

        except Exception as e:
            return f"프롬프트 생성 중 오류 발생: {str(e)}"

    def _generate_role_section(self, roles: List[str]) -> str:
        """Role 섹션 생성"""
        if not roles:
            return ""

        if len(roles) == 1:
            return roles[0]

        return ", ".join(roles)

    def _generate_goal_section(self, goal: str) -> str:
        """Goal 섹션 생성"""
        if not goal or not goal.strip():
            return ""

        # 확장된 목표인지 확인 (길이가 100자 이상이면 확장된 목표로 판단)
        goal_text = goal.strip()
        if len(goal_text) > 100:
            # 확장된 목표: 명확한 구분을 위해 그대로 표시
            return goal_text
        else:
            # 간단한 목표: 기존 방식 유지
            return goal_text

    def _generate_document_section(self, document: str) -> str:
        """Document 섹션 생성"""
        if not document or not document.strip():
            return ""

        # Document가 있으면 그대로 반환
        return document.strip()

    def _generate_context_section(self, contexts: List[str]) -> str:
        """Context 섹션 생성"""
        if not contexts:
            return ""

        # 확장된 맥락인지 확인 (길이가 100자 이상이면 확장된 맥락으로 판단)
        formatted_contexts = []

        for i, context in enumerate(contexts, 1):
            if len(context) > 100:
                # 확장된 맥락: 번호와 함께 단락 형태로 표시
                formatted_contexts.append(f"{i}. {context}")
            else:
                # 간단한 맥락: 기존 불릿 포인트 형태로 표시
                formatted_contexts.append(f"- {context}")

        return "\n\n".join(formatted_contexts)

    def _generate_output_section(self, output: str) -> str:
        """Output 섹션 생성"""
        return output.strip() if output else ""

    def _generate_rule_section(self, rules: List[str]) -> str:
        """Rule 섹션 생성"""
        if not rules:
            return ""

        # 확장된 규칙인지 확인 (길이가 100자 이상이면 확장된 규칙으로 판단)
        formatted_rules = []

        for i, rule in enumerate(rules, 1):
            if len(rule) > 100:
                # 확장된 규칙: 번호와 함께 단락 형태로 표시
                formatted_rules.append(f"{i}. {rule}")
            else:
                # 간단한 규칙: 기존 불릿 포인트 형태로 표시
                formatted_rules.append(f"- {rule}")

        return "\n\n".join(formatted_rules)

    def validate_components(self, components: PromptComponent) -> tuple[bool, str]:
        """컴포넌트 유효성 검증"""
        return components.validate()

    def preview_prompt(self, components: Dict[str, any]) -> str:
        """미리보기용 프롬프트 생성 (딕셔너리 입력)"""
        try:
            # 딕셔너리를 PromptComponent로 변환
            prompt_component = PromptComponent(
                role=components.get('role', []),
                goal=components.get('goal', ''),
                context=components.get('context', []),
                output=components.get('output', ''),
                rule=components.get('rule', [])
            )

            return self.generate_prompt(prompt_component)

        except Exception as e:
            return f"미리보기 생성 중 오류: {str(e)}"

    def generate_prompt_summary(self, components: PromptComponent) -> Dict[str, any]:
        """프롬프트 요약 정보 생성"""
        return {
            "role_count": len(components.role),
            "has_goal": bool(components.goal),
            "context_count": len(components.context),
            "has_document": bool(components.document and components.document.strip()),
            "has_output": bool(components.output),
            "rule_count": len(components.rule),
            "total_sections": sum([
                bool(components.role),
                bool(components.goal),
                bool(components.context),
                bool(components.document and components.document.strip()),
                bool(components.output),
                bool(components.rule)
            ]),
            "estimated_length": len(self.generate_prompt(components))
        }

    def extract_keywords(self, prompt_text: str) -> Dict[str, List[str]]:
        """기존 프롬프트에서 키워드 추출 (역공학)"""
        keywords = {
            "role": [],
            "goal": "",
            "context": [],
            "output": "",
            "rule": []
        }

        try:
            # 각 섹션 파싱
            sections = self._parse_sections(prompt_text)

            for section_name, content in sections.items():
                if section_name.lower() == "role":
                    keywords["role"] = [item.strip() for item in content.split(",")]
                elif section_name.lower() == "goal":
                    keywords["goal"] = content.strip()
                elif section_name.lower() == "context":
                    keywords["context"] = [item.strip() for item in content.split(",")]
                elif section_name.lower() == "output":
                    keywords["output"] = content.strip()
                elif section_name.lower() == "rule":
                    # 규칙은 줄바꿈과 하이픈으로 구분
                    rules = []
                    for line in content.split("\n"):
                        line = line.strip()
                        if line.startswith("- "):
                            rules.append(line[2:])
                        elif line:
                            rules.append(line)
                    keywords["rule"] = rules

        except Exception:
            # 파싱 실패 시 빈 키워드 반환
            pass

        return keywords

    def _parse_sections(self, prompt_text: str) -> Dict[str, str]:
        """프롬프트 텍스트에서 섹션 파싱"""
        sections = {}
        current_section = None
        current_content = []

        lines = prompt_text.split("\n")

        for line in lines:
            line = line.strip()

            # 섹션 시작 태그 확인
            if line.startswith("<") and line.endswith(">") and not line.startswith("</"):
                # 이전 섹션 저장
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # 새 섹션 시작
                current_section = line[1:-1]  # < > 제거
                current_content = []

            # 섹션 종료 태그 확인
            elif line.startswith("</") and line.endswith(">"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                    current_section = None
                    current_content = []

            # 내용 추가
            elif current_section and line:
                current_content.append(line)

        # 마지막 섹션 저장
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def get_template_variations(self, base_components: PromptComponent, variations: Dict[str, List[str]]) -> List[str]:
        """기본 컴포넌트의 변형들 생성"""
        prompts = []

        # 기본 프롬프트
        prompts.append(self.generate_prompt(base_components))

        # 각 변형 적용
        for section, options in variations.items():
            for option in options:
                modified_components = PromptComponent(
                    role=base_components.role.copy(),
                    goal=base_components.goal,
                    context=base_components.context.copy(),
                    output=base_components.output,
                    rule=base_components.rule.copy()
                )

                # 섹션별 변형 적용
                if section == "role" and option not in modified_components.role:
                    modified_components.role.append(option)
                elif section == "context" and option not in modified_components.context:
                    modified_components.context.append(option)
                elif section == "output":
                    modified_components.output = option
                elif section == "rule" and option not in modified_components.rule:
                    modified_components.rule.append(option)

                # 변형된 프롬프트 생성
                variation_prompt = self.generate_prompt(modified_components)
                if variation_prompt not in prompts:
                    prompts.append(variation_prompt)

        return prompts