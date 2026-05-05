#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
BACKEND_PID=""
FRONTEND_PID=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    echo ""
    log_info "正在停止开发服务器..."
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null && log_info "后端已停止"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && log_info "前端已停止"
    log_info "再见！"
    exit 0
}

trap cleanup SIGINT SIGTERM

check_prerequisites() {
    if ! command -v python3 &>/dev/null; then
        log_error "未找到 python3，请先安装 Python 3.10+"
        exit 1
    fi
    if ! command -v node &>/dev/null; then
        log_error "未找到 node，请先安装 Node.js 18+"
        exit 1
    fi
    if ! command -v npm &>/dev/null; then
        log_error "未找到 npm，请先安装 npm"
        exit 1
    fi
}

ensure_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_info "创建 Python 虚拟环境..."
        python3 -m venv "$VENV_DIR"
    fi
    if [ ! -f "$VENV_DIR/bin/uvicorn" ]; then
        log_info "安装后端依赖..."
        . "$VENV_DIR/bin/activate"
        pip install -r "$BACKEND_DIR/requirements.txt" -q
        deactivate
    fi
}

ensure_npm_deps() {
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        log_info "安装前端依赖..."
        cd "$FRONTEND_DIR" && npm install && cd "$ROOT_DIR"
    fi
}

ensure_dirs() {
    mkdir -p "$BACKEND_DIR/data"
    mkdir -p "$BACKEND_DIR/backups"
    mkdir -p "$BACKEND_DIR/uploads"
}

start_backend() {
    log_info "启动后端开发服务器 → ${CYAN}http://localhost:8000${NC}"
    log_info "API 文档 → ${CYAN}http://localhost:8000/docs${NC}"
    cd "$BACKEND_DIR"
    . "$VENV_DIR/bin/activate"
    export DEBUG=True
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd "$ROOT_DIR"
}

start_frontend() {
    log_info "启动前端开发服务器 → ${CYAN}http://localhost:5173${NC}"
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    cd "$ROOT_DIR"
}

wait_for_backend() {
    local max_retries=30
    local count=0
    log_info "等待后端服务就绪..."
    while [ $count -lt $max_retries ]; do
        if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
            log_info "后端服务已就绪！"
            return 0
        fi
        count=$((count + 1))
        sleep 1
    done
    log_warn "后端服务未在预期时间内就绪（可能仍在启动中）"
}

main() {
    echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   中小学走班排课系统 - 本地开发环境   ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
    echo ""

    check_prerequisites
    ensure_dirs
    ensure_venv
    ensure_npm_deps

    start_backend
    start_frontend
    wait_for_backend

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  开发服务器已全部启动！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "  前端:  ${CYAN}http://localhost:5173${NC}"
    echo -e "  后端:  ${CYAN}http://localhost:8000${NC}"
    echo -e "  API文档: ${CYAN}http://localhost:8000/docs${NC}"
    echo -e "  按 ${RED}Ctrl+C${NC} 停止所有服务"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    wait
}

main
