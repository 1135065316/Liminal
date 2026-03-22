#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础操作模块
包含 bash 命令执行等通用基础操作
"""

import os
import subprocess

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
    print(f"  $ {cmd}")
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
