.PHONY: help install dev backend frontend stop clean migrate db-reset lint

PYTHON ?= python3
VENV ?= .venv
BACKEND_DIR := backend
FRONTEND_DIR := frontend

help:
	@echo "走班排课系统 - 本地开发命令"
	@echo ""
	@echo "  make install       安装前后端依赖"
	@echo "  make dev           一键启动前后端开发服务器"
	@echo "  make backend       仅启动后端开发服务器"
	@echo "  make frontend      仅启动前端开发服务器"
	@echo "  make stop          停止所有开发服务器"
	@echo "  make migrate       运行数据库迁移"
	@echo "  make db-reset      重置数据库（删除并重建）"
	@echo "  make lint          运行代码检查"
	@echo "  make clean         清理生成文件"

install:
	@echo "=== 安装后端依赖 ==="
	cd $(BACKEND_DIR) && $(PYTHON) -m venv $(VENV) && . $(VENV)/bin/activate && pip install -r requirements.txt
	@echo "=== 安装前端依赖 ==="
	cd $(FRONTEND_DIR) && npm install
	@echo "=== 依赖安装完成 ==="

dev:
	@bash dev.sh

backend:
	@echo "=== 启动后端开发服务器 (http://localhost:8000) ==="
	cd $(BACKEND_DIR) && . $(VENV)/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "=== 启动前端开发服务器 (http://localhost:5173) ==="
	cd $(FRONTEND_DIR) && npm run dev

stop:
	@echo "=== 停止开发服务器 ==="
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "已停止"

migrate:
	cd $(BACKEND_DIR) && . $(VENV)/bin/activate && alembic upgrade head

db-reset:
	@echo "=== 重置数据库 ==="
	rm -f $(BACKEND_DIR)/data/scheduling.db
	cd $(BACKEND_DIR) && . $(VENV)/bin/activate && alembic upgrade head
	@echo "数据库已重置"

lint:
	cd $(FRONTEND_DIR) && npm run lint

clean:
	rm -rf $(BACKEND_DIR)/$(VENV) $(BACKEND_DIR)/__pycache__ $(BACKEND_DIR)/data
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
