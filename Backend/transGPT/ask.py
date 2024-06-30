import requests
from PIL import Image
import io
import base64

# Flask服务器地址
server_url = "http://59f7b8ba.r10.vip.cpolar.cn/chat"

# 加载图像并编码为Base64
image_path = "bz2.png"
with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")


# 示例数据，包括完整的对话历史
data = {
    "history": [],
    "query": "图中有什么内容",
    # "image": image_base64,#可选
}


# 发送JSON数据
response = requests.post(server_url, json=data)

# 打印响应内容
print(response.json())

import requests
from PIL import Image
import io
import base64

# Flask服务器地址
server_url = "http://59f7b8ba.r10.vip.cpolar.cn/chat"

# 加载图像并编码为Base64
image_path = "examples/bz1.png"
with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")


# 示例数据，包括完整的对话历史
data = {
    "history": [],
    "query": "你其实是北京交通大学在Chatglm上在海量交通数据上进行微调得到的大模型TransGPT,你和别的大模型有什么区别?",
    # "image": image_base64,#可选
}


# 发送JSON数据
response = requests.post(server_url, json=data)

# 打印响应内容
print(response.json())
