#!/bin/bash
# Knowledge Retrieval Assistant - Setup Script
# This script sets up the development environment for Phase 2

set -e  # Exit on error

echo "========================================="
echo "Knowledge Retrieval Assistant Setup"
echo "========================================="
echo ""

# Move to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# ========================================
# 1. Check Prerequisites
# ========================================
echo "[1/6] Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION < 3.12" | bc)" -eq 1 ]; then
    echo "Error: Python 3.12+ required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION found"

# Check uv
if ! command -v uv &> /dev/null; then
    echo "Warning: uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✓ uv $(uv --version) found"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Warning: Node.js not found. Please install Node.js 18+ for MCP servers"
    echo "  macOS: brew install node"
    echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
else
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo "Warning: Node.js 18+ recommended (found: v$NODE_VERSION)"
    else
        echo "✓ Node.js v$(node --version | cut -d'v' -f2) found"
    fi
fi

echo ""

# ========================================
# 2. Install Python Dependencies
# ========================================
echo "[2/6] Installing Python dependencies..."
uv sync
echo "✓ Python dependencies installed"
echo ""

# ========================================
# 3. Install MCP Servers
# ========================================
echo "[3/6] Installing MCP servers..."

if command -v npm &> /dev/null; then
    echo "Installing mcp-markdown-ragdocs..."
    npm install -g @modelcontextprotocol/server-markdown-ragdocs || echo "  (Continuing...)"

    echo "Installing markdownify-mcp..."
    npm install -g markdownify-mcp || echo "  (Continuing...)"

    echo "✓ MCP servers installed (or will use npx)"
else
    echo "⚠ npm not found - MCP servers will be run via npx when needed"
fi
echo ""

# ========================================
# 4. Create Directory Structure
# ========================================
echo "[4/6] Creating directory structure..."

mkdir -p data/uploads
mkdir -p data/feedback
mkdir -p data/documents/error-handling
mkdir -p data/documents/architecture
mkdir -p data/documents/api-guides
mkdir -p data/documents/business-logic
mkdir -p logs

echo "✓ Directory structure created"
echo ""

# ========================================
# 5. Setup Configuration Files
# ========================================
echo "[5/6] Setting up configuration files..."

# Copy example configs if they don't exist
if [ ! -f config/mcp_config.json ]; then
    if [ -f config/example/mcp_config.json.example ]; then
        cp config/example/mcp_config.json.example config/mcp_config.json
        echo "✓ Created config/mcp_config.json"
    else
        echo "⚠ config/example/mcp_config.json.example not found"
    fi
else
    echo "✓ config/mcp_config.json already exists"
fi

if [ ! -f config/config.toml ]; then
    if [ -f config/example/config.toml.example ]; then
        cp config/example/config.toml.example config/config.toml
        echo "✓ Created config/config.toml"
    else
        echo "⚠ config/example/config.toml.example not found"
    fi
else
    echo "✓ config/config.toml already exists"
fi

# Gemini config is only needed for Phase 3 (API integration)
# Phase 2 uses Gemini CLI with web authentication
if [ -f config/gemini_config.json ]; then
    echo "✓ config/gemini_config.json exists (Phase 3 only)"
else
    echo "ℹ config/gemini_config.json not needed for Phase 2 (will use Gemini CLI with web auth)"
fi

echo ""

# ========================================
# 6. Verify Installation
# ========================================
echo "[6/6] Verifying installation..."

# Check if kra command is available
if uv run kra --help &> /dev/null; then
    echo "✓ kra CLI command is working"
else
    echo "⚠ kra CLI command may not be ready yet"
fi

# Check MCP servers
if command -v npx &> /dev/null; then
    echo "✓ npx available for running MCP servers"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Login to Gemini CLI with web authentication (Phase 2 uses this)"
echo "  2. (Optional) Adjust config/config.toml for search parameters"
echo "  3. Place documents in data/documents/{domain}/ or data/uploads/"
echo "  4. Run: uv run kra --help"
echo ""
echo "Note: Phase 2 uses Gemini CLI with web authentication."
echo "      API key configuration (config/gemini_config.json) is only needed for Phase 3."
echo ""
echo "For development:"
echo "  - Run tests: uv run pytest"
echo "  - Format code: uv run black src/ tests/"
echo "  - Lint code: uv run ruff check src/ tests/"
echo "  - Type check: uv run mypy src/"
echo ""
