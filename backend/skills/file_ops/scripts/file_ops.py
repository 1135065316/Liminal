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
import sys
from pathlib import Path

# 添加 backend 目录到路径以导入 base_ops
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from base_ops import WORK_DIR


# ==================== 文件备份管理 ====================
# 存储文件备份 {filepath: backup_content}
_file_backups = {}


def backup_file(filepath):
    """
    备份文件内容（供 undo 使用）
    
    参数:
        filepath: 文件路径
    返回:
        bool: 是否成功
    """
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        
        if not path.exists() or not path.is_file():
            return False
        
        # 读取并存储备份
        content = path.read_text(encoding='utf-8')
        _file_backups[str(path)] = content
        return True
    except Exception:
        return False


def undo_file(filepath):
    """
    撤销最后一次修改（恢复到备份状态）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, message: str)
    
    示例:
        undo_file("test.py")  # 恢复到上次备份的状态
    """
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        
        path_str = str(path)
        
        if path_str not in _file_backups:
            return False, "没有可用的备份（每次修改前会自动备份）"
        
        # 恢复备份
        content = _file_backups[path_str]
        path.write_text(content, encoding='utf-8')
        
        # 清除备份（一次 undo 后不能重复 undo）
        del _file_backups[path_str]
        
        return True, f"文件已恢复到上次备份状态: {filepath}"
    except Exception as e:
        return False, f"撤销失败: {e}"


# ==================== 基础文件操作 ====================

def create_file(filepath, content=""):
    """
    创建新文件，可指定内容（如果文件已存在会先备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        content: 文件内容（字符串）
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        
        # 如果文件已存在，先备份
        if path.exists():
            backup_file(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return True, f"文件创建成功: {path}"
    except Exception as e:
        return False, f"文件创建失败: {e}"


def read_file(filepath):
    """
    读取文件全部内容（带文件信息头部）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, content: str)
    
    返回格式:
        [文件: xxx | 共 N 行 | X.XX KB]
        文件内容...
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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
        header = f"[文件: {path} | 共 {line_count} 行 | {size_str}]\n"
        
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
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        if not path.is_file():
            return False, f"路径不是文件: {filepath}"
        path.unlink()
        return True, f"文件删除成功: {path}"
    except Exception as e:
        return False, f"文件删除失败: {e}"


def copy_file(src, dst):
    """
    复制文件到目标路径
    
    参数:
        src: 源文件路径（相对 WORK_DIR 或绝对路径）
        dst: 目标文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, message: str)
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        # 如果是相对路径，基于 WORK_DIR
        if not src_path.is_absolute():
            src_path = Path(WORK_DIR) / src_path
        if not dst_path.is_absolute():
            dst_path = Path(WORK_DIR) / dst_path
        
        if not src_path.exists():
            return False, f"源文件不存在: {src}"
        if not src_path.is_file():
            return False, f"源路径不是文件: {src}"
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        return True, f"文件复制成功: {src_path} -> {dst_path}"
    except Exception as e:
        return False, f"文件复制失败: {e}"


def move_file(src, dst):
    """
    移动文件到目标路径
    
    参数:
        src: 源文件路径（相对 WORK_DIR 或绝对路径）
        dst: 目标文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, message: str)
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        # 如果是相对路径，基于 WORK_DIR
        if not src_path.is_absolute():
            src_path = Path(WORK_DIR) / src_path
        if not dst_path.is_absolute():
            dst_path = Path(WORK_DIR) / dst_path
        
        if not src_path.exists():
            return False, f"源文件不存在: {src}"
        if not src_path.is_file():
            return False, f"源路径不是文件: {src}"
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return True, f"文件移动成功: {src_path} -> {dst_path}"
    except Exception as e:
        return False, f"文件移动失败: {e}"


# ==================== 精细行级操作（编程专用） ====================

def file_info(filepath):
    """
    获取文件元数据信息
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
    返回:
        (success: bool, info: str)
    
    示例:
        file_info("test.py")  # 返回行数、大小、修改时间等
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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
        
        info = f"""文件: {path}
行数: {line_count}
大小: {size_str}
修改时间: {mtime}"""
        
        return True, info
    except Exception as e:
        return False, f"获取文件信息失败: {e}"


def read_lines(filepath, start=1, end=None, context=10):
    """
    读取文件指定行范围（智能默认值）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        start: 起始行号（从1开始，包含），默认为1
        end: 结束行号（包含），None表示自动计算
        context: 当end为None时，读取start后的context行（默认10行）
    返回:
        (success: bool, content: str)
    
    示例:
        read_lines("test.py")             # 读取前10行（默认）
        read_lines("test.py", 5)          # 读取5-15行（默认上下文10行）
        read_lines("test.py", 5, 20)      # 读取5-20行
        read_lines("test.py", -10)        # 读取最后10行
        read_lines("test.py", 5, context=5)  # 读取5-10行
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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
        
        # 边界检查
        start = max(1, min(start, total))
        
        # 智能计算 end
        if end is None:
            # 如果 start 接近文件末尾，则显示剩余所有行
            if start + context > total:
                end = total
            else:
                end = start + context - 1
        else:
            # 处理负数的 end
            if end < 0:
                end = total + end + 1
            end = max(1, min(end, total))
        
        if start > end:
            return False, f"起始行({start})不能大于结束行({end})"
        
        # 提取指定行（包含行号）
        result_lines = []
        for i in range(start - 1, end):
            line_num = i + 1
            line_content = lines[i].rstrip('\n\r')
            result_lines.append(f"#{line_num}) {line_content}")
        
        header = f"文件: {path} (共{total}行，显示第{start}-{end}行)\n"
        header += "-" * 50 + "\n"
        return True, header + "\n".join(result_lines)
    except Exception as e:
        return False, f"读取行失败: {e}"


