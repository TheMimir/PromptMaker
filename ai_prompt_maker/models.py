"""
AI Prompt Maker 데이터 모델

프롬프트 템플릿, 컴포넌트, 버전 관리를 위한 데이터 구조
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import re
import uuid
from datetime import datetime
from enum import Enum

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not installed. JSON validation will be skipped.")


class PromptCategory(Enum):
    """프롬프트 카테고리"""
    PLANNING = "기획"
    PROGRAMMING = "프로그램"
    ART = "아트"
    QA = "QA"
    ALL = "전체"


class OutputFormat(Enum):
    """출력 포맷"""
    XML = "XML"
    MARKDOWN = "Markdown"


@dataclass
class PromptComponent:
    """프롬프트 구성 요소 (with enhanced security validation)"""
    role: List[str] = field(default_factory=list)
    goal: str = ""
    context: List[str] = field(default_factory=list)
    document: str = ""
    output: str = ""
    rule: List[str] = field(default_factory=list)

    # Validation constants
    MAX_GOAL_LENGTH = 500
    MAX_DOCUMENT_LENGTH = 10_000
    MAX_OUTPUT_LENGTH = 1_000
    MAX_LIST_ITEMS = 10  # Increased from 5 to 10 for more flexibility
    MAX_ITEM_LENGTH = 500  # Increased from 200 to 500 for longer descriptions

    @staticmethod
    def _sanitize_string(value: str, max_length: int, field_name: str = "Field") -> str:
        """Sanitize and validate string input

        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            field_name: Field name for error messages

        Returns:
            Sanitized string

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name}: Expected string, got {type(value)}")

        # Remove whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            raise ValueError(
                f"{field_name}: Input too long ({len(value)} > {max_length} characters)"
            )

        # Check for potentially dangerous patterns (defense in depth)
        dangerous_patterns = [
            (r'<script[^>]*>.*?</script>', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'on\w+\s*=', 'Event handlers'),
            (r'<iframe[^>]*>', 'Iframe tags'),
        ]

        for pattern, pattern_name in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                raise ValueError(f"{field_name}: Potentially malicious content detected ({pattern_name})")

        return value

    @staticmethod
    def _sanitize_list(items: List[str], max_items: int, max_item_length: int,
                      field_name: str = "Field") -> List[str]:
        """Sanitize and validate list input

        Args:
            items: List to sanitize
            max_items: Maximum number of items
            max_item_length: Maximum length per item
            field_name: Field name for error messages

        Returns:
            Sanitized list

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(items, list):
            raise ValueError(f"{field_name}: Expected list, got {type(items)}")

        if len(items) > max_items:
            raise ValueError(
                f"{field_name}: Too many items ({len(items)} > {max_items})"
            )

        sanitized = []
        for i, item in enumerate(items):
            if not isinstance(item, str):
                raise ValueError(
                    f"{field_name}[{i}]: Expected string, got {type(item)}"
                )

            item = item.strip()
            if item:  # Only add non-empty items
                try:
                    sanitized.append(
                        PromptComponent._sanitize_string(
                            item, max_item_length, f"{field_name}[{i}]"
                        )
                    )
                except ValueError as e:
                    raise ValueError(f"{field_name}[{i}]: {e}")

        return sanitized

    def __post_init__(self):
        """데이터 유효성 검사 (enhanced with security validation)"""
        # Validate goal (required field)
        if not self.goal or not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("Goal은 필수 항목입니다")

        try:
            # Sanitize and validate goal
            self.goal = self._sanitize_string(
                self.goal, self.MAX_GOAL_LENGTH, "Goal"
            )

            # Sanitize optional string fields
            if self.document:
                self.document = self._sanitize_string(
                    self.document, self.MAX_DOCUMENT_LENGTH, "Document"
                )
            else:
                self.document = ""

            if self.output:
                self.output = self._sanitize_string(
                    self.output, self.MAX_OUTPUT_LENGTH, "Output"
                )
            else:
                self.output = ""

            # Sanitize list fields
            self.role = self._sanitize_list(
                self.role, self.MAX_LIST_ITEMS, self.MAX_ITEM_LENGTH, "Role"
            )
            self.context = self._sanitize_list(
                self.context, self.MAX_LIST_ITEMS, self.MAX_ITEM_LENGTH, "Context"
            )
            self.rule = self._sanitize_list(
                self.rule, self.MAX_LIST_ITEMS, self.MAX_ITEM_LENGTH, "Rule"
            )

        except ValueError as e:
            # Re-raise with clear error message
            raise ValueError(f"PromptComponent validation failed: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "role": self.role,
            "goal": self.goal,
            "context": self.context,
            "document": self.document,
            "output": self.output,
            "rule": self.rule
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptComponent':
        """딕셔너리에서 생성"""
        return cls(
            role=data.get("role", []),
            goal=data.get("goal", ""),
            context=data.get("context", []),
            document=data.get("document", ""),
            output=data.get("output", ""),
            rule=data.get("rule", [])
        )

    def validate(self) -> tuple[bool, str]:
        """컴포넌트 유효성 검증"""
        if not self.goal:
            return False, "Goal은 필수 항목입니다"

        if len(self.goal) > 500:
            return False, "Goal은 500자 이내여야 합니다"

        if len(self.role) > 10:
            return False, "Role은 최대 10개까지 선택 가능합니다"

        if len(self.context) > 10:
            return False, "Context는 최대 10개까지 선택 가능합니다"

        if len(self.rule) > 10:
            return False, "Rule은 최대 10개까지 선택 가능합니다"

        return True, ""

    def is_empty(self) -> bool:
        """빈 컴포넌트인지 확인"""
        return not any([self.role, self.goal, self.context, self.document, self.output, self.rule])


@dataclass
class PromptVersion:
    """프롬프트 템플릿 버전"""
    version: int
    created_at: datetime
    components: PromptComponent
    generated_prompt: str = ""
    description: str = ""

    def __post_init__(self):
        """초기화 후 처리"""
        if not self.created_at:
            self.created_at = datetime.now()

        self.description = self.description.strip() if self.description else ""

        # 프롬프트가 없으면 자동 생성
        if not self.generated_prompt and not self.components.is_empty():
            from .prompt_generator import PromptGenerator
            generator = PromptGenerator()
            self.generated_prompt = generator.generate_prompt(self.components)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "components": self.components.to_dict(),
            "generated_prompt": self.generated_prompt,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptVersion':
        """딕셔너리에서 생성"""
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()

        return cls(
            version=data.get("version", 1),
            created_at=created_at,
            components=PromptComponent.from_dict(data.get("components", {})),
            generated_prompt=data.get("generated_prompt", ""),
            description=data.get("description", "")
        )


@dataclass
class PromptTemplate:
    """프롬프트 템플릿 (with JSON schema validation)"""
    name: str
    category: PromptCategory
    versions: List[PromptVersion] = field(default_factory=list)
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_version: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # JSON Schema for validation
    JSON_SCHEMA = {
        "type": "object",
        "required": ["name", "category", "template_id", "versions"],
        "properties": {
            "template_id": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9_-]+$",
                "minLength": 1,
                "maxLength": 100
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
            },
            "category": {
                "type": "string",
                "enum": ["기획", "프로그램", "아트", "QA", "전체"]
            },
            "current_version": {
                "type": "integer",
                "minimum": 1
            },
            "versions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "items": {
                    "type": "object",
                    "required": ["version", "components"],
                    "properties": {
                        "version": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "components": {
                            "type": "object",
                            "required": ["goal"],
                            "properties": {
                                "goal": {"type": "string", "minLength": 1, "maxLength": 500},
                                "document": {"type": "string", "maxLength": 10000},
                                "output": {"type": "string", "maxLength": 1000},
                                "role": {
                                    "type": "array",
                                    "maxItems": 10,
                                    "items": {"type": "string", "maxLength": 500}
                                },
                                "context": {
                                    "type": "array",
                                    "maxItems": 10,
                                    "items": {"type": "string", "maxLength": 500}
                                },
                                "rule": {
                                    "type": "array",
                                    "maxItems": 10,
                                    "items": {"type": "string", "maxLength": 500}
                                }
                            }
                        }
                    }
                }
            },
            "tags": {
                "type": "array",
                "maxItems": 10,
                "items": {"type": "string", "maxLength": 50}
            },
            "metadata": {
                "type": "object"
            }
        }
    }

    def __post_init__(self):
        """초기화 후 처리"""
        if not self.name or not self.name.strip():
            raise ValueError("템플릿 이름은 필수입니다")

        self.name = self.name.strip()

        # 카테고리가 문자열로 들어온 경우 변환
        if isinstance(self.category, str):
            try:
                self.category = PromptCategory(self.category)
            except ValueError:
                self.category = PromptCategory.ALL

        # 태그 정리
        self.tags = [tag.strip() for tag in self.tags if tag.strip()]

        # 버전이 없으면 기본 버전 생성
        if not self.versions:
            default_component = PromptComponent(goal="기능 분석")
            self.versions = [PromptVersion(version=1, created_at=datetime.now(), components=default_component)]

        # 현재 버전 검증
        if self.current_version < 1 or self.current_version > len(self.versions):
            self.current_version = len(self.versions)

    def add_version(self, components: PromptComponent, description: str = "") -> int:
        """새 버전 추가"""
        new_version_number = len(self.versions) + 1
        new_version = PromptVersion(
            version=new_version_number,
            created_at=datetime.now(),
            components=components,
            description=description
        )

        self.versions.append(new_version)
        self.current_version = new_version_number

        return new_version_number

    def get_current_version(self) -> Optional[PromptVersion]:
        """현재 버전 반환"""
        if not self.versions:
            return None

        for version in self.versions:
            if version.version == self.current_version:
                return version

        # 현재 버전을 찾지 못한 경우 최신 버전 반환
        return self.versions[-1]

    def get_version(self, version_number: int) -> Optional[PromptVersion]:
        """특정 버전 반환"""
        for version in self.versions:
            if version.version == version_number:
                return version
        return None

    def update_current_version(self, components: PromptComponent, description: str = "") -> bool:
        """현재 버전 업데이트"""
        current = self.get_current_version()
        if not current:
            return False

        current.components = components
        current.description = description

        # 프롬프트 재생성
        from .prompt_generator import PromptGenerator
        generator = PromptGenerator()
        current.generated_prompt = generator.generate_prompt(components)

        return True

    def delete_version(self, version_number: int) -> bool:
        """버전 삭제 (최소 1개 버전은 유지)"""
        if len(self.versions) <= 1:
            return False

        for i, version in enumerate(self.versions):
            if version.version == version_number:
                del self.versions[i]

                # 삭제된 버전이 현재 버전이면 최신 버전으로 변경
                if self.current_version == version_number:
                    self.current_version = self.versions[-1].version

                return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "current_version": self.current_version,
            "versions": [version.to_dict() for version in self.versions],
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """딕셔너리에서 생성"""
        versions = [PromptVersion.from_dict(v_data) for v_data in data.get("versions", [])]

        return cls(
            template_id=data.get("template_id", str(uuid.uuid4())),
            name=data["name"],
            category=PromptCategory(data.get("category", "전체")),
            current_version=data.get("current_version", 1),
            versions=versions,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'PromptTemplate':
        """JSON 문자열에서 생성 (with validation)

        Args:
            json_str: JSON 문자열

        Returns:
            PromptTemplate 객체

        Raises:
            ValueError: JSON이 유효하지 않거나 너무 큰 경우
            PromptValidationError: Schema 검증 실패
        """
        # Size check to prevent DoS
        MAX_JSON_SIZE = 1_000_000  # 1MB
        if len(json_str) > MAX_JSON_SIZE:
            raise ValueError(
                f"JSON payload too large: {len(json_str)} bytes > {MAX_JSON_SIZE} bytes"
            )

        try:
            # Parse JSON
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        # Validate against schema if jsonschema is available
        if JSONSCHEMA_AVAILABLE:
            try:
                jsonschema.validate(instance=data, schema=cls.JSON_SCHEMA)
            except jsonschema.ValidationError as e:
                # Extract useful error information
                error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
                raise PromptValidationError(
                    f"JSON schema validation failed at {error_path}: {e.message}"
                )
            except jsonschema.SchemaError as e:
                # Schema itself is invalid (shouldn't happen in production)
                raise PromptValidationError(f"Invalid JSON schema: {e}")

        # Create template from validated data
        return cls.from_dict(data)

    def get_summary(self) -> Dict[str, Any]:
        """템플릿 요약 정보"""
        current_version = self.get_current_version()

        # datetime 객체를 ISO 형식 문자열로 변환
        created_at = self.versions[0].created_at if self.versions else None
        updated_at = current_version.created_at if current_version else None

        return {
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "version_count": len(self.versions),
            "current_version": self.current_version,
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
            "tags": self.tags,
            "has_components": not current_version.components.is_empty() if current_version else False
        }

    @staticmethod
    def create_example() -> 'PromptTemplate':
        """예시 템플릿 생성"""
        components = PromptComponent(
            role=["게임 기획자", "QA 엔지니어"],
            goal="기능 분석",
            context=["신규 기능 개발", "TestCase 제작 요청"],
            output="기획서",
            rule=["상세 분석 필수", "단계별 접근"]
        )

        template = PromptTemplate(
            name="캐릭터 시스템 분석",
            category=PromptCategory.PLANNING
        )

        # 기본 버전 업데이트
        template.update_current_version(components, "캐릭터 시스템 분석을 위한 기본 템플릿")

        return template


# 커스텀 예외 클래스들
class PromptValidationError(Exception):
    """프롬프트 검증 오류"""
    pass


class TemplateNotFoundError(Exception):
    """템플릿을 찾을 수 없음"""
    pass


class VersionConflictError(Exception):
    """버전 충돌 오류"""
    pass