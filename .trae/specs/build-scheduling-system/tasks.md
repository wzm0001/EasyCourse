# Tasks

- [x] Task 1: 项目初始化与基础架构搭建
  - [x] SubTask 1.1: 初始化后端项目（FastAPI + SQLAlchemy + Alembic），搭建分层架构（Router → Service → Repository → Model）
  - [x] SubTask 1.2: 初始化前端项目（React 18 + TypeScript + Ant Design 5），配置路由、状态管理、API 请求封装
  - [x] SubTask 1.3: 编写 Docker Compose 配置（前端容器、后端容器、Redis 容器、可选 MySQL 容器）
  - [x] SubTask 1.4: 配置 SQLAlchemy 双数据库引擎（SQLite/MySQL），实现数据库连接工厂
  - [x] SubTask 1.5: 配置 Alembic 数据库迁移，编写初始迁移脚本
  - [x] SubTask 1.6: 实现配置外部化（环境变量 + .env 配置文件）

- [x] Task 2: 用户认证与权限体系
  - [x] SubTask 2.1: 设计并实现用户模型（SuperAdmin、SchoolAdmin、Teacher），含角色枚举、学校外键
  - [x] SubTask 2.2: 实现 JWT Token 认证（登录、登出、Token 刷新），密码强度校验
  - [x] SubTask 2.3: 实现基于角色的权限中间件（RBAC），三级权限控制
  - [x] SubTask 2.4: 实现超级管理员 CRUD 学校账户接口
  - [x] SubTask 2.5: 实现学校账户申请接口（含待审核状态）
  - [x] SubTask 2.6: 实现学校账户审批接口（批准/拒绝，拒绝需填原因）
  - [x] SubTask 2.7: 实现学校账户下设教师账户的 CRUD 接口
  - [x] SubTask 2.8: 实现班主任权限分配，教师账户关联班级
  - [x] SubTask 2.9: 实现学校关键数据修改审批流程（修改→待审批→超级管理员审批→生效）
  - [x] SubTask 2.10: 实现前端登录页面、角色路由守卫、权限组件

- [x] Task 3: 多租户数据隔离
  - [x] SubTask 3.1: 实现数据库层面的租户隔离（所有业务表含 school_id 外键）
  - [x] SubTask 3.2: 实现租户隔离中间件，自动注入 school_id 过滤条件
  - [x] SubTask 3.3: 实现超级管理员跨租户查询能力

- [x] Task 4: 学期管理
  - [x] SubTask 4.1: 实现学期模型（名称、起始日期、结束日期、总周数、活跃状态）
  - [x] SubTask 4.2: 实现学期 CRUD 接口，含"设为当前活跃学期"功能
  - [x] SubTask 4.3: 实现复制历史学期基础数据到新学期接口
  - [ ] SubTask 4.4: 实现前端学期管理页面

- [x] Task 5: 时间段精细化控制
  - [x] SubTask 5.1: 设计时间段模型（早读/正课/晚自习，按年级配置，含节数和起止时间）
  - [x] SubTask 5.2: 实现年级时间段配置 CRUD 接口
  - [x] SubTask 5.3: 实现"不排课时段"标记功能（按年级、按天、按时段）
  - [x] SubTask 5.4: 实现常用时段模板（标准五天制、六天制等）
  - [ ] SubTask 5.5: 实现前端时间段配置页面（含可视化时间轴、模板选择）

- [x] Task 6: 基础数据管理
  - [x] SubTask 6.1: 实现年级、班级、课程、教师、教室的模型与 CRUD 接口
  - [x] SubTask 6.2: 实现"教师-课程-班级"关联模型与 CRUD 接口
  - [x] SubTask 6.3: 实现 Excel 模板下载接口（各基础数据类型对应模板）
  - [x] SubTask 6.4: 实现 Excel 批量导入接口（含数据校验、错误明细返回）
  - [x] SubTask 6.5: 实现 Excel 批量导出接口
  - [ ] SubTask 6.6: 实现前端基础数据管理页面（表格 CRUD + 导入导出按钮）

- [x] Task 7: 排课规则与约束
  - [x] SubTask 7.1: 设计排课约束模型（教师不可排课时段、课程时段限制、教室限制、日课时上限等）
  - [x] SubTask 7.2: 实现排课约束 CRUD 接口
  - [x] SubTask 7.3: 实现约束优先级设置
  - [ ] SubTask 7.4: 实现前端排课规则配置页面

- [x] Task 8: 排课核心引擎
  - [x] SubTask 8.1: 设计排课数据模型（课表单元格：学期+年级+班级+星期+时段+课程+教师+教室+固定标记）
  - [x] SubTask 8.2: 实现冲突检测引擎（教师冲突、教室冲突、班级冲突、时段冲突）
  - [x] SubTask 8.3: 实现一键排课算法（约束满足算法，尊重已固定课程）
  - [x] SubTask 8.4: 实现固定排课功能（标记/取消固定）
  - [x] SubTask 8.5: 实现排课结果统计（成功率、冲突数、未安排课程数）
  - [x] SubTask 8.6: 实现排课锁机制（Redis 分布式锁，同一学期同时仅一人可编辑）

- [x] Task 9: 拖动排课前端
  - [x] SubTask 9.1: 实现课表网格组件（行=时间段，列=周一至周日，支持缩放）
  - [x] SubTask 9.2: 集成 React DnD 实现课程卡片拖动
  - [x] SubTask 9.3: 实现拖动时实时冲突检测与可视化反馈（红色=硬冲突、黄色=警告）
  - [x] SubTask 9.4: 实现固定课程锁定图标与取消固定交互
  - [x] SubTask 9.5: 实现调课功能（单节调课、两节课互换）

