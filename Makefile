BACKEND_DIR := backend
BACKEND_SVC := backend
FRONTEND_SVC := frontend

# SVC: backend (default) | frontend
SVC ?= $(BACKEND_SVC)

# ENV: dev (default) | prod
ENV ?= dev

ifeq ($(ENV),dev)
  COMPOSE := docker compose \
    -f envs/docker/docker-compose.yml \
    -f envs/docker/docker-compose.override.yml \
    --env-file .env
else ifeq ($(ENV),prod)
  COMPOSE := docker compose \
    -f envs/docker/docker-compose.prod.yml \
    --env-file .env
else
  COMPOSE := docker compose --env-file .env
endif

# ENV バリデーション（実行時チェック）
.PHONY: _check-env
_check-env:
	@[ "$(ENV)" = "dev" ] || [ "$(ENV)" = "prod" ] || \
	  { echo "Error: ENV は dev または prod を指定してください"; exit 1; }

# =============================================================================
# Docker 操作（ENV=dev [default] | prod）
# =============================================================================

.PHONY: up
up: _check-env
	$(COMPOSE) up -d --build

.PHONY: down
down: _check-env
	$(COMPOSE) down

.PHONY: logs
logs: _check-env
	$(COMPOSE) logs -f

.PHONY: ps
ps: _check-env
	$(COMPOSE) ps

.PHONY: exec
exec: _check-env
	$(COMPOSE) exec $(SVC) /bin/bash

# =============================================================================
# 通常テスト（ローカル実行・モックのみ・実API呼び出しなし）
# =============================================================================

.PHONY: test
test:
	cd $(BACKEND_DIR) && uv run pytest tests/ -v

# =============================================================================
# 実API統合テスト（Docker コンテナ内で実行）
#
# 使い方:
#   make test-llm-api                    # 全ての実APIテスト
#   make test-llm-api PROVIDER=llamacpp  # llama.cpp のみ
#   make test-llm-api PROVIDER=google    # Google GenAI のみ
#   make test-llm-api SUITE=connect      # 接続確認のみ
#
# 前提: make up でコンテナが起動していること
# =============================================================================

.PHONY: test-llm-api
test-llm-api: _check-env
	@if [ -n "$(PROVIDER)" ]; then \
	  if [ "$(PROVIDER)" = "llamacpp" ]; then \
	    target="tests/llm/test_llamaindex_real.py::TestLlamaCppLlamaIndexReal"; \
	  elif [ "$(PROVIDER)" = "google" ]; then \
	    target="tests/llm/test_llamaindex_real.py::TestGoogleGenAILlamaIndexReal"; \
	  else \
	    echo "Error: PROVIDER は llamacpp または google を指定してください"; exit 1; \
	  fi; \
	elif [ -n "$(SUITE)" ]; then \
	  if [ "$(SUITE)" = "connect" ]; then \
	    target="tests/llm/test_connect_2_model.py"; \
	  else \
	    echo "Error: SUITE は connect を指定してください"; exit 1; \
	  fi; \
	else \
	  target="tests/llm/"; \
	fi; \
	$(COMPOSE) exec $(BACKEND_SVC) uv run pytest $$target --run-llm-api -v

# =============================================================================
# DB統合テスト（Docker コンテナ内で実行）
#
# 使い方:
#   make test-db                         # Neo4j 接続テストを実行
#
# 前提: make up でコンテナが起動していること
# =============================================================================

.PHONY: test-db
test-db: _check-env
	$(COMPOSE) exec $(BACKEND_SVC) uv run pytest tests/utils/test_connect_db.py --run-db -v

.PHONY: test-index
test-index: _check-env
	$(COMPOSE) exec $(BACKEND_SVC) uv run pytest tests/services/index/ --run-db --run-llm-api -v

# =============================================================================
# ヘルプ
# =============================================================================

.PHONY: help
help:
	@echo "使用可能なターゲット:"
	@echo ""
	@echo "  Docker 操作（ENV=dev [default] | prod）"
	@echo "    make up                             コンテナをビルド・起動"
	@echo "    make up ENV=prod                    本番環境で起動"
	@echo "    make down                           コンテナを停止・削除"
	@echo "    make down ENV=prod                  本番環境を停止"
	@echo "    make logs                           ログをフォロー"
	@echo "    make ps                             コンテナ一覧を表示"
	@echo "    make exec                           backendコンテナ内にシェルで入る"
	@echo "    make exec SVC=frontend              frontendコンテナ内にシェルで入る"
	@echo ""
	@echo "  通常テスト（ローカル・モックのみ）"
	@echo "    make test                           全ユニットテストを実行"
	@echo ""
	@echo "  実API統合テスト（要: make up）"
	@echo "    make test-llm-api                   全ての実APIテスト"
	@echo "    make test-llm-api PROVIDER=llamacpp llama.cpp テストのみ"
	@echo "    make test-llm-api PROVIDER=google   Google GenAI テストのみ"
	@echo "    make test-llm-api SUITE=connect     接続確認テストのみ"
	@echo ""
	@echo "  DB統合テスト（要: make up）"
	@echo "    make test-db                        Neo4j 接続テストを実行"
	@echo "    make test-index                     インデックスサービス統合テストを実行"
	@echo ""
	@echo "  前提条件（実APIテスト）:"
	@echo "    llama.cpp       ホスト上で起動（host.docker.internal:11406/11407）"
	@echo "    GOOGLE_API_KEY  .env に設定"
	@echo "    Neo4j           make up で起動（lakda-database コンテナ）"
