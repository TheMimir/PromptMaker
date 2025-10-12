# @TEST:EXPORT-001 | SPEC: .moai/specs/SPEC-EXPORT-001/spec.md

"""
Export Service 테스트

프롬프트 내보내기 기능(Markdown, JSON, PDF)에 대한 TDD 테스트
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from ai_prompt_maker.models import PromptComponent, PromptVersion, PromptTemplate, PromptCategory

# 조건부 import - reportlab이 설치되어 있지 않아도 테스트 실행 가능
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ==================== Fixtures ====================

@pytest.fixture
def export_service(temp_dir):
    """ExportService 픽스처"""
    from ai_prompt_maker.export_service import ExportService

    fonts_dir = temp_dir / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    return ExportService(fonts_dir=str(fonts_dir))


@pytest.fixture
def sample_prompt_component():
    """샘플 프롬프트 컴포넌트"""
    return PromptComponent(
        role=["게임 기획자", "QA 엔지니어"],
        goal="캐릭터 레벨업 시스템 분석",
        context=["신규 기능 개발", "TestCase 제작 요청"],
        document="캐릭터 레벨업 시 경험치, 스탯 증가, 스킬 습득 등의 시스템을 분석합니다.",
        output="기획서",
        rule=["상세 분석 필수", "단계별 접근", "데이터 기반 결론"]
    )


@pytest.fixture
def sample_template(sample_prompt_component):
    """샘플 프롬프트 템플릿"""
    version = PromptVersion(
        version=1,
        created_at=datetime.now(),
        components=sample_prompt_component,
        description="캐릭터 시스템 분석 초기 버전"
    )

    return PromptTemplate(
        name="캐릭터 시스템 분석",
        category=PromptCategory.PLANNING,
        versions=[version],
        tags=["캐릭터", "시스템", "분석"]
    )


@pytest.fixture
def export_dir(temp_dir):
    """내보내기 파일 저장 디렉토리"""
    export_path = temp_dir / "exports"
    export_path.mkdir(parents=True, exist_ok=True)
    return export_path


# ==================== 기본 기능 테스트 ====================

class TestMarkdownExport:
    """Markdown 내보내기 테스트"""

    def test_export_to_markdown_success(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-01: Markdown 내보내기 성공"""
        # Given: 유효한 템플릿과 파일명
        filename = "test_prompt"

        # When: Markdown으로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_markdown(
            current_version.components,
            filename,
            str(export_dir)
        )

        # Then: 파일이 생성되고 내용이 올바름
        assert output_path is not None
        assert Path(output_path).exists()
        assert output_path.endswith('.md')

        # 파일 내용 검증
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "캐릭터 레벨업 시스템 분석" in content
            assert "게임 기획자" in content
            assert "QA 엔지니어" in content

    def test_export_markdown_with_korean_text(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-02: 한글 텍스트 Markdown 내보내기"""
        # Given: 한글이 포함된 템플릿 (파일명은 영숫자만 허용)
        filename = "korean_test"

        # When: Markdown으로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_markdown(
            current_version.components,
            filename,
            str(export_dir)
        )

        # Then: 파일 내 한글이 정상적으로 저장됨
        assert output_path is not None
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "캐릭터 레벨업 시스템 분석" in content


class TestJSONExport:
    """JSON 내보내기 테스트"""

    def test_export_to_json_success(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-03: JSON 내보내기 성공"""
        # Given: 유효한 템플릿과 파일명
        filename = "test_prompt"

        # When: JSON으로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_json(
            current_version.components,
            filename,
            str(export_dir),
            metadata={
                "template_name": sample_template.name,
                "created_at": current_version.created_at.isoformat(),
                "exported_at": datetime.now().isoformat()
            }
        )

        # Then: 파일이 생성되고 JSON 구조가 올바름
        assert output_path is not None
        assert Path(output_path).exists()
        assert output_path.endswith('.json')

        # JSON 내용 검증
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data['version'] == '1.0'
            assert 'metadata' in data
            assert 'content' in data
            assert data['content']['goal'] == "캐릭터 레벨업 시스템 분석"

    def test_export_json_utf8_encoding(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-04: JSON UTF-8 인코딩 검증"""
        # Given: 한글이 포함된 템플릿
        filename = "encoding_test"

        # When: JSON으로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_json(
            current_version.components,
            filename,
            str(export_dir)
        )

        # Then: UTF-8로 인코딩되고 한글이 정상 표시됨
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "캐릭터" in data['content']['goal']
            assert "게임 기획자" in data['content']['role']


@pytest.mark.skipif(not REPORTLAB_AVAILABLE, reason="reportlab not installed")
class TestPDFExport:
    """PDF 내보내기 테스트 (reportlab 설치 시에만 실행)"""

    def test_export_to_pdf_success(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-05: PDF 내보내기 성공"""
        # Given: 유효한 템플릿과 파일명
        filename = "test_prompt"

        # When: PDF로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_pdf(
            current_version.components,
            filename,
            str(export_dir)
        )

        # Then: 파일이 생성됨
        assert output_path is not None
        assert Path(output_path).exists()
        assert output_path.endswith('.pdf')

    def test_export_pdf_with_korean_text(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-06: 한글 포함 PDF 내보내기"""
        # Given: 한글이 포함된 템플릿
        filename = "korean_pdf_test"

        # When: PDF로 내보내기
        current_version = sample_template.get_current_version()
        output_path = export_service.export_to_pdf(
            current_version.components,
            filename,
            str(export_dir)
        )

        # Then: PDF 파일이 생성됨 (한글 렌더링은 파일 존재로 검증)
        assert output_path is not None
        assert Path(output_path).exists()


class TestReportlabNotInstalled:
    """reportlab 미설치 시 테스트"""

    def test_pdf_export_without_reportlab(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-07: reportlab 미설치 시 ImportError 발생"""
        if REPORTLAB_AVAILABLE:
            pytest.skip("reportlab is installed, skipping this test")

        # Given: reportlab이 설치되지 않은 환경
        filename = "test_prompt"

        # When/Then: PDF 내보내기 시도 시 ImportError 발생
        current_version = sample_template.get_current_version()
        with pytest.raises(ImportError, match="reportlab이 설치되지 않았습니다"):
            export_service.export_to_pdf(
                current_version.components,
                filename,
                str(export_dir)
            )


# ==================== 보안 테스트 ====================

class TestFilenameSanitization:
    """파일명 Sanitization 테스트"""

    def test_filename_special_characters_removed(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-08: 특수문자 제거"""
        # Given: 특수문자가 포함된 파일명
        dangerous_filenames = [
            "test/file",
            "test\\file",
            "test:file",
            "test*file",
            'test"file',
            "test<file",
            "test>file",
            "test|file"
        ]

        # When/Then: 모든 특수문자가 제거되거나 ValueError 발생
        current_version = sample_template.get_current_version()
        for dangerous_name in dangerous_filenames:
            with pytest.raises(ValueError, match="Invalid filename"):
                export_service.export_to_markdown(
                    current_version.components,
                    dangerous_name,
                    str(export_dir)
                )

    def test_path_traversal_prevention(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-09: Path Traversal 공격 방지"""
        # Given: Path traversal 시도가 포함된 파일명
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "./../../secret",
            "test/../../../etc/passwd"
        ]

        # When/Then: Path traversal이 차단됨
        current_version = sample_template.get_current_version()
        for malicious_name in malicious_filenames:
            with pytest.raises(ValueError, match="Invalid filename"):
                export_service.export_to_markdown(
                    current_version.components,
                    malicious_name,
                    str(export_dir)
                )

    def test_filename_length_limit(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-10: 파일명 길이 제한"""
        # Given: 100자를 초과하는 파일명
        long_filename = "a" * 101

        # When/Then: ValueError 발생
        current_version = sample_template.get_current_version()
        with pytest.raises(ValueError, match="Filename too long"):
            export_service.export_to_markdown(
                current_version.components,
                long_filename,
                str(export_dir)
            )


class TestFileSizeLimit:
    """파일 크기 제한 테스트"""

    def test_file_size_limit_enforcement(self, export_service, export_dir):
        """TEST-EXPORT-001-11: 파일 크기 제한 강제"""
        # Given: 10MB를 초과하는 큰 컴포넌트
        # PromptComponent의 document는 10000자로 제한되므로,
        # goal을 최대 크기로 채우고 반복적으로 Markdown을 생성
        large_goal = "A" * 500  # MAX_GOAL_LENGTH
        large_document = "B" * 9999  # MAX_DOCUMENT_LENGTH 이내

        large_component = PromptComponent(
            goal=large_goal,
            document=large_document,
            role=["role" + str(i) for i in range(10)],  # MAX_LIST_ITEMS
            context=["context" + str(i) for i in range(10)],
            rule=["rule" + str(i) for i in range(10)]
        )

        # Markdown 컨텐츠를 수동으로 확대 (파일 크기 검증 테스트)
        from ai_prompt_maker.export_service import ExportError

        # 11MB 이상의 컨텐츠 생성
        huge_content = "X" * (11 * 1024 * 1024)

        # _validate_file_size를 직접 호출하여 검증
        with pytest.raises(ExportError, match="파일 크기가 제한을 초과"):
            export_service._validate_file_size(huge_content)


# ==================== 엣지 케이스 테스트 ====================

class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_export_with_empty_content(self, export_service, export_dir):
        """TEST-EXPORT-001-12: 빈 컨텐츠 내보내기"""
        # Given: 최소한의 컨텐츠만 있는 컴포넌트
        minimal_component = PromptComponent(goal="Minimal test")

        # When: Markdown으로 내보내기
        output_path = export_service.export_to_markdown(
            minimal_component,
            "minimal",
            str(export_dir)
        )

        # Then: 파일이 생성되고 goal이 포함됨
        assert output_path is not None
        assert Path(output_path).exists()

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Minimal test" in content

    def test_export_format_validation(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-13: 잘못된 형식 검증"""
        # Given: 지원되지 않는 형식
        from ai_prompt_maker.export_service import ExportService

        # When/Then: 존재하지 않는 메서드 호출 시 AttributeError
        with pytest.raises(AttributeError):
            # export_to_xml 같은 메서드는 존재하지 않음
            current_version = sample_template.get_current_version()
            export_service.export_to_xml(  # type: ignore
                current_version.components,
                "test",
                str(export_dir)
            )

    def test_filename_with_whitespace(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-14: 공백이 포함된 파일명"""
        # Given: 공백이 포함된 파일명
        filename = "test file with spaces"

        # When/Then: 공백이 허용되지 않음
        current_version = sample_template.get_current_version()
        with pytest.raises(ValueError, match="Invalid filename"):
            export_service.export_to_markdown(
                current_version.components,
                filename,
                str(export_dir)
            )


# ==================== 추가 커버리지 테스트 ====================

class TestAdditionalCoverage:
    """추가 커버리지를 위한 테스트"""

    def test_sanitize_filename_empty(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-16: 빈 파일명 검증"""
        # Given: 빈 파일명
        current_version = sample_template.get_current_version()

        # When/Then: ValueError 발생
        with pytest.raises(ValueError, match="Filename cannot be empty"):
            export_service.export_to_markdown(
                current_version.components,
                "   ",  # 공백만
                str(export_dir)
            )

    def test_sanitize_filename_none(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-17: None 파일명 검증"""
        # Given: None 파일명
        current_version = sample_template.get_current_version()

        # When/Then: ValueError 발생
        with pytest.raises(ValueError, match="Invalid filename type"):
            export_service.export_to_markdown(
                current_version.components,
                None,
                str(export_dir)
            )

    def test_markdown_all_sections(self, export_service, export_dir):
        """TEST-EXPORT-001-18: 모든 섹션이 있는 Markdown"""
        # Given: 모든 필드가 채워진 컴포넌트
        full_component = PromptComponent(
            role=["Role1", "Role2"],
            goal="Full Goal",
            context=["Context1", "Context2"],
            document="Full Document",
            output="Full Output",
            rule=["Rule1", "Rule2"]
        )

        # When: Markdown으로 내보내기
        output_path = export_service.export_to_markdown(
            full_component,
            "full_test",
            str(export_dir)
        )

        # Then: 모든 섹션이 포함됨
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "# Full Goal" in content
            assert "## Role" in content
            assert "Role1" in content
            assert "## Context" in content
            assert "Context1" in content
            assert "## Document" in content
            assert "Full Document" in content
            assert "## Output" in content
            assert "Full Output" in content
            assert "## Rules" in content
            assert "Rule1" in content

    def test_json_without_metadata(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-19: metadata 없이 JSON 내보내기"""
        # Given: metadata가 없는 경우
        filename = "no_metadata_test"
        current_version = sample_template.get_current_version()

        # When: JSON으로 내보내기 (metadata 미제공)
        output_path = export_service.export_to_json(
            current_version.components,
            filename,
            str(export_dir)
            # metadata 파라미터 생략
        )

        # Then: 기본 exported_at만 있는 metadata 생성
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "exported_at" in data["metadata"]


# ==================== 성능 테스트 ====================

class TestPerformance:
    """성능 테스트"""

    def test_export_performance_under_3_seconds(self, export_service, sample_template, export_dir):
        """TEST-EXPORT-001-15: 3초 이내 내보내기 완료"""
        import time

        # Given: 일반적인 크기의 프롬프트
        filename = "performance_test"
        current_version = sample_template.get_current_version()

        # When: Markdown 내보내기 시간 측정
        start_time = time.time()
        output_path = export_service.export_to_markdown(
            current_version.components,
            filename,
            str(export_dir)
        )
        elapsed_time = time.time() - start_time

        # Then: 3초 이내 완료
        assert elapsed_time < 3.0, f"Export took {elapsed_time:.2f}s (> 3s)"
        assert Path(output_path).exists()
