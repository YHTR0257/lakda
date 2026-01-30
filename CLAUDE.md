# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LAKDA (LLM-Assisted Knowledge Discovery Application)** - A domain-agnostic RAG system that searches local/cloud documents to answer domain-specific questions with context and citations. Initially designed for error handling support, but applicable to architecture design, business logic, and technical documentation domains.

## Development Commands

### Environment Setup
```bash
# Python version: 3.12 (managed by uv via .python-version)
uv sync                  # Install dependencies from pyproject.toml
```

### Running the Application
```bash
# Phase 2: CLI-based question-answering (not yet implemented)
python -m lakda.main       # Entry point for question input/output
```

### Testing
```bash
# バックエンドユニットテスト（uv使用）
cd backend && uv run pytest tests/

# フロントエンドユニットテスト
cd frontend && npm test

# 統合テスト
uv run pytest tests/integration/

# E2Eテスト
uv run pytest tests/e2e/
```

## Architecture Overview

### Phased Development Approach

**Phase 1 (2025-12-29 - 2026-01-02)**: Design phase - Define system concept, select MCP servers (MCP-Markdown-RAG chosen for hybrid search)

**Phase 2 (2026-01-02 - 2026-02-02)**: Validation & Implementation - Simple sequential architecture
- **Week 1**: Setup MCP-Markdown-RAG via symbolic link, evaluate hybrid search (BM25 + Semantic)
- **Week 2-3**: Integrate MarkItDown library directly (no markdownify-mcp), implement CLI question-answering
- **Week 4**: Implement feedback recording, Phase 3 decision
- **Phase 2 evaluation criteria**: Symbolic link approach viability, domain search accuracy (>80%), configuration flexibility

**Phase 3 (2026-02-02 - 2026-03-31)**: Extension phase (conditional implementation based on Phase 2 results)
- Option A: Continue with MCP-Markdown-RAG (if requirements met)
- Option B: Implement custom MCP server (if specialized features needed)
- Option C: Fork & customize MCP-Markdown-RAG (if partial extensions needed)
- Add API integration (Gemini API)
- Add orchestrator & multi-agent architecture (LangGraph/LangChain)

### Phase 2 Architecture (Current Target)

```
User Input → main.py → Gemini CLI (with MCP-Markdown-RAG) → Output → Feedback Recording
                ↓
         MarkItDown library (direct Python import)
```

**Key Design Decisions**:
- **main.py** acts as a thin orchestration layer, calling external CLI tools via subprocess
- **Gemini CLI** handles question interpretation, retrieval (via MCP-Markdown-RAG), and answer generation in one flow
- **MarkItDown Python library** converts PDF/Word documents to Markdown (imported directly, no MCP server)
- No direct MCP server calls from Python - all MCP interaction happens through Gemini CLI
- Domain management is **implicit** via directory structure (no domains.yml needed in Phase 2)
- **Symbolic link setup**: `~/dev/mcp-servers/MCP-Markdown-RAG/documents` → `data/documents` (works around server.py:59 constraint)

### Domain Management Strategy

**Phase 2: Implicit Domain Management**
```
data/raw/
├── papers/             # 論文ドメイン
├── notes/              # ノートドメイン
└── datasets/           # データセットドメイン
```

- Directory name = Domain name
- Search scope controlled via MCP-Markdown-RAG config.toml
- No explicit domain configuration file needed
- Limitations: No Frontmatter filtering, no dynamic domain weights

**Phase 3: Explicit Domain Management** (only if custom MCP server implemented)
- domains.yml with per-domain weights, filters, and metadata
- Frontmatter-based filtering (tags, categories)
- Dynamic domain addition/deletion

### Module Responsibilities

| Module | Role | Phase 2 Behavior |
|--------|------|------------------|
| `backend/src/lakda/main.py` | Entry point | Orchestrates CLI tools, user I/O, feedback recording |
| `backend/src/lakda/cli/commands.py` | CLI commands | CLI command definitions |
| `backend/src/lakda/api/ask.py` | Ask endpoint | Ask API endpoint (FT06) |
| `backend/src/lakda/api/upload.py` | Upload endpoint | Document upload API (FT02) |
| `backend/src/lakda/api/feedback.py` | Feedback endpoint | Feedback API (FT09) |
| `backend/src/lakda/core/processing/generator.py` | Answer generation | Calls Gemini CLI via subprocess (FT07) |
| `backend/src/lakda/core/processing/interpreter.py` | Question interpretation | Prompt templates for Gemini CLI (FT05) |
| `backend/src/lakda/core/ask/service.py` | Ask service | Ask business logic |
| `backend/src/lakda/core/ask/retrieval.py` | Document retrieval | Document retrieval logic (FT06) |
| `backend/src/lakda/core/documents/converter.py` | Document conversion | markitdown integration (FT03) |
| `backend/src/lakda/core/documents/metadata.py` | Metadata generation | LLM-based Frontmatter generation (FT04) |
| `backend/src/lakda/core/documents/indexer.py` | Document indexing | Index registration |
| `backend/src/lakda/core/feedback/service.py` | Feedback service | Feedback business logic (FT09) |

### Data Storage Structure

