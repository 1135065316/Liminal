#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager - 上下文管理模块
包含：token 计数、上下文长度检查、可中断操作包装
"""

import tiktoken

# ==================== Token 计数 ====================

try:
    _encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4/DeepSeek 通用
except Exception:
    _encoding = None


def count_tokens(text: str) -> int:
    """计算单段文本的 token 数"""
    if not text:
        return 0
    if _encoding:
        return len(_encoding.encode(text))
    return len(text) // 4


def count_messages(messages: list) -> int:
    """计算消息列表的总 token 数（用于上下文长度检查）"""
    if _encoding:
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if content:
                total += len(_encoding.encode(content))
        return total
    return sum(len(msg.get("content", "")) for msg in messages) // 4


def get_encoding_info() -> dict:
    """获取当前编码器信息（用于调试）"""
    return {
        "encoding": "cl100k_base" if _encoding else "fallback",
        "available": _encoding is not None,
        "name": _encoding.name if _encoding else None
    }


# ==================== 上下文限制检查 ====================

MAX_CONTEXT_TOKENS = 128 * 1024      # 128K
CONTEXT_LIMIT_THRESHOLD = 0.8        # 80% 阈值


def check_context_limit(messages):
    """
    检查上下文是否超过限制
    
    Returns:
        (bool, int, int): (是否超限, 当前tokens, token限制)
    """
    current_tokens = count_messages(messages)
    token_limit = int(MAX_CONTEXT_TOKENS * CONTEXT_LIMIT_THRESHOLD)
    if current_tokens >= token_limit:
        print(f"\n达到上下文长度限制 ({current_tokens}/{token_limit} tokens)，对话结束")
        return True, current_tokens, token_limit
    return False, current_tokens, token_limit


# ==================== 可中断操作包装器 ====================

class Interruptible:
    """
    可中断操作包装器 - 统一处理 Ctrl+C 中断
    
    Usage:
        with Interruptible(messages, "API请求") as op:
            response = chat(messages)
        if op.interrupted:
            break
        
        # 或
        result = Interruptible(messages, "操作").run(func, arg1, arg2)
    """
    
    def __init__(self, messages: list, label: str = "操作"):
        self.messages = messages
        self.label = label
        self.interrupted = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is KeyboardInterrupt:
            print(f"\n\n用户中断{self.label}，正在保存对话...")
            self.messages.append({"role": "user", "content": f"[用户中断{self.label}]"})
            self.interrupted = True
            return True  # 抑制异常
        return False  # 其他异常正常抛出
    
    def run(self, func, *args, **kwargs):
        """执行函数，如遇中断返回 None"""
        with self:
            return func(*args, **kwargs)
        return None
