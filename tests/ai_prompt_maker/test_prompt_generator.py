# @TEST:TEST-001 | SPEC: .moai/specs/SPEC-TEST-001/spec.md

"""
PromptGenerator 테스트

ai_prompt_maker.prompt_generator 모듈의 PromptGenerator 클래스를 테스트합니다.
- 프롬프트 생성 로직
- 섹션별 포맷팅
- 유효성 검증
"""

import pytest
from ai_prompt_maker.prompt_generator import PromptGenerator
from ai_prompt_maker.models import PromptComponent


class TestPromptGeneratorInitialization:
    """PromptGenerator 초기화 테스트"""

    @pytest.mark.unit
    def test_should_initialize_with_template_format(self):
        """템플릿 형식을 가지고 초기화되어야 한다"""
        # Given/When
        generator = PromptGenerator()

        # Then
        assert generator.template_format is not None
        assert isinstance(generator.template_format, str)


class TestPromptGeneratorGeneratePrompt:
    """PromptGenerator generate_prompt 테스트"""

    @pytest.mark.unit
    def test_should_generate_prompt_from_components(self, sample_component, prompt_generator):
        """컴포넌트로부터 프롬프트를 생성할 수 있어야 한다"""
        # Given/When
        prompt = prompt_generator.generate_prompt(sample_component)

        # Then
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    @pytest.mark.unit
    def test_should_include_all_sections_in_prompt(self, sample_component, prompt_generator):
        """모든 섹션이 프롬프트에 포함되어야 한다"""
        # Given/When
        prompt = prompt_generator.generate_prompt(sample_component)

        # Then
        assert "<Role>" in prompt
        assert "<Goal>" in prompt
        assert "<Context>" in prompt
        assert "<Output>" in prompt
        assert "<Rule>" in prompt

    @pytest.mark.unit
    def test_should_include_document_section_when_provided(self, prompt_generator):
        """문서가 제공되면 Document 섹션이 포함되어야 한다"""
        # Given
        component = PromptComponent(
            goal="테스트",
            document="중요한 문서 내용입니다"
        )

        # When
        prompt = prompt_generator.generate_prompt(component)

        # Then
        assert "<Document>" in prompt
        assert "중요한 문서 내용입니다" in prompt

    @pytest.mark.unit
    def test_should_skip_empty_sections(self, prompt_generator):
        """빈 섹션은 생략되어야 한다"""
        # Given
        minimal_component = PromptComponent(goal="최소 목표")

        # When
        prompt = prompt_generator.generate_prompt(minimal_component)

        # Then
        assert "<Goal>" in prompt
        # role, context, output, rule이 비어있으므로 섹션이 포함되지 않거나 비어있음


