# 文件操作技能

## 技能介绍

本技能提供文件系统的全面操作能力，涵盖从基础文件管理到精细行级代码编辑的完整功能集。专为编程场景设计，支持对代码文件的精确修改，如插入、删除、替换特定行等。

支持的操作系统：Windows / Linux / macOS

## 命令介绍

### 基础文件操作

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `create_file` | 创建新文件，可指定内容 | `create_file("test.txt", "hello")` |
| `read_file` | 读取文件全部内容 | `read_file("test.txt")` |
| `delete_file` | 删除指定文件 | `delete_file("old.txt")` |
| `copy_file` | 复制文件到目标路径 | `copy_file("a.txt", "backup/a.txt")` |
| `move_file` | 移动文件到目标路径 | `move_file("a.txt", "folder/a.txt")` |
| `append_to_file` | 在文件末尾追加内容 | `append_to_file("log.txt", """多行内容""")` |

### 精细行级操作（编程专用）

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `file_info` | 获取文件信息（行数、大小、修改时间） | `file_info("test.py")` |
| `read_lines` | 读取指定行范围（带行号显示） | `read_lines("test.py", 1, 10)` |
| `insert_line` | 在指定行前插入新内容 | `insert_line("test.py", 5, "# 注释")` |
| `delete_line` | 删除指定行（支持负数从末尾计） | `delete_line("test.py", -1)` |
| `replace_multi_lines` | 替换多行内容（-1 表示最后一行） | `replace_multi_lines("test.py", 3, -1, "new_code")` |
| `search_replace` | 全文搜索替换（支持正则） | `search_replace("test.py", "old", "new")` |

### 目录操作

| 命令 | 功能说明 | 示例 |
|------|----------|------|
| `create_dir` | 创建文件夹 | `create_dir("new_folder")` |
| `delete_dir` | 删除文件夹（含内容） | `delete_dir("old_folder")` |
| `list_dir` | 列出目录内容 | `list_dir("./")` |
| `search_files` | 按名称搜索文件 | `search_files("*.py", "./src")` |

## 使用说明

1. 所有路径支持相对路径和绝对路径
2. 操作前会自动检查权限和路径有效性
3. 删除操作不可逆，请谨慎使用
4. 行号从 1 开始计数，支持负数表示从末尾计数（-1 表示最后一行）

## 精细行操作详解

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
# 读取 1-10 行
read_lines("test.py", 1, 10)

# 读取第 5 行到末尾
read_lines("test.py", 5)

# 读取最后 5 行
read_lines("test.py", -5)
```

### 插入行 `insert_line`
```python
# 在第 3 行前插入（原第3行变第4行）
insert_line("test.py", 3, "    print('debug')")

# 在文件末尾添加（-1 表示最后一行之后）
insert_line("test.py", -1, "# EOF")
```

### 删除行 `delete_line`
```python
# 删除第 5 行
delete_line("test.py", 5)

# 删除最后一行
delete_line("test.py", -1)
```

### 替换多行 `replace_multi_lines`
```python
# 使用三引号包裹多行内容
replace_multi_lines("test.py", 3, 10, """    def new_function():
        print("hello")
        return True""")

# 使用 -1 表示最后一行，替换到文件末尾
replace_multi_lines("test.py", 3, -1, "新内容")

# 替换整个文件（从第1行到最后一行）
replace_multi_lines("test.py", 1, -1, """# 全新内容
print("hello world")""")

# 删除多行（替换为空内容）
replace_multi_lines("test.py", 5, 8, "")
```

### 追加内容 `append_to_file`
```python
# 追加单行内容
append_to_file("log.txt", "新日志行\n")

# 使用三引号追加多行内容
append_to_file("test.py", """
def new_function():
    print("这是追加的函数")
    return True
""")
```

### 搜索替换 `search_replace`
```python
# 普通文本替换
search_replace("test.py", "hello", "world")

# 正则表达式替换（将 function_name 改为 func_function_name）
search_replace("test.py", r"def (\w+)", r"func_\1", use_regex=True)
```

## 使用示例

```python
from scripts import file_ops

# 创建 Python 文件
file_ops.create_file("demo.py", "# Demo\ndef hello():\n    pass\n")

# 查看第 2-3 行
ok, content = file_ops.read_lines("demo.py", 2, 3)
print(content)

# 在函数内添加代码
file_ops.insert_line("demo.py", 3, "    print('Hello World')")

# 替换函数名
file_ops.search_replace("demo.py", "hello", "greet")

# 查看修改结果
ok, content = file_ops.read_file("demo.py")
print(content)
```

## CLI 使用示例

```bash
# 读取文件的前 20 行
python cli.py read_lines test.py 1 20

# 在第 5 行前插入代码
python cli.py insert_line test.py 5 "    x = x + 1"

# 删除最后一行
python cli.py delete_line test.py -1

# 替换所有 print 为 log
python cli.py search_replace test.py "print" "log"

# 正则替换函数名前缀
python cli.py search_replace test.py "def old_" "def new_" --regex
```
