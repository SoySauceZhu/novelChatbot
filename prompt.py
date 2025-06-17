import os


def load_prompt_from_file(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, 'prompts', filename)
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def build_story_system_prompt():
    return load_prompt_from_file('story_system.txt')


def build_summary_system_prompt():
    return load_prompt_from_file('summary_system.txt')


def build_story_continuation_prompt(history_summaries, last_story_chunk, user_input):
    template = load_prompt_from_file('story_continuation.txt')
    history_str = '\n'.join(f'- {s}' for s in history_summaries)
    return template.format(
        history_summaries=history_str,
        last_story_chunk=last_story_chunk,
        user_input=user_input
    )


def build_summary_prompt(chunk):
    template = load_prompt_from_file('summary.txt')
    return template.format(chunk=chunk)
