# Agent 项目知识库

> **必读提示**：如果你是刚接手此项目的 AI，请先阅读本文档，了解项目背景和核心理念。

## 项目简介

**项目名称**：涌现式 AI 集群（Emergent AI Cluster）  
**核心理念**：`bash is all you need`  
**目标**：构建一个去中心化的 AI 协作系统，多个专精 Agent 通过 bash/文件/消息总线协作，产生涌现能力

## 当前架构

```
涌现式AI集群/
├── backend/              # 后端核心
│   ├── agent.py          # Agent 主程序（bash 自动化执行）
│   ├── base_ops.py       # 基础操作（bash 执行、环境配置）
│   ├── deepseek.py       # DeepSeek API 封装
│   ├── conversation_logger.py  # 对话记录模块
│   ├── context_manager.py # 上下文管理（Token计数、中断处理）
│   └── skills/           # 技能系统
│       └── file_ops/     # 文件操作技能
├── frontend/             # Vue3 + Vite 前端（端口 14514）
├── conversations/        # 对话记录（.gitignore 忽略）
├── agent/                # 本项目知识库（你在的位置）
└── start.vbs             # Windows 一键启动脚本
```

## 关键设计理念

### 1. Bash is All You Need
- Agent 的核心能力是通过生成 bash 命令操作环境
- 不封装过度抽象的 API，保持与环境的最直接交互
- 每个 Agent 都是"能思考的程序"，而非"被调用的接口"

### 2. 模块化与正交性
- `base_ops`：纯基础操作，与 LLM 无关
- `deepseek.py`：纯模型适配，可替换为 Claude/GPT/本地模型
- `agent.py`：纯业务逻辑，协调调用

### 3. 涌现式设计
- 单个 Agent 能力有限
- 多个专精 Agent 通过**消息传递**和**共享状态**协作
- 复杂任务分解为子任务，分配给不同 Agent

## 开发规范

### 代码风格
- Python：使用中文注释，保持简洁
- 函数返回格式：`(success: bool, result: str)`
- 错误处理：返回元组而非抛出异常（便于 Agent 理解）

### 新增模块原则
1. **单一职责**：一个模块只做一类事
2. **自包含**：依赖明确，不隐式依赖全局状态
3. **可观测**：重要操作要有日志/记录

### 文件组织
```
backend/
├── <name>.py              # 核心模块
├── <name>_test.py         # 测试（可选）
└── skills/
    └── <skill_name>/
        ├── skill.md       # 技能文档（必须）
        └── scripts/       # 实现代码
```

## 待办/路线图

见 [TODO.md](./TODO.md)

## 给其他 AI 的提示

### 接手项目时
1. 先阅读本文件和 [architecture.md](./architecture.md)
2. 检查 `git status` 了解当前改动状态
3. 查看 `backend/agent.py` 了解当前 Agent 能力
4. 阅读最近的 `conversations/*.md` 了解近期对话上下文

### 修改代码时
1. 保持模块化，不要破坏现有接口
2. 更新本文档或相关文档，记录关键决策
3. 敏感数据（API Key、对话记录）及时加入 `.gitignore`

### 遇到问题时
- 优先查看 `agent/` 目录下是否有相关记录
- 复杂决策在 `notes/` 下创建文档说明

---

**维护者**：Kimi Code CLI  
**最后更新**：2026-03-22（添加 context_manager 模块说明）