```
data/
├── raw/                    # 元ドキュメント
│   ├── papers/                 # 論文
│   ├── notes/                  # ノート
│   └── datasets/               # データセット
├── processed/              # チャンク化・埋め込み済み
│   ├── chunks/                 # チャンクデータ
│   └── metadata/               # メタデータ
├── feedback/               # フィードバックデータ
└── logs/                   # アプリケーションログ（オプション）
```

### Configuration Files

| File | Purpose | Phase |
|------|---------|-------|
| `config/config.toml` | MCP-Markdown-RAG settings (search weights, paths) | Phase 2 |
| `config/gemini_config.json` | Gemini CLI configuration | Phase 2 |
| `config/mcp_config.json` | MCP server settings | Phase 2 |
| `config/domains.yml` | Explicit domain definitions | Phase 3 only (if custom MCP server) |

## Implementation Guidelines

### Phase 2 Setup

**1. Install dependencies**
```bash
uv sync                  # Install Python dependencies
uv add markitdown        # Add MarkItDown library for document conversion
```

**2. Setup MCP-Markdown-RAG symbolic link**
```bash
cd ~/dev/mcp-servers/MCP-Markdown-RAG
ln -s ~/dev/github/YHTR0257/lakda/data/documents documents
```

This works around the `server.py:59` constraint where `target_path = os.path.join(current_working_directory, directory)` assumes documents are in the MCP server's directory.

**3. Configure Gemini CLI with MCP**
Edit `config/mcp_config.json` to point to MCP-Markdown-RAG server, then test:
```bash
gemini chat --mcp config/mcp_config.json -c "Index documents in ./documents directory"
```

### Adding New Documents

1. Place PDF/Word files in `data/raw/{domain}/`
2. Run document converter (uses MarkItDown library): `python -m lakda.core.documents.converter`
3. Generate metadata/Frontmatter via LLM: `python -m lakda.core.documents.metadata`
4. Processed files are stored in `data/processed/chunks/` and `data/processed/metadata/`
5. Run indexer: `python -m lakda.core.documents.indexer`

### Configuring Search Behavior

Edit `config/config.toml`:
```toml
[documents]
root_path = "data/documents"
# Restrict to specific domain:
# paths = ["data/documents/error-handling"]

[search]
semantic_weight = 1.0    # Semantic search weight
keyword_weight = 1.0     # BM25 keyword search weight
```

### Phase 2 → Phase 3 Transition Criteria

Evaluate at end of Phase 2 (2026-02-02):
1. **Symbolic link approach**: Is it viable for production use, or does absolute path support become necessary?
2. **Domain search accuracy**: Is implicit directory-based domain management sufficient? (Target: >80% Top 3 hit rate)
3. **Configuration flexibility**: Can config.toml settings meet all requirements?
4. **Missing features**: Are Frontmatter filters, domain weights, or custom scoring needed?

**Decision Tree**:
- ✅ All criteria met → **Option A**: Continue with MCP-Markdown-RAG
- ⚠️ Only absolute path needed → **Option C**: Fork MCP-Markdown-RAG, modify server.py:59 (1 line, 1 day)
- ❌ Custom features required → **Option B**: Implement custom RAG (MarkItDown + sentence-transformers + FAISS, 2-3 weeks)

## Important Constraints & Design Principles

### Phase 2 Constraints
- **No direct Python MCP client**: All MCP interaction through Gemini CLI or other CLI tools
- **Sequential processing**: No parallel agent orchestration (LangGraph/LangChain reserved for Phase 3)
- **Implicit domain management**: No domains.yml - rely on directory structure
- **Local feedback storage**: Use local files, not database

### Phase 3 Features (Conditional)
Only implement if Phase 2 evaluation requires them:
- Multi-agent orchestration (FT12, FT13)
- External API integration beyond Gemini CLI (FT11)
- Custom MCP server with Frontmatter filtering (FT06)
- Explicit domain management with weights (FT10)

### Technology Stack
- **Python**: 3.12 (managed via uv)
- **Type Safety (Backend)**: Pydantic v2 (runtime validation + static type hints)
- **Type Safety (Frontend)**: TypeScript (strict mode)
- **Dependency Management**: uv (pyproject.toml + uv.lock)
- **MCP Servers**: MCP-Markdown-RAG (hybrid search)
- **LLM Interface**: Gemini CLI (Phase 2), Gemini API (Phase 3)
- **Vector DB**: Auto-managed by MCP-Markdown-RAG in `data/.rag_cache/`
- **Orchestration** (Phase 3 only): LangGraph or LangChain

## Project Goals & Success Criteria

| Goal | Target | Measurement |
|------|--------|-------------|
| Reduce domain knowledge access time | 80% reduction | Time from question to relevant information |
| Resolve ambiguous questions | 50% reduction in retries | Number of follow-up questions needed |
| Multi-domain knowledge sharing | 3+ domains operational | System supports multiple knowledge bases |

## Risk Mitigation

**High Risk**: MCP-Markdown-RAG doesn't meet requirements
- Mitigation: Early Phase 2 evaluation (week 1), buffer 2-3 weeks for Phase 3 custom implementation

**Medium Risk**: Document quality is insufficient
- Mitigation: Prepare 3-5 sample documents per domain before Phase 2, establish documentation guidelines

**Low Risk**: Timeline conflicts (thesis, job hunting)
- Mitigation: Focus on MVP in Phase 2, Phase 3 custom implementation only if absolutely necessary
