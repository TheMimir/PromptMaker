"""
Template Manager Component

저장된 프롬프트 템플릿을 관리하는 컴포넌트
"""
import streamlit as st
from typing import Dict, List, Any
from datetime import datetime
import uuid

from utils.data_handler import DataHandler


def render_template_manager():
    """템플릿 관리자 메인 렌더링"""
    st.header("📚 Prompt Template")
    st.write("저장된 프롬프트 템플릿을 관리합니다.")

    try:
        data_handler = DataHandler()
        config = data_handler.load_config()

        # 필터링 및 검색 옵션
        render_filter_options(data_handler, config)

        # 템플릿 목록 조회 및 표시
        render_template_list(data_handler)

    except Exception as e:
        st.error(f"템플릿 관리자 로딩 실패: {e}")


def render_filter_options(data_handler: DataHandler, config: Dict[str, Any]):
    """필터링 및 검색 옵션 렌더링"""

    col1, col2, col3 = st.columns([2, 2, 1])

    # 기본값 설정 (위젯 생성 전에)
    default_category = st.session_state.get('template_category_filter', '전체')
    default_search = st.session_state.get('template_search', '')

    with col1:
        category_filter = st.selectbox(
            "카테고리 필터",
            ["전체"] + config.get('categories', []),
            index=0 if default_category == '전체' else (
                (["전체"] + config.get('categories', [])).index(default_category)
                if default_category in config.get('categories', []) else 0
            ),
            key="template_category_filter"
        )

    with col2:
        search_term = st.text_input(
            "템플릿 이름 검색",
            value=default_search,
            placeholder="검색어를 입력하세요",
            key="template_search"
        )

    with col3:
        if st.button("🔄 새로고침", key="refresh_templates"):
            # 캐시 관련 상태만 초기화
            for key in list(st.session_state.keys()):
                if key.startswith('preview_template') or key.startswith('show_actions'):
                    del st.session_state[key]
            st.rerun()


def render_template_list(data_handler: DataHandler):
    """템플릿 목록 렌더링"""

    # 위젯에서 직접 값 읽기
    category_filter = st.session_state.get('template_category_filter', '전체')
    search_term = st.session_state.get('template_search', '')

    try:
        # 템플릿 목록 조회
        category = None if category_filter == "전체" else category_filter

        if search_term:
            templates = data_handler.search_templates(search_term)
        else:
            templates = data_handler.list_templates(category)

        if not templates:
            if search_term:
                st.info(f"'{search_term}'에 대한 검색 결과가 없습니다.")
            else:
                st.info("저장된 템플릿이 없습니다.")
            return

        # 템플릿 개수 표시
        st.info(f"총 {len(templates)}개의 템플릿이 있습니다.")
        st.divider()

        # 템플릿 카드 렌더링
        for template in templates:
            render_template_card(template, data_handler)

    except Exception as e:
        st.error(f"템플릿 목록 로딩 실패: {e}")


def render_template_card(template: Dict[str, Any], data_handler: DataHandler):
    """개별 템플릿 카드 렌더링"""

    template_id = template['template_id']

    # 카드 컨테이너
    with st.container():
        # 헤더 정보
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.subheader(f"📝 {template['name']}")

            # 메타데이터 정보
            created_date = template.get('created_at', '')[:10] if template.get('created_at') else 'Unknown'
            updated_date = template.get('updated_at', '')[:10] if template.get('updated_at') else 'Unknown'

            st.caption(
                f"카테고리: {template['category']} | "
                f"버전: {template['current_version']} | "
                f"생성일: {created_date}"
            )

            # 태그 표시
            if template.get('tags'):
                tag_str = " ".join([f"`{tag}`" for tag in template['tags']])
                st.markdown(f"**태그:** {tag_str}")

        with col2:
            show_preview = st.button(
                "👁️ 미리보기",
                key=f"preview_btn_{template_id}"
            )
            if show_preview:
                key = f"preview_template_{template_id}"
                st.session_state[key] = not st.session_state.get(key, False)

        with col3:
            if st.button("📋 복사", key=f"copy_btn_{template_id}"):
                current_version_data = get_current_version_data(template)
                if current_version_data:
                    try:
                        import pyperclip
                        pyperclip.copy(current_version_data['prompt'])
                        st.success("클립보드에 복사 완료!", icon="✅")
                    except ImportError:
                        st.session_state.clipboard_content = current_version_data['prompt']
                        st.success("클립보드에 복사 완료! (세션 저장)", icon="✅")
                    except Exception as e:
                        st.session_state.clipboard_content = current_version_data['prompt']
                        st.warning(f"클립보드 복사 실패. 세션에 저장됨: {e}", icon="⚠️")

        with col4:
            show_actions = st.button(
                "⚙️ 관리",
                key=f"actions_btn_{template_id}"
            )
            if show_actions:
                key = f"show_actions_{template_id}"
                st.session_state[key] = not st.session_state.get(key, False)

        # 미리보기 표시
        if st.session_state.get(f"preview_template_{template_id}", False):
            render_template_preview(template)

        # 액션 버튼들 표시
        if st.session_state.get(f"show_actions_{template_id}", False):
            render_template_actions(template, data_handler)

    st.divider()


