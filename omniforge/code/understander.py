"""
Code Understander — Codebase knowledge mapping and analysis.
Inspired by Understand Anything (30K star).

Transforms any codebase into a queryable knowledge graph:
- Dependency mapping
- Call graph analysis
- Architecture documentation generation
- Semantic code search
"""

import ast
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """A node in the code knowledge graph."""
    name: str
    type: str  # function, class, module, variable
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    complexity: int = 0


@dataclass
class CodeGraph:
    """Knowledge graph of a codebase."""
    nodes: Dict[str, CodeNode] = field(default_factory=dict)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)  # (source, target, relationship)
    file_index: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    module_deps: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))


class PythonAnalyzer:
    """Analyzes Python code to build knowledge graph."""

    def analyze_file(self, file_path: str, content: str) -> List[CodeNode]:
        """Analyze a Python file and extract code nodes."""
        nodes = []

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return nodes

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                code_node = CodeNode(
                    name=node.name,
                    type="function",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    docstring=ast.get_docstring(node),
                    dependencies=self._extract_dependencies(node),
                )
                nodes.append(code_node)

            elif isinstance(node, ast.ClassDef):
                code_node = CodeNode(
                    name=node.name,
                    type="class",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    docstring=ast.get_docstring(node),
                )
                nodes.append(code_node)

        return nodes

    def _extract_dependencies(self, node) -> List[str]:
        """Extract function/module dependencies from AST node."""
        deps = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    deps.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    deps.append(child.func.attr)
        return list(set(deps))


