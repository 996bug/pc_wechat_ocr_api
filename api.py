# -*- coding: utf-8 -*-
# ☯ Author  : Anonymous Developer
# ☯ Date    : 2023/11/14 16:22
# ☯ Project : https://github.com/kanadeblisst00/wechat_ocr
# ☯ Warning : For learning purposes only, commercial use prohibited
import json
import os
import time
from hashlib import md5
from flask_cors import CORS
from flask import Flask, request, jsonify
from sdk.ocr_manager import OcrManager, OCR_MAX_TASK_ID

app = Flask(__name__)

CORS(app, supports_credentials=True)

wechat_ocr_dir = r"wechat/WeChatOCR.exe"
wechat_dir = r"wechat/dll"

results_queue = dict()


def parse(file_path: str, result_json: str):

    results_queue[os.path.split(file_path)[-1]] = json.loads(result_json)


ocr_manager = OcrManager(wechat_dir)
# 设置WeChatOcr目录
ocr_manager.SetExePath(wechat_ocr_dir)
# 设置微信所在路径
ocr_manager.SetUsrLibDir(wechat_dir)
# 设置ocr识别结果的回调函数
ocr_manager.SetOcrResultCallback(parse)
# 启动ocr服务
ocr_manager.StartWeChatOCR()


@app.route('/ocr', methods=['POST'])
def index():
    image_byte = request.data

    if image_byte is None:
        return jsonify({"code": 500, "msg": f"no image data", "ocrResult": list()})
    filename = md5(image_byte + str(time.time() * 1000).encode("utf8")).hexdigest()[9:-9]
    None if os.path.exists("temp") else os.mkdir("temp")
    file_path = os.path.join("temp", filename)

    with open(file_path, "wb") as f:
        f.write(image_byte)

    try:
        ocr_manager.DoOCRTask(file_path)

        for _ in range(15):
            time.sleep(0.1)
            result = results_queue.get(filename)
            if result is not None:
                del results_queue[filename]
                os.remove(file_path)
                return jsonify({"code": 200, "msg": f"success", "ocrResult": result})
        os.remove(file_path)
        return jsonify({"code": 200, "msg": f"success", "ocrResult": list()})

    except Exception as e:
        os.remove(file_path)
        return jsonify({"code": 500, "msg": f"{e}", "ocrResult": list()})


if __name__ == '__main__':
    try:
        app.run(
            host="0.0.0.0",
            port=8080,
            threaded=True
        )
    except Exception as e:
        _ = e
    ocr_manager.KillWeChatOCR()
