#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作技能 - 核心实现
提供文件/文件夹的增删改查功能，支持精细的行级操作
"""

import os
import shutil
import glob
import re
from pathlib import Path


# ==================== 基础文件操作 ====================

def create_file(filepath, content=""):
    """
    创建新文件，可指定内容
    
    参数:
        filepath: 文件路径
        content: 文件内容（字符串）
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return True, f"文件创建成功: {filepath}"
    except Exception as e:
        return False, f"文件创建失败: {e}"


def read_file(filepath):
    """
    读取文件全部内容（带文件信息头部）
    
    参数:
        filepath: 文件路径
    返回:
        (success: bool, content: str)
    
    返回格式:
        [文件: xxx | 共 N 行 | X.XX KB]
        文件内容...
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        if not path.is_file():
            return False, f"路径不是文件: {filepath}"
        
        # 读取内容
        content = path.read_text(encoding='utf-8')
        
        # 统计行数
        line_count = content.count('\n')
        if content and not content.endswith('\n'):
            line_count += 1
        
        # 格式化大小
        size_bytes = path.stat().st_size
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes / 1024 / 1024:.2f} MB"
        
        # 添加信息头部
        header = f"[文件: {filepath} | 共 {line_count} 行 | {size_str}]\n"
        
        # 为每行添加行号
        lines = content.split('\n')
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"#{i}) {line}")
        numbered_content = '\n'.join(numbered_lines)
        
        return True, header + numbered_content
    except Exception as e:
        return False, f"文件读取失败: {e}"


def delete_file(filepath):
    """
    删除指定文件
    
    参数:
        filepath: 文件路径
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        if not path.is_file():
            return False, f"路径不是文件: {filepath}"
        path.unlink()
        return True, f"文件删除成功: {filepath}"
    except Exception as e:
        return False, f"文件删除失败: {e}"


def copy_file(src, dst):
    """
    复制文件到目标路径
    
    参数:
        src: 源文件路径
        dst: 目标文件路径
    返回:
        (success: bool, message: str)
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False, f"源文件不存在: {src}"
        if not src_path.is_file():
            return False, f"源路径不是文件: {src}"
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        return True, f"文件复制成功: {src} -> {dst}"
    except Exception as e:
        return False, f"文件复制失败: {e}"


def move_file(src, dst):
    """
    移动文件到目标路径
    
    参数:
        src: 源文件路径
        dst: 目标文件路径
    返回:
        (success: bool, message: str)
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False, f"源文件不存在: {src}"
        if not src_path.is_file():
            return False, f"源路径不是文件: {src}"
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return True, f"文件移动成功: {src} -> {dst}"
    except Exception as e:
        return False, f"文件移动失败: {e}"


# ==================== 精细行级操作（编程专用） ====================

def file_info(filepath):
    """
    获取文件元数据信息
    
    参数:
        filepath: 文件路径
    返回:
        (success: bool, info: str)
    
    示例:
        file_info("test.py")  # 返回行数、大小、修改时间等
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        if not path.is_file():
            return False, f"路径不是文件: {filepath}"
        
        # 获取文件统计信息
        stat = path.stat()
        size_bytes = stat.st_size
        
        # 格式化文件大小
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes / 1024 / 1024:.2f} MB"
        
        # 统计行数
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            line_count = sum(1 for _ in f)
        
        # 格式化修改时间
        from datetime import datetime
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        info = f"""文件: {filepath}
行数: {line_count}
大小: {size_str}
修改时间: {mtime}"""
        
        return True, info
    except Exception as e:
        return False, f"获取文件信息失败: {e}"


def read_lines(filepath, start=1, end=None):
    """
    读取文件指定行范围
    
    参数:
        filepath: 文件路径
        start: 起始行号（从1开始，包含）
        end: 结束行号（包含），None表示到文件末尾
    返回:
        (success: bool, content: str)
    
    示例:
        read_lines("test.py", 1, 10)      # 读取1-10行
        read_lines("test.py", 5, 5)       # 只读第5行
        read_lines("test.py", 20)         # 读取20行到末尾
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return True, "(空文件)"
        
        # 处理负数行号（从末尾计数）
        if start < 0:
            start = total + start + 1
        if end is not None and end < 0:
            end = total + end + 1
        
        # 边界检查
        start = max(1, min(start, total))
        if end is None:
            end = total
        else:
            end = max(1, min(end, total))
        
        if start > end:
            return False, f"起始行({start})不能大于结束行({end})"
        
        # 提取指定行（包含行号）
        result_lines = []
        for i in range(start - 1, end):
            line_num = i + 1
            line_content = lines[i].rstrip('\n\r')
            result_lines.append(f"#{line_num}) {line_content}")
        
        header = f"文件: {filepath} (共{total}行，显示第{start}-{end}行)\n"
        header += "-" * 50 + "\n"
        return True, header + "\n".join(result_lines)
    except Exception as e:
        return False, f"读取行失败: {e}"


