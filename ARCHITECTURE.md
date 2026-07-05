# OmniForge Architecture Documentation

## Overview
OmniForge is a universal framework for creating, managing, and orchestrating AI agent skills across multiple platforms. It solves the fragmentation problem in the AI agent ecosystem by providing a unified skill standard.

## System Architecture

### Core Components

#### 1. Skill Registry (`omniforge/skills/registry.py`)
- **Purpose**: Central skill management and discovery
- **Key Features**:
  - Auto-discovers skills from multiple directories
  - Parses SKILL.md format with YAML frontmatter
  - Supports semantic versioning for skills
  - Cross-platform conversion (Claude Code, Cursor, Codex, etc.)
  - Hot reload capability
- **Data Structures**:
  - `SkillMetadata`: Name, version, author, description, tags
  - `Skill`: Full skill instance with content and configuration
  - `SkillRegistry`: Central registry with search and management

#### 2. Context Optimizer (`omniforge/context/optimizer.py`)
- **Purpose**: Reduce token usage by 60-95% through intelligent compression
- **Strategies**:
  - **Semantic compression**: Remove redundant phrases, filler words
  - **Token compression**: Optimize for token count reduction
  - **Hybrid strategy**: Combine both approaches
- **Components**:
  - `TokenEstimator`: Estimate token count for text
  - `SemanticCompressor`: Identify and remove semantic redundancy
  - `ContextOptimizer`: Main orchestrator with multiple strategies

#### 3. Persistent Memory (`omniforge/memory/persistent.py`)
- **Purpose**: Multi-backend memory system with semantic search
- **Backends**:
  - SQLite (default, lightweight)
  - ChromaDB (vector similarity search)
  - Qdrant (production-grade vector database)
- **Features**:
  - Three-tier memory system (short/medium/long-term)
  - Memory compression and eviction policies (LRU/LFU/FIFO)
  - Memory graph linking for associative recall
  - Semantic search using embeddings

#### 4. Design Taste (`omniforge/design/taste.py`)
- **Purpose**: Enforce design quality and prevent AI design clichés (SLOP)
- **Detection Categories**:
  - Generic placeholder text
  - Overly verbose explanations
  - Unnecessary disclaimers
  - Repetitive patterns
  - Lack of concrete examples
- **Design Systems**:
  - Material: Google's design language
  - Minimal: Clean, focused design
  - Brutalist: Raw, functional design
- **Scoring**: 0-100 quality score with detailed feedback

#### 5. Code Understander (`omniforge/code/understander.py`)
- **Purpose**: Transform codebases into queryable knowledge graphs
- **Supported Languages**: Python, JavaScript, TypeScript, Go, Rust, Java
- **Features**:
  - AST parsing for dependency analysis
  - Call graph generation
  - Impact analysis (what breaks if I change X?)
  - Architecture documentation auto-generation
  - Semantic code search
- **Data Structures**:
  - `CodeNode`: Function, class, or module
  - `CodeGraph`: Complete knowledge graph

#### 6. Agent Coordinator (`omniforge/agents/coordinator.py`)
- **Purpose**: Multi-agent task orchestration
- **Coordination Strategies**:
  - Round-robin: Equal distribution
  - Priority: Based on agent priority
  - Parallel: Concurrent execution
- **Features**:
  - Agent capability matching
  - Fallback handling
  - Timeout and retry mechanisms
  - Execution statistics

#### 7. Core Engine (`omniforge/core/engine.py`)
- **Purpose**: Central orchestrator integrating all components
- **Features**:
  - Lazy initialization of subsystems
  - Context manager for resource cleanup
  - Unified API for all functionality
  - Pipeline execution with monitoring

### Data Flow

```
User Request
    ↓
CLI / API
    ↓
OmniForgeEngine
    ├── Skill Registry (skill lookup)
    ├── Context Optimizer (compress input)
    ├── Persistent Memory (recall context)
    ├── Design Taste (quality check)
    ├── Code Understander (if code-related)
    └── Agent Coordinator (task execution)
        ↓
Result (optimized, quality-checked)
```

### Configuration System

