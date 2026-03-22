#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Counter - 使用 tiktoken 精确计算 token 数
适配 GPT-4/DeepSeek 的 cl100k_base 编码
"""

import tiktoken

# 初始化 tiktoken 编码器（cl100k_base 是 GPT-4 和 DeepSeek 通用）
try:
    _encoding = tiktoken.get_encoding("cl100k_base")
except Exception:
    _encoding = None


def count_tokens(text: str) -> int:
    """计算单段文本的 token 数"""
    if not text:
        return 0
    if _encoding:
        return len(_encoding.encode(text))
    # 降级：简单估算（每4字符≈1token）
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
    # 降级：简单估算
    return sum(len(msg.get("content", "")) for msg in messages) // 4


def get_encoding_info() -> dict:
    """获取当前编码器信息（用于调试）"""
    return {
        "encoding": "cl100k_base" if _encoding else "fallback",
        "available": _encoding is not None,
        "name": _encoding.name if _encoding else None
    }