def insert_line(filepath, line_num, content):
    """
    在指定行前插入新内容
    
    参数:
        filepath: 文件路径
        line_num: 插入位置（从1开始），在该行之前插入
        content: 要插入的内容（字符串，不含换行符会自动添加）
    返回:
        (success: bool, message: str)
    
    示例:
        insert_line("test.py", 5, "# 这是新插入的注释")
        insert_line("test.py", -1, "最后一行新内容")  # 在末尾添加
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        
        # 处理负数行号
        if line_num < 0:
            line_num = total + line_num + 2  # -1 表示在最后一行后插入
        
        # 确保内容以换行符结尾
        if not content.endswith('\n'):
            content += '\n'
        
        # 边界检查：可以在文件末尾插入（line_num = total + 1）
        if line_num < 1:
            line_num = 1
        if line_num > total + 1:
            line_num = total + 1
        
        # 插入新行
        lines.insert(line_num - 1, content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True, f"在第 {line_num} 行前插入成功，文件现在共 {len(lines)} 行"
    except Exception as e:
        return False, f"插入行失败: {e}"


def delete_line(filepath, line_num):
    """
    删除指定行
    
    参数:
        filepath: 文件路径
        line_num: 要删除的行号（从1开始，支持负数表示从末尾计数）
    返回:
        (success: bool, message: str)
    
    示例:
        delete_line("test.py", 3)    # 删除第3行
        delete_line("test.py", -1)   # 删除最后一行
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return False, "文件为空，无法删除"
        
        # 处理负数行号
        if line_num < 0:
            line_num = total + line_num + 1
        
        if line_num < 1 or line_num > total:
            return False, f"行号 {line_num} 超出范围(1-{total})"
        
        # 记录被删除的内容
        deleted_content = lines[line_num - 1].rstrip('\n\r')
        
        # 删除指定行
        del lines[line_num - 1]
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True, f"删除第 {line_num} 行成功，删除内容: {deleted_content[:50]}{'...' if len(deleted_content) > 50 else ''}"
    except Exception as e:
        return False, f"删除行失败: {e}"


