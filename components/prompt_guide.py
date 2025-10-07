"""
Prompt Guide Component

프롬프트 엔지니어링 가이드 리소스를 표시하는 컴포넌트
"""
import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Any


def load_prompt_guides() -> Dict[str, Any]:
    """프롬프트 가이드 데이터 로드"""
    guide_file = Path("data/prompt_guides.json")

    try:
        with open(guide_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"가이드 데이터 로드 실패: {e}")
        return {}


def get_difficulty_badge(difficulty: str, difficulty_kr: str) -> str:
    """난이도 배지 생성"""
    badge_map = {
        "beginner": "🟢",
        "beginner_to_intermediate": "🟢🟡",
        "intermediate": "🟡",
        "intermediate_to_advanced": "🟡🔴",
        "beginner_to_advanced": "🟢🟡🔴",
        "advanced": "🔴",
        "all_levels": "🟢🟡🔴"
    }

    badge = badge_map.get(difficulty, "⚪")
    return f"{badge} {difficulty_kr}"


def get_type_icon(resource_type: str) -> str:
    """리소스 타입 아이콘 반환"""
    icon_map = {
        "Guide": "📚",
        "Cookbook": "💻",
        "API Docs": "📖",
        "Examples": "📝",
        "Community Guide": "👥",
        "Educational Platform": "🎓"
    }

    return icon_map.get(resource_type, "📄")


def render_resource_card(resource: Dict[str, Any], provider_color: str = "#666"):
    """리소스 카드 렌더링"""

    # 카드 스타일
    card_style = f"""
    <div style="
        padding: 1.5rem;
        border-left: 4px solid {provider_color};
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    ">
        <div style="margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem; font-weight: 600;">
                {get_type_icon(resource['type'])} {resource['title_kr']}
            </span>
        </div>
        <div style="margin-bottom: 0.5rem; font-size: 0.9rem; color: #888;">
            {get_difficulty_badge(resource['difficulty'], resource['difficulty_kr'])} |
            {get_type_icon(resource['type'])} {resource['type_kr']}
        </div>
        <div style="margin-bottom: 1rem; line-height: 1.6;">
            {resource['description_kr']}
        </div>
        <div style="margin-bottom: 1rem;">
            <strong>주요 주제:</strong> {', '.join(resource['key_topics_kr'])}
        </div>
    </div>
    """

    st.markdown(card_style, unsafe_allow_html=True)

    # 버튼을 card 밖으로
    if st.button(
        f"📖 가이드 보기",
        key=f"btn_{resource['id']}",
        use_container_width=True,
        type="primary"
    ):
        st.markdown(f"[🔗 {resource['title']} 열기]({resource['url']})")
        st.info(f"💡 링크를 클릭하여 새 탭에서 열기: {resource['url']}")


def render_quick_start_section(guides_data: Dict[str, Any]):
    """빠른 시작 섹션 렌더링"""
    st.markdown("### 🚀 빠른 시작")
    st.markdown("프롬프트 엔지니어링을 처음 시작하시나요? 여기서 시작하세요!")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 0.5rem;">
                <div style="font-size: 2rem;">🟢</div>
                <div style="font-weight: 600; margin: 0.5rem 0;">초보자 가이드</div>
                <div style="font-size: 0.9rem; color: #888;">프롬프트 기초부터 시작</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("초보자 가이드 보기", key="quick_beginner", use_container_width=True):
                st.session_state.guide_filter_difficulty = ["beginner"]
                st.rerun()

    with col2:
        with st.container():
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem;">
                <div style="font-size: 2rem;">💻</div>
                <div style="font-weight: 600; margin: 0.5rem 0;">코드 예제</div>
                <div style="font-size: 0.9rem; color: #888;">실전 예제로 학습</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("예제 보기", key="quick_examples", use_container_width=True):
                st.session_state.guide_filter_type = ["Cookbook", "Examples"]
                st.rerun()

    with col3:
        with st.container():
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 0.5rem;">
                <div style="font-size: 2rem;">🇰🇷</div>
                <div style="font-weight: 600; margin: 0.5rem 0;">한국어 자료</div>
                <div style="font-size: 0.9rem; color: #888;">한국어로 학습</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("한국어 자료", key="quick_korean", use_container_width=True):
                st.markdown("[Prompt Engineering Guide (한국어)](https://www.promptingguide.ai/kr)")


