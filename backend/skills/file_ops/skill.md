# 文件操作技能

## 技能介绍

本技能提供文件系统的全面操作能力，涵盖从基础文件管理到精细行级代码编辑的完整功能集。专为编程场景设计，支持对代码文件的精确修改，如插入、删除、替换特定行等。

支持的操作系统：Windows / Linux / macOS

## 注意事项

1. 诸如replace_batch之类的操作可能导致行号变动, 可以一次性替换多段, 操作完之后应重新read_file查看新的内容结构
2. 所有路径支持相对路径和绝对路径
3. 操作前会自动检查权限和路径有效性
4. 删除操作不可逆，请谨慎使用
5. 行号从 1 开始计数，支持负数表示从末尾计数（-1 表示最后一行）

## 命令介绍

### 基础文件操作

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `create_file` | 创建新文件，可指定内容 | `create_file("test.txt", """hello""")` |
| `read_file` | 读取文件全部内容 | `read_file("test.txt")` |
| `delete_file` | 删除指定文件 | `delete_file("old.txt")` |
| `delete_files` | 批量删除多个文件 | `delete_files("a.txt", "b.txt", "c.txt")` |
| `delete_files_by_pattern` | 按通配符模式删除文件 | `delete_files_by_pattern("*.log", "./logs")` |
| `copy_file` | 复制文件到目标路径 | `copy_file("a.txt", "backup/a.txt")` |
| `move_file` | 移动文件到目标路径 | `move_file("a.txt", "folder/a.txt")` |
| `append_to_file` | 在文件末尾追加内容 | `append_to_file("log.txt", """多行内容""")` |

### 精细行级操作（编程专用）

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `file_info` | 获取文件信息（行数、大小、修改时间） | `file_info("test.py")` |
| `read_lines` | 读取指定行范围（智能默认值） | `read_lines("test.py", 1, 50)` |
| `insert_line` | 在指定行前插入新内容 | `insert_line("test.py", 5, """# 注释""")` |
| `append_to_line` | 在指定行后追加内容 | `append_to_line("test.py", 5, """print("debug")""")` |
| `delete_line` | 删除指定行/批量删除（支持负数） | `delete_line("test.py", 3, 10, 15)` |
| `replace_batch` | 批量替换多行（自动处理行号偏移） | `replace_batch("test.py", (3, 10, """代码"""), (15, 20, """代码2"""))` |
| `search_replace` | 全文搜索替换（支持正则） | `search_replace("test.py", "old", "new")` |
| `undo_file` | 撤销最后一次修改（自动备份） | `undo_file("test.py")` |

### 目录操作

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `create_dir` | 创建文件夹 | `create_dir("new_folder")` |
| `delete_dir` | 删除文件夹（含内容） | `delete_dir("old_folder")` |
| `list_dir` | 列出目录内容 | `list_dir("./")` |
| `search_files` | 按名称搜索文件 | `search_files("*.py", "./src")` |

## 操作详解

### 获取文件信息 `file_info`
```python
# 查看文件行数、大小、修改时间
file_info("test.py")
# 输出:
# 文件: test.py
# 行数: 50
# 大小: 2.34 KB
# 修改时间: 2026-03-22 21:10:42
```

### 读取行范围 `read_lines`
```python
# 默认读取前10行（不传参数或只传start）
read_lines("test.py")
read_lines("test.py", 5)        # 从第5行开始，读取10行
read_lines("test.py", 5, context=20)  # 从第5行开始，读取20行

# 指定范围读取
read_lines("test.py", 1, 50)    # 读取1-50行

# 读取最后几行
read_lines("test.py", -10)      # 读取最后10行
read_lines("test.py", -5, -1)   # 读取倒数5行到倒数1行
```

### 插入行 `insert_line`
```python
# 在第 3 行前插入（原第3行变第4行）
insert_line("test.py", 3, """    print('debug')""")

# 插入多行内容（如添加文档字符串）
insert_line("test.py", 3, '''    """
    函数说明文档
    参数: x - 输入值
    返回: 结果值
    """''')

# 在文件末尾添加（-1 表示最后一行之后）
insert_line("test.py", -1, """# EOF""")
```

### 追加行 `append_to_line`
```python
# 在第 5 行后追加
append_to_line("test.py", 5, """    print('debug')""")

# 追加多行内容
append_to_line("test.py", 5, '''    # 初始化
    x = 0
    y = 0''')

# 在最后一行后追加（文件末尾）
append_to_line("test.py", -1, """# 文件结束""")
```

### 撤销修改 `undo_file`
```python
# 撤销最后一次修改（恢复到上次备份）
undo_file("test.py")

# 注意：每次修改操作（insert/delete/replace等）会自动备份
# undo_file 只能撤销最后一次修改，执行后会清除备份
```

### 删除行 `delete_line`
```python
# 删除单行
delete_line("test.py", 5)     # 删除第5行
delete_line("test.py", -1)    # 删除最后一行

# 批量删除多行
delete_line("test.py", 3, 10, 15)   # 删除第3、10、15行
delete_line("test.py", -1, -3, -5)  # 删除最后1、3、5行
```

### 批量替换 `replace_batch`
```python
# 格式1：元组形式（推荐，清晰明了）
replace_batch("test.py", (3, 10, """new content"""))
replace_batch("test.py", (3, 10, """content1"""), (15, 20, """content2"""))

# 格式2：平铺形式（更简洁）
replace_batch("test.py", 3, 10, """new content""")
replace_batch("test.py", 3, 10, """content1""", 15, 20, """content2""")

# 单次替换多行内容
replace_batch("test.py", 3, 10, """    def new_function():
        print("hello")
        return True""")

# 批量替换多个区域
replace_batch("test.py",
    (3, 10, """    def func1():
        pass"""),
    (15, 20, """    def func2():
        pass""")
)

# 替换整个文件
replace_batch("test.py", 1, -1, """# 全新内容
print("hello world")""")

# 删除多行（替换为空内容）
replace_batch("test.py", 5, 8, "")
```

### 追加内容 `append_to_file`
```python
# 追加单行内容
append_to_file("log.txt", """新日志行\n""")

# 追加多行内容（在文件末尾添加新函数）
append_to_file("test.py", '''
def new_function():
    """新添加的函数"""
    print("这是追加的函数")
    return True
''')

# 追加类定义
append_to_file("test.py", '''
class MyClass:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
''')
```
```

### 搜索替换 `search_replace`
```python
# 普通文本替换
search_replace("test.py", "hello", "world")

# 替换多行文本（如修改函数体）
search_replace("test.py", 
    """def old_func():\n    pass""",
    """def old_func():\n    print('updated')\n    return True""")

# 正则表达式替换（批量修改函数名前缀）
search_replace("test.py", r"def (\w+)", r"func_\1", use_regex=True)

# 正则替换并添加参数类型注解
search_replace("test.py", 
    r"def (\w+)\(x\):", 
    r"def \1(x: int) -> int:", 
    use_regex=True)
```

