#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能命令调度器
解析 agent 输出的 skill 命令，自动路由到对应技能

命令格式: create_file("test.txt", "hello")
"""

import os
import sys
import re
from pathlib import Path

# skills 目录路径
SKILLS_DIR = Path(__file__).parent / "skills"


def parse_command(cmd_str):
    """
    解析命令字符串
    
    参数:
        cmd_str: 如 'create_file("test.txt", "hello")'
    返回:
        (func_name, args_list, kwargs_dict) 或 None
    """
    cmd_str = cmd_str.strip()
    
    # 匹配函数调用格式: func_name(args)，支持多行和超长内容
    # 使用 [\s\S]*? 非贪婪匹配，确保能处理不完整命令
    pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([\s\S]*)\)\s*$'
    match = re.match(pattern, cmd_str)
    
    if not match:
        # 检查是否是被截断的不完整命令（以函数名开头，有左括号但缺少右括号）
        incomplete_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\([\s\S]*$'
        incomplete_match = re.match(incomplete_pattern, cmd_str)
        if incomplete_match:
            # 命令不完整，返回特殊标记
            return None  # 不处理不完整命令，让调用方知道解析失败
        return None
    
    func_name = match.group(1)
    args_str = match.group(2).strip()
    
    # 解析参数
    args = _parse_args(args_str) if args_str else []
    kwargs = {}  # 暂不支持 kwargs 解析
    
    return func_name, args, kwargs


def _parse_args(args_str):
    """
    解析参数列表，正确处理引号内的逗号和转义引号
    支持双引号、单引号和反引号（模板字符串）
    
    示例:
        '"test.txt", "hello world"' -> ['test.txt', 'hello world']
        '"demo.py", 1, 10' -> ['demo.py', 1, 10]
        '"content \\"quoted\\" end"' -> ['content "quoted" end']
        '`content with, commas` -> ['content with, commas']
    """
    args = []
    current = ""
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(args_str):
        char = args_str[i]
        
        if char == '\\' and i + 1 < len(args_str) and args_str[i + 1] in ('"', "'", '`'):
            # 转义的引号，保留反斜杠，跳过下一个字符的特殊处理
            current += char  # 保留反斜杠
            i += 1
            current += args_str[i]  # 保留引号
        elif char in ('"', "'", '`'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
                current += char
            else:
                current += char
        elif char == ',' and not in_quotes:
            # 参数分隔
            if current.strip():
                args.append(_convert_arg(current.strip()))
            current = ""
        else:
            current += char
        
        i += 1
    
    # 处理最后一个参数
    if current.strip():
        args.append(_convert_arg(current.strip()))
    
    return args


def _convert_arg(arg):
    """转换参数为合适类型，处理转义字符"""
    arg = arg.strip()
    
    # 字符串：去除外层引号（支持双引号、单引号、反引号），并处理转义字符
    if (len(arg) >= 2 and arg[0] == arg[-1] and arg[0] in ('"', "'", '`')):
        inner = arg[1:-1]
        # 处理转义字符
        inner = inner.replace('\\n', '\n')  # 换行
        inner = inner.replace('\\t', '\t')  # 制表符
        inner = inner.replace('\\\\', '\\')  # 反斜杠（必须在其他转义之后）
        inner = inner.replace('\\"', '"')   # 双引号
        inner = inner.replace("\\'", "'")   # 单引号
        inner = inner.replace('\\`', '`')   # 反引号
        return inner
    
    # 布尔值
    if arg == 'True':
        return True
    if arg == 'False':
        return False
    if arg == 'None':
        return None
    
    # 数字
    try:
        if '.' in arg:
            return float(arg)
        return int(arg)
    except ValueError:
        pass
    
    # 保持原样
    return arg


def scan_skills():
    """
    扫描 skills 目录，收集所有可用命令
    
    返回:
        {命令名: (技能模块, 函数)} 的字典
    """
    commands = {}
    
    if not SKILLS_DIR.exists():
        return commands
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        scripts_init = skill_dir / "scripts" / "__init__.py"
        if not scripts_init.exists():
            continue
        
        skill_name = skill_dir.name
        
        try:
            # 动态导入
            skill_scripts = skill_dir / "scripts"
            sys.path.insert(0, str(skill_scripts))
            
            # 导入 file_ops 模块
            import file_ops
            
            # 如果模块有 COMMANDS 字典，使用它
            if hasattr(file_ops, 'COMMANDS'):
                for cmd_name, func in file_ops.COMMANDS.items():
                    commands[cmd_name] = (skill_name, func)
            
            sys.path.pop(0)
            
        except Exception as e:
            print(f"  [SkillDispatcher] 加载技能 {skill_name} 失败: {e}")
            continue
    
    return commands


def execute_skill_command(cmd_str):
    """
    执行 skill 命令
    
    参数:
        cmd_str: 命令字符串，如 'create_file("test.txt", "hello")'
    返回:
        (success: bool, result: str)
    """
    parsed = parse_command(cmd_str)
    if not parsed:
        # 检查是否是不完整命令
        incomplete_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\([\s\S]*$'
        if re.match(incomplete_pattern, cmd_str.strip()):
            return False, "命令不完整（可能是内容太长被截断），请缩短内容后重试"
        return False, f"命令格式错误"
    
    func_name, args, kwargs = parsed
    
    # 扫描可用技能
    commands = scan_skills()
    
    if func_name not in commands:
        available = ", ".join(sorted(commands.keys())) if commands else "无"
        return False, f"未知命令: {func_name}\n可用命令: {available}"
    
    skill_name, func = commands[func_name]
    
    try:
        # 执行函数
        result = func(*args, **kwargs)
        
        # 如果函数返回元组 (success, message)，直接传递
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], bool):
            return result
        else:
            return True, str(result)
            
    except TypeError as e:
        return False, f"参数错误: {e}"
    except Exception as e:
        return False, f"执行命令失败: {e}"


def is_skill_command(cmd_str):
    """
    判断是否为 skill 命令（函数调用格式）
    
    参数:
        cmd_str: 命令字符串
    返回:
        bool
    """
    # 匹配函数调用格式: func_name(args)，支持多行内容
    # 匹配: 函数名(参数)，参数可以包含换行符
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\([\s\S]*\)\s*$'
    return bool(re.match(pattern, cmd_str.strip()))


def get_skill_help_text():
    """
    获取所有 skill 的帮助文本（用于系统提示）
    
    格式:
    可用 Skill 列表:
      - file_ops
      - xxx
    
    file_ops:
    [skill.md 内容]
    
    xxx:
    [skill.md 内容]
    """
    if not SKILLS_DIR.exists():
        return "暂无可用 skill"
    
    # 收集所有 skill
    skills = []
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "skill.md"
        if skill_md.exists():
            skills.append(skill_dir.name)
    
    if not skills:
        return "暂无可用 skill"
    
    lines = ["可用 Skill 列表:"]
    for skill_name in sorted(skills):
        lines.append(f"  - {skill_name}")
    
    lines.append("")  # 空行
    
    # 为每个 skill 添加详细说明
    for skill_name in sorted(skills):
        skill_md = SKILLS_DIR / skill_name / "skill.md"
        if skill_md.exists():
            lines.append(f"{skill_name}:")
            try:
                content = skill_md.read_text(encoding='utf-8')
                # 缩进每一行，作为代码块展示
                for line in content.split('\n'):
                    lines.append(f"  {line}")
            except Exception:
                lines.append("  [无法读取 skill.md]")
            lines.append("")  # 空行分隔
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("=== Skill Dispatcher 测试 ===\n")
    
    # 测试命令解析
    test_cmds = [
        'create_file("test.txt", "hello")',
        'read_lines("demo.py", 1, 10)',
        'delete_line("file.txt", -1)',
        'list_dir("./")',
    ]
    
    print("1. 命令解析测试:")
    for cmd in test_cmds:
        parsed = parse_command(cmd)
        if parsed:
            print(f"  {cmd}")
            print(f"    -> 函数: {parsed[0]}, 参数: {parsed[1]}")
    
    print("\n2. 扫描技能:")
    commands = scan_skills()
    print(f"  发现 {len(commands)} 个命令")
    for cmd_name, (skill_name, _) in commands.items():
        print(f"  - {cmd_name} (来自 {skill_name})")
    
    print("\n3. 执行测试:")
    result = execute_skill_command('create_file("_test_dispatch.txt", "hello from dispatcher")')
    print(f"  create_file: {result}")
    
    result = execute_skill_command('read_file("_test_dispatch.txt")')
    print(f"  read_file: {result}")
    
    result = execute_skill_command('delete_file("_test_dispatch.txt")')
    print(f"  delete_file: {result}")