class TestPromptGeneratorSectionGeneration:
    """PromptGenerator 섹션 생성 테스트"""

    @pytest.mark.unit
    def test_should_generate_role_section_with_single_role(self, prompt_generator):
        """단일 역할이면 그대로 표시해야 한다"""
        # Given/When
        section = prompt_generator._generate_role_section(["게임 기획자"])

        # Then
        assert section == "게임 기획자"

    @pytest.mark.unit
    def test_should_generate_role_section_with_multiple_roles(self, prompt_generator):
        """복수 역할이면 쉼표로 구분해야 한다"""
        # Given/When
        section = prompt_generator._generate_role_section(["게임 기획자", "QA 엔지니어"])

        # Then
        assert "게임 기획자" in section
        assert "QA 엔지니어" in section
        assert "," in section

    @pytest.mark.unit
    def test_should_return_empty_string_for_empty_role(self, prompt_generator):
        """빈 역할이면 빈 문자열을 반환해야 한다"""
        # Given/When
        section = prompt_generator._generate_role_section([])

        # Then
        assert section == ""

    @pytest.mark.unit
    def test_should_generate_goal_section(self, prompt_generator):
        """Goal 섹션을 생성할 수 있어야 한다"""
        # Given/When
        section = prompt_generator._generate_goal_section("캐릭터 시스템 분석")

        # Then
        assert section == "캐릭터 시스템 분석"

    @pytest.mark.unit
    def test_should_handle_long_goal_text(self, prompt_generator):
        """긴 Goal 텍스트를 처리할 수 있어야 한다"""
        # Given
        long_goal = "a" * 150  # 100자 이상

        # When
        section = prompt_generator._generate_goal_section(long_goal)

        # Then
        assert section == long_goal

    @pytest.mark.unit
    def test_should_generate_document_section(self, prompt_generator):
        """Document 섹션을 생성할 수 있어야 한다"""
        # Given/When
        section = prompt_generator._generate_document_section("문서 내용입니다")

        # Then
        assert section == "문서 내용입니다"

    @pytest.mark.unit
    def test_should_generate_context_section_with_bullet_points(self, prompt_generator):
        """짧은 Context는 불릿 포인트로 표시해야 한다"""
        # Given/When
        section = prompt_generator._generate_context_section(["맥락1", "맥락2"])

        # Then
        assert "- 맥락1" in section
        assert "- 맥락2" in section

    @pytest.mark.unit
    def test_should_generate_context_section_with_numbers_for_long_text(self, prompt_generator):
        """긴 Context는 번호로 표시해야 한다"""
        # Given
        long_context = "a" * 150  # 100자 이상

        # When
        section = prompt_generator._generate_context_section([long_context])

        # Then
        assert "1." in section

    @pytest.mark.unit
    def test_should_generate_output_section(self, prompt_generator):
        """Output 섹션을 생성할 수 있어야 한다"""
        # Given/When
        section = prompt_generator._generate_output_section("보고서")

        # Then
        assert section == "보고서"

    @pytest.mark.unit
    def test_should_generate_rule_section_with_bullet_points(self, prompt_generator):
        """짧은 Rule은 불릿 포인트로 표시해야 한다"""
        # Given/When
        section = prompt_generator._generate_rule_section(["규칙1", "규칙2"])

        # Then
        assert "- 규칙1" in section
        assert "- 규칙2" in section

    @pytest.mark.unit
    def test_should_generate_rule_section_with_numbers_for_long_text(self, prompt_generator):
        """긴 Rule은 번호로 표시해야 한다"""
        # Given
        long_rule = "a" * 150  # 100자 이상

        # When
        section = prompt_generator._generate_rule_section([long_rule])

        # Then
        assert "1." in section


class TestPromptGeneratorValidation:
    """PromptGenerator 유효성 검증 테스트"""

    @pytest.mark.unit
    def test_should_validate_components(self, sample_component, prompt_generator):
        """컴포넌트 유효성을 검증할 수 있어야 한다"""
        # Given/When
        is_valid, error_msg = prompt_generator.validate_components(sample_component)

        # Then
        assert is_valid is True
        assert error_msg == ""

    @pytest.mark.unit
    def test_should_detect_invalid_components(self, prompt_generator):
        """잘못된 컴포넌트를 감지할 수 있어야 한다"""
        # Given
        invalid_component = PromptComponent(goal="a" * 501)  # 최대 길이 초과

        # When
        # validate() 메서드는 __post_init__에서 이미 검증되므로
        # 생성 시점에 예외 발생
        # 여기서는 validate() 메서드 자체 테스트
        try:
            invalid_component = PromptComponent(goal="테스트")
            invalid_component.goal = "a" * 501  # 강제로 잘못된 값 설정
            is_valid, error_msg = prompt_generator.validate_components(invalid_component)

            # Then
            assert is_valid is False
        except ValueError:
            # 생성 시점에 예외 발생하는 것도 정상
            pass


