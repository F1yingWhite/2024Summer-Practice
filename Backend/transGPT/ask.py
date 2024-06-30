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
