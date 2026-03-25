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

class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    project_path: str
    session_type: str = SessionType.SINGLE

class RenameSessionRequest(BaseModel):
    name: str

class SendMessageRequest(BaseModel):
    content: str
    model: str = "deepseek-reasoner"  # 或 deepseek-chat

# ============ 内存存储 (后续可换数据库) ============

sessions_db = {}

# ============ API 路由 ============

@app.get("/")
def root():
    return {"message": "Liminal API v1.0.0"}

# ---- 会话管理 ----

@app.get("/api/sessions", response_model=List[Session])
def list_sessions():
    """获取所有会话列表"""
    return list(sessions_db.values())

@app.post("/api/sessions", response_model=Session)
def create_session(req: CreateSessionRequest):
    """创建新会话"""
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    name = req.name or f"会话 {len(sessions_db) + 1}"
    
    session = Session(
        id=session_id,
        name=name,
        project_path=req.project_path,
        session_type=req.session_type,
        created_at=now,
        updated_at=now,
        messages=[]
    )
    
    sessions_db[session_id] = session.dict()
    return session

@app.get("/api/sessions/{session_id}", response_model=Session)
def get_session(session_id: str):
    """获取单个会话详情"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    return sessions_db[session_id]

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """删除会话"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    del sessions_db[session_id]
    return {"success": True}

@app.patch("/api/sessions/{session_id}/rename")
def rename_session(session_id: str, req: RenameSessionRequest):
    """重命名会话"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    sessions_db[session_id]["name"] = req.name
    sessions_db[session_id]["updated_at"] = datetime.now().isoformat()
    return {"success": True}

# ---- 消息处理 ----

@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: str):
    """获取会话消息列表"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"messages": sessions_db[session_id]["messages"]}

@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: str, req: SendMessageRequest):
    """发送消息给 Agent"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = sessions_db[session_id]
    
    # 添加用户消息
    user_msg = {
        "id": str(uuid.uuid4())[:8],
        "role": "user",
        "content": req.content,
        "timestamp": datetime.now().isoformat()
    }
    session["messages"].append(user_msg)
    
    # TODO: 调用 Agent 核心处理
    # 现在返回模拟响应
    assistant_msg = {
        "id": str(uuid.uuid4())[:8],
        "role": "assistant",
        "content": f"[{req.model}] 收到: {req.content[:50]}...",
        "timestamp": datetime.now().isoformat()
    }
    session["messages"].append(assistant_msg)
    session["updated_at"] = datetime.now().isoformat()
    
    return {"success": True, "message": assistant_msg}

# ---- Token 信息 ----

@app.get("/api/token-info")
def get_token_info():
    """获取 Token 使用情况"""
    # TODO: 接入真实的 token 计数
    return {
        "current": 0,
        "limit": 128000,
        "percentage": 0
    }

# ============ 启动 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18080)