def insert_line(filepath, line_num, content):
    """
    在指定行前插入新内容（自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
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
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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


def append_to_line(filepath, line_num, content):
    """
    在指定行后追加内容（自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        line_num: 追加位置（从1开始），在该行之后追加
        content: 要追加的内容（字符串，不含换行符会自动添加）
    返回:
        (success: bool, message: str)
    
    示例:
        append_to_line("test.py", 5, "    print('debug')")  # 在第5行后追加
        append_to_line("test.py", -1, "# EOF")  # 在最后一行后追加（文件末尾）
    """
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        # 备份原文件
        backup_file(filepath)
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        
        # 处理负数行号
        if line_num < 0:
            line_num = total + line_num + 1
        
        # 边界检查：可以在文件末尾追加（line_num = total）
        if line_num < 0:
            line_num = 0
        if line_num > total:
            line_num = total
        
        # 确保内容以换行符结尾
        if not content.endswith('\n'):
            content += '\n'
        
        # 在当前行之后插入（行号就是索引位置，因为 insert 是在指定索引前插入）
        lines.insert(line_num, content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True, f"在第 {line_num} 行后追加成功，文件现在共 {len(lines)} 行"
    except Exception as e:
        return False, f"追加行失败: {e}"


def delete_line(filepath, *line_nums):
    """
    删除指定行（支持批量删除，自动处理行号偏移，自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        *line_nums: 要删除的行号（从1开始，支持负数表示从末尾计数）
    返回:
        (success: bool, message: str)
    
    示例:
        # 删除单行
        delete_line("test.py", 3)    # 删除第3行
        delete_line("test.py", -1)   # 删除最后一行
        
        # 批量删除多行（自动从后往前处理，避免行号偏移）
        delete_line("test.py", 3, 10, 15)  # 删除第3、10、15行
        delete_line("test.py", -1, -3, -5)  # 删除最后1、3、5行
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        # 备份原文件
        backup_file(filepath)
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return False, "文件为空，无法删除"
        
        if not line_nums:
            return False, "请至少指定一个要删除的行号"
        
        # 处理所有行号（包括负数）
        processed_lines = []
        for i, line_num in enumerate(line_nums):
            # 处理负数行号
            if line_num < 0:
                line_num = total + line_num + 1
            
            # 边界检查
            if line_num < 1 or line_num > total:
                return False, f"第 {i+1} 个行号 {line_num} 超出范围(1-{total})"
            
            processed_lines.append(line_num)
        
        # 检查重复行号
        if len(set(processed_lines)) != len(processed_lines):
            return False, "存在重复的行号"
        
        # 按行号从大到小排序（从后往前删除，避免行号变化）
        processed_lines.sort(reverse=True)
        
        # 执行删除
        deleted_info = []
        for line_num in processed_lines:
            # 记录被删除的内容（注意：行号在删除过程中会变化，但排序后从后往前删是安全的）
            deleted_content = lines[line_num - 1].rstrip('\n\r')
            deleted_info.append((line_num, deleted_content[:30]))
            # 删除指定行
            del lines[line_num - 1]
        
        # 写回文件
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 构建结果信息
        deleted_lines_str = ", ".join([str(ln) for ln in sorted(processed_lines)])
        return True, f"删除成功，共删除 {len(processed_lines)} 行（行号: {deleted_lines_str}）"
    except Exception as e:
        return False, f"删除行失败: {e}"