#### `OmniForgeConfig` (`omniforge/config.py`)
- **MemoryConfig**: Backend, storage path, compression settings
- **ContextConfig**: Optimization strategy, target compression ratio
- **SkillConfig**: Directories, auto-discovery, platform preferences
- **DesignConfig**: Quality thresholds, design system preferences
- **AgentConfig**: Coordination strategy, timeout, retry settings

### Built-in Skills

#### Production Skills
1. **code-review** (`skills/builtin/code-review/`)
   - Production-grade code review with quality gates
   - Security, error handling, testing, performance checks
   - Structured feedback with severity levels

2. **test-generator** (`skills/builtin/test-generator/`)
   - Comprehensive test suites with >90% coverage
   - Property-based testing, edge case coverage
   - CI pipeline integration

3. **document-generator** (`skills/builtin/document-generator/`)
   - Auto-generates project documentation
   - README, API docs, architecture docs, contributor guides
   - Quality standards enforcement

4. **project-bootstrap** (`skills/builtin/project-bootstrap/`)
   - Best-practice project scaffolding
   - Tooling setup (linting, formatting, testing)
   - CI/CD pipeline configuration

### Cross-Platform Compatibility

#### Platform Converters
- **Claude Code**: `SKILL.md` → Native skill format
- **Cursor**: `.cursorrules` format
- **Codex**: `.codex/skills` directory structure
- **Aider**: `.aider/skills` with specific formatting
- **Windsurf**: `.windsurfrules` format
- **Copilot**: `.github/copilot-instructions.md`

### Performance Characteristics

#### Context Optimization
| Strategy | Compression | Use Case | Time Complexity |
|----------|-------------|----------|-----------------|
| Semantic | 60-70% | Documentation | O(n) |
| Token | 70-85% | Code/Config | O(n log n) |
| Hybrid | 85-95% | Long-form | O(n²) worst case |

#### Memory System
- **Query Speed**: <100ms for 10K memories (SQLite)
- **Storage Efficiency**: ~1KB per memory with compression
- **Scalability**: Linear scaling with memory count

#### Skill Registry
- **Discovery**: O(n) where n = number of skill directories
- **Lookup**: O(1) average case with hash table
- **Conversion**: O(m) where m = skill content length

### Security Considerations

#### Input Validation
- All user inputs are validated and sanitized
- File paths are restricted to prevent directory traversal
- Skill content is scanned for malicious patterns

#### Memory Isolation
- Each project gets isolated memory storage
- No cross-project memory leakage
- Encryption for sensitive memories

#### Skill Sandboxing
- Skills run in restricted environment
- Network access controlled by configuration
- File system access limited to project directories

### Error Handling

#### Graceful Degradation
- If a component fails, others continue working
- Fallback strategies for critical operations
- Detailed error logging with context

#### Recovery Mechanisms
- Automatic retry for transient failures
- State persistence for crash recovery
- Health checks for all components

### Monitoring and Observability

#### Metrics Collection
- Request latency per component
- Memory usage statistics
- Skill execution success rates
- Compression ratio tracking

#### Logging
- Structured JSON logging
- Configurable log levels
- Rotating log files
- Performance tracing

### Deployment Considerations

#### Single Machine
- All components in one process
- SQLite for memory storage
- File-based skill storage

#### Distributed
- Microservices architecture
- Redis for shared memory
- Object storage for skills
- Load balancing for agents

#### Cloud Native
- Containerized deployment
- Kubernetes orchestration
- Auto-scaling based on load
- Managed database services

### Future Extensions

#### Plugin System
- Third-party skill providers
- Custom memory backends
- Additional design systems
- New platform converters

#### Marketplace Integration
- Skill discovery and rating
- Automated skill updates
- Quality verification
- Usage statistics

#### Advanced Features
- Visual skill editor
- Team collaboration
- Enterprise SSO
- Compliance reporting

## Conclusion

OmniForge provides a comprehensive solution to the AI agent skill fragmentation problem. By offering a unified skill format, cross-platform compatibility, and built-in quality enforcement, it enables developers to create skills once and use them everywhere. The modular architecture allows for easy extension and customization while maintaining high performance and reliability.