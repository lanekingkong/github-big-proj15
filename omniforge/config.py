"""
OmniForge Configuration System
Manages all configuration with sensible defaults and environment override.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class MemoryConfig:
    """Persistent memory configuration."""
    backend: str = "sqlite"  # sqlite, chromadb, qdrant
    db_path: str = field(default_factory=lambda: str(
        Path.home() / ".omniforge" / "memory.db"
    ))
    embedding_model: str = "all-MiniLM-L6-v2"
    max_memories: int = 10000
    compression_threshold: int = 500
    eviction_policy: str = "lru"  # lru, lfu, fifo


@dataclass
class ContextConfig:
    """Context optimization configuration."""
    enabled: bool = True
    strategy: str = "semantic"  # semantic, token, hybrid
    compression_ratio: float = 0.6  # Target 60% compression
    max_tokens: int = 128000
    preserve_keywords: bool = True
    chunk_size: int = 512
    overlap: int = 64


@dataclass
class SkillConfig:
    """Skill management configuration."""
    skills_dir: str = field(default_factory=lambda: str(
        Path.home() / ".omniforge" / "skills"
    ))
    auto_discover: bool = True
    hot_reload: bool = True
    max_skill_depth: int = 5
    skill_format: str = "markdown"  # markdown, yaml, json


@dataclass
class DesignConfig:
    """Design taste configuration."""
    enabled: bool = True
    anti_slop: bool = True
    design_system: str = "material"  # material, minimal, brutalist
    color_palette: str = "adaptive"
    accessibility_check: bool = True
    responsive_breakpoints: bool = True


@dataclass
class AgentConfig:
    """Multi-agent orchestration configuration."""
    max_agents: int = 10
    coordination_strategy: str = "round_robin"  # round_robin, priority, parallel
    timeout_seconds: int = 300
    retry_attempts: int = 3
    fallback_agent: Optional[str] = "generalist"


@dataclass
class OmniForgeConfig:
    """Master configuration for OmniForge."""
    project_name: str = "OmniForge"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    memory: MemoryConfig = field(default_factory=MemoryConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    skill: SkillConfig = field(default_factory=SkillConfig)
    design: DesignConfig = field(default_factory=DesignConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)

    def save(self, path: Optional[str] = None) -> str:
        """Save configuration to file."""
        save_path = path or str(Path.home() / ".omniforge" / "config.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        config_dict = {
            "project_name": self.project_name,
            "version": self.version,
            "debug": self.debug,
            "log_level": self.log_level,
            "memory": self._dataclass_to_dict(self.memory),
            "context": self._dataclass_to_dict(self.context),
            "skill": self._dataclass_to_dict(self.skill),
            "design": self._dataclass_to_dict(self.design),
            "agent": self._dataclass_to_dict(self.agent),
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        return save_path

    @classmethod
    def load(cls, path: Optional[str] = None) -> "OmniForgeConfig":
        """Load configuration from file, with fallback to defaults."""
        load_path = path or str(Path.home() / ".omniforge" / "config.json")
        config = cls()

        if os.path.exists(load_path):
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key in ["project_name", "version", "debug", "log_level"]:
                if key in data:
                    setattr(config, key, data[key])

            for section_name in ["memory", "context", "skill", "design", "agent"]:
                if section_name in data:
                    section_config = getattr(config, section_name)
                    for k, v in data[section_name].items():
                        if hasattr(section_config, k):
                            setattr(section_config, k, v)

        return config

    @staticmethod
    def _dataclass_to_dict(obj) -> Dict[str, Any]:
        """Convert dataclass instance to dictionary."""
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            result[field_name] = value
        return result