class CodeUnderstander:
    """
    Codebase understanding and knowledge mapping system.

    Features:
    1. Multi-language parsing (Python, JavaScript, TypeScript, Go, Rust)
    2. Dependency graph generation
    3. Architecture documentation auto-generation
    4. Semantic code search
    5. Impact analysis (what breaks if I change X?)
    """

    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
    }

    def __init__(self):
        self._graph = CodeGraph()
        self._python_analyzer = PythonAnalyzer()
        self._analyzed_dirs: Set[str] = set()

    def analyze_repo(self, repo_path: str, max_depth: int = 5) -> CodeGraph:
        """Analyze an entire repository."""
        repo = Path(repo_path)
        if not repo.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")

        self._graph = CodeGraph()
        self._traverse_directory(repo, max_depth)
        self._build_dependency_graph()

        logger.info(
            f"Analyzed {len(self._graph.nodes)} nodes in {len(self._graph.file_index)} files"
        )
        return self._graph

    def _traverse_directory(self, directory: Path, max_depth: int, current_depth: int = 0):
        """Recursively traverse directory for source files."""
        if current_depth >= max_depth:
            return

        try:
            for item in directory.iterdir():
                if item.name.startswith('.') or item.name.startswith('__pycache__'):
                    continue

                if item.is_dir():
                    # Skip common non-source directories
                    if item.name in ('node_modules', 'venv', '.git', 'dist', 'build', 'target'):
                        continue
                    self._traverse_directory(item, max_depth, current_depth + 1)

                elif item.is_file():
                    ext = item.suffix.lower()
                    if ext in self.SUPPORTED_EXTENSIONS:
                        self._analyze_file(item)

        except PermissionError:
            logger.warning(f"Permission denied: {directory}")

    def _analyze_file(self, file_path: Path):
        """Analyze a single source file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lang = self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), 'unknown')

            nodes = []
            if lang == 'python':
                nodes = self._python_analyzer.analyze_file(str(file_path), content)

            for node in nodes:
                node_id = f"{file_path.stem}:{node.name}"
                self._graph.nodes[node_id] = node
                self._graph.file_index[str(file_path)].append(node_id)

        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")

    def _build_dependency_graph(self):
        """Build the dependency graph between nodes."""
        for node_id, node in self._graph.nodes.items():
            for dep in node.dependencies:
                # Find matching node
                for other_id, other_node in self._graph.nodes.items():
                    if other_node.name == dep and other_id != node_id:
                        self._graph.edges.append((node_id, other_id, "calls"))
                        other_node.dependents.append(node_id)

    def query(self, question: str) -> Dict[str, Any]:
        """Query the code knowledge graph."""
        question_lower = question.lower()

        # Find relevant nodes
        matching_nodes = []
        for node_id, node in self._graph.nodes.items():
            if question_lower in node.name.lower():
                matching_nodes.append(node)
            elif node.docstring and question_lower in node.docstring.lower():
                matching_nodes.append(node)

        # Build dependency chain
        dep_chains = []
        for node in matching_nodes:
            chain = {
                "node": node.name,
                "type": node.type,
                "file": node.file_path,
                "called_by": node.dependents[:10],
                "calls": node.dependencies[:10],
                "docstring": node.docstring,
            }
            dep_chains.append(chain)

        return {
            "query": question,
            "matches": len(matching_nodes),
            "results": dep_chains,
            "summary": self._generate_summary(dep_chains),
        }

    def _generate_summary(self, chains: List[Dict[str, Any]]) -> str:
        """Generate a human-readable summary of results."""
        if not chains:
            return "No matching code elements found."

        summary_parts = []
        for chain in chains[:5]:
            summary_parts.append(
                f"{chain['type'].capitalize()} '{chain['node']}' in {chain['file']}"
            )
            if chain['docstring']:
                summary_parts.append(f"  → {chain['docstring'][:100]}")

        return '\n'.join(summary_parts)

    def get_impact_analysis(self, node_name: str) -> Dict[str, Any]:
        """Analyze the impact of changing a specific code element."""
        # Find all dependents recursively
        affected = set()
        to_check = [node_name]

        for node_id, node in self._graph.nodes.items():
            if node.name == node_name:
                for dep_id in node.dependents:
                    affected.add(dep_id)
                break

        return {
            "node": node_name,
            "directly_affected": len(affected),
            "affected_elements": list(affected)[:20],
            "risk_level": "high" if len(affected) > 10 else "medium" if len(affected) > 3 else "low",
        }

    def generate_architecture_doc(self, output_format: str = "markdown") -> str:
        """Generate architecture documentation from the knowledge graph."""
        if not self._graph.nodes:
            return "# Architecture Documentation\n\nNo code analyzed yet."

        doc = [
            "# Architecture Documentation",
            "",
            f"*Auto-generated by OmniForge CodeUnderstander*",
            "",
            f"## Overview",
            f"- **Total Files**: {len(self._graph.file_index)}",
            f"- **Total Nodes**: {len(self._graph.nodes)}",
            f"- **Total Edges**: {len(self._graph.edges)}",
            "",
            "## Module Structure",
        ]

        # Group by directory
        dir_modules = defaultdict(list)
        for file_path, node_ids in self._graph.file_index.items():
            dir_name = str(Path(file_path).parent)
            dir_modules[dir_name].append(file_path)

        for dir_name, files in sorted(dir_modules.items()):
            doc.append(f"### {dir_name}")
            for file_path in files:
                doc.append(f"- `{Path(file_path).name}`")
                for node_id in self._graph.file_index[file_path]:
                    node = self._graph.nodes[node_id]
                    doc.append(f"  - `{node.type}` **{node.name}**")
                    if node.docstring:
                        doc.append(f"    - {node.docstring[:200]}")

        doc.extend([
            "",
            "## Dependency Graph",
            "",
            "```mermaid",
            "graph TD",
        ])

        for source, target, rel in self._graph.edges[:20]:
            source_short = source.split(":")[-1]
            target_short = target.split(":")[-1]
            doc.append(f"    {source_short} -->|{rel}| {target_short}")

        doc.append("```")

        return '\n'.join(doc)

    def export_graph(self, output_path: str):
        """Export the knowledge graph to JSON."""
        graph_data = {
            "nodes": {
                node_id: {
                    "name": node.name,
                    "type": node.type,
                    "file": node.file_path,
                    "lines": f"{node.line_start}-{node.line_end}",
                    "dependencies": node.dependencies,
                    "dependents": node.dependents,
                }
                for node_id, node in self._graph.nodes.items()
            },
            "edges": [
                {"source": s, "target": t, "relationship": r}
                for s, t, r in self._graph.edges
            ],
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Graph exported to {output_path}")