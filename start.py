#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_DIR = BACKEND_DIR / ".venv"

backend_process = None
frontend_process = None

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
NC = "\033[0m"

CHECK = "✓"
CROSS = "✗"
ARROW = "→"
DOT = "●"

def log_step(step, msg):
    print(f"{BLUE}{step}{NC} {msg}")

def log_success(msg):
    print(f"{GREEN}{CHECK}{NC} {msg}")

def log_error(msg):
    print(f"{RED}{CROSS}{NC} {msg}")

def log_warn(msg):
    print(f"{YELLOW}!{NC} {msg}")

def log_info(msg):
    print(f"{CYAN}{DOT}{NC} {msg}")

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print(f"{CYAN}{'═' * 50}{NC}")
    print(f"{CYAN}║{NC}{BOLD}    中小学走班排课系统 - 本地开发环境    {NC}{CYAN}║{NC}")
    print(f"{CYAN}{'═' * 50}{NC}")
    print()

def print_footer():
    print()
    print(f"{GREEN}{'═' * 50}{NC}")
    print(f"{GREEN}║{NC}  {BOLD}🎉 开发服务器启动成功！{NC}                         {GREEN}║{NC}")
    print(f"{GREEN}{'═' * 50}{NC}")
    print()
    print(f"  {CYAN}前端地址:{NC}    http://localhost:5173")
    print(f"  {CYAN}后端地址:{NC}    http://localhost:8000")
    print(f"  {CYAN}API 文档:{NC}    http://localhost:8000/docs")
    print()
    print(f"  {YELLOW}提示:{NC} 按 {RED}Ctrl+C{NC} 停止所有服务")
    print()
    print(f"{GREEN}{'═' * 50}{NC}")
    print()

def cleanup(signum=None, frame=None):
    global backend_process, frontend_process
    print()
    print(f"\n{YELLOW}正在停止开发服务器...{NC}")
    
    stopped = []
    
    if backend_process and backend_process.poll() is None:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            stopped.append("后端")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            stopped.append("后端")
    
    if frontend_process and frontend_process.poll() is None:
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
            stopped.append("前端")
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            stopped.append("前端")
    
    if stopped:
        print(f"{GREEN}{CHECK}{NC} 已停止: {', '.join(stopped)}")
    
    print(f"{CYAN}再见！{NC}")
    sys.exit(0)

def find_node():
    common_paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs",
        Path.home() / "AppData" / "Roaming" / "npm",
    ]
    
    for p in common_paths:
        node_exe = p / "node.exe"
        if node_exe.exists():
            return str(node_exe)
    return None

def find_npm():
    common_paths = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs",
        Path.home() / "AppData" / "Roaming" / "npm",
    ]
    
    for p in common_paths:
        npm_cmd = p / "npm.cmd"
        if npm_cmd.exists():
            return str(npm_cmd)
    return None

def check_prerequisites():
    print(f"{BOLD}[1/5] 检查系统环境{NC}")
    print()
    
    if sys.version_info < (3, 10):
        log_error(f"Python 版本过低: {sys.version.split()[0]}")
        log_info("需要 Python 3.10 或更高版本")
        sys.exit(1)
    log_success(f"Python {sys.version.split()[0]}")
    
    node_path = find_node()
    if not node_path:
        log_error("未找到 Node.js")
        log_info("请安装 Node.js 18+ : https://nodejs.org/")
        sys.exit(1)
    log_success(f"Node.js 已安装")
    
    npm_path = find_npm()
    if not npm_path:
        log_error("未找到 npm")
        sys.exit(1)
    log_success("npm 已安装")
    
    print()
    return node_path, npm_path

def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def get_venv_pip():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"

def get_venv_uvicorn():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "uvicorn.exe"
    return VENV_DIR / "bin" / "uvicorn"

