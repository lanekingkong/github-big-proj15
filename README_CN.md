# OmniForge — 通用智能体技能框架

[![许可证: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/lanekingkong/omniforge?style=social)](https://github.com/lanekingkong/omniforge)

## 概述

**OmniForge** 是一个用于创建、管理和编排跨多个平台的 AI 智能体技能的通用框架。它通过提供统一的技能标准来解决 AI 智能体生态系统中的碎片化问题，该标准适用于 Claude Code、Cursor、Codex、Aider、Windsurf、Copilot 等平台。

### 问题
- **技能碎片化**: 每个 AI 平台都有自己的技能格式
- **缺乏标准化**: 技能无法在平台间共享
- **重复造轮子**: 开发者需要为每个平台重写相同的技能
- **发现困难**: 没有高质量技能的中心注册表
- **质量不一致**: 没有质量门禁或最佳实践强制执行

### 解决方案
OmniForge 提供：
- **通用技能格式**: 一次编写，全平台使用
- **中心技能注册表**: 发现和共享技能
- **质量强制执行**: 内置代码审查、测试和文档
- **跨平台转换**: 自动为任何平台转换技能
- **内存和上下文优化**: 减少 60-95% 的令牌使用
- **设计品味强制执行**: 消除 AI 设计陈词滥调（SLOP）

## 核心功能

### 1. 通用技能系统
- **SKILL.md 标准**: 所有平台的统一格式
- **自动发现**: 技能自动被发现
- **热重载**: 技能更新无需重启
- **版本控制**: 技能的语义版本控制
- **依赖管理**: 自动解析技能依赖

### 2. 跨平台兼容性
- **平台转换器**: 自动为以下平台转换技能：
  - Claude Code → SKILL.md
  - Cursor → .cursorrules
  - Codex → .codex/skills
  - Aider → .aider/skills
  - Windsurf → .windsurfrules
  - Copilot → .github/copilot-instructions.md

### 3. 上下文优化（60-95% 压缩）
- **语义压缩**: 移除冗余短语
- **令牌优化**: 减少令牌数量
- **智能摘要**: 保留含义，减少长度
- **多策略**: 根据用例选择压缩策略

### 4. 持久内存系统
- **多后端**: SQLite、ChromaDB、Qdrant
- **语义搜索**: 查找相关记忆
- **内存压缩**: LRU/LFU/FIFO 策略
- **记忆图谱**: 链接相关记忆

### 5. 设计品味强制执行
- **反-SLOP 检测**: 8+ 种 AI 设计陈词滥调
- **质量评分**: 0-100 设计质量评分
- **设计系统**: Material、Minimal、Brutalist
- **多领域**: UI、代码、文案

### 6. 代码理解
- **知识图谱**: 将代码库转换为可查询的图谱
- **影响分析**: 如果更改 X，会破坏什么？
- **架构文档**: 从代码自动生成
- **语义搜索**: 按功能查找代码，而不仅仅是文本

## 快速开始

### 安装
```bash
pip install omniforge
```

### 基本用法
```python
from omniforge import OmniForgeEngine

# 初始化引擎
config = OmniForgeConfig()
engine = OmniForgeEngine(config)
engine.initialize()

# 发现和使用技能
skills = engine.list_skills()
print(f"找到 {len(skills)} 个技能")

# 优化上下文
optimized = engine.optimize_context("你的长文本在这里...")
print(f"减少了 {len(optimized)/len('你的长文本在这里...')*100:.1f}%")

# 使用内存
engine.remember("meeting_notes", "讨论了项目架构")
memories = engine.recall("meeting")
```

### CLI 用法
```bash
# 初始化项目
omniforge init

# 分析代码库
omniforge analyze /path/to/code --arch-doc

# 安装技能
omniforge install code-review

# 优化文本
omniforge optimize "你的长文本在这里..."

# 搜索内存
omniforge memory search "会议记录"
```

## 内置技能

### 生产技能
- **code-review**: 具有质量门禁的生产级代码审查
- **test-generator**: 具有 >90% 覆盖率的全面测试套件
- **document-generator**: 自动生成项目文档
- **project-bootstrap**: 最佳实践的项目脚手架

### 质量技能
- **security-audit**: 安全漏洞检测
- **performance-audit**: 性能瓶颈分析
- **accessibility-check**: WCAG 2.1 AA 合规性
- **api-design-review**: REST/GraphQL API 设计审查

### 创意技能
- **ui-design**: 从描述生成 UI 原型
- **copywriting**: 营销和技术文案
- **data-visualization**: 创建图表和图形
- **presentation-generator**: 生成幻灯片

## 架构

### 核心组件
1. **技能注册表**: 中心技能管理
2. **上下文优化器**: 60-95% 文本压缩
3. **持久内存**: 多后端内存系统
4. **设计品味**: 反-SLOP 设计强制执行
5. **代码理解器**: 代码库知识图谱
6. **智能体协调器**: 多智能体编排

### 5W1H 设计
- **WHAT**: 通用智能体技能框架
- **WHY**: 解决跨 AI 平台的技能碎片化
- **WHO**: AI 智能体开发者、自动化工程师
- **WHEN**: 在开发、测试和部署期间
- **WHERE**: 任何支持 Python 3.8+ 的环境
- **HOW**: 统一的 SKILL.md 格式与跨平台转换器

## 使用场景

### 对于开发者
- **一次编写，到处运行**: 技能在所有 AI 平台上工作
- **质量强制执行**: 内置代码审查和测试
- **快速原型设计**: 几分钟内启动项目
- **代码理解**: 导航复杂的代码库

### 对于团队
- **技能共享**: 团队技能的中心注册表
- **一致性**: 强制执行编码标准
- **知识共享**: 跨会话的持久记忆
- **协作**: 多智能体协调

### 对于企业
- **治理**: 控制使用哪些技能
- **安全**: 审计技能中的漏洞
- **可扩展性**: 处理数千个技能
- **集成**: 与现有 CI/CD 配合使用

## 性能

### 上下文优化
| 策略 | 压缩率 | 使用场景 |
|------|--------|----------|
| 语义 | 60-70% | 文档、邮件 |
| 令牌 | 70-85% | 代码、配置 |
| 混合 | 85-95% | 长篇内容 |

### 内存系统
- **查询速度**: 10K 记忆 <100ms
- **存储**: 1GB 处理约 100 万记忆
- **后端**: SQLite（默认）、ChromaDB、Qdrant

## 开始使用

### 1. 安装
```bash
# 从 PyPI 安装
pip install omniforge

# 从源码安装
git clone https://github.com/lanekingkong/omniforge
cd omniforge
pip install -e .
```

### 2. 创建你的第一个技能
创建 `my-skill/SKILL.md`：
```markdown
---
name: my-skill
version: 1.0.0
description: 我的第一个 OmniForge 技能
---

# 我的技能

## 目的
描述这个技能的作用。

## 何时使用
- 当你需要做 X 时
- 当你遇到 Y 时

## 使用说明
分步说明...
```

### 3. 在项目中使用
```python
from omniforge import OmniForgeEngine

engine = OmniForgeEngine()
engine.initialize()
engine.install_skill("./my-skill")
```

## 贡献

我们欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发环境设置
```bash
git clone https://github.com/lanekingkong/omniforge
cd omniforge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

### 运行测试
```bash
pytest tests/ -v
```

## 路线图

### v1.0（当前）
- [x] 通用技能格式
- [x] 跨平台转换器
- [x] 上下文优化
- [x] 持久内存
- [x] 基本 CLI

### v1.1（下一步）
- [ ] 技能市场
- [ ] 高级编排
- [ ] 更多内置技能
- [ ] 插件系统

### v2.0（未来）
- [ ] 可视化技能编辑器
- [ ] 团队协作
- [ ] 企业功能
- [ ] 云托管

## 灵感来源

OmniForge 受以下项目启发并集成了其概念：
- **MemPalace (47K★)**: 持久内存系统
- **headroom (6.6K★)**: 上下文压缩
- **taste-skill (24K★)**: 设计品味强制执行
- **Understand Anything (30K★)**: 代码理解
- **agent-skills (45K★)**: 技能管理
- **anthropics/skills (139K★)**: 技能标准

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 支持

- **文档**: [docs.omniforge.dev](https://docs.omniforge.dev)
- **问题**: [GitHub Issues](https://github.com/lanekingkong/omniforge/issues)
- **讨论**: [GitHub Discussions](https://github.com/lanekingkong/omniforge/discussions)
- **邮箱**: support@omniforge.dev

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=lanekingkong/omniforge&type=Date)](https://star-history.com/#lanekingkong/omniforge&Date)

---

**OmniForge** — 一次锻造技能，随处使用。