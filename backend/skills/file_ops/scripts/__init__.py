#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作技能模块
"""

from .file_ops import (
    # 基础操作
    create_file,
    read_file,
    delete_file,
    copy_file,
    move_file,
    append_to_file,
    # 精细行操作
    read_lines,
    insert_line,
    delete_line,
    replace_line,
    search_replace,
    # 目录操作
    create_dir,
    delete_dir,
    list_dir,
    search_files,
    # 通用接口
    execute_command,
    COMMANDS,
)

__all__ = [
    # 基础操作
    "create_file",
    "read_file",
    "delete_file",
    "copy_file",
    "move_file",
    "append_to_file",
    # 精细行操作
    "read_lines",
    "insert_line",
    "delete_line",
    "replace_line",
    "search_replace",
    # 目录操作
    "create_dir",
    "delete_dir",
    "list_dir",
    "search_files",
    # 通用接口
    "execute_command",
    "COMMANDS",
]
