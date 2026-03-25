#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话记录模块
记录每组messages到markdown文件，按日期组织
"""

import os
import json
from datetime import datetime
from pathlib import Path

# 对话记录根目录（项目根目录下的conversations文件夹）
CONVERSATION_DIR = Path(__file__).parent.parent / "conversations"


def ensure_dir():
    """确保对话记录目录存在"""
    CONVERSATION_DIR.mkdir(parents=True, exist_ok=True)


def get_conversation_file(timestamp=None):
    """
    获取对话记录文件路径
    
    参数:
        timestamp: 时间戳，默认为当前时间
    返回:
        文件路径，格式：conversations/年_月_日_时分秒.md
    """
    ensure_dir()
    if timestamp is None:
        timestamp = datetime.now()
    filename = f"{timestamp.year}_{timestamp.month}_{timestamp.day}_{timestamp.hour:02d}.{timestamp.minute:02d}.{timestamp.second:02d}.md"
    return CONVERSATION_DIR / filename


def generate_conversation_id():
    """
    生成对话ID
    
    返回:
        基于开始时间的ID：YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_message(msg):
    """
    格式化单条消息为markdown
    
    参数:
        msg: 消息字典，包含role和content
    返回:
        markdown字符串
    """
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    
    # 根据角色设置标题样式
    if role == "system":
        header = "## 🎯 System"
    elif role == "user":
        header = "## 👤 User"
    elif role == "assistant":
        header = "## 🤖 Assistant"
    else:
        header = f"## {role.title()}"
    
    # 代码块包裹内容，保持格式
    return f"""{header}

```
{content}
```

---

"""


def save_conversation(conversation_id, messages):
    """
    保存对话记录到markdown文件
    
    参数:
        conversation_id: 对话ID（时间戳格式）
        messages: 消息列表
    """
    file_path = get_conversation_file()
    
    # 解析ID中的时间
    try:
        conv_time = datetime.strptime(conversation_id, "%Y%m%d_%H%M%S")
        time_str = conv_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        time_str = conversation_id
    
    # 构建markdown内容
    content = f"""# 对话记录

**对话ID**: `{conversation_id}`  
**开始时间**: {time_str}

"""
    
    for msg in messages:
        content += format_message(msg)
    
    # 追加模式写入文件
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)
        f.write("\n---\n\n")  # 对话分隔线
    
    return file_path


def get_conversation_summary(messages):
    """
    获取对话摘要（用于日志输出）
    
    参数:
        messages: 消息列表
    返回:
        摘要字符串
    """
    if not messages:
        return "空对话"
    
    # 统计各角色消息数
    counts = {}
    for msg in messages:
        role = msg.get("role", "unknown")
        counts[role] = counts.get(role, 0) + 1
    
    return f"共 {len(messages)} 条消息: " + ", ".join([f"{k}={v}" for k, v in counts.items()])
