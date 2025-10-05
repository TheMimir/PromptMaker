#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt Maker - Standalone Application
게임 개발을 위한 AI 프롬프트 생성 도구
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import time
import uuid
import os
from pathlib import Path

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    print("Warning: bleach not installed. HTML sanitization disabled.")

from components.template_manager import render_template_manager
from components.prompt_editor import render_prompt_editor
from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import PromptTemplate, PromptComponent, PromptCategory, PromptValidationError


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks

    Args:
        html_content: HTML string to sanitize

    Returns:
        Sanitized HTML string
    """
    if not BLEACH_AVAILABLE:
        # If bleach not available, return as-is with warning logged
        return html_content

    # Allow safe HTML tags and attributes for styling
    allowed_tags = ['div', 'span', 'h1', 'h2', 'h3', 'p', 'br', 'style']
    allowed_attributes = {
        '*': ['style', 'class'],
        'div': ['style', 'class'],
        'span': ['style', 'class'],
        'h1': ['style', 'class'],
        'h2': ['style', 'class'],
        'h3': ['style', 'class'],
        'p': ['style', 'class']
    }

    # Allow common CSS properties
    allowed_styles = [
        'color', 'background', 'background-color', 'background-clip',
        '-webkit-background-clip', '-webkit-text-fill-color',
        'font-size', 'font-weight', 'font-family',
        'margin', 'padding', 'border', 'border-bottom', 'border-radius',
        'box-shadow', 'transition', 'text-align',
        'width', 'height', 'max-width', 'min-height',
        'display', 'flex-direction', 'align-items', 'justify-content', 'gap'
    ]

    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        styles=allowed_styles,
        strip=True
    )


def apply_custom_css():
    """커스텀 CSS 스타일 적용"""
    st.markdown("""
    <style>
        /* 전역 스타일 */
        .main {
            padding: 2rem 3rem;
        }

        h1 {
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem !important;
        }

        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: transparent;
            padding: 0.5rem 0;
        }

        .stTabs [data-baseweb="tab"] {
            height: 3.5rem;
            padding: 0 2rem;
            background-color: rgba(240, 242, 246, 0.6);
            border-radius: 0.75rem;
            font-weight: 500;
            font-size: 1rem;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(240, 242, 246, 1);
            border-color: rgba(255, 75, 75, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
            color: white;
            border-color: #ff4b4b;
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }

        /* 버튼 스타일 */
        .stButton button {
            border-radius: 0.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            border-color: #ff4b4b;
        }

        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
            border: none;
        }

        /* 입력 요소 스타일 */
        .stTextInput input, .stTextArea textarea {
            border-radius: 0.5rem;
            border: 2px solid rgba(0, 0, 0, 0.1);
            transition: border-color 0.2s ease;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #ff4b4b;
            box-shadow: 0 0 0 1px #ff4b4b;
        }
    </style>
    """, unsafe_allow_html=True)  # Safe: Static HTML/CSS only, no user input  # Safe: Static CSS only, no user input


def render_header():
    """헤더 렌더링"""
    st.markdown("""
    <div style='
        padding: 2rem 0 1.5rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid rgba(240, 242, 246, 0.8);
    '>
        <h1 style='
            font-size: 2.5rem;
            margin: 0;
            background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 50%, #ff8b8b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        '>
            🤖 AI Prompt Maker
        </h1>
        <p style='
            font-size: 1.1rem;
            color: #666;
            margin: 0.5rem 0 0 0;
            font-weight: 400;
        '>
            게임 개발을 위한 AI 프롬프트 생성 및 관리 도구
        </p>
    </div>
    """, unsafe_allow_html=True)  # Safe: Static HTML/CSS only, no user input


def render_prompt_generator(domain: str = "game_dev"):
    """프롬프트 생성기 UI 렌더링

    Args:
        domain: 도메인 ID (game_dev, uiux 등)
    """
    service = PromptMakerService()

    # 세션 상태 초기화
    session_key = f"{domain}_prompt_maker"
    session_key_category = f"{domain}_output_category"
    session_key_format = f"{domain}_output_format"
    session_key_formats_data = f"{domain}_output_formats_data"

    if f"{session_key}_last_generated_prompt" not in st.session_state:
        st.session_state[f"{session_key}_last_generated_prompt"] = None
    if f"{session_key}_show_save_dialog" not in st.session_state:
        st.session_state[f"{session_key}_show_save_dialog"] = False
    if session_key_category not in st.session_state:
        st.session_state[session_key_category] = ""
    if session_key_format not in st.session_state:
        st.session_state[session_key_format] = None
    if session_key_formats_data not in st.session_state:
        st.session_state[session_key_formats_data] = None

    st.subheader("🎯 프롬프트 생성")

    # 설정 파일 로드
    try:
        domain_config = service.get_domain_config(domain)
        keywords = domain_config.get('keywords', {})
        goal_expansions = domain_config.get('goal_expansions', {})
        context_expansions = domain_config.get('context_expansions', {})
        rule_expansions = domain_config.get('rule_expansions', {})
    except Exception as e:
        st.error(f"설정 파일 로드 실패: {e}")
        keywords = {}
        goal_expansions = {}
        context_expansions = {}
        rule_expansions = {}

    # 출력 형식 데이터 로드 (session state에 캐싱) - 나중에 사용
    try:
        if st.session_state[session_key_formats_data] is None:
            st.session_state[session_key_formats_data] = service.load_output_formats()

        formats_data = st.session_state[session_key_formats_data]
        categories = formats_data.get('categories', {})
        formats = formats_data.get('formats', {})
    except Exception as e:
        st.error(f"출력 형식 로드 실패: {e}")
        categories = {}
        formats = {}

    # ═══════════════════════════════════════════════════════════
    # 프롬프트 입력 폼 (role, goal, context, document, rules)
    # ═══════════════════════════════════════════════════════════
    with st.form(f"{domain}_prompt_form", border=False):
        # 역할 입력 (다중 선택)
        role_options = keywords.get('role', [])
        selected_roles = st.multiselect(
            "👤 역할 (Role)",
            options=role_options,
            help="AI가 수행할 역할을 선택하세요 (여러 개 선택 가능)",
            key=f"{domain}_role_widget"
        )

        # 목표 입력 (단일 선택)
        goal_options = keywords.get('goal', [])
        selected_goal = st.selectbox(
            "🎯 목표 (Goal) *",
            options=goal_options,
            help="달성하고자 하는 목표를 선택하세요",
            key=f"{domain}_goal_widget"
        )

        # 컨텍스트 입력 (다중 선택)
        context_options = keywords.get('context', [])
        selected_contexts = st.multiselect(
            "📋 컨텍스트 (Context)",
            options=context_options,
            help="상황 설명 및 배경 정보를 선택하세요 (여러 개 선택 가능)",
            key=f"{domain}_context_widget"
        )

        # 문서/데이터 입력 (자유 입력)
        selected_document = st.text_area(
            "📄 문서/데이터 (Document)",
            placeholder="예: [아이템 스탯 테이블]\n이름: 화염검\n공격력: 150\n...",
            help="게임 디자인 문서의 관련 부분을 붙여넣으세요",
            height=150,
            key=f"{domain}_document_widget"
        )

        # 규칙 입력 (다중 선택)
        rule_options = keywords.get('rule', [])
        selected_rules = st.multiselect(
            "📏 규칙 (Rules)",
            options=rule_options,
            help="AI가 따라야 할 규칙이나 제약사항을 선택하세요 (여러 개 선택 가능)",
            key=f"{domain}_rules_widget"
        )

        # 폼 내부 안내 메시지와 submit 버튼
        st.markdown("")  # 간격
        st.info("💡 아래에서 출력 형식을 선택한 후 '프롬프트 생성' 버튼을 클릭하세요")

        # 폼 submit 버튼
        form_submitted = st.form_submit_button("✅ 항목 적용", type="primary", use_container_width=True)

    # ═══════════════════════════════════════════════════════════
    # 출력 형식 설정 섹션 (폼 외부 - 즉시 반응형 동작)
    # ═══════════════════════════════════════════════════════════

    # 시각적 구분선
    st.divider()

    # 출력 형식 섹션 시작
    with st.container():
        st.markdown("### 📊 출력 형식 설정")
        st.markdown("프롬프트 생성 시 사용할 출력 형식을 선택하세요")

        # STEP 1: 카테고리 선택
        category_options = {cat_id: cat_data['name']
                          for cat_id, cat_data in categories.items()}
        category_keys = [""] + list(category_options.keys())

        # 현재 선택된 카테고리의 index 찾기
        current_category_index = 0
        if st.session_state[session_key_category] in category_keys:
            current_category_index = category_keys.index(st.session_state[session_key_category])

        selected_category = st.selectbox(
            "📊 출력 형식 카테고리 선택 *",
            options=category_keys,
            format_func=lambda x: "⬇️ 먼저 카테고리를 선택하세요" if x == "" else category_options[x],
            key=f"{domain}_category_select_widget",
            help="출력 형식의 카테고리를 먼저 선택하세요 (필수)",
            index=current_category_index
        )

        # 카테고리 변경 감지 및 session state 업데이트
        if selected_category != st.session_state[session_key_category]:
            st.session_state[session_key_category] = selected_category
            # 카테고리 변경 시 형식 초기화
            st.session_state[session_key_format] = None
            st.rerun()

        # STEP 2: 세부 형식 선택 (카테고리 선택 시에만 표시)
        if selected_category and selected_category != "":
            # 해당 카테고리의 포맷 필터링
            category_formats = {fmt_id: fmt_data
                               for fmt_id, fmt_data in formats.items()
                               if fmt_data.get('category') == selected_category}

            if category_formats:
                format_options = {fmt_id: fmt_data['name']
                                for fmt_id, fmt_data in category_formats.items()}
                format_keys = list(format_options.keys())

                # 현재 선택된 형식의 index 찾기
                current_format_index = 0
                if st.session_state[session_key_format] in format_keys:
                    current_format_index = format_keys.index(st.session_state[session_key_format])

                selected_format = st.selectbox(
                    "📝 세부 출력 형식 선택 *",
                    options=format_keys,
                    format_func=lambda x: format_options[x],
                    key=f"{domain}_format_select_widget",
                    help="원하는 세부 출력 형식을 선택하세요 (필수)",
                    index=current_format_index
                )

                # 형식 변경 감지 및 session state 업데이트
                if selected_format != st.session_state[session_key_format]:
                    st.session_state[session_key_format] = selected_format
                    st.rerun()

                # STEP 3: 선택한 형식 정보 표시
                if selected_format:
                    format_data = formats[selected_format]
                    with st.expander("ℹ️ 선택한 형식 정보", expanded=False):
                        st.markdown(f"**형식명:** {format_data['name']}")
                        st.markdown(f"**설명:** {format_data['description']}")
                        if format_data.get('example_output'):
                            st.markdown("**예시 출력:**")
                            st.code(format_data['example_output'], language="text")
            else:
                st.warning("⚠️ 해당 카테고리에 사용 가능한 형식이 없습니다.")
        else:
            st.info("💡 위에서 출력 형식 카테고리를 먼저 선택하세요")

    # 시각적 구분선
    st.divider()

    # ═══════════════════════════════════════════════════════════
    # 프롬프트 생성 버튼 (폼 외부)
    # ═══════════════════════════════════════════════════════════
    submitted = st.button(
        "✨ 프롬프트 생성",
        type="primary",
        use_container_width=True,
        key=f"{domain}_generate_button"
    )

    # 프롬프트 생성
    if submitted:
        # Session state에서 폼 입력값 읽기
        selected_roles = st.session_state.get(f"{domain}_role_widget", [])
        selected_goal = st.session_state.get(f"{domain}_goal_widget", "")
        selected_contexts = st.session_state.get(f"{domain}_context_widget", [])
        selected_document = st.session_state.get(f"{domain}_document_widget", "")
        selected_rules = st.session_state.get(f"{domain}_rules_widget", [])

        # 입력 검증: session state에서 출력 형식 확인
        validation_errors = []

        if not st.session_state[session_key_category] or st.session_state[session_key_category] == "":
            validation_errors.append("📊 출력 형식 카테고리를 선택하세요")

        if not st.session_state[session_key_format]:
            validation_errors.append("📝 세부 출력 형식을 선택하세요")

        # 검증 오류 표시
        if validation_errors:
            for error in validation_errors:
                st.error(f"❌ {error}")
            st.info("💡 위의 '출력 형식 설정' 섹션에서 카테고리와 세부 형식을 선택해주세요")
        else:
            try:
                # Session state에서 출력 형식 정보 읽기
                selected_format_id = st.session_state[session_key_format]
                format_data = formats[selected_format_id]

                selected_output = format_data.get('name', '보고서 형식')
                template_instruction = format_data.get('template', '')

                # Goal expansion 적용
                expanded_goal = goal_expansions.get(selected_goal, selected_goal)

                # Context expansion 적용
                expanded_contexts = [
                    context_expansions.get(ctx, ctx) for ctx in selected_contexts
                ]

                # Rule expansion 적용
                expanded_rules = [
                    rule_expansions.get(rule, rule) for rule in selected_rules
                ]

                # Enhanced output with template
                enhanced_output = selected_output
                if template_instruction:
                    if selected_output:
                        enhanced_output = f"{selected_output}\n\n{template_instruction}"
                    else:
                        enhanced_output = template_instruction

                components = PromptComponent(
                    role=selected_roles,
                    goal=expanded_goal,
                    context=expanded_contexts,
                    document=selected_document,
                    output=enhanced_output,
                    rule=expanded_rules
                )

                generated_prompt = service.generate_prompt(components)
                st.session_state[f"{session_key}_last_generated_prompt"] = generated_prompt

                # 프롬프트 표시
                st.code(generated_prompt, language="text")

                # 복사 안내 메시지
                st.caption("💡 위 코드 블록 오른쪽 상단의 복사 아이콘(📋)을 클릭하여 클립보드에 복사할 수 있습니다")

                # 다운로드 버튼
                st.download_button(
                    label="💾 텍스트 파일로 저장",
                    data=generated_prompt,
                    file_name=f"prompt_{int(time.time())}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ 프롬프트 생성 오류: {e}")
                import traceback
                with st.expander("🔍 상세 오류 정보"):
                    st.code(traceback.format_exc())


def main():
    """메인 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="🤖 AI Prompt Maker",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 커스텀 CSS 적용
    apply_custom_css()

    # 헤더
    render_header()

    # 탭 생성 (도메인별 프롬프트 생성 탭 추가)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎮 게임 개발",
        "🎨 UI/UX 디자인",
        "📋 템플릿 관리",
        "✏️ 프롬프트 편집"
    ])

    with tab1:
        render_prompt_generator(domain="game_dev")

    with tab2:
        render_prompt_generator(domain="uiux")

    with tab3:
        render_template_manager()

    with tab4:
        render_prompt_editor()

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem 0;'>
        <p style='margin: 0; font-size: 0.9rem;'>
            AI Prompt Maker v2.3.0 | Made with ❤️ by TheMimir
        </p>
    </div>
    """, unsafe_allow_html=True)  # Safe: Static HTML/CSS only, no user input


if __name__ == "__main__":
    main()