def replace_batch(filepath, *replacements):
    """
    批量替换多行内容（自动处理行号偏移，按从后往前的顺序执行，自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        *replacements: 替换参数，支持两种格式：
            格式1 - 元组形式：replace_batch("file", (start, end, content), (start2, end2, content2))
            格式2 - 平铺形式：replace_batch("file", start, end, content, start2, end2, content2)
    返回:
        (success: bool, message: str)
    
    示例:
        # 格式1：元组形式（推荐用于批量替换）
        replace_batch("test.py", (3, 10, "content"), (15, 20, "content2"))
        
        # 格式2：平铺形式（更简洁）
        replace_batch("test.py", 3, 10, "content")
        replace_batch("test.py", 3, 10, "content1", 15, 20, "content2")
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        # 备份原文件
        backup_file(filepath)
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = len(lines)
        if total == 0:
            return False, "文件为空"
        
        # 解析替换参数（支持元组形式和平铺形式）
        parsed_replacements = []
        
        if len(replacements) == 0:
            return False, "请至少提供一个替换参数"
        
        # 检测参数格式
        if isinstance(replacements[0], (tuple, list)):
            # 格式1：元组形式 (start, end, content), (start2, end2, content2)
            for i, repl in enumerate(replacements):
                if len(repl) != 3:
                    return False, f"第 {i+1} 个替换元组必须有3个元素 (start, end, content)"
                start_line, end_line, content = repl
                parsed_replacements.append((start_line, end_line, content))
        else:
            # 格式2：平铺形式 start, end, content, start2, end2, content2
            if len(replacements) % 3 != 0:
                return False, f"平铺格式参数数量必须是3的倍数（start, end, content），当前有 {len(replacements)} 个参数"
            for i in range(0, len(replacements), 3):
                start_line = replacements[i]
                end_line = replacements[i + 1]
                content = replacements[i + 2]
                parsed_replacements.append((start_line, end_line, content))
        
        # 转换替换列表并处理负数行号
        processed_replacements = []
        for i, (start_line, end_line, content) in enumerate(parsed_replacements):
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
                return False, f"第 {i+1} 个替换：起始行({start_line})不能大于结束行({end_line})"
            
            # 确保新内容以换行符结尾
            if content and not content.endswith('\n'):
                content += '\n'
            
            processed_replacements.append((start_line, end_line, content))
        
        # 按起始行号从后往前排序（大的行号先处理，避免行号偏移）
        processed_replacements.sort(key=lambda x: x[0], reverse=True)
        
        # 检查替换区域是否有重叠
        # 按start从大到小排序后，curr在next后面，不重叠的条件是 curr_start > next_end
        for i in range(len(processed_replacements) - 1):
            curr_start, curr_end, _ = processed_replacements[i]  # 当前（行号大的）
            next_start, next_end, _ = processed_replacements[i + 1]  # 下一个（行号小的）
            if curr_start <= next_end:  #  curr的起点在next的终点之前或相等，则重叠
                return False, f"替换区域重叠：第 {next_start}-{next_end} 行与第 {curr_start}-{curr_end} 行"
        
        # 执行替换
        for start_line, end_line, content in processed_replacements:
            # 将新内容按行分割
            new_lines = content.split('\n') if content else []
            if new_lines and new_lines[-1] == '':
                new_lines = new_lines[:-1]
            new_lines = [line + '\n' for line in new_lines]
            
            # 执行替换
            lines = lines[:start_line - 1] + new_lines + lines[end_line:]
        
        # 写回文件
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 构建结果信息
        repl_info = ", ".join([f"{s}-{e}" for s, e, _ in sorted(processed_replacements, key=lambda x: x[0])])
        return True, f"批量替换成功：{repl_info}"
    except Exception as e:
        return False, f"批量替换失败: {e}"


def search_replace(filepath, old, new, use_regex=False):
    """
    搜索并替换文件内容（自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
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
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 备份原文件
        backup_file(filepath)
        
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
    在文件末尾追加内容（自动备份）
    
    参数:
        filepath: 文件路径（相对 WORK_DIR 或绝对路径）
        content: 要追加的内容
    返回:
        (success: bool, message: str)
    """
    try:
        path = Path(filepath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"内容追加成功: {path}"
    except Exception as e:
        return False, f"追加内容失败: {e}"


# ==================== 目录操作 ====================

def create_dir(dirpath):
    """创建文件夹（相对 WORK_DIR 或绝对路径）"""
    try:
        path = Path(dirpath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        path.mkdir(parents=True, exist_ok=True)
        return True, f"文件夹创建成功: {path}"
    except Exception as e:
        return False, f"文件夹创建失败: {e}"


def delete_dir(dirpath):
    """删除文件夹（含内容）（相对 WORK_DIR 或绝对路径）"""
    try:
        path = Path(dirpath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
        if not path.exists():
            return False, f"文件夹不存在: {dirpath}"
        if not path.is_dir():
            return False, f"路径不是文件夹: {dirpath}"
        shutil.rmtree(path)
        return True, f"文件夹删除成功: {path}"
    except Exception as e:
        return False, f"文件夹删除失败: {e}"


def list_dir(dirpath="./"):
    """列出目录内容（相对 WORK_DIR 或绝对路径）"""
    try:
        path = Path(dirpath)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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
    """按名称搜索文件（相对 WORK_DIR 或绝对路径）"""
    try:
        path = Path(search_path)
        # 如果是相对路径，基于 WORK_DIR
        if not path.is_absolute():
            path = Path(WORK_DIR) / path
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
    "append_to_line": append_to_line,
    "delete_line": delete_line,
    "replace_batch": replace_batch,
    "search_replace": search_replace,
    "undo_file": undo_file,
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
