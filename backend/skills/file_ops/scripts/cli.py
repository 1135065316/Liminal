#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作技能 - 命令行入口
用法: python cli.py <命令> [参数...]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_ops import (
    # 基础操作
    create_file, read_file, delete_file, copy_file, move_file, append_to_file,
    # 精细行操作
    read_lines, insert_line, delete_line, replace_line, search_replace,
    # 目录操作
    create_dir, delete_dir, list_dir, search_files,
    execute_command
)


def print_help():
    help_text = """
文件操作技能 CLI

【基础文件操作】
  create_file <文件路径> [内容]           创建文件
  read_file <文件路径>                    读取文件全部内容
  delete_file <文件路径>                  删除文件
  copy_file <源文件> <目标文件>           复制文件
  move_file <源文件> <目标文件>           移动文件
  append_to_file <文件路径> <内容>        追加内容到文件末尾

【精细行级操作（编程专用）】
  read_lines <文件路径> [起始行] [结束行]  读取指定行范围
                                            示例: read_lines test.py 1 10
                                            示例: read_lines test.py 5     # 从第5行到末尾
  insert_line <文件路径> <行号> <内容>    在指定行前插入内容
                                            示例: insert_line test.py 3 "# 新注释"
                                            示例: insert_line test.py -1 "末尾添加"  # -1=末尾
  delete_line <文件路径> <行号>           删除指定行
                                            示例: delete_line test.py 5
                                            示例: delete_line test.py -1   # 删除最后一行
  replace_line <文件路径> <行号> <内容>   替换指定行内容
                                            示例: replace_line test.py 2 "print('hello')"
  search_replace <文件路径> <旧内容> <新内容> [--regex]  搜索替换
                                            示例: search_replace test.py "old" "new"
                                            示例: search_replace test.py "def (\\w+)" "func_\\1" --regex

【目录操作】
  create_dir <目录路径>                   创建目录
  delete_dir <目录路径>                   删除目录（含内容）
  list_dir [目录路径]                     列出目录内容（默认当前目录）
  search_files <模式> [搜索路径]          搜索文件（如 *.py）

【帮助】
  help 或 -h 或 --help                    显示此帮助信息
"""
    print(help_text)


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # ==================== 帮助 ====================
    if command in ("help", "-h", "--help"):
        print_help()
        return
    
    # ==================== 基础文件操作 ====================
    elif command == "create_file":
        if len(args) < 1:
            print("用法: create_file <文件路径> [内容]")
            sys.exit(1)
        filepath = args[0]
        content = args[1] if len(args) > 1 else ""
        ok, msg = create_file(filepath, content)
        print(msg)
    
    elif command == "read_file":
        if len(args) < 1:
            print("用法: read_file <文件路径>")
            sys.exit(1)
        ok, msg = read_file(args[0])
        print(msg)
    
    elif command == "delete_file":
        if len(args) < 1:
            print("用法: delete_file <文件路径>")
            sys.exit(1)
        ok, msg = delete_file(args[0])
        print(msg)
    
    elif command == "copy_file":
        if len(args) < 2:
            print("用法: copy_file <源文件> <目标文件>")
            sys.exit(1)
        ok, msg = copy_file(args[0], args[1])
        print(msg)
    
    elif command == "move_file":
        if len(args) < 2:
            print("用法: move_file <源文件> <目标文件>")
            sys.exit(1)
        ok, msg = move_file(args[0], args[1])
        print(msg)
    
    elif command == "append_to_file":
        if len(args) < 2:
            print("用法: append_to_file <文件路径> <内容>")
            sys.exit(1)
        ok, msg = append_to_file(args[0], args[1])
        print(msg)
    
    # ==================== 精细行级操作 ====================
    elif command == "read_lines":
        if len(args) < 1:
            print("用法: read_lines <文件路径> [起始行] [结束行]")
            sys.exit(1)
        filepath = args[0]
        start = int(args[1]) if len(args) > 1 else 1
        end = int(args[2]) if len(args) > 2 else None
        ok, msg = read_lines(filepath, start, end)
        print(msg)
    
    elif command == "insert_line":
        if len(args) < 3:
            print("用法: insert_line <文件路径> <行号> <内容>")
            sys.exit(1)
        filepath = args[0]
        try:
            line_num = int(args[1])
        except ValueError:
            print(f"错误: 行号必须是整数，收到: {args[1]}")
            sys.exit(1)
        content = args[2]
        ok, msg = insert_line(filepath, line_num, content)
        print(msg)
    
    elif command == "delete_line":
        if len(args) < 2:
            print("用法: delete_line <文件路径> <行号>")
            sys.exit(1)
        filepath = args[0]
        try:
            line_num = int(args[1])
        except ValueError:
            print(f"错误: 行号必须是整数，收到: {args[1]}")
            sys.exit(1)
        ok, msg = delete_line(filepath, line_num)
        print(msg)
    
    elif command == "replace_line":
        if len(args) < 3:
            print("用法: replace_line <文件路径> <行号> <内容>")
            sys.exit(1)
        filepath = args[0]
        try:
            line_num = int(args[1])
        except ValueError:
            print(f"错误: 行号必须是整数，收到: {args[1]}")
            sys.exit(1)
        content = args[2]
        ok, msg = replace_line(filepath, line_num, content)
        print(msg)
    
    elif command == "search_replace":
        if len(args) < 3:
            print("用法: search_replace <文件路径> <旧内容> <新内容> [--regex]")
            sys.exit(1)
        filepath = args[0]
        old = args[1]
        new = args[2]
        use_regex = "--regex" in args
        ok, msg = search_replace(filepath, old, new, use_regex)
        print(msg)
    
    # ==================== 目录操作 ====================
    elif command == "create_dir":
        if len(args) < 1:
            print("用法: create_dir <目录路径>")
            sys.exit(1)
        ok, msg = create_dir(args[0])
        print(msg)
    
    elif command == "delete_dir":
        if len(args) < 1:
            print("用法: delete_dir <目录路径>")
            sys.exit(1)
        ok, msg = delete_dir(args[0])
        print(msg)
    
    elif command == "list_dir":
        path = args[0] if args else "./"
        ok, msg = list_dir(path)
        print(msg)
    
    elif command == "search_files":
        if len(args) < 1:
            print("用法: search_files <模式> [搜索路径]")
            sys.exit(1)
        pattern = args[0]
        path = args[1] if len(args) > 1 else "./"
        ok, msg = search_files(pattern, path)
        print(msg)
    
    else:
        print(f"未知命令: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
