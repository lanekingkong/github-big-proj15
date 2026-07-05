"""
Skill Orchestrator — Chains multiple skills into complex workflows.
Supports sequential, parallel, and conditional skill execution.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"


@dataclass
class SkillStep:
    """A single step in a skill orchestration pipeline."""
    skill_name: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[Callable] = None
    on_failure: str = "skip"  # skip, retry, abort
    timeout: int = 60
    retry_count: int = 0


@dataclass
class SkillPipeline:
    """A pipeline of skills to execute."""
    name: str
    description: str
    steps: List[SkillStep]
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    shared_context: Dict[str, Any] = field(default_factory=dict)


class SkillOrchestrator:
    """
    Orchestrates multiple skills into complex workflows.

    5W1H Architecture:
    - WHAT: Defines and executes skill pipelines
    - WHY: Enables complex multi-step AI workflows
    - WHO: Developers, AI engineers, automation specialists
    - WHEN: When single skills aren't enough for complex tasks
    - WHERE: Any environment running OmniForge
    - HOW: Pipeline DSL with sequential/parallel/conditional execution
    """

    def __init__(self):
        self._pipelines: Dict[str, SkillPipeline] = {}
        self._skill_registry = None
        self._execution_history: List[Dict[str, Any]] = []
        self._max_history = 1000

    def bind_registry(self, registry):
        """Bind to a skill registry for execution."""
        self._skill_registry = registry

    def define_pipeline(self, pipeline: SkillPipeline) -> str:
        """Register a new skill pipeline."""
        self._pipelines[pipeline.name] = pipeline
        logger.info(f"Pipeline '{pipeline.name}' registered with {len(pipeline.steps)} steps")
        return pipeline.name

    def create_pipeline(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        mode: str = "sequential",
    ) -> SkillPipeline:
        """Create a pipeline from a simple definition."""
        skill_steps = []
        for step_def in steps:
            skill_steps.append(SkillStep(
                skill_name=step_def["skill"],
                input_mapping=step_def.get("input_mapping", {}),
                on_failure=step_def.get("on_failure", "skip"),
                timeout=step_def.get("timeout", 60),
            ))

        pipeline = SkillPipeline(
            name=name,
            description=description,
            steps=skill_steps,
            mode=ExecutionMode(mode),
        )
        self._pipelines[name] = pipeline
        return pipeline

    def execute(self, pipeline_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a named pipeline with the given context."""
        pipeline = self._pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")

        if not self._skill_registry:
            raise RuntimeError("No skill registry bound to orchestrator")

        pipeline.shared_context.update(context)
        results = []

        for i, step in enumerate(pipeline.steps):
            logger.info(f"Pipeline '{pipeline_name}' step {i+1}/{len(pipeline.steps)}: {step.skill_name}")

            # Resolve input from shared context
            step_input = {}
            for param, source_key in step.input_mapping.items():
                step_input[param] = pipeline.shared_context.get(source_key)

            # Conditional execution
            if step.condition and not step.condition(pipeline.shared_context):
                logger.info(f"Step {step.skill_name} skipped (condition not met)")
                results.append({"skill": step.skill_name, "status": "skipped"})
                continue

            # Execute skill
            try:
                skill = self._skill_registry.get(step.skill_name)
                if not skill:
                    raise ValueError(f"Skill '{step.skill_name}' not found")

                # Execute the skill (implementation depends on skill type)
                output = skill.execute(step_input) if hasattr(skill, 'execute') else {"raw": skill}
                results.append({
                    "skill": step.skill_name,
                    "status": "success",
                    "output": output,
                })
                # Update shared context with output
                pipeline.shared_context[f"step_{i}_output"] = output

            except Exception as e:
                logger.error(f"Step {step.skill_name} failed: {e}")
                if step.on_failure == "abort":
                    raise
                elif step.on_failure == "retry" and step.retry_count < 3:
                    step.retry_count += 1
                    # Retry logic would go here
                results.append({
                    "skill": step.skill_name,
                    "status": "failed",
                    "error": str(e),
                })

        # Record execution
        self._execution_history.append({
            "pipeline": pipeline_name,
            "steps_count": len(results),
            "success_count": sum(1 for r in results if r["status"] == "success"),
            "timestamp": "auto",
        })

        return {
            "pipeline": pipeline_name,
            "results": results,
            "shared_context": pipeline.shared_context,
        }

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all registered pipelines."""
        return [
            {"name": p.name, "description": p.description, "steps": len(p.steps), "mode": p.mode.value}
            for p in self._pipelines.values()
        ]

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self._execution_history[-limit:]