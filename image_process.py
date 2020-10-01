import cv2
from PIL import Image
from copy import deepcopy


def canny(image):
    return cv2.Canny(image, 100, 200)


def getResizeImg(img, max_size):
    w, h = img.size
    aspect_rate = max(list(img.size)) / min(list(img.size))

    if w >= h:
        h = int(h * max_size / w)
        paste_size = (max_size, h)
    else:
        w = int(w * max_size / h)
        paste_size = (w, max_size)

    return img.resize(paste_size)


def getSierraSyntheticImage(bg, img, binary_thr=230, cx=2000, cy=2100, expansion=1.8):
    print('in getSierraSyntheticImage')
    # 透明部分を白くする
    if img.mode == 'RGBA':
        img.load()
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    # 二値化
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < binary_thr else 255)
    img = img.convert('RGBA')

    # 背景透過(白のみ)
    trans = Image.new('RGBA', img.size, (0, 0, 0, 0))

    width = img.size[0]
    height = img.size[1]

    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))

            # 白なら処理しない
            if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
                continue

            # 白以外なら、用意した画像にピクセルを書き込み
            trans.putpixel((x, y), pixel)

    img = trans

    # デザイン画像のアスペクト比を変えずにpaste_max_sizeに合わせてリサイズ
    img = getResizeImg(img, 1000)

    # 背景画像にイラスト画像をペーストする
    # expansion = 1.8

    edit_img = img.rotate(-15)
    edit_img = edit_img.resize(
        (int(img.size[0] * expansion), int(img.size[1] * expansion)))

    # cx, cy = 2000, 2100
    half_size = edit_img.size[0] // 2
    x = edit_img.size[0] // 2
    y = edit_img.size[1] // 2

    dst = deepcopy(bg)
    dst.paste(edit_img, (cx - x, cy - y), mask=edit_img.split()[3])

    dst = dst.resize((400, 400))

    return dst
