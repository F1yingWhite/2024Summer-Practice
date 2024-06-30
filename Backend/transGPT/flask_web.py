# -*- encoding: utf-8 -*-

import os
import sys
import torch
from transformers import AutoTokenizer
from sat.model.mixins import CachedAutoregressiveMixin
from sat.quantization.kernels import quantize
from model import chat
from flask_cors import CORS

from sat.model import AutoModel
from flask import Flask, request, jsonify
import argparse
from typing import List, Tuple
from PIL import Image
import base64
from io import BytesIO

os.environ["https_proxy"] = "http://127.0.0.1:7897"
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["all_proxy"] = "socks5://127.0.0.1:7897"

app = Flask(__name__)
CORS(app)

max_length = 2048
top_p = 0.4
top_k = 100
temperature = 0.8
quant = 4
from_pretrained = "visualglm-6b"

args = argparse.Namespace(
    fp16=True,
    skip_init=True,
    use_gpu_initialization=(
        True if (torch.cuda.is_available() and quant is None) else False
    ),
    device=("cuda" if (torch.cuda.is_available() and quant is None) else "cpu"),
)

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

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)


# Flask endpoint
@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    full_history = data.get("history", [])
    query = data.get("query")
    english = data.get("english", False)  # 默认值为 False
    image_base64 = data.get("image", None)
    image = None

    if image_base64:
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))

    response = None

    try:
        response, _, _ = chat(
            None,
            model,
            tokenizer,
            query,
            history=full_history,
            image=image,
            max_length=max_length,
            top_p=top_p,
            temperature=temperature,
            top_k=top_k,
            english=english,
            invalid_slices=[slice(63823, 130000)] if english else [],
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    sep = "A:" if english else "答："
    response_text = response.split(sep)[-1].strip()
    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
