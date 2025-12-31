"""Configuration utilities for Knowledge Retrieval Assistant.

This module provides functions to load various configuration files.
"""

import json
import tomllib
from pathlib import Path
from typing import Optional, Union


def load_config(config_path: Union[str, Path]) -> dict:
    """Load configuration file (supports .toml and .json).

    Args:
        config_path: Path to config file (.toml or .json)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file extension is not supported
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".toml":
        with open(path, "rb") as f:
            return tomllib.load(f)
    elif suffix == ".json":
        with open(path, "r") as f:
            return json.load(f)
    else:
        raise ValueError(
            f"Unsupported config file extension: {suffix}\n"
            f"Supported extensions: .toml, .json"
        )


def get_mcp_server_path(server_name: str, config_path: Optional[Path] = None) -> Path:
    """Get the path to a specific MCP server.

    Args:
        server_name: Name of the MCP server (e.g., "markdown-rag", "markdownify")
        config_path: Path to mcp_config.json. Defaults to config/mcp_config.json

    Returns:
        Path to the MCP server directory

    Raises:
        FileNotFoundError: If server not found or path doesn't exist
        KeyError: If server doesn't have serverPath configured
    """
    if config_path is None:
        config_path = Path("config/mcp_config.json")

    mcp_config = load_config(config_path)

    if server_name not in mcp_config.get("mcpServers", {}):
        available = list(mcp_config.get("mcpServers", {}).keys())
        raise FileNotFoundError(
            f"MCP server '{server_name}' not found in configuration.\n"
            f"Available servers: {available}"
        )

    server_config = mcp_config["mcpServers"][server_name]

    if "serverPath" not in server_config:
        raise KeyError(
            f"MCP server '{server_name}' doesn't have 'serverPath' configured.\n"
            f"Please add 'serverPath' to {config_path}"
        )

    server_path = Path(server_config["serverPath"]).expanduser()

    if not server_path.exists():
        raise FileNotFoundError(
            f"MCP server directory not found: {server_path}\n"
            f"Please check your {config_path} configuration"
        )

    return server_path