def render_provider_section(
    provider_id: str,
    provider_data: Dict[str, Any],
    guides_data: Dict[str, Any],
    expanded: bool = False
):
    """제공업체별 리소스 섹션 렌더링"""

    provider_icon = provider_data.get('icon', '📚')
    provider_name = provider_data.get('name', provider_id)
    provider_color = provider_data.get('color', '#666666')
    resources = provider_data.get('resources', [])

    # 필터 적용
    difficulty_filter = st.session_state.get('guide_filter_difficulty', [])
    type_filter = st.session_state.get('guide_filter_type', [])

    # 필터링
    filtered_resources = resources
    if difficulty_filter:
        filtered_resources = [
            r for r in filtered_resources
            if any(d in r['difficulty'] for d in difficulty_filter)
        ]
    if type_filter:
        filtered_resources = [
            r for r in filtered_resources
            if r['type'] in type_filter
        ]

    # 섹션 렌더링
    with st.expander(f"{provider_icon} {provider_name} ({len(filtered_resources)}개)", expanded=expanded):
        if not filtered_resources:
            st.info("선택한 필터에 해당하는 리소스가 없습니다.")
            return

        for resource in filtered_resources:
            render_resource_card(resource, provider_color)


def render_topic_section(guides_data: Dict[str, Any]):
    """주제별 가이드 섹션"""
    st.markdown("---")
    st.markdown("### 🎯 주제별 가이드")
    st.markdown("특정 주제에 대한 리소스를 빠르게 찾아보세요.")

    topics = guides_data.get('topics', {})

    # 2열 레이아웃
    cols = st.columns(2)

    for idx, (topic_id, topic_data) in enumerate(topics.items()):
        col = cols[idx % 2]

        with col:
            topic_icon = topic_data.get('icon', '📌')
            topic_name_kr = topic_data.get('name_kr', topic_data.get('name', topic_id))
            related_ids = topic_data.get('related_resources', [])

            with st.expander(f"{topic_icon} {topic_name_kr}", expanded=False):
                st.markdown(f"**관련 리소스 ({len(related_ids)}개)**")

                # 관련 리소스 찾기
                for provider_id, provider_data in guides_data['providers'].items():
                    for resource in provider_data['resources']:
                        if resource['id'] in related_ids:
                            provider_icon = provider_data.get('icon', '📚')
                            st.markdown(
                                f"{provider_icon} [{resource['title_kr']}]({resource['url']}) "
                                f"({get_difficulty_badge(resource['difficulty'], resource['difficulty_kr'])})"
                            )


def render_additional_resources(guides_data: Dict[str, Any]):
    """추가 학습 자료 섹션"""
    st.markdown("---")
    st.markdown("### 📖 추가 학습 자료")

    additional = guides_data.get('additional_resources', [])

    for resource in additional:
        with st.container():
            st.markdown(f"#### {get_type_icon(resource['type'])} {resource['title_kr']}")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(resource['description_kr'])
                st.markdown(f"**주요 주제:** {', '.join(resource['key_topics_kr'])}")

                if 'note_kr' in resource:
                    st.info(f"💡 {resource['note_kr']}")

            with col2:
                st.markdown(f"**난이도:** {resource['difficulty_kr']}")
                st.markdown(f"**타입:** {resource['type_kr']}")

                # 한국어 링크가 있으면 우선 표시
                url = resource.get('url_kr', resource['url'])
                if st.button("🔗 바로가기", key=f"additional_{resource['id']}", use_container_width=True):
                    st.markdown(f"[새 탭에서 열기]({url})")

            st.divider()


