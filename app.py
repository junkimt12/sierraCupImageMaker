from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import numpy as np
import cv2
from image_process import *
from datetime import datetime
import os
import string
import random
from PIL import Image
import base64
from io import BytesIO


app = Flask(__name__, static_url_path="")

# 背景画像読み込み
bg = Image.open('sierra_wood_square.jpg')
img = Image.open('illusts/download.png')


def random_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])


def pil2base64(img):
    buf = BytesIO()
    img.save(buf, format="png")
    b64str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return "data:image/png;base64,{}".format(b64str)


@app.route('/')
def index():
    # return render_template('index.html', images=os.listdir(SAVE_DIR)[::-1])
    bg = Image.open('illusts/download-1.png').resize((400, 400))
    img = Image.open('illusts/download.png').resize((400, 400))
    bg = pil2base64(bg)
    img = pil2base64(img)

    debug_b64data = pil2base64(Image.open(
        'illusts/drive-download-20200930T231240Z-001/202009292013_data_alpha.png').resize((400, 400)))
    return render_template('index.html', qr_b64data=bg, input_b64data=img, binary_thr=128, expansion=1.8, cx=2000, cy=2100)


@app.route('/reset')
def reset():
    image = None
    return redirect('/')

# 参考: https://qiita.com/yuuuu3/items/6e4206fdc8c83747544b
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    print(request.method)
    binary_thr = request.args.get('binarySlider', 128, type=int)
    expansion = request.args.get('expansionSlider', 1.8, type=float)
    cx = request.args.get('cxSlider', 2000, type=int)
    cy = request.args.get('cySlider', 2100, type=int)
    global bg, img
    if request.method == 'POST':
        if request.files['image']:
            print('2')
            # if request.files['upload_file']:
            # 画像として読み込み
            stream = request.files['image'].stream
            # stream = request.files['upload_file'].stream
            img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
            img = Image.fromarray(img)

            dst = getSierraSyntheticImage(
                bg, img, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)

            b64data = pil2base64(dst)

            input_b64data = pil2base64(getResizeImg(img, 400))

            # return redirect('/')
            # return redirect('/', qr_b64data=bg_b64data)
            return render_template('index.html', qr_b64data=b64data, input_b64data=input_b64data, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)
        else:
            print('3')
            if bg is not None and img is not None:
                dst = getSierraSyntheticImage(
                    bg, img, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)

                b64data = pil2base64(dst)

                input_b64data = pil2base64(getResizeImg(img, 400))

                return render_template('index.html', qr_b64data=b64data, input_b64data=input_b64data, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)
            else:
                return redirect('/')
    else:
        print('4', binary_thr, expansion, cx, cy)
        dst = getSierraSyntheticImage(
            bg, img, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)
        # dst.save('dst.png')

        b64data = pil2base64(dst)

        input_b64data = pil2base64(getResizeImg(img, 400))

        return render_template('index.html', qr_b64data=b64data, input_b64data=input_b64data, binary_thr=binary_thr, expansion=expansion, cx=cx, cy=cy)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
