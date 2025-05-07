import json
import os
import re

# 翻译缓存字典
translation_cache = {}

# 缓存文件路径
CACHE_FILE = 'translation.json'

def load_cache():
    global translation_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                translation_cache = json.load(f)
        except Exception as e:
            print(f"Load cache failed: {e}")
            translation_cache = {}

def translate(query):
    # 检查缓存
    if query in translation_cache:
        translation_text = translation_cache[query]
        if  translation_text.startswith('[TR]'):
            return query
        return translation_text
    
    return query

def process_file(file_path, output_path=None):
    if output_path is None:
        output_path = file_path
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = re.compile(
        r'"([^"]*)"'
    )

    def replace_match(match):
        text = match.group(1)      # 函数名
        
        translated = translate(text)
        
        # 构造替换后的字符串，保持原始括号类型
        return f'"{translated}"'

    new_content = pattern.sub(replace_match, content)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

def process_directory(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = input_dir
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.cpp'):
                input_path = os.path.join(root, file)
                if output_dir == input_dir:
                    output_path = input_path  # 覆盖原文件
                else:
                    # 保持相同的目录结构
                    rel_path = os.path.relpath(root, input_dir)
                    output_root = os.path.join(output_dir, rel_path)
                    os.makedirs(output_root, exist_ok=True)
                    output_path = os.path.join(output_root, file)
                print(f"Process file: {input_path} -> {output_path}")
                process_file(input_path, output_path)
# 主程序
if __name__ == '__main__':
    # 加载缓存
    load_cache()
    
    # 处理目录
    process_directory("YimMenuV2/src/game/frontend")
    process_directory("YimMenuV2/src/game/features")