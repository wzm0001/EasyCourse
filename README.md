# 中小学走班排课系统 (EasyCourse)

一套面向中小学的智能走班排课管理系统，支持多学校 SaaS 模式，提供自动排课、手动拖拽排课、冲突检测、课表导出等核心功能。

## 功能特性

### 🏫 多学校管理（SaaS）
- **三级角色体系**：超级管理员 → 学校管理员 → 教师
- 学校自主注册，超级管理员审批后激活
- 多学校数据隔离，互不影响

### 📅 学期与时段管理
- 创建和管理学期，支持学期归档
- 灵活配置早读、正课、晚自习时段
- 内置时段模板，一键应用

### 📋 基础数据管理
- 年级、班级、课程（必修/选修）、教师、教室等全面管理
- 教学安排：关联教师、课程与班级
- 支持 Excel 模板导入导出，批量处理数据

### 🔒 排课约束配置
支持多种约束条件，确保排课合理性：
- 教师不可用时段 / 教室不可用时段
- 每日最大课时限制
- 课程分散、不连排、最小间隔
- 固定位置约束
- 约束优先级：强制 / 高 / 中 / 低

### 📊 智能排课
- **自动排课**：基于教学安排和约束条件，一键生成完整课表
- **手动拖拽排课**：可视化拖拽界面，自由调整课程安排
- **实时冲突检测**：教师冲突、教室冲突、班级冲突、约束冲突即时提醒
- **排课锁定机制**：防止多人同时编辑造成冲突
- 单元格锁定 / 解锁、课程交换、拖动放置

### 📺 课表查看
- 班级课表、教师课表、年级课表、教室课表多视角查看
- 按日/周维度展示，清晰直观

### 📤 导出功能
- 课表导出为 Excel 文件
- 课表导出为 PDF 文件
- 支持自定义导出内容

### 🔔 通知与日志
- 通知中心：注册审批、排课完成等消息推送
- 系统日志：操作日志、登录日志、排课日志、系统日志全方位记录

### 💾 数据备份
- 手动备份与自动备份
- 支持备份文件下载和恢复

### 🧭 排课向导
四步引导式流程：学期设置 → 基础数据 → 排课 → 导出课表，降低使用门槛

### 🌓 深色模式
支持明亮 / 深色主题切换，适配不同使用环境

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| **Python 3.10+** | 开发语言 |
| **FastAPI** | Web 框架 |
| **SQLAlchemy 2.0** (异步) | ORM |
| **Alembic** | 数据库迁移 |
| **SQLite / MySQL** | 数据库（开发/生产） |
| **Redis** | 缓存与会话管理 |
| **JWT (python-jose)** | 用户认证 |
| **Pydantic v2** | 数据校验 |
| **openpyxl** | Excel 导入导出 |
| **ReportLab** | PDF 生成 |
| **APScheduler** | 定时任务（自动备份） |

### 前端
| 技术 | 用途 |
|------|------|
| **React 19** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Vite** | 构建工具 |
| **Ant Design 5 + Ant Design Pro Components** | UI 组件库 |
| **React Router v6** | 路由管理 |
| **Zustand** | 状态管理 |
| **TanStack React Query** | 服务端状态/数据请求 |
| **react-dnd** | 拖拽排课 |
| **Axios** | HTTP 请求 |
| **dayjs** | 日期处理 |
| **xlsx** | 前端 Excel 处理 |

### 部署
| 技术 | 用途 |
|------|------|
| **Docker + Docker Compose** | 容器化部署 |
| **Nginx** | 前端静态资源服务 |

## 项目结构

```
EasyCourse/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接与初始化
│   │   ├── middleware/        # 中间件（认证、日志、安全、租户）
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── routers/           # API 路由层
│   │   ├── schemas/           # Pydantic 校验模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── repositories/      # 数据访问层
│   │   ├── utils/             # 工具函数
│   │   └── scripts/           # 脚本（初始化管理员等）
│   ├── alembic/               # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API 请求封装
│   │   ├── components/        # 通用组件（布局、排课表格、向导）
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── pages/             # 页面组件
│   │   ├── router/            # 路由配置与守卫
│   │   ├── store/             # Zustand 状态管理
│   │   ├── styles/            # 样式与主题
│   │   ├── types/             # TypeScript 类型定义
│   │   └── utils/             # 工具函数（请求封装、常量）
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml          # Docker Compose 编排
├── Makefile                    # 开发命令快捷方式
├── start.py                    # 一键启动脚本（Windows/Mac/Linux）
└── dev.sh                      # 开发启动脚本
```

