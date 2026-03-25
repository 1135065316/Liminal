#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent - 极简自动化执行
基于 'bash is all you need' 理念，输入任务，自动调用 bash/skill 完成
"""

import sys
from base_ops import WORK_DIR, run_command, get_skill_commands_help, parse_ai_response
from deepseek import chat, check_api_key
from conversation_logger import (
    generate_conversation_id,
    save_conversation,
    get_conversation_summary
)
from context_manager import (
    check_context_limit,
    Interruptible
)


def main():
    # 检查API密钥是否已配置
    if not check_api_key():
        print("请先配置 DEEPSEEK_API_KEY")
        return

    # 生成对话ID（基于开始时间的时间戳）
    conversation_id = generate_conversation_id()
    print(f"对话ID: {conversation_id}\n")

    # 获取 skill 命令帮助
    skill_help = get_skill_commands_help()

    # 设置系统提示词
    system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
你可以使用两种类型的命令：
1. **Bash 命令**: 普通的 shell 命令，如 `ls -la`, `cat file.txt`
2. **Skill 命令**: 预定义的文件/代码操作函数，格式为 `函数名(参数1, 参数2, ...)`

输出格式（严格JSON）:
{{"command": "要执行的bash或skill命令", "thought": "你的想法/说明（可选）"}}

规则:
- 必须输出合法的JSON格式
- command 字段为纯命令，不含任何解释
- thought 字段可空，用于表达你的想法（会显示给用户）
- 如果任务完成，command 填 "DONE:结果描述"
- 如果无法完成，command 填 "FAIL:原因"

{skill_help}"""

    messages = [{"role": "system", "content": system_msg}]

    # 获取初始输入（命令行或交互式）
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        messages.append({"role": "user", "content": user_input})
    else:
        user_input = None  # 将在循环中获取

    try:
        round_num = 0
        while True:
            round_num += 1
            
            # 获取用户输入（首次交互式或任务完成后）
            if user_input is None:
                user_input = input("> ").strip()
                if not user_input:
                    break
                messages.append({"role": "user", "content": user_input})
                user_input = ""  # 标记为已处理，进入 AI 自动执行模式
            
            # 检查上下文长度
            is_limited, current_tokens, token_limit = check_context_limit(messages)
            if is_limited:
                break
            
            # 可中断的 API 调用
            with Interruptible(messages, "API请求") as op:
                response = chat(messages)
            if op.interrupted:
                break
            
            # 解析 AI 响应
            command, thought, is_json = parse_ai_response(response)
            # 显示 AI 的想法（如果有）
            if thought:
                print(f"  [🤖] {thought}")
            
            # 处理 DONE/FAIL
            if command.startswith("DONE:"):
                result = command[5:] if len(command) > 5 else "任务完成"
                print(f"✅ 完成: {result}")
                messages.append({"role": "assistant", "content": response})
                user_input = None  # 继续对话，下一轮获取输入
                continue
            
            if command.startswith("FAIL:"):
                reason = command[5:] if len(command) > 5 else "未知原因"
                print(f"❌ 失败: {reason}")
                messages.append({"role": "assistant", "content": response})
                user_input = None  # 继续对话，下一轮获取输入
                continue
            
            # 可中断的命令执行
            with Interruptible(messages, "命令执行") as op:
                output = run_command(command)
            if op.interrupted:
                break
            
            print(f"  -> {output[:200]}{'...' if len(output) > 200 else ''}\n")
            
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"执行结果:\n{output}\n\n请继续:"})
            
            # 显示当前 token 使用情况
            print(f"[上下文: {current_tokens}/{token_limit} tokens]")
            # user_input 保持原值，下一轮继续 AI 自动执行
    except KeyboardInterrupt:
        print("\n\n用户强制退出，正在保存对话...")
        messages.append({"role": "user", "content": "[用户强制退出]"})
    finally:
        # 保存对话记录
        file_path = save_conversation(conversation_id, messages)
        print(f"\n对话已保存: {file_path}")
        print(get_conversation_summary(messages))


if __name__ == "__main__":
    main()
