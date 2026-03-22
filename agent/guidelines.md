# 开发规范与约定

## 代码风格

### Python

```python
# 1. 文件头必须包含编码声明
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 2. 使用中文注释（本项目约定）
def run_bash(cmd):
    """执行 bash 命令"""
    print(f"  $ {cmd}")  # 打印要执行的命令

# 3. 函数返回格式统一为元组
# (success: bool, result: str)
def read_file(filepath):
    try:
        content = Path(filepath).read_text()
        return True, content  # 成功返回 True + 结果
    except Exception as e:
        return False, f"读取失败: {e}"  # 失败返回 False + 错误信息

# 4. 错误处理优先返回，不抛异常（便于 Agent 理解）
```

### 文件组织

```
backend/
├── module.py              # 核心实现
├── module_test.py         # 测试文件（可选）
└── skills/
    └── skill_name/
        ├── skill.md       # 技能文档（必须）
        ├── scripts/
        │   ├── __init__.py
        │   └── skill_name.py
        └── tests/         # 技能测试（可选）
```

## 文档规范

### skill.md 模板

```markdown
# 技能名称

## 技能介绍
- 一句话描述功能
- 适用场景
- 支持的操作系统

## 命令介绍
| 命令 | 功能 | 示例 |

## 使用说明
- 重要提示
- 边界情况

## 使用示例
```python 代码示例
```

### Agent 知识库文档

- `README.md`：项目总览，必读
- `architecture.md`：架构设计，关键决策
- `TODO.md`：任务列表
- `guidelines.md`：本文件
- `notes/*.md`：零散笔记

## Git 提交规范

```
<type>(<scope>): <subject>

<body>
```

**type**：
- `feat`：新功能
- `fix`：修复
- `refactor`：重构
- `docs`：文档
- `chore`：杂项

**示例**：
```
feat(agent): 增加对话记录功能

- 生成对话ID（时间戳格式）
- 自动保存对话到 markdown
- 异常时也能保存记录
```

## 安全规范

### 必须加入 .gitignore 的内容

```
# 敏感配置
.env
.env.local
*.key

# 运行时数据
conversations/
logs/
temp/

# 个人数据
*.private.md
```

### 代码中处理敏感信息

```python
# ✅ 正确：从环境变量读取
API_KEY = os.getenv("API_KEY", "")

# ❌ 错误：硬编码
API_KEY = "sk-abc123..."
```

## 模块间依赖规则

```
agent.py
  ├── base_ops.py (OK)
  ├── deepseek.py (OK)
  └── skills/file_ops (OK)

base_ops.py
  └── (无依赖，最底层)

deepseek.py
  └── (自包含，不依赖其他业务模块)

skills/*
  ├── base_ops.py (OK)
  └── deepseek.py (避免，技能应保持独立)
```

**原则**：
- 上层可以依赖下层
- 下层不能依赖上层
- 同层尽量减少依赖
- 禁止循环依赖

## 给其他 AI 的代码审查清单

修改代码前问自己：

- [ ] 是否保持了模块化？
- [ ] 是否更新了相关文档？
- [ ] 敏感数据是否已排除？
- [ ] 错误处理是否完善？
- [ ] 是否破坏了现有接口？

---

**维护者**：Kimi Code CLI  
**最后更新**：2026-03-22
