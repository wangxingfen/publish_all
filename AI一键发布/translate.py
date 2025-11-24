from openai import OpenAI
import json
from retrying import retry
@retry(stop_max_attempt_number=200, wait_exponential_multiplier=200, wait_exponential_max=400)
def chanslater(text):
    '''生成运镜提示词'''
    with open("settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    client = OpenAI(
    # 请用知识引擎原子能力API Key将下行替换为：api_key="sk-xxx",
    api_key=config["api_key"], # 如何获取API Key：https://cloud.tencent.com/document/product/1772/115970
    base_url=config["base_url"],
)
    completion = client.chat.completions.create(
        model=config['model'],  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        temperature=0.5,
        messages=[
            {'role': 'system', 'content':"你是infj人格的富有创意的起标题的大师，请根据输入的信息写出一个可能有点无厘头并且充满活人感的哔站标题即可。不多于50个字。"},
            {'role': 'user', 'content': text}
            ]
)
    chanslated_prompt=completion.choices[0].message.content
    return chanslated_prompt
def describer(text):
    '''生成运镜提示词'''
    with open("settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    client = OpenAI(
    # 请用知识引擎原子能力API Key将下行替换为：api_key="sk-xxx",
    api_key=config["api_key"], # 如何获取API Key：https://cloud.tencent.com/document/product/1772/115970
    base_url=config["base_url"],
)
    completion = client.chat.completions.create(
        model=config['model'],  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        temperature=0.3,
        messages=[
            {'role': 'system', 'content':"你是infj人格的富有创意的写作大师，请把视频内容变成富有创意并且充满活人感的视频描述。不少于50个字。"},
            {'role': 'user', 'content': text}
            ]
)
    chanslated_prompt=completion.choices[0].message.content
    return chanslated_prompt
if __name__ == "__main__":
    print(chanslater("A close-up shot of a person holding a smartphone, with the screen displaying a vibrant app interface. The background is softly blurred, emphasizing the device and the user's hand. The image is in focus, with a soft gradient overlay."))