"""
Agent Coordinator — Multi-agent orchestration system.
Inspired by agency-agents and multica.

Features:
- Round-robin, priority, and parallel execution modes
- Agent capability matching and routing
- Fallback handling
- Execution timeout and retry
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from omniforge.config import AgentConfig

logger = logging.getLogger(__name__)


class CoordinationStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    PARALLEL = "parallel"


@dataclass
class AgentDefinition:
    """Definition of a registered agent."""
    name: str
    capability: str
    handler: Callable
    priority: int = 0
    max_concurrent: int = 5
    timeout: int = 300
    description: str = ""
    tags: List[str] = field(default_factory=list)


class AgentCoordinator:
    """
    Multi-agent coordination system.

    Routes tasks to appropriate agents based on capability matching,
    supports multiple coordination strategies, and handles failures gracefully.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._agents: Dict[str, AgentDefinition] = {}
        self._executor = ThreadPoolExecutor(max_workers=config.max_agents)
        self._active_tasks: Dict[str, threading.Thread] = {}
        self._task_counter = 0

    def register(self, name: str, capability: str, handler: Callable,
                 priority: int = 0, description: str = "", tags: Optional[List[str]] = None):
        """Register a new agent."""
        agent = AgentDefinition(
            name=name,
            capability=capability,
            handler=handler,
            priority=priority,
            timeout=self.config.timeout_seconds,
            description=description,
            tags=tags or [],
        )
        self._agents[name] = agent
        logger.info(f"Registered agent: {name} ({capability})")

    def unregister(self, name: str) -> bool:
        """Unregister an agent."""
        if name in self._agents:
            del self._agents[name]
            return True
        return False

    def dispatch(self, task: str, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Dispatch a task to the appropriate agent."""
        if agent_type and agent_type in self._agents:
            agent = self._agents[agent_type]
            return self._execute_agent(agent, task)

        # Auto-match agent based on capability
        best_agent = self._match_agent(task)
        if best_agent:
            return self._execute_agent(best_agent, task)

        # Fallback to generalist if configured
        if self.config.fallback_agent and self.config.fallback_agent in self._agents:
            logger.info(f"No specific agent matched, using fallback: {self.config.fallback_agent}")
            return self._execute_agent(
                self._agents[self.config.fallback_agent], task
            )

        return {
            "agent": "none",
            "status": "no_match",
            "output": "No suitable agent found for this task.",
        }

    def _match_agent(self, task: str) -> Optional[AgentDefinition]:
        """Match a task to the most suitable agent."""
        task_lower = task.lower()
        best_score = 0
        best_agent = None

        for agent in self._agents.values():
            score = 0
            capability_lower = agent.capability.lower()

            # Direct capability match
            if capability_lower in task_lower or task_lower in capability_lower:
                score += 20

            # Tag matching
            for tag in agent.tags:
                if tag.lower() in task_lower:
                    score += 10

            # Description relevance
            if agent.description and agent.description.lower() in task_lower:
                score += 5

            # Priority bonus
            score += agent.priority * 2

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent if best_score > 0 else None

    def _execute_agent(self, agent: AgentDefinition, task: str) -> Dict[str, Any]:
        """Execute a task via the specified agent."""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"

        future = self._executor.submit(agent.handler, task)
        start_time = time.time()

        try:
            result = future.result(timeout=agent.timeout)
            elapsed = time.time() - start_time

            return {
                "task_id": task_id,
                "agent": agent.name,
                "status": "success",
                "output": result if isinstance(result, (dict, str)) else str(result),
                "elapsed_seconds": round(elapsed, 2),
            }

        except FutureTimeoutError:
            future.cancel()
            logger.warning(f"Agent '{agent.name}' timed out after {agent.timeout}s")
            return {
                "task_id": task_id,
                "agent": agent.name,
                "status": "timeout",
                "output": f"Task execution timed out after {agent.timeout} seconds",
            }

        except Exception as e:
            logger.error(f"Agent '{agent.name}' execution failed: {e}")
            return {
                "task_id": task_id,
                "agent": agent.name,
                "status": "failed",
                "output": str(e),
            }

    def dispatch_parallel(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Dispatch multiple tasks in parallel."""
        futures = []
        for task_spec in tasks:
            task = task_spec["task"]
            agent_type = task_spec.get("agent")
            agent = self._match_agent(task) if not agent_type else self._agents.get(agent_type)

            if agent:
                futures.append({
                    "agent": agent.name,
                    "task": task,
                    "future": self._executor.submit(agent.handler, task),
                })

        results = []
        for f in futures:
            try:
                result = f["future"].result(timeout=self.config.timeout_seconds)
                results.append({
                    "agent": f["agent"],
                    "task": f["task"][:100],
                    "status": "success",
                    "output": result,
                })
            except Exception as e:
                results.append({
                    "agent": f["agent"],
                    "task": f["task"][:100],
                    "status": "failed",
                    "output": str(e),
                })

        return results

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [
            {
                "name": a.name,
                "capability": a.capability,
                "priority": a.priority,
                "description": a.description,
                "tags": a.tags,
            }
            for a in self._agents.values()
        ]

    def get_agent(self, name: str) -> Optional[AgentDefinition]:
        """Get a specific agent by name."""
        return self._agents.get(name)

    def shutdown(self):
        """Shutdown the agent coordinator."""
        self._executor.shutdown(wait=True)
        logger.info("Agent coordinator shut down")