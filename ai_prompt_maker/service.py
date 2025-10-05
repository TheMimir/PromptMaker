"""
Prompt Maker Service

프롬프트 템플릿 관리, 키워드 설정, 파일 시스템 연동을 담당하는 서비스
"""
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import shutil

from .models import PromptTemplate, PromptComponent, PromptVersion, PromptCategory
from .models import TemplateNotFoundError, PromptValidationError
from .prompt_generator import PromptGenerator


class PromptMakerService:
    """프롬프트 메이커 서비스"""

    def __init__(self,
                 config_path: str = "data/config.json",
                 templates_dir: str = "ai_prompt_maker/templates"):
        """서비스 초기화

        Args:
            config_path: 설정 파일 경로
            templates_dir: 템플릿 저장 디렉토리
        """
        self.config_path = Path(config_path)
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # 프롬프트 생성기 초기화
        self.generator = PromptGenerator()

        # 설정 캐시
        self._config_cache: Optional[Dict] = None
        self._config_last_modified: Optional[float] = None

        # 템플릿 캐시
        self._templates_cache: Dict[str, PromptTemplate] = {}
        self._cache_valid = False

        # 통계
        self.stats = {
            "templates_created": 0,
            "templates_loaded": 0,
            "templates_updated": 0,
            "templates_deleted": 0,
            "prompts_generated": 0,
            "last_operation": None,
            "service_started": datetime.now()
        }

        # 초기 설정
        self._ensure_config_exists()
        self._load_templates_cache()

    def _sanitize_template_id(self, template_id: str) -> str:
        """Sanitize template ID to prevent path traversal attacks

        Args:
            template_id: Template ID to sanitize

        Returns:
            Sanitized template ID

        Raises:
            ValueError: If template ID contains invalid characters
        """
        if not template_id or not isinstance(template_id, str):
            raise ValueError(f"Invalid template ID type: {type(template_id)}")

        # Remove whitespace
        template_id = template_id.strip()

        # Allow only alphanumeric, hyphens, and underscores (UUID format)
        if not re.match(r'^[a-zA-Z0-9_-]+$', template_id):
            raise ValueError(
                f"Invalid template ID: {template_id}. "
                "Only alphanumeric characters, hyphens, and underscores are allowed."
            )

        # Additional length check (UUIDs are typically 36 chars with hyphens)
        if len(template_id) > 100:
            raise ValueError(f"Template ID too long: {len(template_id)} characters")

        return template_id

    def _validate_template_path(self, template_path: Path) -> None:
        """Validate that template path is within templates directory

        Args:
            template_path: Path to validate

        Raises:
            ValueError: If path traversal is detected
        """
        try:
            # Resolve to absolute path and check if it's within templates dir
            resolved_template = template_path.resolve()
            resolved_templates_dir = self.templates_dir.resolve()

            if not resolved_template.is_relative_to(resolved_templates_dir):
                raise ValueError(
                    f"Path traversal detected: {template_path} is not within {self.templates_dir}"
                )
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid template path: {e}")

    def _ensure_config_exists(self):
        """설정 파일 존재 확인 및 생성"""
        if not self.config_path.exists():
            # 기본 설정 생성
            default_config = {
                "keywords": {
                    "role": ["게임 기획자", "게임 프로그래머", "QA 엔지니어", "데이터 분석가"],
                    "goal": ["기능 분석", "시스템 설계", "버그 해결", "성능 최적화"],
                    "context": ["신규 기능 개발", "TestCase 제작 요청", "버그 수정", "밸런스 테스트"],
                    "output": ["보고서", "TestCase", "분석 결과", "기획서", "코드"],
                    "rule": ["상세 분석 필수", "단계별 접근", "데이터 기반 결론", "실행 가능한 제안"]
                },
                "categories": ["기획", "프로그램", "아트", "QA", "전체"]
            }

            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

    def get_config(self, force_reload: bool = False) -> Dict:
        """설정 파일 로드"""
        try:
            # 파일 변경 시간 확인
            current_mtime = self.config_path.stat().st_mtime if self.config_path.exists() else 0

            # 캐시 유효성 검사
            if (not force_reload and
                self._config_cache and
                self._config_last_modified and
                current_mtime <= self._config_last_modified):
                return self._config_cache

            # 설정 파일 로드
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 캐시 업데이트
            self._config_cache = config
            self._config_last_modified = current_mtime

            return config

        except Exception as e:
            # 설정 로드 실패 시 기본 설정 반환
            return {
                "keywords": {
                    "role": ["게임 기획자"],
                    "goal": ["기능 분석"],
                    "context": ["신규 기능 개발"],
                    "output": ["보고서"],
                    "rule": ["상세 분석 필수"]
                },
                "categories": ["전체"]
            }

    def get_keywords(self) -> Dict[str, List[str]]:
        """키워드 목록 반환"""
        config = self.get_config()
        return config.get("keywords", {})

    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """특정 도메인 설정 반환

        Args:
            domain: 도메인 ID (예: "game_dev", "uiux")

        Returns:
            도메인 설정 딕셔너리
        """
        config = self.get_config()

        # 새 도메인 구조 확인
        if 'domains' in config:
            domains = config.get('domains', {})
            if domain in domains:
                return domains[domain]
            # 기본값으로 game_dev 반환
            return domains.get('game_dev', {})

        # 레거시 구조 (도메인 없음) - 자동 마이그레이션
        return self._migrate_legacy_to_domain(config, 'game_dev')

    def _migrate_legacy_to_domain(self, legacy_config: Dict, domain: str = 'game_dev') -> Dict[str, Any]:
        """레거시 config를 도메인 구조로 변환

        Args:
            legacy_config: 기존 config 구조
            domain: 변환할 도메인명

        Returns:
            도메인 형식의 설정
        """
        return {
            'name': '게임 개발',
            'description': '게임 기획, 개발, QA 관련 프롬프트',
            'icon': '🎮',
            'enabled': True,
            'keywords': legacy_config.get('keywords', {}),
            'goal_expansions': legacy_config.get('goal_expansions', {}),
            'context_expansions': legacy_config.get('context_expansions', {}),
            'rule_expansions': legacy_config.get('rule_expansions', {})
        }

    def list_domains(self) -> List[Dict[str, str]]:
        """활성화된 도메인 목록 반환

        Returns:
            도메인 정보 리스트 [{'id': 'game_dev', 'name': '게임 개발', ...}, ...]
        """
        config = self.get_config()

        # 새 도메인 구조
        if 'domains' in config:
            domains = config.get('domains', {})
            return [
                {
                    'id': domain_id,
                    'name': domain_data.get('name', domain_id),
                    'description': domain_data.get('description', ''),
                    'icon': domain_data.get('icon', '📁')
                }
                for domain_id, domain_data in domains.items()
                if domain_data.get('enabled', True)
            ]

        # 레거시 구조 - 게임 개발만 반환
        return [
            {
                'id': 'game_dev',
                'name': '게임 개발',
                'description': '게임 기획, 개발, QA 관련 프롬프트',
                'icon': '🎮'
            }
        ]

    def get_categories(self) -> List[str]:
        """카테고리 목록 반환"""
        config = self.get_config()
        return config.get("categories", ["전체"])

    def load_output_formats(self) -> Dict[str, Any]:
        """출력 형식 파일 로드"""
        try:
            output_formats_path = Path("data/output_formats.json")

            if not output_formats_path.exists():
                # 기본 포맷 반환
                return {
                    "categories": {
                        "basic_format": {
                            "name": "기본 출력 형식",
                            "description": "일반적으로 사용되는 기본적인 문서 형태"
                        }
                    },
                    "formats": {
                        "basic_report": {
                            "format_id": "basic_report",
                            "name": "보고서",
                            "category": "basic_format",
                            "description": "기본 보고서 형식",
                            "template": "보고서 형식으로 작성해주세요.",
                            "keywords": ["보고서"]
                        }
                    }
                }

            with open(output_formats_path, 'r', encoding='utf-8') as f:
                formats_data = json.load(f)

            return formats_data

        except Exception as e:
            print(f"출력 형식 로드 실패: {e}")
            # 에러 발생 시 기본 포맷 반환
            return {
                "categories": {
                    "basic_format": {
                        "name": "기본 출력 형식",
                        "description": "일반적으로 사용되는 기본적인 문서 형태"
                    }
                },
                "formats": {
                    "basic_report": {
                        "format_id": "basic_report",
                        "name": "보고서",
                        "category": "basic_format",
                        "description": "기본 보고서 형식",
                        "template": "보고서 형식으로 작성해주세요.",
                        "keywords": ["보고서"]
                    }
                }
            }

    def generate_prompt(self, components: PromptComponent) -> str:
        """프롬프트 생성"""
        try:
            # 유효성 검증
            is_valid, error_msg = components.validate()
            if not is_valid:
                raise PromptValidationError(error_msg)

            # 프롬프트 생성
            prompt = self.generator.generate_prompt(components)

            # 통계 업데이트
            self.stats["prompts_generated"] += 1
            self.stats["last_operation"] = "프롬프트 생성"

            return prompt

        except Exception as e:
            raise PromptValidationError(f"프롬프트 생성 실패: {e}")

    def create_template(self, name: str, category: str, components: PromptComponent,
                       description: str = "", tags: List[str] = None) -> PromptTemplate:
        """새 템플릿 생성"""
        try:
            # 카테고리 변환
            if category in [cat.value for cat in PromptCategory]:
                template_category = PromptCategory(category)
            else:
                template_category = PromptCategory.ALL

            # 템플릿 생성
            template = PromptTemplate(
                name=name,
                category=template_category,
                tags=tags or []
            )

            # 첫 번째 버전 생성
            template.update_current_version(components, description)

            # 통계 업데이트
            self.stats["templates_created"] += 1
            self.stats["last_operation"] = f"템플릿 생성: {name}"

            return template

        except Exception as e:
            raise PromptValidationError(f"템플릿 생성 실패: {e}")

    def save_template(self, template: PromptTemplate, overwrite: bool = True) -> bool:
        """템플릿 저장

        Args:
            template: 저장할 템플릿
            overwrite: 기존 파일 덮어쓰기 허용 여부

        Returns:
            저장 성공 여부

        Raises:
            ValueError: 잘못된 template ID
            PromptValidationError: 저장 실패
        """
        try:
            # Sanitize template ID to prevent path traversal
            safe_id = self._sanitize_template_id(template.template_id)
            template_path = self.templates_dir / f"{safe_id}.json"

            # Additional path validation
            self._validate_template_path(template_path)

            # 덮어쓰기 확인
            if not overwrite and template_path.exists():
                raise PromptValidationError(f"템플릿이 이미 존재합니다: {template.name}")

            # JSON 파일로 저장
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template.to_json())

            # 캐시 업데이트
            self._templates_cache[template.template_id] = template
            self._cache_valid = True

            # 통계 업데이트
            if template_path.exists():
                self.stats["templates_updated"] += 1
            else:
                self.stats["templates_created"] += 1

            self.stats["last_operation"] = f"템플릿 저장: {template.name}"

            return True

        except ValueError as e:
            # Path traversal or invalid ID
            raise ValueError(f"Invalid template ID: {e}")
        except Exception as e:
            raise PromptValidationError(f"템플릿 저장 실패: {e}")

    def load_template(self, template_id: str) -> Optional[PromptTemplate]:
        """템플릿 로드

        Args:
            template_id: 로드할 템플릿 ID

        Returns:
            템플릿 객체 또는 None (존재하지 않는 경우)

        Raises:
            ValueError: 잘못된 template ID
        """
        try:
            # Sanitize template ID to prevent path traversal
            safe_id = self._sanitize_template_id(template_id)

            # 캐시 확인 (sanitized ID 사용)
            if safe_id in self._templates_cache:
                self.stats["templates_loaded"] += 1
                return self._templates_cache[safe_id]

            # 파일에서 로드
            template_path = self.templates_dir / f"{safe_id}.json"

            # Additional path validation
            self._validate_template_path(template_path)

            if not template_path.exists():
                return None

            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = f.read()

            template = PromptTemplate.from_json(template_data)

            # 캐시에 저장
            self._templates_cache[safe_id] = template

            # 통계 업데이트
            self.stats["templates_loaded"] += 1
            self.stats["last_operation"] = f"템플릿 로드: {template.name}"

            return template

        except ValueError as e:
            # Invalid template ID
            print(f"Invalid template ID ({template_id}): {e}")
            return None
        except Exception as e:
            print(f"템플릿 로드 실패 ({template_id}): {e}")
            return None

    def list_templates(self, category: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """템플릿 목록 조회"""
        try:
            templates = []

            # 모든 템플릿 파일 스캔
            for template_file in self.templates_dir.glob("*.json"):
                template_id = template_file.stem
                template = self.load_template(template_id)

                if template:
                    # 카테고리 필터
                    if category and category != "전체" and template.category.value != category:
                        continue

                    # 태그 필터
                    if tags and not any(tag in template.tags for tag in tags):
                        continue

                    templates.append(template.get_summary())

            # 업데이트 시간으로 정렬 (최신순) - ISO 형식 문자열 정렬
            templates.sort(key=lambda x: x.get("updated_at") or "", reverse=True)

            return templates

        except Exception as e:
            print(f"템플릿 목록 조회 실패: {e}")
            return []

    def delete_template(self, template_id: str) -> bool:
        """템플릿 삭제

        Args:
            template_id: 삭제할 템플릿 ID

        Returns:
            삭제 성공 여부

        Raises:
            ValueError: 잘못된 template ID
        """
        try:
            # Sanitize template ID to prevent path traversal
            safe_id = self._sanitize_template_id(template_id)
            template_path = self.templates_dir / f"{safe_id}.json"

            # Additional path validation
            self._validate_template_path(template_path)

            if not template_path.exists():
                return False

            # 백업 (선택적)
            backup_dir = self.templates_dir / "backup"
            backup_dir.mkdir(exist_ok=True)

            # Use sanitized ID for backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{safe_id}_{timestamp}.json"

            # Validate backup path as well
            self._validate_template_path(backup_path)

            # Atomic copy and delete
            shutil.copy2(template_path, backup_path)

            # 원본 파일 삭제
            template_path.unlink()

            # 캐시에서 제거 (sanitized ID 사용)
            self._templates_cache.pop(safe_id, None)

            # 통계 업데이트
            self.stats["templates_deleted"] += 1
            self.stats["last_operation"] = f"템플릿 삭제: {safe_id}"

            return True

        except ValueError as e:
            # Invalid template ID or path traversal
            print(f"Invalid template ID ({template_id}): {e}")
            return False
        except Exception as e:
            print(f"템플릿 삭제 실패 ({template_id}): {e}")
            return False

    def copy_template(self, template_id: str, new_name: str,
                     new_category: Optional[str] = None) -> Optional[PromptTemplate]:
        """템플릿 복사"""
        try:
            # 원본 템플릿 로드
            original = self.load_template(template_id)
            if not original:
                raise TemplateNotFoundError(f"템플릿을 찾을 수 없습니다: {template_id}")

            # 새 템플릿 생성
            new_template = PromptTemplate(
                name=new_name,
                category=PromptCategory(new_category) if new_category else original.category,
                tags=original.tags.copy()
            )

            # 현재 버전 복사
            current_version = original.get_current_version()
            if current_version:
                new_template.update_current_version(
                    current_version.components,
                    f"{current_version.description} (복사본)"
                )

            # 저장
            self.save_template(new_template)

            return new_template

        except Exception as e:
            raise PromptValidationError(f"템플릿 복사 실패: {e}")

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """템플릿 검색"""
        if not query.strip():
            return self.list_templates()

        query = query.lower().strip()
        matching_templates = []

        try:
            all_templates = self.list_templates()

            for template_summary in all_templates:
                # 이름에서 검색
                if query in template_summary["name"].lower():
                    matching_templates.append(template_summary)
                    continue

                # 태그에서 검색
                if any(query in tag.lower() for tag in template_summary.get("tags", [])):
                    matching_templates.append(template_summary)
                    continue

                # 실제 템플릿 로드해서 내용 검색
                template = self.load_template(template_summary["template_id"])
                if template:
                    current_version = template.get_current_version()
                    if current_version:
                        # 프롬프트 내용에서 검색
                        prompt_text = current_version.generated_prompt.lower()
                        if query in prompt_text:
                            matching_templates.append(template_summary)

        except Exception as e:
            print(f"템플릿 검색 실패: {e}")

        return matching_templates

    def get_service_stats(self) -> Dict[str, Any]:
        """서비스 통계 반환"""
        try:
            total_templates = len(list(self.templates_dir.glob("*.json")))

            return {
                **self.stats,
                "total_templates": total_templates,
                "templates_directory": str(self.templates_dir),
                "config_path": str(self.config_path),
                "cache_size": len(self._templates_cache),
                "cache_valid": self._cache_valid
            }
        except Exception:
            return self.stats

    def export_template(self, template_id: str, export_format: str = "json") -> Optional[str]:
        """템플릿 내보내기"""
        try:
            template = self.load_template(template_id)
            if not template:
                return None

            if export_format.lower() == "json":
                return template.to_json()
            elif export_format.lower() == "text":
                current_version = template.get_current_version()
                return current_version.generated_prompt if current_version else ""
            else:
                return None

        except Exception:
            return None

    def import_template_from_json(self, json_data: str) -> Optional[PromptTemplate]:
        """JSON에서 템플릿 가져오기"""
        try:
            template = PromptTemplate.from_json(json_data)
            self.save_template(template)
            return template
        except Exception as e:
            raise PromptValidationError(f"템플릿 가져오기 실패: {e}")

    def _load_templates_cache(self):
        """템플릿 캐시 로드"""
        try:
            # 최대 50개의 최신 템플릿만 캐시
            template_files = sorted(
                self.templates_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:50]

            for template_file in template_files:
                template_id = template_file.stem
                self.load_template(template_id)

            self._cache_valid = True

        except Exception as e:
            print(f"템플릿 캐시 로드 실패: {e}")
            self._cache_valid = False

    def cleanup_service(self):
        """서비스 정리"""
        try:
            # 통계 저장 등 정리 작업
            self._templates_cache.clear()
            self._config_cache = None
            self._cache_valid = False
        except Exception:
            pass

    def validate_template_data(self, template_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """템플릿 데이터 검증"""
        errors = []

        try:
            # 기본 필드 검증
            if not template_data.get("name", "").strip():
                errors.append("템플릿 이름이 필요합니다")

            if not template_data.get("category"):
                errors.append("카테고리가 필요합니다")

            # 버전 데이터 검증
            versions = template_data.get("versions", [])
            if not versions:
                errors.append("최소 하나의 버전이 필요합니다")
            else:
                for i, version_data in enumerate(versions):
                    components_data = version_data.get("components", {})
                    if not components_data.get("goal", "").strip():
                        errors.append(f"버전 {i+1}: Goal이 필요합니다")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"데이터 검증 중 오류: {e}"]


class PromptMakerServiceError(Exception):
    """서비스 관련 일반 오류"""
    pass