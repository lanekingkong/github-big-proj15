"""
OmniForge — Universal Agent Skill Framework
=============================================
The first open-source framework that combines persistent memory,
cross-platform skill standardization, context optimization,
design taste, and multi-agent orchestration into one unified system.

Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "lanekingkong"
__license__ = "MIT"

from omniforge.core.engine import OmniForgeEngine
from omniforge.core.orchestrator import SkillOrchestrator
from omniforge.memory.persistent import PersistentMemory
from omniforge.context.optimizer import ContextOptimizer
from omniforge.design.taste import DesignTaste

__all__ = [
    "OmniForgeEngine",
    "SkillOrchestrator",
    "PersistentMemory",
    "ContextOptimizer",
    "DesignTaste",
]