def ensure_venv():
    print(f"{BOLD}[2/5] 准备后端环境{NC}")
    print()
    
    venv_python = get_venv_python()
    
    if not VENV_DIR.exists():
        log_step("→", "创建 Python 虚拟环境...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log_success("虚拟环境创建完成")
    
    venv_uvicorn = get_venv_uvicorn()
    if not venv_uvicorn.exists():
        log_step("→", "安装后端依赖...")
        venv_pip = get_venv_pip()
        result = subprocess.run(
            [str(venv_pip), "install", "-r", str(BACKEND_DIR / "requirements.txt"), "-q"],
            cwd=str(BACKEND_DIR),
            capture_output=True
        )
        if result.returncode == 0:
            log_success("后端依赖安装完成")
        else:
            log_warn("部分依赖安装可能存在问题")
    else:
        log_success("后端环境已就绪")
    
    print()

def ensure_npm_deps(npm_path):
    print(f"{BOLD}[3/5] 准备前端环境{NC}")
    print()
    
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        log_step("→", "安装前端依赖...")
        result = subprocess.run(
            [npm_path, "install"],
            cwd=str(FRONTEND_DIR),
            capture_output=True
        )
        if result.returncode == 0:
            log_success("前端依赖安装完成")
        else:
            log_warn("部分依赖安装可能存在问题")
    else:
        log_success("前端环境已就绪")
    
    print()

def ensure_dirs():
    dirs = ["data", "backups", "uploads"]
    for d in dirs:
        (BACKEND_DIR / d).mkdir(exist_ok=True)

def start_backend():
    print(f"{BOLD}[4/5] 启动后端服务{NC}")
    print()
    
    global backend_process
    venv_python = get_venv_python()
    env = os.environ.copy()
    env["DEBUG"] = "True"
    
    log_step("→", "启动 FastAPI 服务器...")
    print()
    
    backend_process = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        env=env
    )
    
    log_success(f"后端服务已启动 (PID: {backend_process.pid})")
    print()

def start_frontend(npm_path):
    print(f"{BOLD}[5/5] 启动前端服务{NC}")
    print()
    
    global frontend_process
    node_dir = Path(npm_path).parent
    env = os.environ.copy()
    if "PATH" in env:
        env["PATH"] = str(node_dir) + os.pathsep + env["PATH"]
    else:
        env["PATH"] = str(node_dir)
    
    log_step("→", "启动 Vite 开发服务器...")
    print()
    
    frontend_process = subprocess.Popen(
        [npm_path, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        env=env
    )
    
    log_success(f"前端服务已启动 (PID: {frontend_process.pid})")
    print()

def wait_for_services():
    import urllib.request
    import urllib.error
    
    log_step("→", "等待服务就绪")
    
    max_retries = 30
    backend_ready = False
    frontend_ready = False
    
    for i in range(max_retries):
        if not backend_ready:
            try:
                urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=1)
                backend_ready = True
                print(f"\n{GREEN}{CHECK}{NC} 后端服务就绪", end="")
            except:
                print(f"{YELLOW}.{NC}", end="", flush=True)
        
        if not frontend_ready:
            try:
                urllib.request.urlopen("http://localhost:5173", timeout=1)
                frontend_ready = True
                print(f"\n{GREEN}{CHECK}{NC} 前端服务就绪", end="")
            except:
                if backend_ready:
                    print(f"{YELLOW}.{NC}", end="", flush=True)
        
        if backend_ready and frontend_ready:
            break
        
        time.sleep(0.5)
    
    print()
    
    if not backend_ready:
        log_warn("后端服务启动超时")
    if not frontend_ready:
        log_warn("前端服务启动超时")
    
    return backend_ready and frontend_ready

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    print_header()
    
    node_path, npm_path = check_prerequisites()
    ensure_dirs()
    ensure_venv()
    ensure_npm_deps(npm_path)
    
    start_backend()
    start_frontend(npm_path)
    
    wait_for_services()
    
    print_footer()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
