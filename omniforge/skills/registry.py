"""
Skill Registry — Cross-platform skill management system.
Inspired by anthropics/skills (139K star) and agent-skills (45K star).

Supports SKILL.md format with extensions for:
- Cross-platform compatibility (Claude Code, Cursor, Codex, Aider, etc.)
- Skill versioning and dependency resolution
- Hot reload and auto-discovery
- Built-in skill marketplace integration
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from omniforge.config import SkillConfig

logger = logging.getLogger(__name__)


class SkillFormat(Enum):
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
    PYTHON = "python"


@dataclass
class SkillMetadata:
    """Metadata for a registered skill."""
    name: str
    version: str = "1.0.0"
    author: str = "unknown"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)  # claude-code, cursor, codex
    category: str = "general"
    format: str = "markdown"
    path: Optional[str] = None
    installed_at: Optional[str] = None


@dataclass
class Skill:
    """A fully loaded skill instance."""
    metadata: SkillMetadata
    content: str  # The SKILL.md content
    triggers: List[str] = field(default_factory=list)  # When to activate
    instructions: str = ""  # Parsed instructions
    examples: List[Dict[str, str]] = field(default_factory=list)
    raw_config: Dict[str, Any] = field(default_factory=dict)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute this skill with given context."""
        # Base skill execution — subclasses can override
        return {
            "skill": self.metadata.name,
            "content": self.content,
            "context": context,
        }