- [x] Task 10: 课表查看与导出
  - [x] SubTask 10.1: 实现多维度课表查看（班级/教师/教室/年级/全校）
  - [x] SubTask 10.2: 实现单教师/单班级课表导出（Excel/PDF）
  - [x] SubTask 10.3: 实现批量导出教师课表（ZIP 打包）
  - [x] SubTask 10.4: 实现批量导出班级课表（ZIP 打包）
  - [x] SubTask 10.5: 实现自定义导出（选择范围、格式、内容选项）
  - [x] SubTask 10.6: 实现班主任查看/下载所管班级课表

- [x] Task 11: 流程式排课指引
  - [x] SubTask 11.1: 实现步骤条组件（7步：学期设置→年级与时间段→基础数据→教学安排→排课规则→排课操作→课表查看与导出）
  - [x] SubTask 11.2: 实现步骤间导航与状态管理（已完成/当前/待完成）
  - [x] SubTask 11.3: 实现基础数据变更检测与重新排课提示

- [x] Task 12: 走班制支持
  - [x] SubTask 12.1: 设计教学班模型（走班组合，关联多个行政班）
  - [x] SubTask 12.2: 实现教学班 CRUD 接口
  - [x] SubTask 12.3: 实现排课引擎对教学班的支持（教学班作为排课单元）
  - [x] SubTask 12.4: 实现行政班课表自动汇总教学班课程

- [x] Task 13: 日志系统
  - [x] SubTask 13.1: 实现操作日志记录中间件（自动记录增删改操作）
  - [x] SubTask 13.2: 实现登录日志记录
  - [x] SubTask 13.3: 实现系统异常日志记录
  - [x] SubTask 13.4: 实现排课操作日志记录
  - [x] SubTask 13.5: 实现日志查询接口（按时间、类型、用户、关键词筛选）
  - [x] SubTask 13.6: 实现前端日志管理页面（仅超级管理员可见）

- [x] Task 14: 系统备份与还原
  - [x] SubTask 14.1: 实现数据库备份接口（SQLite 文件复制 / MySQL mysqldump）
  - [x] SubTask 14.2: 实现数据库还原接口（含二次确认机制）
  - [x] SubTask 14.3: 实现自动定时备份（APScheduler / Celery Beat）
  - [x] SubTask 14.4: 实现备份文件管理（列表、下载、删除）
  - [x] SubTask 14.5: 实现前端备份还原管理页面（仅超级管理员可见）

- [x] Task 15: 通知系统
  - [x] SubTask 15.1: 设计通知模型（类型、内容、接收人、已读状态）
  - [x] SubTask 15.2: 实现通知发送接口（审批结果、排课完成、系统维护）
  - [x] SubTask 15.3: 实现通知查询与已读标记接口
  - [x] SubTask 15.4: 实现前端通知中心（铃铛图标、通知列表、已读/未读）

- [x] Task 16: 系统设置
  - [x] SubTask 16.1: 实现超级管理员系统设置页面（数据库切换、MySQL 配置、密码策略、Token 有效期、维护模式）
  - [x] SubTask 16.2: 实现数据库切换功能（连接测试→数据迁移→服务重启）
  - [x] SubTask 16.3: 实现学校账户设置页面（基本信息、排课参数、课表偏好）

- [x] Task 17: 系统安全加固
  - [x] SubTask 17.1: 实现 CSRF Token 防护
  - [x] SubTask 17.2: 实现 API Rate Limiting（慢速/快速限制）
  - [x] SubTask 17.3: 实现单设备登录限制（可配置）
  - [x] SubTask 17.4: 实现 HTTPS 配置（Docker Nginx 反向代理）
  - [x] SubTask 17.5: 实现输入校验与 XSS 防护

- [x] Task 18: 界面美化与主题
  - [x] SubTask 18.1: 实现深色/浅色主题切换
  - [x] SubTask 18.2: 实现响应式布局适配
  - [x] SubTask 18.3: 实现全局 Toast 提示与加载动画
  - [x] SubTask 18.4: 实现课表网格缩放与拖动交互优化

- [x] Task 19: 集成测试与部署验证
  - [x] SubTask 19.1: 编写后端核心模块单元测试
  - [x] SubTask 19.2: 编排课算法集成测试
  - [x] SubTask 19.3: 编写前端核心组件测试
  - [x] SubTask 19.4: Docker Compose 全链路部署验证
  - [x] SubTask 19.5: 多用户并发访问压力测试

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 2, Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 4]
- [Task 7] depends on [Task 5, Task 6]
- [Task 8] depends on [Task 5, Task 6, Task 7]
- [Task 9] depends on [Task 8]
- [Task 10] depends on [Task 8]
- [Task 11] depends on [Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10]
- [Task 12] depends on [Task 6, Task 8]
- [Task 13] depends on [Task 1, Task 2]
- [Task 14] depends on [Task 1]
- [Task 15] depends on [Task 2]
- [Task 16] depends on [Task 1, Task 2]
- [Task 17] depends on [Task 1, Task 2]
- [Task 18] depends on [Task 1]
- [Task 19] depends on [Task 1 ~ Task 18]

# Parallelizable Work
- Task 4, Task 13, Task 14, Task 15 可在 Task 2 完成后并行开发
- Task 5 和 Task 6 可在 Task 4 完成后并行开发
- Task 9 和 Task 10 可在 Task 8 完成后并行开发
- Task 12 可在 Task 6 完成后与 Task 7 并行开发
- Task 17 和 Task 18 可在 Task 1 完成后并行开发