def replace_line(filepath, line_num, content):
    """
    替换指定行的内容
    
    参数:
        filepath: 文件路径
        line_num: 要替换的行号（从1开始，支持负数）
        content: 新内容（字符串，不含换行符）
    返回:
        (success: bool, message: str)
    
    示例:
        replace_line("test.py", 5, "    print('new')")
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return False, "文件为空"
        
        # 处理负数行号
        if line_num < 0:
            line_num = total + line_num + 1
        
        if line_num < 1 or line_num > total:
            return False, f"行号 {line_num} 超出范围(1-{total})"
        
        # 记录旧内容
        old_content = lines[line_num - 1].rstrip('\n\r')
        
        # 确保新内容以换行符结尾
        if not content.endswith('\n'):
            content += '\n'
        
        # 替换
        lines[line_num - 1] = content
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True, f"替换第 {line_num} 行成功\n原内容: {old_content[:50]}{'...' if len(old_content) > 50 else ''}"
    except Exception as e:
        return False, f"替换行失败: {e}"


def replace_multi_lines(filepath, start_line, end_line, content):
    """
    替换多行内容（将指定范围的行替换为新内容）
    
    参数:
        filepath: 文件路径
        start_line: 起始行号（从1开始，包含），支持 -1 表示最后一行
        end_line: 结束行号（包含），支持 -1 表示最后一行，必须 >= start_line
        content: 新内容（字符串，可包含多行）
    返回:
        (success: bool, message: str)
    
    示例:
        replace_multi_lines("test.py", 3, 10, "    # 新代码块\n    pass")
        replace_multi_lines("test.py", 1, -1, "新内容")  # 替换整个文件
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return False, "文件为空"
        
        # 处理负数行号
        if start_line < 0:
            start_line = total + start_line + 1
        if end_line < 0:
            end_line = total + end_line + 1
        
        # 边界检查
        if start_line < 1:
            start_line = 1
        if end_line > total:
            end_line = total
        
        if start_line > end_line:
            return False, f"起始行({start_line})不能大于结束行({end_line})"
        
        # 确保新内容以换行符结尾（如果不是空内容）
        if content and not content.endswith('\n'):
            content += '\n'
        
        # 将新内容按行分割
        new_lines = content.split('\n') if content else []
        # split 会产生一个空字符串作为最后一个元素（如果内容以换行符结尾）
        if new_lines and new_lines[-1] == '':
            new_lines = new_lines[:-1]
        
        # 为新内容添加换行符
        new_lines = [line + '\n' for line in new_lines]
        
        # 构建新文件内容：保留起始行之前的行 + 新内容 + 结束行之后的行
        new_file_lines = lines[:start_line - 1] + new_lines + lines[end_line:]
        
        # 写回文件
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_file_lines)
        
        replaced_count = end_line - start_line + 1
        new_count = len(new_lines)
        return True, f"替换第 {start_line}-{end_line} 行成功（替换 {replaced_count} 行，新增 {new_count} 行）"
    except Exception as e:
        return False, f"替换多行失败: {e}"


def search_replace(filepath, old, new, use_regex=False):
    """
    搜索并替换文件内容
    
    参数:
        filepath: 文件路径
        old: 要搜索的内容（或正则表达式）
        new: 替换为的内容
        use_regex: 是否使用正则表达式，默认False
    返回:
        (success: bool, message: str)
    
    示例:
        search_replace("test.py", "hello", "world")                    # 普通替换
        search_replace("test.py", r"def\s+(\w+)", r"function \1", True) # 正则替换
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        if use_regex:
            # 正则替换
            new_content, count = re.subn(old, new, content)
        else:
            # 普通替换
            count = content.count(old)
            new_content = content.replace(old, new)
        
        if count == 0:
            return False, f"未找到匹配内容: {old}"
        
        # 写回文件
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"替换成功，共替换 {count} 处"
    except Exception as e:
        return False, f"搜索替换失败: {e}"


def append_to_file(filepath, content):
    """
    在文件末尾追加内容
    
    参数:
        filepath: 文件路径
        content: 要追加的内容
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"内容追加成功: {filepath}"
    except Exception as e:
        return False, f"追加内容失败: {e}"


# ==================== 目录操作 ====================

def create_dir(dirpath):
    """创建文件夹"""
    try:
        path = Path(dirpath)
        path.mkdir(parents=True, exist_ok=True)
        return True, f"文件夹创建成功: {dirpath}"
    except Exception as e:
        return False, f"文件夹创建失败: {e}"


def delete_dir(dirpath):
    """删除文件夹（含内容）"""
    try:
        path = Path(dirpath)
        if not path.exists():
            return False, f"文件夹不存在: {dirpath}"
        if not path.is_dir():
            return False, f"路径不是文件夹: {dirpath}"
        shutil.rmtree(path)
        return True, f"文件夹删除成功: {dirpath}"
    except Exception as e:
        return False, f"文件夹删除失败: {e}"


