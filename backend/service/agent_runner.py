#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 后台执行器
在独立线程中运行 Agent，每步执行更新消息
"""

import sys
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# 添加 core 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from base_ops import WORK_DIR, run_command, get_skill_commands_help, parse_ai_response
from deepseek import chat, check_api_key
from context_manager import check_context_limit, Interruptible

# 存储运行中的 Agent 状态
_agent_tasks = {}


def get_agent_status(session_id: str):
    """获取 Agent 执行状态"""
    return _agent_tasks.get(session_id, {"running": False})


def stop_agent(session_id: str):
    """停止 Agent 执行"""
    if session_id in _agent_tasks:
        _agent_tasks[session_id]["stop_flag"] = True
        _agent_tasks[session_id]["stopping"] = True
        return True
    return False


def is_stopping(session_id: str):
    """检查是否正在停止"""
    if session_id in _agent_tasks:
        return _agent_tasks[session_id].get("stopping", False)
    return False


def run_agent_steps(session_id: str, messages: list, update_callback):
    """
    在后台线程中运行 Agent 步骤
    
    参数:
        session_id: 会话ID
        messages: 消息列表（会被修改）
        update_callback: 每步执行的回调函数 callback(messages, status_msg)
    """
    if session_id in _agent_tasks and _agent_tasks[session_id]["running"]:
        return False, "Agent 正在运行中"
    
    task_info = {
        "running": True,
        "stop_flag": False,
        "stopping": False,  # 新增：正在停止中
        "thread": None
    }
    _agent_tasks[session_id] = task_info
    
    def agent_loop():
        # 创建线程池用于可中断的 API 调用
        executor = ThreadPoolExecutor(max_workers=1)
        
        try:
            skill_help = get_skill_commands_help()
            
            # 确保有系统消息
            has_system = any(m.get("role") == "system" for m in messages)
            if not has_system:
                system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
你可以使用两种类型的命令：
1. **Bash 命令**: 普通的 shell 命令，如 `ls -la`, `cat file.txt`
2. **Skill 命令**: 预定义的文件/代码操作函数，格式为 `函数名(参数1, 参数2, ...)`

输出格式（严格JSON）:
{{"command": "要执行的bash或skill命令", "thought": "你的想法/说明（可选）"}}

规则:
- 必须输出合法的JSON格式
- command 字段为纯命令，不含任何解释
- thought 字段可空，用于表达你的想法（会显示给用户）
- 如果任务完成，command 填 "DONE:结果描述"
- 如果无法完成，command 填 "FAIL:原因"

{skill_help}"""
                messages.insert(0, {"role": "system", "content": system_msg})
            
            max_steps = 50  # 最大执行步数，防止死循环
            step = 0
            
            while step < max_steps:
                step += 1
                
                # 检查停止标志
                if task_info.get("stop_flag"):
                    update_callback(messages, {"type": "status", "content": "已停止"})
                    break
                
                # 检查上下文长度
                is_limited, current_tokens, token_limit = check_context_limit(messages)
                if is_limited:
                    update_callback(messages, {"type": "status", "content": f"达到上下文限制 ({current_tokens}/{token_limit})"})
                    break
                
                # 调用 AI
                update_callback(messages, {"type": "thinking", "content": "AI 思考中..."})
                
                # 净化 messages，只保留 role 和 content（API 只需要这两个字段）
                api_messages = [{"role": m["role"], "content": m["content"]} 
                                for m in messages if "content" in m]
                
                # 使用线程池执行 chat，支持取消
                future = executor.submit(chat, api_messages)
                
                # 等待结果，同时检查停止标志
                response = None
                while True:
                    if task_info.get("stop_flag"):
                        future.cancel()
                        update_callback(messages, {"type": "status", "content": "已停止"})
                        executor.shutdown(wait=False)
                        return
                    
                    if future.done():
                        try:
                            response = future.result(timeout=0.1)
                        except Exception as e:
                            update_callback(messages, {"type": "error", "content": f"API 调用失败: {e}"})
                            response = None
                        break
                    
                    time.sleep(0.1)  # 小延迟避免 CPU 占用过高
                
                if response is None:
                    break
                
                if not response or response.startswith("ERROR:"):
                    update_callback(messages, {"type": "error", "content": response or "空响应"})
                    break
                
                # 解析响应
                command, thought, is_json = parse_ai_response(response)
                
                # 添加 AI 消息
                assistant_msg = {
                    "id": f"{session_id}_a{step}",
                    "role": "assistant", 
                    "content": response,
                    "command": command,
                    "thought": thought,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                }
                messages.append(assistant_msg)
                
                # 如果有想法，通知前端
                if thought:
                    update_callback(messages, {"type": "thought", "content": thought})
                
                # 检查 DONE/FAIL
                if command.startswith("DONE:"):
                    result = command[5:] if len(command) > 5 else "任务完成"
                    update_callback(messages, {"type": "done", "content": result})
                    break
                
                if command.startswith("FAIL:"):
                    reason = command[5:] if len(command) > 5 else "未知原因"
                    update_callback(messages, {"type": "fail", "content": reason})
                    break
                
                # 执行命令
                update_callback(messages, {"type": "executing", "content": command[:100]})
                
                try:
                    output = run_command(command)
                except Exception as e:
                    output = f"执行错误: {e}"
                
                # 添加执行结果
                result_msg = {
                    "id": f"{session_id}_r{step}",
                    "role": "user",  # 用 user 角色表示系统/执行结果
                    "content": f"执行结果:\n```\n{output[:2000]}\n```\n\n请继续:",
                    "is_result": True,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                }
                messages.append(result_msg)
                
                update_callback(messages, {"type": "result", "content": output[:200]})
                
                # 小延迟，避免请求过快
                time.sleep(0.5)
            
            else:
                update_callback(messages, {"type": "status", "content": "达到最大执行步数"})
            
        except Exception as e:
            update_callback(messages, {"type": "error", "content": f"执行异常: {e}"})
        finally:
            task_info["running"] = False
            executor.shutdown(wait=False)
    
    # 启动后台线程
    thread = threading.Thread(target=agent_loop, daemon=True)
    task_info["thread"] = thread
    thread.start()
    
    return True, "Agent 已启动"