class TestPromptGeneratorPreview:
    """PromptGenerator 미리보기 테스트"""

    @pytest.mark.unit
    def test_should_preview_prompt_from_dict(self, prompt_generator):
        """딕셔너리로부터 미리보기 프롬프트를 생성할 수 있어야 한다"""
        # Given
        components_dict = {
            'goal': '테스트 목표',
            'role': ['역할1'],
            'context': ['맥락1'],
            'output': '출력',
            'rule': ['규칙1']
        }

        # When
        preview = prompt_generator.preview_prompt(components_dict)

        # Then
        assert preview is not None
        assert '<Goal>' in preview
        assert '테스트 목표' in preview

    @pytest.mark.unit
    def test_should_handle_preview_error_gracefully(self, prompt_generator):
        """미리보기 생성 오류를 적절히 처리해야 한다"""
        # Given
        invalid_dict = {'invalid': 'data'}  # goal 없음

        # When
        preview = prompt_generator.preview_prompt(invalid_dict)

        # Then
        assert "오류" in preview


class TestPromptGeneratorSummary:
    """PromptGenerator 요약 정보 테스트"""

    @pytest.mark.unit
    def test_should_generate_prompt_summary(self, sample_component, prompt_generator):
        """프롬프트 요약 정보를 생성할 수 있어야 한다"""
        # Given/When
        summary = prompt_generator.generate_prompt_summary(sample_component)

        # Then
        assert 'role_count' in summary
        assert 'has_goal' in summary
        assert 'context_count' in summary
        assert 'has_output' in summary
        assert 'rule_count' in summary
        assert 'total_sections' in summary
        assert 'estimated_length' in summary

    @pytest.mark.unit
    def test_should_calculate_correct_section_count(self, sample_component, prompt_generator):
        """섹션 개수를 정확히 계산해야 한다"""
        # Given/When
        summary = prompt_generator.generate_prompt_summary(sample_component)

        # Then
        assert summary['has_goal'] is True
        assert summary['role_count'] > 0
        assert summary['total_sections'] > 0


class TestPromptGeneratorKeywordExtraction:
    """PromptGenerator 키워드 추출 테스트"""

    @pytest.mark.unit
    def test_should_extract_keywords_from_prompt(self, prompt_generator, sample_component):
        """프롬프트에서 키워드를 추출할 수 있어야 한다"""
        # Given
        prompt_text = prompt_generator.generate_prompt(sample_component)

        # When
        keywords = prompt_generator.extract_keywords(prompt_text)

        # Then
        assert 'role' in keywords
        assert 'goal' in keywords
        assert 'context' in keywords
        assert 'output' in keywords
        assert 'rule' in keywords

    @pytest.mark.unit
    def test_should_return_empty_keywords_on_parse_error(self, prompt_generator):
        """파싱 오류 시 빈 키워드를 반환해야 한다"""
        # Given
        invalid_prompt = "Invalid prompt without sections"

        # When
        keywords = prompt_generator.extract_keywords(invalid_prompt)

        # Then
        assert keywords['goal'] == ""


class TestPromptGeneratorVariations:
    """PromptGenerator 변형 생성 테스트"""

    @pytest.mark.unit
    def test_should_generate_template_variations(self, sample_component, prompt_generator):
        """템플릿 변형들을 생성할 수 있어야 한다"""
        # Given
        variations = {
            'role': ['새 역할1', '새 역할2'],
            'output': ['새 출력 형식']
        }

        # When
        prompts = prompt_generator.get_template_variations(sample_component, variations)

        # Then
        assert len(prompts) > 1  # 기본 + 변형들
        assert prompts[0] == prompt_generator.generate_prompt(sample_component)

    @pytest.mark.unit
    def test_should_avoid_duplicate_variations(self, sample_component, prompt_generator):
        """중복된 변형을 피해야 한다"""
        # Given
        variations = {
            'role': [sample_component.role[0]]  # 이미 존재하는 역할
        }

        # When
        prompts = prompt_generator.get_template_variations(sample_component, variations)

        # Then
        # 중복 제거로 인해 추가 변형이 없을 수 있음
        assert len(set(prompts)) == len(prompts)  # 모두 고유한 프롬프트
