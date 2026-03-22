# Liminal

> **Liminal: The AI at the threshold of emergence**

一个涌现式 AI 集群系统，多个专精 Agent 通过 bash 命令与文件系统协作，在临界状态中涌现复杂能力。

---

## 核心理念

### Bash is All You Need
Agent 不依赖复杂的 API 封装，而是通过生成 bash 命令和 skill 函数直接与环境交互。这种极简接口带来最大化的通用性和涌现可能性。

### 涌现式设计
- **简单规则**：每个 Agent 能力有限
- **临界交互**：Agent 间通过消息和文件系统协作
- **复杂涌现**：简单个体在交互中产生超越个体的集体智能

---

## 快速开始

### 环境准备

```bash
# 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 启动 Agent

```bash
# 交互模式
python agent.py

# 或者直接执行任务
python agent.py "创建一个简单的 HTML 页面"
```

### Windows 一键启动

双击 `start.vbs` 启动前后端服务。

---

## 项目结构

```
Liminal/
├── agent/                  # 项目知识库（给其他 AI 看的）
│   ├── architecture.md     # 架构设计
│   ├── guidelines.md       # 开发规范
│   └── TODO.md             # 路线图
├── backend/                # 后端核心
│   ├── agent.py            # Agent 主程序
│   ├── context_manager.py  # 上下文管理（Token 计数、中断处理）
│   ├── deepseek.py         # DeepSeek API 封装（R1 思考模型）
│   ├── skill_dispatcher.py # Skill 命令调度
│   └── skills/             # 技能系统
│       └── file_ops/       # 文件操作技能
├── frontend/               # Vue3 + Vite 前端
├── conversations/          # 对话记录（自动保存）
└── design/                 # 设计文档
```

---

## 核心特性

### 🤖 Agent 能力
- **自动化执行**：通过 bash/skill 完成任务
- **上下文感知**：128K Token 上下文，自动长度管理
- **对话连续**：任务完成后可继续对话，保持同一 session
- **安全中断**：Ctrl+C 立即保存对话记录

### 🛠️ Skill 系统
- **文件操作**：精细行级编辑（read_lines, insert_line, replace_multi_lines 等）
- **多行支持**：Python 三引号风格多行字符串
- **自动路由**：自动识别 bash 命令 vs skill 命令

### 🧠 思考模型
- **DeepSeek R1**：使用 deepseek-reasoner 思考模型
- **64K 输出**：支持超长代码生成

---

## 使用示例

```
> 创建一个坦克大战游戏
[SKILL] create_dir("坦克大战")
 -> OK: 文件夹创建成功: 坦克大战
[SKILL] create_file("坦克大战/index.html", """<!DOCTYPE html>...""")
 -> OK: 文件创建成功: 坦克大战/index.html
...
完成: DONE: 已创建完整的坦克大战游戏

> 帮我美化一下页面        # 继续对话，同一 session
...
```

---

## 涌现式协作

Liminal 设计用于多 Agent 协作场景：

1. **文件系统作为共享状态**：Agent 通过读写文件交换信息
2. **对话记录作为记忆**：完整保存每次交互，支持上下文继承
3. **临界触发**：当多个 Agent 的输出在文件中交汇，涌现新能力

---

## 许可证

MIT

---

**Liminal** — 站在涌现的门槛上。
