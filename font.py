import os

def ttf_to_header(ttf_path, output_path, font_name):
    # 读取TTF文件内容
    with open(ttf_path, 'rb') as f:
        ttf_data = f.read()
    
    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 写入头文件
    with open(output_path, 'w') as f:
        f.write(f'#include "Fonts.hpp"\n\n')
        f.write(f'namespace YimMenu::Fonts\n')
        f.write('{\n')
        f.write(f'    const uint8_t {font_name}[] = {{\n')
        
        # 写入字节数组，每行16个字节
        for i in range(0, len(ttf_data), 16):
            chunk = ttf_data[i:i+16]
            hex_str = ', '.join(f'0x{b:02x}' for b in chunk)
            f.write(f'        {hex_str},\n')
        
        f.write('    };\n')
        f.write('}\n')

if __name__ == '__main__':
    # 示例用法
    ttf_path = 'hei.TTF'  # 替换为你的TTF文件路径
    output_path = './MainFont.cpp'  # 输出头文件路径
    font_name = 'MainFont'  # 字体变量名
    
    ttf_to_header(ttf_path, output_path, font_name)
    print(f'Successfully converted {ttf_path} to {output_path}')