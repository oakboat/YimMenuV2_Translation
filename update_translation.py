import json
import re
import os

# 翻译缓存字典
translation_cache = {}

# 缓存文件路径
CACHE_FILE = 'translation.json'

def load_cache():
    """加载翻译缓存"""
    global translation_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                translation_cache = json.load(f)
        except Exception as e:
            print(f"加载缓存失败: {e}")
            translation_cache = {}

def save_cache():
    """保存翻译缓存"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(translation_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存缓存失败: {e}")

def translate(query):
    """翻译函数，带缓存功能"""
    if not query:
        return query
    # 检查缓存
    if query in translation_cache:
        return translation_cache[query]
    
    translated_text = f"[TR]{query}"
    translation_cache[query] = translated_text
    return translated_text

def process_command(content):
    # 匹配以下格式：
    # [前缀] _函数名(或{)"str1", "str2", "str3"[,...]}[或);
    pattern = re.compile(
        r'(_\w+)\s*'                  # Function name (_ prefix)
        r'([\(\{])\s*'                # Opening bracket (( or {)
        r'"([^"]*)"\s*,\s*'           # First quoted string
        r'"([^"]*)"\s*,\s*'           # Second quoted string
        r'"([^"]*)"'                  # Third quoted string
        r'\s*(.*?[\)\}])\s*;',           # Closing bracket () or }) and semicolon
    )
    
    def replace_match(match):
        func_name = match.group(1)      # 函数名
        open_bracket = match.group(2)   # 开始括号（(或{）
        str1 = match.group(3)           # 第一个字符串（通常不翻译）
        str2 = match.group(4)           # 第二个字符串
        str3 = match.group(5)           # 第三个字符串
        close_bracket = match.group(6)  # 结束括号（)或}）
        
        # 翻译字符串（这里只翻译str2和str3）
        translated_str2 = translate(str2)
        translated_str3 = translate(str3)
        
        # 构造替换后的字符串，保持原始括号类型
        return f'{func_name}{open_bracket}"{str1}", "{translated_str2}", "{translated_str3}"{close_bracket};'
    
    # 执行替换
    new_content = pattern.sub(replace_match, content)
    return new_content

def process_imgui(content):
    # 简化的正则表达式模式（不考虑转义字符）
    pattern = re.compile(
        r'(ImGui::\w+)\s*\(\s*"([^"]*)"(.*?)\)'  # 匹配函数名、字符串内容和剩余参数
    )
    
    def replace_match(match):
        func_name = match.group(1)   # 函数名（如ImGui::Text）
        original = match.group(2)    # 原始字符串内容
        params = match.group(3)      # 剩余参数
        
        # 直接调用翻译函数（示例仅添加CN_前缀）
        translated = translate(original)
        
        # 返回新字符串（直接拼接，不处理转义）
        return f'{func_name}("{translated}"{params})'
    
    # 执行替换
    new_content = pattern.sub(replace_match, content)
    
    return new_content

def process_shared_ptrs(content):
    # 匹配 std::make_shared<Category> 和 std::make_shared<Group> 的字符串参数
    pattern = re.compile(
        r'(std::make_shared<(Category|Group)>)\s*\(\s*"([^"]*)"(.*?)\)'
    )
    
    def replace_match(match):
        prefix = match.group(1)      # 前缀（包括模板类型）
        template_type = match.group(2)  # Category 或 Group
        original = match.group(3)    # 原始字符串内容
        suffix = match.group(4)      # 后缀（可能包含其他参数或括号）
        
        translated = translate(original)  # 假设有 translate 函数
        # 返回新字符串
        return f'{prefix}("{translated}"{suffix})'
    
    # 执行替换
    new_content = pattern.sub(replace_match, content)
    return new_content

def process_submenu(content):
    # 匹配 sSubmenu::Submenu
    pattern = re.compile(
        r'(Submenu::Submenu)\s*\(\s*"([^"]*)"\s*\)'
    )
    
    def replace_match(match):
        prefix = match.group(1)      # 前缀（包括模板类型）
        original = match.group(2)    # 原始字符串内容
        translated = translate(original)  # 假设有 translate 函数
        # 返回新字符串
        return f'{prefix}("{translated}")'
    
    # 执行替换
    new_content = pattern.sub(replace_match, content)
    return new_content

def process_file(file_path, output_path=None):
    if output_path is None:
        output_path = file_path
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = process_command(content)
    new_content = process_imgui(new_content)
    new_content = process_shared_ptrs(new_content)
    new_content = process_submenu(new_content)

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
    
    try:
        # 处理目录
        process_directory("YimMenuV2/src/game/frontend")
        process_directory("YimMenuV2/src/game/features")
    finally:
        # 保存缓存
        save_cache()