def list_dir(dirpath="./"):
    """列出目录内容"""
    try:
        path = Path(dirpath)
        if not path.exists():
            return False, f"文件夹不存在: {dirpath}"
        if not path.is_dir():
            return False, f"路径不是文件夹: {dirpath}"
        
        items = []
        for item in path.iterdir():
            item_type = "📁" if item.is_dir() else "📄"
            size = ""
            if item.is_file():
                size_bytes = item.stat().st_size
                if size_bytes < 1024:
                    size = f"({size_bytes} B)"
                elif size_bytes < 1024 * 1024:
                    size = f"({size_bytes / 1024:.1f} KB)"
                else:
                    size = f"({size_bytes / 1024 / 1024:.1f} MB)"
            items.append(f"{item_type} {item.name} {size}")
        
        if not items:
            return True, "文件夹为空"
        return True, "\n".join(items)
    except Exception as e:
        return False, f"列出目录失败: {e}"


def search_files(pattern, search_path="./"):
    """按名称搜索文件"""
    try:
        path = Path(search_path)
        if not path.exists():
            return False, f"搜索路径不存在: {search_path}"
        if not path.is_dir():
            return False, f"搜索路径不是文件夹: {search_path}"
        
        matches = list(Path(path).rglob(pattern))
        
        if not matches:
            return True, f"未找到匹配的文件: {pattern}"
        
        results = []
        for match in matches:
            rel_path = match.relative_to(path)
            item_type = "📁" if match.is_dir() else "📄"
            results.append(f"{item_type} {rel_path}")
        
        return True, f"找到 {len(results)} 个匹配项:\n" + "\n".join(results)
    except Exception as e:
        return False, f"搜索文件失败: {e}"


# 命令映射表
COMMANDS = {
    # 基础操作
    "create_file": create_file,
    "read_file": read_file,
    "delete_file": delete_file,
    "copy_file": copy_file,
    "move_file": move_file,
    "append_to_file": append_to_file,
    # 精细行操作
    "file_info": file_info,
    "read_lines": read_lines,
    "insert_line": insert_line,
    "delete_line": delete_line,
    "replace_line": replace_line,
    "replace_multi_lines": replace_multi_lines,
    "search_replace": search_replace,
    # 目录操作
    "create_dir": create_dir,
    "delete_dir": delete_dir,
    "list_dir": list_dir,
    "search_files": search_files,
}


def execute_command(command_name, *args, **kwargs):
    """
    执行指定命令
    
    参数:
        command_name: 命令名称
        *args: 位置参数
        **kwargs: 关键字参数
    返回:
        (success: bool, result: str)
    """
    if command_name not in COMMANDS:
        return False, f"未知命令: {command_name}"
    
    func = COMMANDS[command_name]
    return func(*args, **kwargs)


if __name__ == "__main__":
    # 简单测试
    print("=== 文件操作技能测试 ===")
    
    # 基础操作测试
    create_dir("test_folder")
    create_file("test_folder/demo.py", "# 测试文件\nline1\nline2\nline3\n")
    
    print("\n1. 读取全部内容:")
    print(read_file("test_folder/demo.py")[1])
    
    print("\n2. 读取指定行范围(1-2):")
    print(read_lines("test_folder/demo.py", 1, 2)[1])
    
    print("\n3. 在第2行前插入新行:")
    print(insert_line("test_folder/demo.py", 2, "# 插入的注释")[1])
    
    print("\n4. 查看插入后的内容:")
    print(read_lines("test_folder/demo.py", 1, 5)[1])
    
    print("\n5. 替换第4行:")
    print(replace_line("test_folder/demo.py", 4, "line2_modified")[1])
    
    print("\n6. 删除最后一行:")
    print(delete_line("test_folder/demo.py", -1)[1])
    
    print("\n7. 搜索替换:")
    print(search_replace("test_folder/demo.py", "line2_modified", "LINE2_MODIFIED")[1])
    
    print("\n8. 最终内容:")
    print(read_file("test_folder/demo.py")[1])
    
    # 清理
    delete_dir("test_folder")
    print("\n测试完成，已清理")