## 快速开始

### 环境要求

- **Python** >= 3.10
- **Node.js** >= 18
- **npm** >= 9
- **Redis**（可选，开发模式可用内存缓存）
- **Docker**（可选，用于容器化部署）

### 方式一：一键启动（推荐）

```bash
python start.py
```

脚本会自动完成虚拟环境创建、依赖安装、前后端启动，浏览器访问：

- 前端地址：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

> 首次启动会自动创建默认管理员账号：`admin` / `Admin@123`

### 方式二：Make 命令

```bash
# 安装依赖
make install

# 一键启动前后端
make dev

# 或分别启动
make backend    # 后端 http://localhost:8000
make frontend   # 前端 http://localhost:5173

# 数据库迁移
make migrate

# 停止服务
make stop
```

### 方式三：手动启动

**后端**：
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**：
```bash
cd frontend
npm install
npm run dev
```

### 方式四：Docker Compose

```bash
# 使用 SQLite 启动（默认）
docker compose up -d

# 使用 MySQL 启动
docker compose --profile mysql up -d
```

启动后访问：
- 前端：http://localhost
- 后端 API：http://localhost:8000/docs

## 系统角色

| 角色 | 权限范围 |
|------|----------|
| **超级管理员** (super_admin) | 全部权限：学校审批、用户管理、系统设置、日志查看、数据备份 |
| **学校管理员** (school_admin) | 所属学校：基础数据、排课管理、课表查看、导出、通知、本校设置 |
| **教师** (teacher) | 查看课表、个人信息管理 |

## 使用流程

1. **超级管理员登录** → 审批学校注册申请
2. **学校管理员登录** → 创建学期
3. **配置时段** → 设置早读/正课/晚自习时间段
4. **录入基础数据** → 年级、班级、课程、教师、教室
5. **建立教学安排** → 将教师、课程、班级关联起来
6. **设置排课约束** → 配置教师/教室不可用时段等限制条件
7. **执行排课** → 自动排课生成课表，或手动拖拽微调
8. **查看与导出** → 多视角查看课表，导出 Excel/PDF

> 也可使用「排课向导」功能，按步骤引导完成上述流程。

## 配置说明

后端配置通过环境变量或 `.env` 文件设置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_TYPE` | 数据库类型：sqlite / mysql | sqlite |
| `SQLITE_PATH` | SQLite 文件路径 | ./data/scheduling.db |
| `MYSQL_HOST` | MySQL 主机 | localhost |
| `MYSQL_PORT` | MySQL 端口 | 3306 |
| `MYSQL_USER` | MySQL 用户名 | root |
| `MYSQL_PASSWORD` | MySQL 密码 | - |
| `MYSQL_DATABASE` | MySQL 数据库名 | scheduling |
| `REDIS_URL` | Redis 连接地址 | redis://localhost:6379/0 |
| `SECRET_KEY` | JWT 签名密钥 | change-me-in-production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | 480 |
| `DEBUG` | 调试模式 | false |
| `CORS_ORIGINS` | 允许的跨域来源 | localhost:3000,5173 |

## 数据库

默认使用 SQLite，数据文件位于 `backend/data/scheduling.db`，开箱即用。生产环境建议切换为 MySQL：

```bash
# 修改 backend/.env 或环境变量
DATABASE_TYPE=mysql
MYSQL_HOST=your-mysql-host
MYSQL_PASSWORD=your-password
```

数据库迁移使用 Alembic：

```bash
cd backend
alembic upgrade head    # 执行迁移
alembic revision --autogenerate -m "描述"   # 生成新迁移
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | Admin@123 |

> ⚠️ 请在首次登录后及时修改默认密码！

## License

MIT
