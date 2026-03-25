#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liminal Web Service
提供会话管理和 Agent 通信 API
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 添加 core 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from agent_runner import run_agent_steps, get_agent_status, stop_agent, is_stopping
from deepseek import check_api_key

app = FastAPI(title="Liminal API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class SessionType:
    SINGLE = "single"
    HIERARCHICAL = "hierarchical"
    EMERGENT = "emergent"

class Session(BaseModel):
    id: str
    name: str
    project_path: str
    session_type: str
    created_at: str
    updated_at: str
    messages: List[dict] = []
    agent_running: bool = False

class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    project_path: str
    session_type: str = SessionType.SINGLE

class RenameSessionRequest(BaseModel):
    name: str

class SendMessageRequest(BaseModel):
    content: str
    model: str = "deepseek-reasoner"

# ============ 内存存储 ============

sessions_db = {}
session_messages = {}  # 存储完整消息历史

# ============ 辅助函数 ============

def update_session_messages(session_id: str, messages: list, status: dict):
    """更新会话消息（由 Agent 回调调用）"""
    if session_id in session_messages:
        session_messages[session_id] = messages.copy()
        # 同时更新会话的更新时间
        if session_id in sessions_db:
            sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
            sessions_db[session_id]["agent_running"] = get_agent_status(session_id).get("running", False)

# ============ API 路由 ============

@app.get("/")
def root():
    return {"message": "Liminal API v1.0.0", "api_key_configured": check_api_key()}

# ---- 会话管理 ----

@app.get("/api/sessions", response_model=List[Session])
def list_sessions():
    """获取所有会话列表"""
    result = []
    for sid, session in sessions_db.items():
        # 添加运行状态
        s = session.copy()
        s["agent_running"] = get_agent_status(sid).get("running", False)
        result.append(s)
    return result

@app.post("/api/sessions", response_model=Session)
def create_session(req: CreateSessionRequest):
    """创建新会话"""
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    name = req.name or f"会话 {len(sessions_db) + 1}"
    
    session = {
        "id": session_id,
        "name": name,
        "project_path": req.project_path,
        "session_type": req.session_type,
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "agent_running": False
    }
    
    sessions_db[session_id] = session
    session_messages[session_id] = []
    
    return session

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """获取单个会话详情"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    result = sessions_db[session_id].copy()
    result["messages"] = session_messages.get(session_id, [])
    result["agent_running"] = get_agent_status(session_id).get("running", False)
    return result

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """删除会话"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 先停止运行的 Agent
    stop_agent(session_id)
    
    del sessions_db[session_id]
    if session_id in session_messages:
        del session_messages[session_id]
    
    return {"success": True}

@app.patch("/api/sessions/{session_id}/rename")
def rename_session(session_id: str, req: RenameSessionRequest):
    """重命名会话"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    sessions_db[session_id]["name"] = req.name
    sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
    return {"success": True}

# ---- 消息和 Agent ----

@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: str):
    """获取会话消息列表（轮询接口）"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    messages = session_messages.get(session_id, [])
    running = get_agent_status(session_id).get("running", False)
    stopping = is_stopping(session_id)
    
    return {
        "messages": messages,
        "agent_running": running,
        "is_stopping": stopping,
        "count": len(messages)
    }

@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: str, req: SendMessageRequest):
    """发送消息给 Agent，启动后台执行"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    if not check_api_key():
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY 未配置")
    
    # 检查是否已有运行中的 Agent
    if get_agent_status(session_id).get("running"):
        return {"success": False, "error": "Agent 正在执行中，请等待"}
    
    # 获取或初始化消息列表
    if session_id not in session_messages:
        session_messages[session_id] = []
    
    messages = session_messages[session_id]
    
    # 添加用户消息
    user_msg = {
        "id": str(uuid.uuid4())[:8],
        "role": "user",
        "content": req.content,
        "timestamp": datetime.now().isoformat()
    }
    messages.append(user_msg)
    
    # 设置模型（通过环境变量，实际应在 deepseek.py 中支持动态切换）
    # TODO: 支持动态切换模型
    
    # 启动 Agent 后台执行
    success, msg = run_agent_steps(
        session_id, 
        messages, 
        lambda msgs, status: update_session_messages(session_id, msgs, status)
    )
    
    if success:
        sessions_db[session_id]["agent_running"] = True
        return {"success": True, "message": "Agent 已启动，请轮询获取结果"}
    else:
        return {"success": False, "error": msg}

@app.post("/api/sessions/{session_id}/stop")
def stop_session_agent(session_id: str):
    """停止 Agent 执行"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    success = stop_agent(session_id)
    if success:
        sessions_db[session_id]["agent_running"] = False
    
    return {"success": success}

# ---- Token 信息 ----

@app.get("/api/token-info")
def get_token_info():
    """获取 Token 使用情况"""
    # TODO: 接入真实的 token 计数
    # 从 context_manager 获取
    try:
        from context_manager import count_messages
        # 计算所有会话的总 token（简化）
        total_tokens = 0
        for msgs in session_messages.values():
            total_tokens += count_messages(msgs)
        
        limit = 128000
        percentage = min(100, int(total_tokens / limit * 100))
        
        return {
            "current": total_tokens,
            "limit": limit,
            "percentage": percentage
        }
    except:
        return {"current": 0, "limit": 128000, "percentage": 0}

# ============ 启动 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18080)
