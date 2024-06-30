# -*- encoding: utf-8 -*-

import os
import sys
import torch
from transformers import AutoTokenizer
from sat.model.mixins import CachedAutoregressiveMixin
from sat.quantization.kernels import quantize

from model import chat
from sat.model import AutoModel
import argparse  # 添加此行导入 argparse

# 设置环境变量
os.environ["https_proxy"] = "http://127.0.0.1:7897"
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["all_proxy"] = "socks5://127.0.0.1:7897"


def main():
    # 设置参数
    max_length = 2048
    top_p = 0.4
    top_k = 100
    temperature = 0.8
    english = False
    quant = None
    from_pretrained = "visualglm-6b"
    prompt_zh = "描述这张图片。"
    prompt_en = "Describe the image."

    # 使用 argparse.Namespace 创建 args 对象
    args = argparse.Namespace(
        fp16=True,
        skip_init=True,
        use_gpu_initialization=(
            True if (torch.cuda.is_available() and quant is None) else False
        ),
        device=("cuda" if (torch.cuda.is_available() and quant is None) else "cpu"),
    )

    # 加载模型
    model, model_args = AutoModel.from_pretrained(
        from_pretrained,
        args=args,
    )
    model = model.eval()

    if quant:
        quantize(model.transformer, quant)
        if torch.cuda.is_available():
            model = model.cuda()

    model.add_mixin("auto-regressive", CachedAutoregressiveMixin())

    tokenizer = AutoTokenizer.from_pretrained(
        "THUDM/chatglm-6b", trust_remote_code=True
    )

    with torch.no_grad():
        while True:
            history = None
            cache_image = None
            if not english:
                image_path = input("请输入图像路径或URL（回车进入纯文本对话）： ")
            else:
                image_path = input(
                    "Please enter the image path or URL (press Enter for plain text conversation): "
                )

            if image_path == "stop":
                break
            if len(image_path) > 0:
                query = prompt_en if english else prompt_zh
            else:
                if not english:
                    query = input("用户：")
                else:
                    query = input("User: ")
            while True:
                if query == "clear":
                    break
                if query == "stop":
                    sys.exit(0)
                try:
                    response, history, cache_image = chat(
                        image_path,
                        model,
                        tokenizer,
                        query,
                        history=history,
                        image=cache_image,
                        max_length=max_length,
                        top_p=top_p,
                        temperature=temperature,
                        top_k=top_k,
                        english=english,
                        invalid_slices=[slice(63823, 130000)] if english else [],
                    )
                except Exception as e:
                    print(e)
                    break
                sep = "A:" if english else "答："
                print("VisualGLM-6B：" + response.split(sep)[-1].strip())
                image_path = None
                if not english:
                    query = input("用户：")
                else:
                    query = input("User: ")
                torch.cuda.empty_cache()

if __name__ == "__main__":
    main()