class SkillRegistry:
    """
    Central registry for all skills.

    5W1H:
    - WHAT: Manages skill discovery, loading, versioning, and execution
    - WHY: Unifies fragmented skill landscape across AI platforms
    - WHO: AI agent developers, automation engineers
    - WHEN: At agent initialization and skill installation
    - WHERE: Any OmniForge-enabled environment
    - HOW: File-based skill definitions with auto-discovery
    """

    # Cross-platform conversion mapping
    PLATFORM_CONVERTERS = {
        "claude-code": "SKILL.md",
        "cursor": ".cursorrules",
        "codex": ".codex/skills",
        "aider": ".aider/skills",
        "windsurf": ".windsurfrules",
        "copilot": ".github/copilot-instructions.md",
    }

    def __init__(self, config: SkillConfig):
        self.config = config
        self._skills: Dict[str, Skill] = {}
        self._installed: Dict[str, SkillMetadata] = {}
        self._marketplace: List[Dict[str, Any]] = []
        self._state_path = Path(config.skills_dir) / "registry_state.json"

    def discover_skills(self) -> int:
        """Auto-discover skills from configured directories."""
        discovered = 0

        # Discover from built-in skills
        builtin_dir = Path(__file__).parent / "builtin"
        if builtin_dir.exists():
            for skill_dir in builtin_dir.iterdir():
                if skill_dir.is_dir():
                    if self._load_skill(skill_dir):
                        discovered += 1

        # Discover from user skills directory
        user_dir = Path(self.config.skills_dir)
        if user_dir.exists():
            for skill_dir in user_dir.iterdir():
                if skill_dir.is_dir():
                    if self._load_skill(skill_dir):
                        discovered += 1

        # Discover from project-local skills
        project_dir = Path.cwd() / ".omniforge" / "skills"
        if project_dir.exists():
            for skill_dir in project_dir.iterdir():
                if skill_dir.is_dir():
                    if self._load_skill(skill_dir):
                        discovered += 1

        logger.info(f"Discovered {discovered} skills")
        return discovered

    def _load_skill(self, skill_path: Path) -> bool:
        """Load a single skill from a directory."""
        # Check for SKILL.md first (standard format)
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            skill_file = skill_path / "skill.md"
        if not skill_file.exists():
            skill_file = skill_path / "skill.yaml"
        if not skill_file.exists():
            return False

        try:
            content = skill_file.read_text(encoding="utf-8")
            metadata = self._parse_metadata(content, skill_path, skill_file.suffix)

            skill = Skill(
                metadata=metadata,
                content=content,
                triggers=self._extract_triggers(content),
                instructions=self._extract_instructions(content),
                examples=self._extract_examples(content),
                raw_config=self._extract_config(content),
            )

            self._skills[metadata.name] = skill
            self._installed[metadata.name] = metadata
            logger.debug(f"Loaded skill: {metadata.name} v{metadata.version}")
            return True

        except Exception as e:
            logger.warning(f"Failed to load skill from {skill_path}: {e}")
            return False

    def _parse_metadata(self, content: str, path: Path, suffix: str) -> SkillMetadata:
        """Parse skill metadata from content."""
        metadata = SkillMetadata(
            name=path.parent.name,
            path=str(path),
            installed_at="now",
        )

        # Extract YAML frontmatter if present
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    if isinstance(fm, dict):
                        metadata.name = fm.get("name", metadata.name)
                        metadata.version = fm.get("version", metadata.version)
                        metadata.author = fm.get("author", metadata.author)
                        metadata.description = fm.get("description", metadata.description)
                        metadata.tags = fm.get("tags", [])
                        metadata.dependencies = fm.get("dependencies", [])
                        metadata.platforms = fm.get("platforms", [])
                        metadata.category = fm.get("category", metadata.category)
                        metadata.format = fm.get("format", "markdown")
                except (yaml.YAMLError, KeyError):
                    pass

        return metadata

    def _extract_triggers(self, content: str) -> List[str]:
        """Extract trigger keywords from skill content."""
        triggers = []
        for line in content.split('\n'):
            if 'when:' in line.lower() or 'trigger:' in line.lower():
                trigger = line.split(':', 1)[-1].strip()
                if trigger:
                    triggers.append(trigger)
        return triggers

    def _extract_instructions(self, content: str) -> str:
        """Extract core instructions from SKILL.md."""
        lines = content.split('\n')
        instructions = []
        in_instructions = False

        for line in lines:
            if '## Instructions' in line or '## How to use' in line:
                in_instructions = True
                continue
            elif line.startswith('## ') and in_instructions:
                break
            elif in_instructions:
                instructions.append(line)

        return '\n'.join(instructions).strip()

    def _extract_examples(self, content: str) -> List[Dict[str, str]]:
        """Extract usage examples from skill content."""
        examples = []
        lines = content.split('\n')
        in_examples = False
        current = {}

        for line in lines:
            if '## Examples' in line or '## Usage' in line:
                in_examples = True
                continue
            elif line.startswith('## ') and in_examples:
                break
            elif in_examples:
                if line.startswith('### '):
                    if current:
                        examples.append(current)
                    current = {"title": line[4:].strip()}
                elif line.strip():
                    if 'input' in line.lower() or 'task' in line.lower():
                        current['input'] = line.split(':', 1)[-1].strip()
                    elif 'output' in line.lower() or 'result' in line.lower():
                        current['output'] = line.split(':', 1)[-1].strip()

        if current:
            examples.append(current)

        return examples

    def _extract_config(self, content: str) -> Dict[str, Any]:
        """Extract configuration from SKILL.md."""
        config = {}
        # Look for JSON or YAML configuration blocks
        for block in content.split('```'):
            block = block.strip()
            if block.startswith('json') or block.startswith('yaml'):
                try:
                    config_body = block.split('\n', 1)[-1]
                    if block.startswith('json'):
                        config.update(json.loads(config_body))
                    else:
                        config.update(yaml.safe_load(config_body))
                except Exception:
                    pass
        return config

    def get(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name."""
        skill = self._skills.get(skill_name)
        if not skill:
            # Try fuzzy match
            for name, s in self._skills.items():
                if skill_name.lower() in name.lower():
                    return s
        return skill

    def list_all(self) -> List[Dict[str, Any]]:
        """List all registered skills with metadata."""
        return [
            {
                "name": s.metadata.name,
                "version": s.metadata.version,
                "description": s.metadata.description,
                "category": s.metadata.category,
                "tags": s.metadata.tags,
                "platforms": s.metadata.platforms,
            }
            for s in self._skills.values()
        ]

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for skills by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for skill in self._skills.values():
            score = 0
            if query_lower in skill.metadata.name.lower():
                score += 10
            if query_lower in skill.metadata.description.lower():
                score += 5
            for tag in skill.metadata.tags:
                if query_lower in tag.lower():
                    score += 3
            if score > 0:
                results.append({**skill.metadata.__dict__, "relevance": score})

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results

    def install(self, skill_path: str) -> bool:
        """Install a skill from a file or URL."""
        path = Path(skill_path)

        if path.exists() and path.is_dir():
            return self._load_skill(path)

        # For URLs, download and install
        if skill_path.startswith(("http://", "https://")):
            logger.info(f"Installing skill from URL: {skill_path}")
            # URL installation would download and extract here
            return False  # Placeholder

        return False

    def uninstall(self, skill_name: str) -> bool:
        """Uninstall a skill by name."""
        if skill_name in self._skills:
            del self._skills[skill_name]
            if skill_name in self._installed:
                del self._installed[skill_name]
            logger.info(f"Uninstalled skill: {skill_name}")
            return True
        return False

    def export_for_platform(self, skill_name: str, platform: str) -> Optional[str]:
        """Export a skill for a specific AI platform."""
        skill = self._skills.get(skill_name)
        if not skill:
            return None

        converter = self.PLATFORM_CONVERTERS.get(platform, "SKILL.md")
        return f"# Converted for {platform}\n\n{skill.content}"

    def save_state(self):
        """Save registry state to disk."""
        state = {
            "installed": {
                name: meta.__dict__
                for name, meta in self._installed.items()
            },
            "skill_count": len(self._skills),
        }
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    def load_state(self):
        """Load registry state from disk."""
        if self._state_path.exists():
            try:
                state = json.loads(self._state_path.read_text())
                logger.info(f"Loaded registry state: {state.get('skill_count', 0)} skills")
            except Exception as e:
                logger.warning(f"Failed to load registry state: {e}")