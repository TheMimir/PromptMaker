"""
AI Prompt Maker 데이터 모델

프롬프트 템플릿, 컴포넌트, 버전 관리를 위한 데이터 구조
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
from enum import Enum


class PromptCategory(Enum):
    """프롬프트 카테고리"""
    PLANNING = "기획"
    PROGRAMMING = "프로그램"
    ART = "아트"
    QA = "QA"
    ALL = "전체"


@dataclass
class PromptComponent:
    """프롬프트 구성 요소"""
    role: List[str] = field(default_factory=list)
    goal: str = ""
    context: List[str] = field(default_factory=list)
    document: str = ""
    output: str = ""
    rule: List[str] = field(default_factory=list)

    def __post_init__(self):
        """데이터 유효성 검사"""
        # goal은 필수 항목
        if not self.goal or not self.goal.strip():
            raise ValueError("Goal은 필수 항목입니다")

        # 문자열 정리
        self.goal = self.goal.strip()
        self.document = self.document.strip() if self.document else ""
        self.output = self.output.strip() if self.output else ""

        # 리스트 요소들 정리
        self.role = [role.strip() for role in self.role if role.strip()]
        self.context = [ctx.strip() for ctx in self.context if ctx.strip()]
        self.rule = [rule.strip() for rule in self.rule if rule.strip()]

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

        if len(self.role) > 5:
            return False, "Role은 최대 5개까지 선택 가능합니다"

        if len(self.context) > 5:
            return False, "Context는 최대 5개까지 선택 가능합니다"

        if len(self.rule) > 5:
            return False, "Rule은 최대 5개까지 선택 가능합니다"

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
    """프롬프트 템플릿"""
    name: str
    category: PromptCategory
    versions: List[PromptVersion] = field(default_factory=list)
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_version: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

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
        """JSON 문자열에서 생성"""
        data = json.loads(json_str)
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