def render_template_preview(template: Dict[str, Any]):
    """템플릿 미리보기 렌더링"""

    current_version_data = get_current_version_data(template)
    if not current_version_data:
        st.error("현재 버전을 찾을 수 없습니다.")
        return

    # 프롬프트 텍스트 표시
    st.code(current_version_data['prompt'], language="text")

    # 컴포넌트 정보 표시
    components = current_version_data.get('components', {})

    with st.expander("📋 컴포넌트 정보"):
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            if components.get('role'):
                st.write("**역할:**", ", ".join(components['role']))
            if components.get('goal'):
                st.write("**목표:**", components['goal'])
            if components.get('context'):
                st.write("**맥락:**", ", ".join(components['context']))

        with col_info2:
            if components.get('output'):
                st.write("**출력:**", components['output'])
            if components.get('rule'):
                st.write("**규칙:**")
                for rule in components['rule']:
                    st.write(f"  • {rule}")


def render_template_actions(template: Dict[str, Any], data_handler: DataHandler):
    """템플릿 액션 버튼 렌더링"""

    template_id = template['template_id']

    st.markdown("---")
    st.markdown("**🛠️ 템플릿 관리 옵션**")

    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        if st.button("✏️ 수정", key=f"edit_{template_id}"):
            st.session_state.edit_template_id = template_id
            st.session_state.active_tab = "Prompt 수정"
            st.success("편집 모드로 전환됩니다...")
            st.rerun()

    with action_col2:
        if st.button("🔗 복제", key=f"duplicate_{template_id}"):
            new_name = f"{template['name']}_복사본_{datetime.now().strftime('%m%d_%H%M')}"

            with st.spinner("템플릿 복제 중..."):
                new_id = data_handler.duplicate_template(template_id, new_name)

                if new_id:
                    st.success(f"새로운 템플릿 '{new_name}'으로 복사되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("복제에 실패했습니다.")

    with action_col3:
        if st.button("📤 내보내기", key=f"export_{template_id}"):
            render_export_options(template, data_handler)

    with action_col4:
        if st.button("🗑️ 삭제", key=f"delete_btn_{template_id}", type="secondary"):
            st.session_state[f"confirm_delete_{template_id}"] = True

    # 삭제 확인 대화상자
    if st.session_state.get(f"confirm_delete_{template_id}", False):
        render_delete_confirmation(template, data_handler)


def render_delete_confirmation(template: Dict[str, Any], data_handler: DataHandler):
    """삭제 확인 대화상자"""

    template_id = template['template_id']

    st.warning(f"⚠️ **'{template['name']}'** 템플릿을 정말 삭제하시겠습니까?")
    st.write("이 작업은 되돌릴 수 없습니다.")

    confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 2])

    with confirm_col1:
        if st.button("✅ 삭제 확인", key=f"confirm_yes_{template_id}", type="primary"):
            with st.spinner("삭제 중..."):
                if data_handler.delete_template(template_id):
                    st.success(f"템플릿 '{template['name']}'이 삭제되었습니다!")
                    # 삭제 후 상태 초기화
                    for key in list(st.session_state.keys()):
                        if template_id in key:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("삭제에 실패했습니다.")

    with confirm_col2:
        if st.button("❌ 취소", key=f"confirm_no_{template_id}"):
            st.session_state[f"confirm_delete_{template_id}"] = False
            st.rerun()


def render_export_options(template: Dict[str, Any], data_handler: DataHandler):
    """내보내기 옵션 렌더링"""

    st.info("📤 내보내기 옵션")

    export_format = st.selectbox(
        "내보내기 형식",
        ["텍스트 (.txt)", "JSON (.json)"],
        key=f"export_format_{template['template_id']}"
    )

    if st.button("📥 다운로드", key=f"download_{template['template_id']}"):
        current_version_data = get_current_version_data(template)

        if export_format == "텍스트 (.txt)":
            content = current_version_data['prompt']
            filename = f"{template['name']}.txt"
        else:
            content = str(template)  # JSON 형태
            filename = f"{template['name']}.json"

        st.download_button(
            label="💾 파일 다운로드",
            data=content,
            file_name=filename,
            mime="text/plain" if export_format.endswith("txt)") else "application/json",
            key=f"download_file_{template['template_id']}"
        )


def get_current_version_data(template: Dict[str, Any]) -> Dict[str, Any]:
    """현재 버전의 데이터 반환"""
    current_version = template['current_version']
    versions = template.get('versions', [])

    for version_data in versions:
        if version_data['version'] == current_version:
            return version_data

    # 현재 버전을 찾을 수 없으면 가장 최신 버전 반환
    if versions:
        return sorted(versions, key=lambda x: x['version'], reverse=True)[0]

    return {}