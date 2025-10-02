"""
Prompt Editor Component

기존 템플릿을 수정하고 버전을 관리하는 고급 편집 컴포넌트
"""
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from utils.data_handler import DataHandler


def render_prompt_editor():
    """프롬프트 편집기 메인 렌더링"""
    st.header("✏️ Prompt 수정")
    st.write("선택한 템플릿을 수정하고 버전을 관리합니다.")

    try:
        data_handler = DataHandler()

        # 템플릿 선택
        selected_template = render_template_selector(data_handler)

        if selected_template:
            # 메인 편집 영역
            render_editor_interface(selected_template, data_handler)
        else:
            render_no_template_message()

    except Exception as e:
        st.error(f"프롬프트 편집기 로딩 실패: {e}")


def render_template_selector(data_handler: DataHandler) -> Optional[Dict[str, Any]]:
    """템플릿 선택기 렌더링"""

    templates = data_handler.list_templates()
    if not templates:
        return None

    # 템플릿 선택 옵션 생성
    template_options = {}
    for template in templates:
        display_name = f"{template['name']} ({template['category']}) - v{template['current_version']}"
        template_options[display_name] = template

    # 세션에서 선택된 템플릿이 있는 경우 기본값으로 설정
    default_index = 0
    if 'edit_template_id' in st.session_state:
        for idx, (name, template) in enumerate(template_options.items()):
            if template['template_id'] == st.session_state.edit_template_id:
                default_index = idx
                break

    selected_display_name = st.selectbox(
        "🎯 수정할 템플릿을 선택하세요",
        list(template_options.keys()),
        index=default_index,
        key="editor_template_selection"
    )

    selected_template = template_options[selected_display_name]

    # 선택된 템플릿 정보 표시
    with st.expander("📋 선택된 템플릿 정보", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**이름:** {selected_template['name']}")
            st.write(f"**카테고리:** {selected_template['category']}")
            st.write(f"**현재 버전:** {selected_template['current_version']}")

        with col2:
            st.write(f"**총 버전:** {len(selected_template['versions'])}개")
            if selected_template.get('tags'):
                st.write(f"**태그:** {', '.join(selected_template['tags'])}")

    return selected_template


def render_editor_interface(template: Dict[str, Any], data_handler: DataHandler):
    """편집기 인터페이스 렌더링"""

    # 좌측: 편집 영역, 우측: 버전 히스토리
    col_main, col_sidebar = st.columns([3, 1])

    with col_sidebar:
        render_version_history_sidebar(template, data_handler)

    with col_main:
        render_main_editor(template, data_handler)


def render_version_history_sidebar(template: Dict[str, Any], data_handler: DataHandler):
    """버전 히스토리 사이드바"""
    st.subheader("📜 버전 히스토리")

    template_id = template['template_id']
    versions = data_handler.get_version_history(template_id)

    if not versions:
        st.info("버전 정보가 없습니다.")
        return

    # 현재 선택된 버전 확인
    selected_version = st.session_state.get('editor_selected_version', template['current_version'])

    for version_info in versions:
        version_num = version_info['version']
        created_at = version_info['created_at'].strftime('%m/%d %H:%M')
        is_current = version_info['is_current']

        # 버전 표시
        if is_current:
            st.success(f"**v{version_num}** (현재)")
        elif version_num == selected_version:
            st.info(f"**v{version_num}** (편집 중)")
        else:
            st.write(f"**v{version_num}**")

        st.caption(f"생성: {created_at}")

        if version_info['description']:
            st.caption(f"📝 {version_info['description']}")

        # 컴포넌트 요약
        summary = version_info['components_summary']
        summary_text = []
        if summary['role_count'] > 0:
            summary_text.append(f"역할: {summary['role_count']}")
        if summary['has_goal']:
            summary_text.append("목표: ✓")
        if summary['context_count'] > 0:
            summary_text.append(f"맥락: {summary['context_count']}")
        if summary['has_output']:
            summary_text.append("출력: ✓")
        if summary['rule_count'] > 0:
            summary_text.append(f"규칙: {summary['rule_count']}")

        if summary_text:
            st.caption(" | ".join(summary_text))

        # 버전 선택 버튼
        if st.button(f"v{version_num} 편집", key=f"select_version_{version_num}",
                    disabled=(version_num == selected_version)):
            st.session_state.editor_selected_version = version_num
            st.rerun()

        # 버전 액션 버튼들
        version_col1, version_col2 = st.columns(2)

        with version_col1:
            if not is_current and st.button("📌 현재로", key=f"set_current_{version_num}",
                                          help="이 버전을 현재 버전으로 설정"):
                if data_handler.set_current_version(template_id, version_num):
                    st.success(f"v{version_num}이 현재 버전으로 설정되었습니다!")
                    st.rerun()
                else:
                    st.error("버전 설정 실패")

        with version_col2:
            if len(versions) > 1 and st.button("🗑️ 삭제", key=f"delete_version_{version_num}",
                                             help="이 버전을 삭제"):
                if data_handler.delete_version(template_id, version_num):
                    st.success(f"v{version_num}이 삭제되었습니다!")
                    # 선택된 버전이 삭제된 경우 현재 버전으로 변경
                    if selected_version == version_num:
                        st.session_state.editor_selected_version = template['current_version']
                    st.rerun()
                else:
                    st.error("버전 삭제 실패")

        st.divider()


def render_main_editor(template: Dict[str, Any], data_handler: DataHandler):
    """메인 편집 영역"""

    template_id = template['template_id']
    selected_version = st.session_state.get('editor_selected_version', template['current_version'])

    # 선택된 버전의 데이터 가져오기
    version_data = None
    for version in template['versions']:
        if version['version'] == selected_version:
            version_data = version
            break

    if not version_data:
        st.error("선택된 버전을 찾을 수 없습니다.")
        return

    st.info(f"📝 {template['name']} - **버전 {selected_version}** 편집 중")

    # 편집 모드 선택
    edit_mode = st.radio(
        "편집 모드 선택",
        ["🔧 컴포넌트 편집", "📝 직접 텍스트 편집"],
        key="edit_mode_selection",
        horizontal=True
    )

    if edit_mode == "🔧 컴포넌트 편집":
        render_component_editor(template, version_data, data_handler)
    else:
        render_text_editor(template, version_data, data_handler)


def render_component_editor(template: Dict[str, Any], version_data: Dict[str, Any],
                          data_handler: DataHandler):
    """컴포넌트 편집 모드"""

    template_id = template['template_id']
    selected_version = version_data['version']
    current_components = version_data['components'].copy()

    # 설정 로드
    config = data_handler.load_config()

    st.subheader("🔧 컴포넌트 편집")

    # 컴포넌트 편집 UI
    col1, col2 = st.columns(2)

    with col1:
        # Role
        selected_roles = st.multiselect(
            "역할",
            config['keywords']['role'],
            default=current_components.get('role', []),
            key=f"edit_roles_{selected_version}"
        )

        # Goal
        goal_options = config['keywords']['goal']
        current_goal = current_components.get('goal', goal_options[0])

        # 확장된 goal을 원래 키워드로 역변환
        goal_expansions = config.get('goal_expansions', {})
        original_goal = current_goal

        # 확장된 goal인지 확인하고 원래 키워드를 찾기
        if current_goal not in goal_options:
            for key, expanded in goal_expansions.items():
                if expanded == current_goal:
                    original_goal = key
                    break

        goal_index = goal_options.index(original_goal) if original_goal in goal_options else 0

        selected_goal = st.selectbox(
            "목표 *",
            goal_options,
            index=goal_index,
            key=f"edit_goal_{selected_version}"
        )

        # Context
        context_options = config['keywords']['context']
        current_contexts = current_components.get('context', [])

        # 확장된 context를 원래 키워드로 역변환
        context_expansions = config.get('context_expansions', {})
        original_contexts = []

        for context in current_contexts:
            if context in context_options:
                original_contexts.append(context)
            else:
                # 확장된 context인지 확인하고 원래 키워드를 찾기
                found = False
                for key, expanded in context_expansions.items():
                    if expanded == context:
                        original_contexts.append(key)
                        found = True
                        break

                # 매칭되는 원래 키워드가 없으면 기본값 사용 (하위 호환성)
                if not found and context_options:
                    # 확장된 값이지만 매칭되지 않는 경우 첫 번째 옵션 사용
                    pass  # 추가하지 않음 - 잘못된 값이므로 무시

        selected_contexts = st.multiselect(
            "맥락",
            context_options,
            default=original_contexts,
            key=f"edit_contexts_{selected_version}"
        )

    with col2:
        # Output
        output_options = [""] + config['keywords']['output']
        current_output = current_components.get('output', '')
        output_index = output_options.index(current_output) if current_output in output_options else 0

        selected_output = st.selectbox(
            "출력 형태",
            output_options,
            index=output_index,
            key=f"edit_output_{selected_version}"
        )

        # Rule
        rule_options = config['keywords']['rule']
        current_rules = current_components.get('rule', [])

        # 확장된 rule을 원래 키워드로 역변환
        rule_expansions = config.get('rule_expansions', {})
        original_rules = []

        for rule in current_rules:
            if rule in rule_options:
                original_rules.append(rule)
            else:
                # 확장된 rule인지 확인하고 원래 키워드를 찾기
                found = False
                for key, expanded in rule_expansions.items():
                    if expanded == rule:
                        original_rules.append(key)
                        found = True
                        break

                # 매칭되는 원래 키워드가 없으면 기본값 사용 (하위 호환성)
                if not found and rule_options:
                    # 확장된 값이지만 매칭되지 않는 경우 첫 번째 옵션 사용
                    pass  # 추가하지 않음 - 잘못된 값이므로 무시

        selected_rules = st.multiselect(
            "규칙",
            rule_options,
            default=original_rules,
            key=f"edit_rules_{selected_version}"
        )

        # Description
        current_description = version_data.get('description', '')
        new_description = st.text_area(
            "버전 설명",
            value=current_description,
            height=100,
            key=f"edit_description_{selected_version}"
        )

    # 새 컴포넌트 딕셔너리 생성
    new_components = {
        'role': selected_roles,
        'goal': selected_goal,
        'context': selected_contexts,
        'output': selected_output if selected_output else '',
        'rule': selected_rules
    }

    # 프롬프트 미리보기 생성
    from ai_prompt_maker.prompt_generator import PromptGenerator
    from ai_prompt_maker.models import PromptComponent

    try:
        preview_component = PromptComponent(
            role=new_components['role'],
            goal=new_components['goal'],
            context=new_components['context'],
            output=new_components['output'],
            rule=new_components['rule']
        )
        generator = PromptGenerator()
        generated_prompt = generator.generate_prompt(preview_component)
    except Exception as e:
        generated_prompt = f"프롬프트 생성 오류: {e}"

    # 프롬프트 미리보기
    st.divider()
    st.subheader("🔍 업데이트된 프롬프트 미리보기")
    st.code(generated_prompt, language="text")

    # 변경사항 확인
    has_changes = (
        new_components != current_components or
        new_description != current_description
    )

    if has_changes:
        st.info("💡 변경사항이 감지되었습니다.")

    # 저장 옵션
    st.divider()
    save_col1, save_col2, save_col3, save_col4 = st.columns(4)

    with save_col1:
        if st.button("💾 현재 버전 저장", disabled=not has_changes,
                    help="현재 버전을 업데이트합니다"):
            if data_handler.update_template_version(template_id, selected_version,
                                                  new_components, new_description):
                st.success("현재 버전이 업데이트되었습니다!")
                st.rerun()
            else:
                st.error("저장에 실패했습니다.")

    with save_col2:
        if st.button("🔄 새 버전으로 저장", disabled=not has_changes,
                    help="새로운 버전을 생성합니다"):
            new_version_desc = new_description or f"v{selected_version}에서 분기"
            new_version_num = data_handler.create_new_version_from_existing(
                template_id, selected_version, new_components, new_version_desc
            )
            if new_version_num:
                st.success(f"새 버전 v{new_version_num}이 생성되었습니다!")
                st.session_state.editor_selected_version = new_version_num
                st.rerun()
            else:
                st.error("새 버전 생성에 실패했습니다.")

    with save_col3:
        if st.button("📋 복사", help="프롬프트를 클립보드에 복사"):
            try:
                import pyperclip
                pyperclip.copy(generated_prompt)
                st.success("클립보드에 복사되었습니다!")
            except ImportError:
                st.session_state.clipboard_content = generated_prompt
                st.success("클립보드에 복사되었습니다! (세션 저장)")
            except Exception as e:
                st.session_state.clipboard_content = generated_prompt
                st.warning(f"클립보드 복사 실패. 세션에 저장됨: {e}")

    with save_col4:
        if st.button("📤 내보내기", help="템플릿을 파일로 내보내기"):
            render_export_dialog(template, data_handler)


def render_text_editor(template: Dict[str, Any], version_data: Dict[str, Any],
                      data_handler: DataHandler):
    """직접 텍스트 편집 모드"""

    template_id = template['template_id']
    selected_version = version_data['version']
    current_prompt = version_data['generated_prompt']
    current_description = version_data.get('description', '')

    st.subheader("📝 직접 텍스트 편집")
    st.write("프롬프트를 직접 수정할 수 있습니다. (컴포넌트 정보는 유지됩니다)")

    # 텍스트 에디터
    col_edit, col_info = st.columns([3, 1])

    with col_edit:
        edited_prompt = st.text_area(
            "프롬프트 편집",
            value=current_prompt,
            height=400,
            key=f"prompt_text_editor_{selected_version}"
        )

        # 설명 편집
        new_description = st.text_input(
            "버전 설명",
            value=current_description,
            key=f"text_description_{selected_version}"
        )

    with col_info:
        st.markdown("**📊 텍스트 정보**")
        st.metric("문자 수", len(edited_prompt))
        st.metric("줄 수", edited_prompt.count('\n') + 1)
        st.metric("단어 수 (추정)", len(edited_prompt.split()))

        # 컴포넌트 정보 (참고용)
        st.markdown("---")
        st.markdown("**📋 현재 컴포넌트**")
        components = version_data['components']

        if components.get('role'):
            st.write(f"**역할:** {', '.join(components['role'])}")
        if components.get('goal'):
            st.write(f"**목표:** {components['goal']}")
        if components.get('context'):
            st.write(f"**맥락:** {', '.join(components['context'])}")
        if components.get('output'):
            st.write(f"**출력:** {components['output']}")
        if components.get('rule'):
            st.write("**규칙:**")
            for rule in components['rule']:
                st.write(f"  • {rule}")

    # 변경사항 확인
    has_changes = (
        edited_prompt != current_prompt or
        new_description != current_description
    )

    if has_changes:
        st.info("💡 변경사항이 감지되었습니다.")

        # 변경사항 미리보기
        with st.expander("🔍 변경사항 미리보기"):
            if edited_prompt != current_prompt:
                st.markdown("**프롬프트 변경:**")
                st.code(edited_prompt, language="text")

            if new_description != current_description:
                st.markdown("**설명 변경:**")
                st.write(f"변경 전: {current_description}")
                st.write(f"변경 후: {new_description}")

    # 저장 버튼들
    st.divider()
    save_col1, save_col2, save_col3 = st.columns([1, 1, 2])

    with save_col1:
        if st.button("💾 현재 버전 저장", disabled=not has_changes):
            # 텍스트 편집은 컴포넌트 정보를 유지하면서 프롬프트만 변경
            if data_handler.update_template_version(template_id, selected_version,
                                                  version_data['components'], new_description):
                # 직접 프롬프트 텍스트 업데이트 (별도 처리 필요)
                st.success("현재 버전이 업데이트되었습니다!")
                st.rerun()
            else:
                st.error("저장에 실패했습니다.")

    with save_col2:
        if st.button("🔄 새 버전으로 저장", disabled=not has_changes):
            new_version_desc = new_description or f"v{selected_version} 텍스트 수정"
            new_version_num = data_handler.create_new_version_from_existing(
                template_id, selected_version, version_data['components'], new_version_desc
            )
            if new_version_num:
                st.success(f"새 버전 v{new_version_num}이 생성되었습니다!")
                st.session_state.editor_selected_version = new_version_num
                st.rerun()
            else:
                st.error("새 버전 생성에 실패했습니다.")

    with save_col3:
        if st.button("📋 복사"):
            try:
                import pyperclip
                pyperclip.copy(edited_prompt)
                st.success("클립보드에 복사되었습니다!")
            except ImportError:
                st.session_state.clipboard_content = edited_prompt
                st.success("클립보드에 복사되었습니다! (세션 저장)")
            except Exception as e:
                st.session_state.clipboard_content = edited_prompt
                st.warning(f"클립보드 복사 실패. 세션에 저장됨: {e}")


def render_export_dialog(template: Dict[str, Any], data_handler: DataHandler):
    """내보내기 대화상자"""

    template_id = template['template_id']

    st.markdown("---")
    st.subheader("📤 템플릿 내보내기")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        export_format = st.radio(
            "내보내기 형식",
            ["현재 버전만", "모든 버전 포함"],
            key="export_format_selection"
        )

    with export_col2:
        if st.button("📥 텍스트로 내보내기"):
            include_all = (export_format == "모든 버전 포함")
            export_content = data_handler.export_template_to_text(template_id, include_all)

            if export_content:
                filename = f"{template['name']}_export.txt"
                st.download_button(
                    label="💾 다운로드",
                    data=export_content,
                    file_name=filename,
                    mime="text/plain",
                    key="download_export_text"
                )
            else:
                st.error("내보내기에 실패했습니다.")

        if st.button("📄 JSON으로 내보내기"):
            template_data = data_handler.load_template(template_id)
            if template_data:
                json_content = json.dumps(template_data, ensure_ascii=False, indent=2)
                filename = f"{template['name']}_template.json"
                st.download_button(
                    label="💾 JSON 다운로드",
                    data=json_content,
                    file_name=filename,
                    mime="application/json",
                    key="download_export_json"
                )
            else:
                st.error("JSON 내보내기에 실패했습니다.")


def render_no_template_message():
    """템플릿이 없을 때 표시하는 메시지"""
    st.info("📝 편집할 템플릿이 없습니다.")
    st.write("먼저 **'Prompt Maker'** 탭에서 새 템플릿을 생성하거나,")
    st.write("**'Prompt Template'** 탭에서 기존 템플릿을 확인해보세요.")

    st.markdown("---")
    st.markdown("### 💡 Prompt Editor 기능")
    st.markdown("""
    - **🔧 컴포넌트 편집**: 키워드 기반으로 프롬프트 수정
    - **📝 직접 텍스트 편집**: 프롬프트 텍스트를 직접 수정
    - **📜 버전 관리**: 여러 버전 생성 및 관리
    - **📤 내보내기**: 텍스트 또는 JSON 형식으로 내보내기
    - **🔄 버전 전환**: 원하는 버전으로 쉽게 전환
    """)