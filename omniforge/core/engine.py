"""
OmniForge Core Engine
The central orchestrator that ties together memory, skills,
context optimization, design taste, and multi-agent coordination.
"""

import logging
from typing import Optional, Dict, Any, List

from omniforge.config import OmniForgeConfig
from omniforge.memory.persistent import PersistentMemory
from omniforge.context.optimizer import ContextOptimizer
from omniforge.design.taste import DesignTaste
from omniforge.skills.registry import SkillRegistry
from omniforge.agents.coordinator import AgentCoordinator

logger = logging.getLogger(__name__)


class OmniForgeEngine:
    """
    The central engine of OmniForge.

    Integrates:
    - Persistent memory for cross-session learning
    - Context optimization for token efficiency
    - Design taste for anti-SLOP output quality
    - Skill registry for cross-platform skill management
    - Agent coordination for multi-agent orchestration
    """

    def __init__(self, config: Optional[OmniForgeConfig] = None):
        self.config = config or OmniForgeConfig()
        self._setup_logging()

        # Core subsystems (lazy initialization)
        self._memory: Optional[PersistentMemory] = None
        self._context_optimizer: Optional[ContextOptimizer] = None
        self._design_taste: Optional[DesignTaste] = None
        self._skill_registry: Optional[SkillRegistry] = None
        self._agent_coordinator: Optional[AgentCoordinator] = None

        self._initialized = False

    def _setup_logging(self):
        """Configure logging based on config."""
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    def initialize(self) -> "OmniForgeEngine":
        """Initialize all subsystems."""
        if self._initialized:
            return self

        logger.info(f"Initializing OmniForge v{self.config.version}")

        # Initialize memory system
        self._memory = PersistentMemory(self.config.memory)
        self._memory.initialize()

        # Initialize context optimizer
        self._context_optimizer = ContextOptimizer(self.config.context)

        # Initialize design taste
        self._design_taste = DesignTaste(self.config.design)

        # Initialize skill registry
        self._skill_registry = SkillRegistry(self.config.skill)
        self._skill_registry.discover_skills()

        # Initialize agent coordinator
        self._agent_coordinator = AgentCoordinator(self.config.agent)

        self._initialized = True
        logger.info("OmniForge engine fully initialized")
        return self

    def shutdown(self):
        """Gracefully shutdown all subsystems."""
        if self._memory:
            self._memory.close()
        if self._skill_registry:
            self._skill_registry.save_state()
        self._initialized = False
        logger.info("OmniForge engine shut down")

    # ---- Memory API ----

    def remember(self, key: str, value: Any, metadata: Optional[Dict] = None) -> str:
        """Store a memory persistently."""
        self._ensure_initialized()
        return self._memory.store(key, value, metadata)

    def recall(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories by key."""
        self._ensure_initialized()
        return self._memory.retrieve(key, limit)

    def forget(self, key: str) -> bool:
        """Remove memories by key."""
        self._ensure_initialized()
        return self._memory.remove(key)

    def search_memory(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search across all memories."""
        self._ensure_initialized()
        return self._memory.semantic_search(query, top_k)

    # ---- Context Optimization API ----

    def optimize_context(self, content: str, preserve_sections: Optional[List[str]] = None) -> str:
        """Compress and optimize context while preserving meaning."""
        self._ensure_initialized()
        return self._context_optimizer.optimize(content, preserve_sections)

    def estimate_tokens(self, content: str) -> int:
        """Estimate token count for content."""
        return self._context_optimizer.estimate_tokens(content)

    # ---- Design Taste API ----

    def taste_check(self, content: str, content_type: str = "ui") -> Dict[str, Any]:
        """Check content against design taste rules (anti-SLOP)."""
        self._ensure_initialized()
        return self._design_taste.evaluate(content, content_type)

    def apply_design_rules(self, content: str, design_system: Optional[str] = None) -> str:
        """Apply design taste rules to improve output quality."""
        self._ensure_initialized()
        return self._design_taste.apply(content, design_system)

    # ---- Skill API ----

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all registered skills."""
        self._ensure_initialized()
        return self._skill_registry.list_all()

    def load_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific skill by name."""
        self._ensure_initialized()
        return self._skill_registry.get(skill_name)

    def install_skill(self, skill_path: str) -> bool:
        """Install a skill from a file or URL."""
        self._ensure_initialized()
        return self._skill_registry.install(skill_path)

    # ---- Agent API ----

    def dispatch(self, task: str, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Dispatch a task to the appropriate agent."""
        self._ensure_initialized()
        return self._agent_coordinator.dispatch(task, agent_type)

    def register_agent(self, name: str, capability: str, handler: callable):
        """Register a custom agent."""
        self._ensure_initialized()
        self._agent_coordinator.register(name, capability, handler)

    # ---- Pipeline API (Combined workflows) ----

    def process(self, task: str, use_memory: bool = True,
                use_context_opt: bool = True, use_taste: bool = True) -> Dict[str, Any]:
        """
        Full pipeline: memory-enhanced, context-optimized,
        taste-checked task processing.
        """
        self._ensure_initialized()

        result = {"task": task, "steps": []}

        # Step 1: Memory-enhanced context
        if use_memory:
            memories = self._memory.semantic_search(task, top_k=5)
            if memories:
                result["steps"].append({"stage": "memory", "found": len(memories)})
                result["memories"] = memories

        # Step 2: Context optimization
        if use_context_opt:
            result["steps"].append({"stage": "context_opt", "status": "ready"})

        # Step 3: Dispatch to agents
        dispatch_result = self._agent_coordinator.dispatch(task)
        result["steps"].append({"stage": "dispatch", "agent": dispatch_result.get("agent")})
        result["output"] = dispatch_result.get("output", "")

        # Step 4: Design taste check
        if use_taste:
            taste_result = self._design_taste.evaluate(
                result["output"], content_type="general"
            )
            result["steps"].append({"stage": "taste_check", "score": taste_result.get("score", 0)})
            result["taste"] = taste_result

        # Step 5: Store in memory
        if use_memory:
            self._memory.store(
                f"task:{task[:50]}",
                result,
                {"type": "task_result", "timestamp": "auto"}
            )

        return result

    def _ensure_initialized(self):
        """Ensure engine is initialized before use."""
        if not self._initialized:
            self.initialize()

    def __enter__(self):
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False