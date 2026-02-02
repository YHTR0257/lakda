"""pytest設定ファイル"""

import pytest


def pytest_addoption(parser):
    """カスタムコマンドラインオプションを追加"""
    parser.addoption(
        "--run-llm-api",
        action="store_true",
        default=False,
        help="LLM APIを使用する統合テストを実行する",
    )


def pytest_configure(config):
    """カスタムマーカーを登録"""
    config.addinivalue_line(
        "markers", "llm_api: LLM APIを使用する統合テスト（--run-llm-apiで実行）"
    )


def pytest_collection_modifyitems(config, items):
    """llm_apiマーカーが付いたテストをデフォルトでスキップ"""
    if config.getoption("--run-llm-api"):
        # --run-llm-apiが指定された場合はスキップしない
        return

    skip_llm_api = pytest.mark.skip(reason="LLM APIテストをスキップ（--run-llm-apiで実行）")
    for item in items:
        if "llm_api" in item.keywords:
            item.add_marker(skip_llm_api)
