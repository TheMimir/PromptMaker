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

from components.template_manager import render_template_manager
from components.prompt_editor import render_prompt_editor
from ai_prompt_maker.service import PromptMakerService
from ai_prompt_maker.models import PromptTemplate, PromptComponent, PromptCategory, PromptValidationError


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
    """, unsafe_allow_html=True)


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
    """, unsafe_allow_html=True)


def render_prompt_generator(domain: str = "game_dev"):
    """프롬프트 생성기 UI 렌더링

    Args:
        domain: 도메인 ID (game_dev, uiux 등)
    """
    service = PromptMakerService()

    # 세션 상태 초기화
    session_key = f"{domain}_prompt_maker"
    if f"{session_key}_last_generated_prompt" not in st.session_state:
        st.session_state[f"{session_key}_last_generated_prompt"] = None
    if f"{session_key}_show_save_dialog" not in st.session_state:
        st.session_state[f"{session_key}_show_save_dialog"] = False

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

    # ========================================
    # PART 1: 출력 형식 카테고리 선택 (Form 외부 - 즉시 반응)
    # ========================================
    st.markdown("#### 📊 출력 형식 선택")

    category_key = f"{domain}_output_category"

    try:
        formats_data = service.load_output_formats()
        categories = formats_data.get('categories', {})
        formats = formats_data.get('formats', {})

        # 카테고리 선택 - FORM 외부에서 즉시 반응
        category_options = {"": "📂 출력 형식을 선택하세요"}
        category_options.update({
            cat_id: cat_data['name']
            for cat_id, cat_data in categories.items()
        })

        selected_category = st.selectbox(
            "출력 형식 카테고리 *",
            options=list(category_options.keys()),
            format_func=lambda x: category_options[x],
            help="출력 형식 카테고리를 먼저 선택하세요",
            key=category_key  # session_state에 자동 저장
        )

        # 선택된 카테고리에 해당하는 형식만 필터링 (Form 전에 미리 처리)
        category_formats = {}
        if selected_category and selected_category != "":
            category_formats = {
                fmt_id: fmt_data
                for fmt_id, fmt_data in formats.items()
                if fmt_data.get('category') == selected_category
            }

            if category_formats:
                st.success(f"✅ {len(category_formats)}개의 세부 형식을 사용할 수 있습니다")
            else:
                st.warning("⚠️ 이 카테고리에는 사용 가능한 형식이 없습니다")
        else:
            st.info("💡 출력 형식 카테고리를 선택하면 세부 형식을 선택할 수 있습니다")

    except Exception as e:
        st.error(f"출력 형식 로드 실패: {e}")
        selected_category = ""
        category_formats = {}
        formats = {}

    st.divider()

    # ========================================
    # PART 2: 프롬프트 구성 요소 입력 (Form 내부)
    # ========================================
    st.markdown("#### 📝 프롬프트 구성 요소")

    with st.form(f"{domain}_prompt_form"):
        # 역할 입력 (다중 선택)
        role_options = keywords.get('role', [])
        selected_roles = st.multiselect(
            "👤 역할 (Role)",
            options=role_options,
            help="AI가 수행할 역할을 선택하세요 (여러 개 선택 가능)"
        )

        # 목표 입력 (단일 선택)
        goal_options = keywords.get('goal', [])
        selected_goal = st.selectbox(
            "🎯 목표 (Goal) *",
            options=goal_options,
            help="달성하고자 하는 목표를 선택하세요"
        )

        # 컨텍스트 입력 (다중 선택)
        context_options = keywords.get('context', [])
        selected_contexts = st.multiselect(
            "📋 컨텍스트 (Context)",
            options=context_options,
            help="상황 설명 및 배경 정보를 선택하세요 (여러 개 선택 가능)"
        )

        # 문서/데이터 입력 (자유 입력)
        selected_document = st.text_area(
            "📄 문서/데이터 (Document)",
            placeholder="예: [아이템 스탯 테이블]\n이름: 화염검\n공격력: 150\n...",
            help="게임 디자인 문서의 관련 부분을 붙여넣으세요",
            height=150
        )

        # 세부 형식 선택 - Form 내부 (이미 필터링된 category_formats 사용)
        selected_format = None
        format_data = None
        selected_output = "보고서 형식"
        template_instruction = ""

        if category_formats:
            # 카테고리가 선택되고 형식이 있는 경우
            format_options = {
                fmt_id: fmt_data['name']
                for fmt_id, fmt_data in category_formats.items()
            }

            selected_format = st.selectbox(
                "📝 세부 형식 *",
                options=list(format_options.keys()),
                format_func=lambda x: format_options[x],
                help="선택한 카테고리의 세부 형식을 선택하세요",
                key=f"{domain}_output_format"
            )

            # 선택된 포맷 정보 표시
            if selected_format:
                format_data = formats.get(selected_format)
                if format_data:
                    with st.expander("ℹ️ 형식 정보", expanded=False):
                        st.write(f"**설명:** {format_data['description']}")
                        if format_data.get('example_output'):
                            st.markdown("**예시 출력:**")
                            st.code(format_data['example_output'], language="text")

                    selected_output = format_data.get('name', '보고서 형식')
                    template_instruction = format_data.get('template', '')

        elif selected_category and selected_category != "":
            # 카테고리는 선택되었지만 형식이 없는 경우
            st.selectbox(
                "📝 세부 형식",
                options=[""],
                format_func=lambda x: "⚠️ 사용 가능한 형식이 없습니다",
                disabled=True
            )
        else:
            # 카테고리가 선택되지 않은 경우
            st.selectbox(
                "📝 세부 형식",
                options=[""],
                format_func=lambda x: "⬆️ 먼저 출력 형식 카테고리를 선택하세요",
                disabled=True,
                help="출력 형식 카테고리를 먼저 선택하세요"
            )

        # 규칙 입력 (다중 선택)
        rule_options = keywords.get('rule', [])
        selected_rules = st.multiselect(
            "📏 규칙 (Rules)",
            options=rule_options,
            help="AI가 따라야 할 규칙이나 제약사항을 선택하세요 (여러 개 선택 가능)"
        )

        # 생성 버튼
        submitted = st.form_submit_button("✨ 프롬프트 생성", type="primary", use_container_width=True)

    # 프롬프트 생성
    if submitted:
        # 검증: 필수 항목 확인
        if not selected_category or selected_category == "":
            st.error("❌ 출력 형식 카테고리를 선택해주세요")
            st.stop()

        if not selected_format:
            st.error("❌ 세부 형식을 선택해주세요")
            st.stop()

        if not selected_goal:
            st.error("❌ 목표(Goal)는 필수 항목입니다")
            st.stop()

        try:
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
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
