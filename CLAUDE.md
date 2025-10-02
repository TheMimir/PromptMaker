# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Prompt Maker** is a Streamlit-based web application for game developers to generate structured AI prompts. The tool helps create prompts for AI assistants (ChatGPT, Claude) with consistent structure using the Role-Goal-Context-Document-Output-Rule framework.

**Primary Language**: Korean (UI, documentation, and configuration)
**Tech Stack**: Python 3.8+, Streamlit 1.28+, pandas, pyperclip

## Quick Start Commands

### Run the application
```bash
# Method 1: Direct Streamlit
streamlit run app.py

# Method 2: Using launcher script
python run.py
# or
python3 run.py
```

The app will be available at `http://localhost:8501`

### Install dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Components

The application follows a three-layer architecture:

1. **Service Layer** (`ai_prompt_maker/`)
   - `service.py`: Main service orchestrating template management, configuration, and prompt generation
   - `prompt_generator.py`: Core engine that generates structured prompts from components
   - `models.py`: Data models (PromptComponent, PromptTemplate, PromptVersion, PromptCategory)

2. **UI Layer** (`app.py`, `components/`)
   - `app.py`: Main Streamlit application with three tabs (Generator, Template Manager, Editor)
   - `components/template_manager.py`: UI for browsing, filtering, and managing saved templates
   - `components/prompt_editor.py`: Advanced editor with version control and component/text editing modes

3. **Data Layer** (`data/`)
   - `config.json`: Keywords library with expansions for role, goal, context, output, and rule
   - `output_formats.json`: Output format templates (20+ formats: tables, lists, reports, Q&A, guides)
   - `ai_prompt_maker/templates/`: Stored prompt templates (JSON files)

### Prompt Structure

Generated prompts follow this XML-like structure:
```
<Role>
{role}
</Role>

<Goal>
{goal}
</Goal>

<Document>
{document}
</Document>

<Context>
{context}
</Context>

<Output>
{output}
</Output>

<Rule>
{rule}
</Rule>
```

### Template System

- Templates support versioning (multiple versions per template)
- Each version contains: components, generated_prompt, description, created_at
- Templates are categorized: 기획, 프로그램, 아트, QA, 전체
- Templates stored as JSON files in `ai_prompt_maker/templates/` with UUID filenames

### Keyword Expansion System

The configuration supports "expansions" for:
- `goal_expansions`: Short keywords expand to detailed goal descriptions (100+ chars)
- `context_expansions`: Short keywords expand to rich contextual scenarios
- `rule_expansions`: Short keywords expand to comprehensive rule definitions

This allows users to select simple keywords in the UI while generating detailed, structured prompts.

## Key Design Patterns

### Service Layer Caching
- `PromptMakerService` caches templates (max 50 most recent) and configuration
- Cache invalidation based on file modification time
- Statistics tracking for service operations

### Session State Management
- Streamlit session state used for:
  - Template selection and editing state
  - Filter preferences (category, search terms)
  - Clipboard content fallback (when pyperclip unavailable)
  - Preview/action toggles for template cards

### Component Validation
- `PromptComponent.validate()`: Validates required fields, length limits, max items
- Goal is the only required field
- Validation enforced before prompt generation

## File Locations

### Configuration Files
- `data/config.json`: Keywords and expansions
- `data/output_formats.json`: Output format templates with categories
- Template storage: `ai_prompt_maker/templates/{uuid}.json`
- Template backups: `ai_prompt_maker/templates/backup/`

### Python Modules
- Entry point: `app.py`, `run.py`
- Core logic: `ai_prompt_maker/service.py`, `ai_prompt_maker/prompt_generator.py`
- Data models: `ai_prompt_maker/models.py`
- UI components: `components/template_manager.py`, `components/prompt_editor.py`

## Development Notes

### Version Management
- Current version: 2.3.0
- Config version: 2.2.0
- Version stored in config.json and displayed in UI footer

### Output Formats
- 20+ predefined formats organized in categories:
  - 표 형식 (Tables): Test case tables, analysis matrices, comparison tables
  - 목록 형식 (Lists): Checklists, priority lists, categorized lists
  - 보고서 형식 (Reports): Detailed/summary reports
  - Q&A 형식: FAQ, problem-solution Q&A
  - 가이드 형식 (Guides): Step-by-step, checkpoint guides
  - 데이터 형식 (Data): Numeric dashboards
  - 기본 형식 (Basic): Reports, TestCase, analysis results, specifications, code, documents, presentations

### Clipboard Functionality
- Primary: Uses `pyperclip` for system clipboard
- Fallback: Uses JavaScript injection via `st.components.html`
- Last resort: Stores in session state for manual copying

### Error Handling
- Service layer catches exceptions and returns user-friendly messages
- Validation errors raised as `PromptValidationError`
- Template operations support backup before deletion
- Version conflicts handled with `VersionConflictError`

## Working with Templates

### Creating a New Template
Templates are created through `PromptMakerService.create_template()` which:
1. Converts category string to `PromptCategory` enum
2. Creates initial version with provided components
3. Auto-generates prompt using `PromptGenerator`
4. Saves to templates directory

### Loading and Caching
- Templates loaded on-demand with LRU cache (50 most recent)
- Cache invalidation on save/delete operations
- `list_templates()` scans directory and filters by category/tags

### Version Control
- Add version: `template.add_version(components, description)`
- Update current: `template.update_current_version(components, description)`
- Delete version: `template.delete_version(version_number)` (min 1 version required)
- Switch version: Update `template.current_version` field

## Korean Localization

All UI text, messages, and documentation are in Korean. When modifying:
- Maintain Korean for user-facing strings
- Keep English for code identifiers, function names, comments
- Config keywords use Korean terms (게임 기획자, 기능 분석, etc.)
- Error messages should be in Korean for end users
