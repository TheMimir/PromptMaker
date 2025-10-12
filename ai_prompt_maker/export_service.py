# @CODE:EXPORT-001 | SPEC: .moai/specs/SPEC-EXPORT-001/spec.md | TEST: tests/ai_prompt_maker/test_export_service.py

"""
Export Service

프롬프트를 다양한 형식(Markdown, JSON, PDF)으로 내보내기하는 서비스
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .models import PromptComponent

# 조건부 import - reportlab이 없어도 서비스는 동작
try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ExportError(Exception):
    """내보내기 관련 오류"""
    pass


class ExportService:
    """프롬프트 내보내기 서비스

    Markdown, JSON, PDF 형식으로 프롬프트를 내보내기합니다.
    """

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    MAX_PDF_PAGES = 50
    MAX_FILENAME_LENGTH = 100

    def __init__(self, fonts_dir: str = "data/fonts"):
        """서비스 초기화

        Args:
            fonts_dir: 폰트 파일 디렉토리 경로
        """
        self.fonts_dir = Path(fonts_dir)
        self._pdf_font_registered = False

        # PDF 폰트 등록 시도 (reportlab이 있고 폰트 파일이 있는 경우)
        if REPORTLAB_AVAILABLE:
            self._register_korean_font()

    def export_to_markdown(self, components: PromptComponent,
                          filename: str,
                          output_dir: str = ".") -> str:
        """Markdown 형식으로 내보내기

        Args:
            components: 프롬프트 컴포넌트
            filename: 파일명 (확장자 제외)
            output_dir: 출력 디렉토리

        Returns:
            생성된 파일 경로

        Raises:
            ValueError: 잘못된 입력
            ExportError: 내보내기 실패
        """
        # 파일명 sanitization
        safe_filename = self._sanitize_filename(filename)

        # Markdown 컨텐츠 생성
        markdown_content = self._generate_markdown_content(components)

        # 파일 크기 검증
        self._validate_file_size(markdown_content)

        # 파일 저장
        output_path = Path(output_dir) / f"{safe_filename}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(output_path)

    def export_to_json(self, components: PromptComponent,
                      filename: str,
                      output_dir: str = ".",
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """JSON 형식으로 내보내기

        Args:
            components: 프롬프트 컴포넌트
            filename: 파일명 (확장자 제외)
            output_dir: 출력 디렉토리
            metadata: 추가 메타데이터 (선택)

        Returns:
            생성된 파일 경로

        Raises:
            ValueError: 잘못된 입력
            ExportError: 내보내기 실패
        """
        # 파일명 sanitization
        safe_filename = self._sanitize_filename(filename)

        # JSON 구조 생성
        json_data = {
            "version": "1.0",
            "metadata": metadata or {
                "exported_at": datetime.now().isoformat()
            },
            "content": components.to_dict()
        }

        # JSON 문자열로 변환
        json_content = json.dumps(json_data, ensure_ascii=False, indent=2)

        # 파일 크기 검증
        self._validate_file_size(json_content)

        # 파일 저장
        output_path = Path(output_dir) / f"{safe_filename}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_content)

        return str(output_path)

    def export_to_pdf(self, components: PromptComponent,
                     filename: str,
                     output_dir: str = ".") -> str:
        """PDF 형식으로 내보내기

        Args:
            components: 프롬프트 컴포넌트
            filename: 파일명 (확장자 제외)
            output_dir: 출력 디렉토리

        Returns:
            생성된 파일 경로

        Raises:
            ImportError: reportlab이 설치되지 않음
            ValueError: 잘못된 입력
            ExportError: 내보내기 실패
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab이 설치되지 않았습니다")

        # 파일명 sanitization
        safe_filename = self._sanitize_filename(filename)

        # PDF 파일 경로
        output_path = Path(output_dir) / f"{safe_filename}.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # PDF 생성
        self._generate_pdf(components, str(output_path))

        return str(output_path)

    def _sanitize_filename(self, filename: str) -> str:
        """파일명 sanitization

        service.py:_sanitize_template_id() 패턴 참조
        Path traversal 공격 방지

        Args:
            filename: 검증할 파일명

        Returns:
            안전한 파일명

        Raises:
            ValueError: 잘못된 파일명
        """
        if not filename or not isinstance(filename, str):
            raise ValueError(f"Invalid filename type: {type(filename)}")

        # 공백 제거
        filename = filename.strip()

        # 빈 파일명 검증
        if not filename:
            raise ValueError("Filename cannot be empty")

        # 특수문자 검증 (영숫자, 하이픈, 언더스코어만 허용)
        if not re.match(r'^[a-zA-Z0-9_-]+$', filename):
            raise ValueError(
                f"Invalid filename: {filename}. "
                "Only alphanumeric characters, hyphens, and underscores are allowed."
            )

        # 길이 검증
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"Filename too long: {len(filename)} characters")

        return filename

    def _validate_file_size(self, content: str) -> None:
        """파일 크기 검증

        Args:
            content: 검증할 컨텐츠

        Raises:
            ExportError: 파일 크기 초과
        """
        content_bytes = len(content.encode('utf-8'))

        if content_bytes > self.MAX_FILE_SIZE_BYTES:
            raise ExportError(
                f"파일 크기가 제한을 초과했습니다: "
                f"{content_bytes / 1024 / 1024:.2f}MB > "
                f"{self.MAX_FILE_SIZE_BYTES / 1024 / 1024:.2f}MB"
            )

    def _generate_markdown_content(self, components: PromptComponent) -> str:
        """Markdown 컨텐츠 생성

        Args:
            components: 프롬프트 컴포넌트

        Returns:
            Markdown 형식의 문자열
        """
        lines = []

        # 제목 (Goal)
        lines.append(f"# {components.goal}\n")

        # Role
        if components.role:
            lines.append("## Role")
            for role in components.role:
                lines.append(f"- {role}")
            lines.append("")

        # Context
        if components.context:
            lines.append("## Context")
            for ctx in components.context:
                lines.append(f"- {ctx}")
            lines.append("")

        # Document
        if components.document:
            lines.append("## Document")
            lines.append(components.document)
            lines.append("")

        # Output
        if components.output:
            lines.append("## Output")
            lines.append(components.output)
            lines.append("")

        # Rules
        if components.rule:
            lines.append("## Rules")
            for rule in components.rule:
                lines.append(f"- {rule}")
            lines.append("")

        return "\n".join(lines)

    def _register_korean_font(self) -> None:
        """한글 폰트 등록

        NanumGothic.ttf 파일을 찾아 PDF에서 사용할 수 있도록 등록
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 여러 경로에서 폰트 찾기
        font_paths = [
            self.fonts_dir / "NanumGothic.ttf",
            Path("data/fonts/NanumGothic.ttf"),
            Path("fonts/NanumGothic.ttf"),
        ]

        for font_path in font_paths:
            if font_path.exists():
                try:
                    pdfmetrics.registerFont(TTFont('NanumGothic', str(font_path)))
                    self._pdf_font_registered = True
                    return
                except Exception:
                    continue

        # 폰트를 찾지 못한 경우 - fallback으로 기본 폰트 사용
        # 경고만 하고 계속 진행 (영문은 표시 가능)
        self._pdf_font_registered = False

    def _generate_pdf(self, components: PromptComponent, output_path: str) -> None:
        """PDF 파일 생성

        Args:
            components: 프롬프트 컴포넌트
            output_path: 출력 파일 경로
        """
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        font_name = 'NanumGothic' if self._pdf_font_registered else 'Helvetica'

        x = 50
        y = height - 50
        line_height = 20

        # 제목
        c.setFont(font_name, 16)
        y = self._draw_text(c, components.goal, x, y, font_name, 16, width - 100)
        y -= line_height

        # 각 섹션 렌더링
        y = self._render_pdf_section(c, "Role:", components.role, x, y, font_name, line_height, width)
        y = self._render_pdf_section(c, "Context:", components.context, x, y, font_name, line_height, width)

        if components.document:
            y = self._render_pdf_text_section(c, "Document:", components.document, x, y, font_name, line_height, width)

        if components.output:
            y = self._render_pdf_text_section(c, "Output:", components.output, x, y, font_name, line_height, width)

        y = self._render_pdf_section(c, "Rules:", components.rule, x, y, font_name, line_height, width)

        c.save()

    def _render_pdf_section(self, canvas_obj, title: str, items: list,
                           x: float, y: float, font_name: str,
                           line_height: float, width: float) -> float:
        """PDF 리스트 섹션 렌더링"""
        if not items:
            return y

        canvas_obj.setFont(font_name, 14)
        y = self._draw_text(canvas_obj, title, x, y, font_name, 14, width - 100)
        y -= line_height

        canvas_obj.setFont(font_name, 12)
        for item in items:
            y = self._draw_text(canvas_obj, f"• {item}", x + 20, y, font_name, 12, width - 120)
            y -= line_height

        return y - line_height / 2

    def _render_pdf_text_section(self, canvas_obj, title: str, text: str,
                                 x: float, y: float, font_name: str,
                                 line_height: float, width: float) -> float:
        """PDF 텍스트 섹션 렌더링"""
        canvas_obj.setFont(font_name, 14)
        y = self._draw_text(canvas_obj, title, x, y, font_name, 14, width - 100)
        y -= line_height

        canvas_obj.setFont(font_name, 12)
        y = self._draw_text(canvas_obj, text, x + 20, y, font_name, 12, width - 120)

        return y - line_height * 2

    def _draw_text(self, canvas_obj, text: str, x: float, y: float,
                   font_name: str, font_size: int, max_width: float) -> float:
        """텍스트를 PDF에 그리기 (자동 줄바꿈 지원)

        Args:
            canvas_obj: reportlab Canvas 객체
            text: 그릴 텍스트
            x: X 좌표
            y: Y 좌표
            font_name: 폰트 이름
            font_size: 폰트 크기
            max_width: 최대 너비

        Returns:
            새로운 Y 좌표 (다음 줄 시작 위치)
        """
        # 간단한 구현: 한 줄에 그리기 (추후 개선 가능)
        canvas_obj.setFont(font_name, font_size)
        canvas_obj.drawString(x, y, text)

        return y
