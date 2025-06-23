from flask import json
import openai
import yaml
import os
from memory import init_index, add_memory, search_memory, save_index, get_embedding
from state import load_state, save_state, update_state, get_state, update_past_status, get_past_status
from prompt import build_story_continuation_prompt, build_summary_prompt, build_story_system_prompt, build_summary_system_prompt
import shutil
import re


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def canonicalize_text(text):
    lines = text.strip().splitlines()
    if len(lines) <= 2:
        return ""
    return "\n".join(lines[1:-1]).strip()


def main():
    config = load_config()
    api_key = config["openai_api_key"]
    base_url = config["base_url"]
    model = config["model"]

    os.makedirs("data", exist_ok=True)

    index = init_index()
    state = load_state()

    summary_index = 0

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    story_system_prompt = build_story_system_prompt()
    summary_system_prompt = build_summary_system_prompt()

    while True:
        user_input = input("请输入您的故事续写内容（或输入 'exit' 退出）：\n")
        if user_input.lower() in ["exit", "quit"]:
            break

        # 检索历史记忆概要
        if index.ntotal > 0:
            I, D = search_memory(index, user_input)
            memory_texts = [get_state(state, i) for i in I if i < len(state["history"])]
        else:
            memory_texts = []
        
        last_story_chunk = ""
        for i in range(len(get_past_status(state))):
            if i >= 3:
                break
            last_story_chunk += get_past_status(state)[i] + "\n"


        # 构建故事续写 Prompt
        prompt = build_story_continuation_prompt(memory_texts, last_story_chunk, user_input)

        # 调用 LLM 生成故事
        openai.api_key = api_key
        print("\n正在生成故事续写...\n")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": story_system_prompt},
                      {"role": "user", "content": prompt}
                      ],
            max_tokens=3500,  # 预留安全余量（实测需 3000+）
            temperature=0.7,
            top_p=0.95,
            n=1
        )
        output = canonicalize_text(response.choices[0].message.content)
        story_chunk = json.loads(output)["story_chunk"]
        options = json.loads(output).get("options", [])
        word_count = json.loads(output).get("word_count", 0)
        if options:
            output_text = story_chunk + "\n\n选项：\n" + \
                "\n".join(f"{opt}" for i, opt in enumerate(options))
        else:
            output_text = story_chunk
        print("\n" + output_text + "\n" + f"章节字数：{word_count}\n")


        # 生成简洁概要用于长期记忆
        summary_prompt = build_summary_prompt(output_text)
        summary_response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": summary_system_prompt},
                      {"role": "user", "content": summary_prompt},
                      ],
            # max_tokens=3500,  # 预留安全余量（实测需 3000+）
            # temperature=0.7,
            # top_p=0.95,
            n=1
        )
        summary_output = canonicalize_text(
            summary_response.choices[0].message.content.strip())
        summary_text = json.loads(summary_output)["summary"]

        # 存入长期记忆
        for summary in summary_text:
            print(f"存入长期记忆：{summary.strip()}")
            add_memory(index, summary.strip())
            update_state(state, summary.strip())
        
        update_past_status(state, output_text)
        save_state(state)
        save_index(index)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if os.path.exists("data"):
            shutil.rmtree("data")
        print(f"Error: {e}")