def render_prompt_guide():
    """프롬프트 가이드 메인 렌더링"""

    # 가이드 데이터 로드
    guides_data = load_prompt_guides()

    if not guides_data:
        st.error("가이드 데이터를 로드할 수 없습니다.")
        return

    # 헤더
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>
            📚 프롬프트 엔지니어링 가이드
        </h1>
        <p style='font-size: 1.1rem; color: #666;'>
            AI 모델을 효과적으로 활용하기 위한 공식 가이드 모음
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    각 AI 제공업체의 **공식 문서**와 **실무 예제**를 학습하여 더 나은 프롬프트를 작성해보세요.
    모든 리소스는 최신 정보를 제공하며, 초급부터 고급까지 다양한 수준을 다룹니다.
    """)

    # 빠른 시작 섹션
    render_quick_start_section(guides_data)

    st.markdown("---")

    # 필터 섹션
    st.markdown("### 🔍 리소스 필터")

    col1, col2, col3 = st.columns(3)

    with col1:
        difficulty_options = {
            "beginner": "🟢 초급",
            "intermediate": "🟡 중급",
            "advanced": "🔴 고급"
        }

        selected_difficulties = st.multiselect(
            "난이도",
            options=list(difficulty_options.keys()),
            format_func=lambda x: difficulty_options[x],
            key="guide_filter_difficulty_widget",
            help="보고 싶은 난이도를 선택하세요"
        )

        if selected_difficulties != st.session_state.get('guide_filter_difficulty', []):
            st.session_state.guide_filter_difficulty = selected_difficulties

    with col2:
        type_options = {
            "Guide": "📚 가이드",
            "Cookbook": "💻 쿡북",
            "Examples": "📝 예제",
            "API Docs": "📖 API 문서"
        }

        selected_types = st.multiselect(
            "리소스 타입",
            options=list(type_options.keys()),
            format_func=lambda x: type_options[x],
            key="guide_filter_type_widget",
            help="보고 싶은 리소스 타입을 선택하세요"
        )

        if selected_types != st.session_state.get('guide_filter_type', []):
            st.session_state.guide_filter_type = selected_types

    with col3:
        provider_options = {
            "anthropic": "🟣 Anthropic",
            "google": "🔵 Google",
            "openai": "🟢 OpenAI"
        }

        selected_providers = st.multiselect(
            "제공업체",
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options[x],
            default=list(provider_options.keys()),
            key="guide_filter_provider_widget",
            help="보고 싶은 제공업체를 선택하세요"
        )

    # 필터 초기화 버튼
    if st.button("🔄 필터 초기화", key="reset_filters"):
        st.session_state.guide_filter_difficulty = []
        st.session_state.guide_filter_type = []
        st.rerun()

    st.markdown("---")

    # 공식 문서 섹션
    st.markdown("### 📚 공식 문서")

    providers = guides_data.get('providers', {})

    # 선택된 제공업체만 표시
    for idx, (provider_id, provider_data) in enumerate(providers.items()):
        if provider_id in selected_providers:
            # 첫 번째는 expanded=True
            render_provider_section(
                provider_id,
                provider_data,
                guides_data,
                expanded=(idx == 0 and not selected_difficulties and not selected_types)
            )

    # 주제별 가이드
    if not selected_difficulties and not selected_types:
        render_topic_section(guides_data)

    # 추가 학습 자료
    render_additional_resources(guides_data)

    # 푸터 정보
    st.markdown("---")
    st.info("""
    💡 **팁:**
    - 초보자는 먼저 "기본 프롬프팅" 가이드부터 시작하세요
    - 실전 예제가 필요하면 각 제공업체의 "Cookbook"을 확인하세요
    - 한국어 자료는 "추가 학습 자료" 섹션의 DAIR.AI 가이드를 참고하세요
    """)

    st.caption(f"📅 마지막 업데이트: {guides_data.get('last_updated', 'N/A')} | 버전: {guides_data.get('version', '1.0.0')}")
