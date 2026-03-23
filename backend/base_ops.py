#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础操作模块
包含 bash 命令执行和 skill 命令调度等通用基础操作
"""

import os
import subprocess
import json

# 工作目录
WORK_DIR = os.getcwd()


def run_bash(cmd):
    """
    执行 bash 命令
    
    参数:
        cmd: 要执行的命令字符串
    返回:
        命令输出（stdout + stderr），最多4000字符
    """
    # 截断显示，避免输出过长
    display_cmd = cmd[:50] + "..." if len(cmd) > 50 else cmd
    print(f"  $ {display_cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=300, cwd=WORK_DIR
        )
        output = result.stdout + result.stderr
        if not output:
            output = "(无输出)"
        return output[:4000]
    except subprocess.TimeoutExpired:
        return "ERROR: 命令超时"
    except Exception as e:
        return f"ERROR: {e}"


def run_command(cmd):
    """
    执行命令（自动识别 bash 或 skill 命令）
    
    参数:
        cmd: 命令字符串
          - bash 命令: ls -la, cat file.txt
          - skill 命令: create_file("test.txt", "hello")
    返回:
        命令执行结果
    """
    # 延迟导入避免循环依赖
    from skill_dispatcher import execute_skill_command, parse_command, scan_skills
    
    # 尝试解析为 skill 命令
    parsed = parse_command(cmd)
    if parsed:
        func_name = parsed[0]
        # 检查命令是否存在
        commands = scan_skills()
        if func_name in commands:
            print(f"  [SKILL] {func_name}(...)")
            success, result = execute_skill_command(cmd)
            # 统一输出格式（使用 ASCII 字符避免编码问题）
            status = "OK" if success else "FAIL"
            return f"{status}: {result}"
    
    # 普通 bash 命令
    return run_bash(cmd)


def get_skill_commands_help():
    """获取 skill 命令帮助文本"""
    try:
        from skill_dispatcher import get_skill_help_text
        return get_skill_help_text()
    except Exception:
        return ""


def parse_ai_response(response):
    """
    解析 AI 的 JSON 格式响应
    
    返回:
        (command: str, thought: str, is_json: bool)
    """
    response = response.strip()
    
    # 尝试解析 JSON
    try:
        resp = json.loads(response)
        if isinstance(resp, dict):
            command = resp.get("command", "").strip()
            thought = resp.get("thought", "").strip()
            return command, thought, True
    except json.JSONDecodeError:
        pass
    
    # 兼容旧格式：检查是否是 DONE:/FAIL: 格式
    if response.startswith("DONE:") or response.startswith("FAIL:"):
        return response, "", False
    
    # 兼容旧格式：纯命令
    return response, "", False
