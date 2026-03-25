# 项目待办事项

## 高优先级

- [ ] **Agent 注册中心**
  - 设计 Agent 发现机制
  - Agent 能力声明格式
  - 本地注册表（JSON/YAML）

- [ ] **消息总线**
  - 选择通信机制（文件/socket/消息队列）
  - 消息格式定义
  - 异步消息处理

- [ ] **任务调度器**
  - 任务分解策略
  - Agent 选择算法
  - 任务状态追踪

## 中优先级

- [ ] **多模型支持**
  - 抽象模型接口基类
  - Claude API 适配器
  - OpenAI API 适配器
  - 本地模型适配器（ollama）

- [ ] **状态管理**
  - 共享状态存储方案
  - 状态版本控制
  - 状态冲突解决

- [ ] **前端控制台**
  - 集群状态可视化
  - 实时对话流展示
  - Agent 管理界面

## 低优先级

- [ ] **安全加固**
  - bash 命令沙箱
  - 敏感操作确认机制
  - 权限分级系统

- [ ] **测试体系**
  - 单元测试框架
  - 集成测试
  - Agent 行为回归测试

- [ ] **文档完善**
  - API 文档自动生成
  - 技能开发指南
  - 贡献者指南

## 已完成

- [x] Agent 核心拆分（agent/base_ops/deepseek）
- [x] 文件操作技能（file_ops）
- [x] 对话记录系统
- [x] Agent 知识库（本目录）
- [x] 上下文管理模块（context_manager）
  - [x] tiktoken 精确 Token 计数（cl100k_base）
  - [x] 128K 上下文长度限制（80% 阈值）
  - [x] Ctrl+C 中断处理（Interruptible 包装器）
- [x] **代码结构重构**（2026-03-25）
  - [x] 创建 backend/core/ 目录
  - [x] 迁移 agent 相关代码到 core/
  - [x] 更新 skill_dispatcher 路径
- [x] **JSON 响应格式**（2026-03-25）
  - [x] 强制 JSON 格式：`{"command": "...", "thought": "..."}`
  - [x] base_ops.parse_ai_response() 统一解析
  - [x] 向后兼容 DONE:/FAIL: 格式
- [x] **文件操作增强**（2026-03-25）
  - [x] delete_files(*paths)：批量删除文件
  - [x] delete_files_by_pattern(pattern, path)：按通配符删除
  - [x] replace_batch 支持元组和平铺两种格式
  - [x] delete_line 支持批量删除
  - [x] undo_file：撤销最后一次修改

## 想法池（待讨论）

- 是否需要 Agent 间的"信任机制"？
- 如何处理 Agent 间的冲突决策？
- 长期记忆存储方案（向量数据库？）
- 是否支持 Agent 动态加载/卸载？

---

**维护者**：Kimi Code CLI  
**最后更新**：2026-03-25（更新已完成任务）
