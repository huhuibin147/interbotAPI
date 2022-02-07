# -*- coding: utf-8 -*-
import uuid
import logging
from PIL import Image, ImageDraw, ImageFont


pre = 'draws/'
font_cn = '%s/font/msyh.ttc' % pre



def drawText(s, fontsize=14, debug=0, offset=(3,1)):
    font = ImageFont.truetype(font_cn, fontsize)
    img_size = get_str_size(s, font)

    img = Image.new('RGB', (img_size[0]+offset[0]+5, img_size[1]), "white")
    drawer = ImageDraw.Draw(img)
    drawer.text(offset, s, font=font, fill='black')

    if debug:
        img.show()
        return ""

    else:
        p = '%s.png' % uuid.uuid4()
        f = '/static/interbot/image/tmp/%s' % p
        img.save(f)
        logging.info('生成图片[%s]' % f)
        return f"tmp/{p}"

def get_str_size(s, font):
    ws = s.split("\n")
    img_size = [0, 0] # 宽高
    d_size = font.getsize("字") # 填充空行
    for r in ws:
        r_size = font.getsize(r)
        img_size[0] = r_size[0] if r_size[0] > img_size[0] else img_size[0]
        img_size[1] += r_size[1] + 2 if r_size[1] >= d_size[1] else d_size[1] + 2
    return img_size



if __name__ == "__main__":
    # drawText("test")
    drawText("test\nceshiccec测试  测试  测试\ntest11\nasdasd\naaaaaaaaaaaaa")

