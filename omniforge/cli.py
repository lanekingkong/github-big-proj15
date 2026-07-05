"""
OmniForge CLI — Command-line interface for the OmniForge framework.

Usage:
    omniforge init              # Initialize a new OmniForge project
    omniforge analyze <path>    # Analyze a codebase
    omniforge install <skill>   # Install a skill
    omniforge list skills       # List all skills
    omniforge optimize <text>   # Optimize context
    omniforge memory search <q> # Search persistent memory
    omniforge serve             # Start API server
    omniforge version           # Show version
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from omniforge import __version__
from omniforge.config import OmniForgeConfig
from omniforge.core.engine import OmniForgeEngine


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="omniforge",
        description="OmniForge — Universal Agent Skill Framework",
        epilog="For more info: https://github.com/lanekingkong/omniforge",
    )

    parser.add_argument(
        "--version", action="version",
        version=f"OmniForge v{__version__}"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new OmniForge project")
    init_parser.add_argument("--path", type=str, default=".", help="Project path")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a codebase")
    analyze_parser.add_argument("path", type=str, help="Path to analyze")
    analyze_parser.add_argument("--output", type=str, help="Output file path")
    analyze_parser.add_argument("--query", type=str, help="Query the analyzed codebase")
    analyze_parser.add_argument("--arch-doc", action="store_true", help="Generate architecture doc")

    # install
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_parser.add_argument("skill", type=str, help="Skill name or path")

    # list
    list_parser = subparsers.add_parser("list", help="List resources")
    list_parser.add_argument("resource", choices=["skills", "pipelines", "agents", "memories"],
                             help="Resource type to list")

    # remove (uninstall)
    remove_parser = subparsers.add_parser("remove", help="Remove a resource")
    remove_parser.add_argument("resource", choices=["skill", "memory"],
                               help="Resource type to remove")
    remove_parser.add_argument("name", type=str, help="Resource name")

    # optimize
    optimize_parser = subparsers.add_parser("optimize", help="Optimize context")
    optimize_parser.add_argument("text", type=str, help="Text to optimize")
    optimize_parser.add_argument("--analyze", action="store_true", help="Show analysis only")

    # memory
    memory_parser = subparsers.add_parser("memory", help="Memory operations")
    memory_sub = memory_parser.add_subparsers(dest="memory_command")

    mem_store = memory_sub.add_parser("store", help="Store a memory")
    mem_store.add_argument("key", type=str)
    mem_store.add_argument("value", type=str)

    mem_recall = memory_sub.add_parser("recall", help="Recall memories")
    mem_recall.add_argument("key", type=str)

    mem_search = memory_sub.add_parser("search", help="Search memories")
    mem_search.add_argument("query", type=str)

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--host", type=str, default="127.0.0.1")

    # pipeline
    pipeline_parser = subparsers.add_parser("pipeline", help="Pipeline operations")
    pipeline_sub = pipeline_parser.add_subparsers(dest="pipeline_command")
    pipeline_run = pipeline_sub.add_parser("run", help="Run a pipeline")
    pipeline_run.add_argument("name", type=str, help="Pipeline name")
    pipeline_run.add_argument("--context", type=str, default="{}", help="JSON context")

    return parser


def cmd_init(args, engine: OmniForgeEngine):
    """Initialize a new OmniForge project."""
    project_path = Path(args.path).resolve()
    omniforge_dir = project_path / ".omniforge"

    # Create directory structure
    (omniforge_dir / "skills").mkdir(parents=True, exist_ok=True)
    (omniforge_dir / "pipelines").mkdir(parents=True, exist_ok=True)
    (omniforge_dir / "memory").mkdir(parents=True, exist_ok=True)

    # Save config
    config_path = omniforge_dir / "config.json"
    engine.config.save(str(config_path))

    print(f"Initialized OmniForge project at {omniforge_dir}")
    print(f"Skills directory: {omniforge_dir / 'skills'}")
    print(f"Config: {config_path}")


def cmd_analyze(args, engine: OmniForgeEngine):
    """Analyze a codebase."""
    from omniforge.code.understander import CodeUnderstander

    understander = CodeUnderstander()
    graph = understander.analyze_repo(args.path)

    if args.arch_doc:
        doc = understander.generate_architecture_doc()
        output_path = args.output or "ARCHITECTURE.md"
        Path(output_path).write_text(doc, encoding="utf-8")
        print(f"Architecture documentation written to {output_path}")

    if args.query:
        result = understander.query(args.query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Analyzed {len(graph.nodes)} code elements in {len(graph.file_index)} files")
        print(f"Found {len(graph.edges)} dependency relationships")


def cmd_install(args, engine: OmniForgeEngine):
    """Install a skill."""
    skill_name = args.skill

    # Check if it's a file path
    skill_path = Path(skill_name)
    if skill_path.exists():
        success = engine.install_skill(str(skill_path))
    else:
        # Try installing by name
        success = engine.install_skill(skill_name)

    if success:
        print(f"Skill '{skill_name}' installed successfully")
    else:
        print(f"Failed to install skill '{skill_name}'")


def cmd_list(args, engine: OmniForgeEngine):
    """List resources."""
    if args.resource == "skills":
        skills = engine.list_skills()
        if not skills:
            print("No skills installed")
            return
        print(f"{'Name':<30} {'Version':<10} {'Category':<15}")
        print("-" * 55)
        for skill in skills:
            print(f"{skill['name']:<30} {skill.get('version', '1.0.0'):<10} {skill.get('category', 'general'):<15}")

    elif args.resource == "agents":
        agents = engine._agent_coordinator.list_agents()
        if not agents:
            print("No agents registered")
            return
        for agent in agents:
            print(f"  {agent['name']}: {agent['capability']}")

    elif args.resource == "pipelines":
        orchestrator = engine._agent_coordinator
        print("Pipelines available via orchestrator")


def cmd_remove(args, engine: OmniForgeEngine):
    """Remove a resource."""
    if args.resource == "skill":
        success = engine._skill_registry.uninstall(args.name)
        if success:
            print(f"Skill '{args.name}' removed")
        else:
            print(f"Skill '{args.name}' not found")


def cmd_optimize(args, engine: OmniForgeEngine):
    """Optimize text/context."""
    if args.analyze:
        analysis = engine._context_optimizer.analyze(args.text)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        result = engine.optimize_context(args.text)
        print(result)


def cmd_memory(args, engine: OmniForgeEngine):
    """Memory operations."""
    if args.memory_command == "store":
        memory_id = engine.remember(args.key, args.value)
        print(f"Stored memory: {memory_id}")

    elif args.memory_command == "recall":
        memories = engine.recall(args.key)
        if not memories:
            print(f"No memories found for key '{args.key}'")
            return
        for mem in memories:
            print(f"[{mem['id']}] {mem['value']}")

    elif args.memory_command == "search":
        memories = engine.search_memory(args.query)
        if not memories:
            print(f"No memories found for query '{args.query}'")
            return
        for mem in memories:
            print(f"[{mem['id']}] {mem['key']}: {mem['value']}")


def cmd_serve(args, engine: OmniForgeEngine):
    """Start API server."""
    print(f"Starting OmniForge API server on {args.host}:{args.port}")
    print("API server mode - use 'omniforge serve' for production use")
    # In a full implementation, this would start a FastAPI/Flask server
    print("Server ready (placeholder mode)")


def cmd_pipeline(args, engine: OmniForgeEngine):
    """Pipeline operations."""
    if args.pipeline_command == "run":
        context = json.loads(args.context)
        orchestrator = engine._agent_coordinator
        print(f"Running pipeline '{args.name}' with context: {context}")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize engine
    config = OmniForgeConfig.load(args.config) if args.config else OmniForgeConfig()
    if args.debug:
        config.debug = True
        config.log_level = "DEBUG"

    engine = OmniForgeEngine(config)
    engine.initialize()

    # Route commands
    commands = {
        "init": cmd_init,
        "analyze": cmd_analyze,
        "install": cmd_install,
        "list": cmd_list,
        "remove": cmd_remove,
        "optimize": cmd_optimize,
        "memory": cmd_memory,
        "serve": cmd_serve,
        "pipeline": cmd_pipeline,
    }

    handler = commands.get(args.command)
    if handler:
        try:
            handler(args, engine)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if args.debug:
                raise
    else:
        parser.print_help()

    engine.shutdown()


if __name__ == "__main__":
    main()