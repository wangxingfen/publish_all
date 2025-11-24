import requests
import random
from openai import OpenAI
import json
import time
import os
from retrying import retry
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
from retrying import retry

@retry(stop_max_attempt_number=200, wait_exponential_multiplier=200, wait_exponential_max=400)
def image_prompt(prompt,config):
    '''生成图像提示词'''
    image_prompts=config["image_prompt"]
    system_prompt=f"{image_prompts}请直接使用英文短语形式合理地输出绘图提示词。"

    client = OpenAI(
    # 请用知识引擎原子能力API Key将下行替换为：api_key="sk-xxx",
    api_key=config["api_key"], # 如何获取API Key：https://cloud.tencent.com/document/product/1772/115970
    base_url=config["base_url"],
)
    completion = client.chat.completions.create(
        model=config['model'],  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        temperature=0,
        messages=[
            {'role': 'system', 'content':system_prompt},
            {'role': 'user', 'content': prompt}
            ]
)
    img_prompt=completion.choices[0].message.content
    print(f"初始提示词：{img_prompt}")
    return img_prompt
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_image(prompt,title=None,seed=1234):
    '''生成图像'''
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        url = config.get('images_base_url')+'/images/generations'
        model = config.get('images_model')
        api_key = config.get('api_key')

        if not url or not model or not api_key:
            raise ValueError("图像生成配置不完整，请在设置中配置图像模型相关参数")
        prompts = image_prompt(prompt,config).strip()
        prompts=prompts
        print(f"生成图像的提示词为：{prompts}")

        payload = {
            "model": model,
            "prompt": prompts,
            "seed":seed,
            "image_size": "1600x1200",
            "num_inference_steps": 40,
            "negative_prompt": "bad anime, bad illustration,Incomplete body,lowres, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        image_url = response.json()["images"][0]["url"]   
        image_response = requests.get(image_url, timeout=50)
        image_response.raise_for_status()
        file_path = os.path.abspath(os.path.join("images/", uuid4().hex + '.png'))
        print(file_path)

        with open(file_path, 'wb') as f:
            f.write(image_response.content)
        add_chinese_text_to_image(file_path, title)
        return file_path,prompts
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        raise e

def add_chinese_text_to_image(image_path, text, output_path=None):
    """
    在图片正中央添加指定的中文文字，并自动调整字体大小以适应图片
    
    Args:
        image_path (str): 输入图片路径
        text (str): 要添加的中文文字
        output_path (str, optional): 输出图片路径，默认为None表示覆盖原图
    
    Returns:
        str: 处理后的图片路径
    """
    # 打开图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # 获取图片尺寸
    img_width, img_height = image.size
    
    # 设置字体和大小
    # 尝试使用系统默认中文字体
    font_paths = [
        "STXINGKA.TTF",  # 华文行楷
        "simhei.ttf",  # 黑体
        "simsun.ttc",  # 宋体
        "msyh.ttc",    # 微软雅黑
        "STHeiti.ttf", # 华文黑体
        "Arial Unicode.ttf"  # 通用Unicode字体
    ]
    
    font = None
    # 尝试加载中文字体
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size=100)
            break
        except IOError:
            continue
    
    # 如果没有找到合适的字体，则使用默认字体（可能不支持中文）
    if font is None:
        font = ImageFont.load_default()
    
    # 自动调整字体大小
    font_size = adjust_font_size(draw, text, img_width, img_height, font)
    
    # 重新加载正确大小的字体
    if isinstance(font, ImageFont.FreeTypeFont):
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, size=font_size)
                break
            except IOError:
                continue
    
    # 文本自动换行处理（每行最多10个字符）
    wrapped_text = wrap_text(text, 10)
    
    # 计算多行文本的整体尺寸
    lines = wrapped_text.split('\n')
    line_heights = []
    line_widths = []
    
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = text_bbox[2] - text_bbox[0]
        line_height = text_bbox[3] - text_bbox[1]
        line_widths.append(line_width)
        line_heights.append(line_height)
    
    # 计算整体文本块的高度和最大宽度
    total_height = sum(line_heights) + (len(lines) - 1) * 10  # 10像素行间距
    max_width = max(line_widths) if line_widths else 0
    
    # 计算文本块左上角位置使其居中
    x = (img_width - max_width) // 2
    y = (img_height - total_height) // 2
    
    # 添加带描边和加粗的文字到图片
    # 先绘制白色描边（多次偏移绘制形成轮廓效果）
    outline_color = (0, 0, 0)  # 黑色描边
    text_color = (255, 255, 255)  # 白色文字
    outline_range = 20  # 描边宽度
    bold_offset = 1  # 加粗偏移量

    # 绘制每行文字
    current_y = y
    for i, line in enumerate(lines):
        # 计算当前行的宽度以居中对齐
        line_width = line_widths[i]
        line_x = x + (max_width - line_width) // 2
        
        # 绘制描边
        for adj_x in range(-outline_range, outline_range+1):
            for adj_y in range(-outline_range, outline_range+1):
                if adj_x != 0 or adj_y != 0:  # 不在中心点绘制
                    draw.text((line_x+adj_x, current_y+adj_y), line, font=font, fill=outline_color)
        
        # 绘制加粗文字
        for bold_x in range(-bold_offset, bold_offset+1):
            for bold_y in range(-bold_offset, bold_offset+1):
                draw.text((line_x+bold_x, current_y+bold_y), line, font=font, fill=text_color)
        
        # 更新Y坐标到下一行
        current_y += line_heights[i] + 10  # 加上行间距
    
    # 保存图片
    if output_path is None:
        output_path = image_path
    
    image.save(output_path)
    return output_path

def wrap_text(text, max_chars_per_line):
    """
    对文本进行自动换行处理
    
    Args:
        text (str): 要处理的文本
        max_chars_per_line (int): 每行最大字符数
    
    Returns:
        str: 处理后的文本（包含换行符）
    """
    if len(text) <= max_chars_per_line:
        return text
    
    lines = []
    current_line = ""
    
    for char in text:
        if len(current_line) >= max_chars_per_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line += char
    
    # 添加最后一行
    if current_line:
        lines.append(current_line)
    
    return '\n'.join(lines)

def adjust_font_size(draw, text, img_width, img_height, font):
    """
    根据图片尺寸和文本长度自动调整字体大小
    
    Args:
        draw: ImageDraw对象
        text (str): 文本内容
        img_width (int): 图片宽度
        img_height (int): 图片高度
        font: 字体对象
    
    Returns:
        int: 合适的字体大小
    """
    # 设置目标宽度为图片宽度的90%
    target_width = img_width * 0.95
    
    # 初始字体大小
    font_size = 100
    
    # 测试当前字体大小下的文本宽度
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    
    # 根据比例调整字体大小
    if text_width > 0:
        print(text_width,target_width)
        font_size = int(font_size * target_width / text_width)
    
    # 限制字体大小范围，避免过大或过小
    min_font_size = max(160, min(img_width, img_height) // 50)
    max_font_size = min(800, min(img_width, img_height) *2)
    
    font_size = max(min_font_size, min(font_size, max_font_size))
    
    return font_size

if __name__ == '__main__':
    path="2.png"

    add_chinese_text_to_image(path,"建设计上课时库萨克库萨克酷酷的","output.png")
    #get_image("a girl rabbit lost in a forest form home with a fox meet a kind old man","","a fantasy forest background")