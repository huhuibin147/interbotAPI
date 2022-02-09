# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('./')

import re
import uuid
import logging
from commLib import interRequest
from PIL import Image, ImageDraw, ImageFont


pre = 'draws/'
font_cn = '%s/font/msyh.ttc' % pre
img_path = "/static/interbot/image/tmp/"

MAP_COVER = "https://assets.ppy.sh/beatmaps/{sid}/covers/cover.jpg"
MAP_THUMB = "https://b.ppy.sh/thumb/{sid}l.jpg"



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

def drawTextWithRawCover(s, fontsize=14, debug=0, offset=(5,5), img_offset=(5,5)):
    cqImgs = getCqImage(s)
    text_s = rm_cq_image(s)

    font = ImageFont.truetype(font_cn, fontsize)
    img_size = get_str_size(text_s, font)
    img_size[0] += offset[0] + 5
    y = 0
    
    if cqImgs:
        osuid = cqImgs[0].split("?")[0].split("/")[-1]
        fname = downImage(cqImgs[0], f'headimg_cover_{osuid}')
        if fname:
            bg = getLocalImage(img_path+fname)
            x = bg.size[0]
            y = bg.size[1]
            img = Image.new('RGB', (img_size[0], img_size[1]+y), "white")
            # 居中
            img.paste(bg, (img_offset[0], img_offset[1]), mask=None)
        else:
            img = Image.new('RGB', (img_size[0], img_size[1]), "white")
            logging.error("图片下载失败!")
            
    drawer = ImageDraw.Draw(img)
    drawer.text((offset[0], offset[1]+y), text_s, font=font, fill='black')

    if debug:
        img.show()
        return ""

    else:
        p = '%s.png' % uuid.uuid4()
        p = 'test3.png'
        f = '/static/interbot/image/tmp/%s' % p
        img.save(f)
        print(p)
        logging.info('生成图片[%s]' % f)
        return f"tmp/{p}"

def drawTextWithCover(s, fontsize=14, debug=0, offset=(5,5)):
    cqImgs = getCqImage(s)
    text_s = rm_cq_image(s)

    font = ImageFont.truetype(font_cn, fontsize)
    img_size = get_str_size(text_s, font)
    img_size[0] += offset[0] + 5
    y = 0

    if cqImgs:
        sid, cover = Thumb2Cover(cqImgs[0])
        fname = downImage(cover, f'map_cover_{sid}')
        if fname:
            bg = getLocalImage(img_path+fname)
            x = img_size[0]
            y = int(img_size[1]*img_size[0]/bg.size[0])
            bg_rsize = bg.resize((x, y))
            img = Image.new('RGB', (img_size[0], img_size[1]+y), "white")
            img.paste(bg_rsize, (0, 0), mask=None)
        else:
            img = Image.new('RGB', (img_size[0], img_size[1]), "white")
            logging.error("图片下载失败!")
            
    drawer = ImageDraw.Draw(img)
    drawer.text((offset[0], offset[1]+y), text_s, font=font, fill='black')

    if debug:
        img.show()
        return ""

    else:
        p = '%s.png' % uuid.uuid4()
        f = '/static/interbot/image/tmp/%s' % p
        img.save(f)
        logging.info('生成图片[%s]' % f)
        return f"tmp/{p}"

def getCqImage(s):
    p = re.compile('\[CQ:image,cache=0,file=(.*?)\]')
    cqimg = p.findall(s)
    return cqimg

def Thumb2Cover(img):
    p = re.compile('https://b.ppy.sh/thumb/(\d+)l.jpg')
    rs = p.match(img)
    sid, cover = -1, ""
    if rs:
        sid = rs.group(1)
        cover = MAP_COVER.format(sid=sid)
    return sid, cover

def rm_cq_image(s):
    p = re.compile('\[CQ:image,cache=0,file=(.*?)\]')
    cqimg = p.findall(s)
    for img in cqimg:
        s = s.replace(f'[CQ:image,cache=0,file={img}]', '')
    return s

def downImage(url, iname, useCache=1):
    r = interRequest.interReq()
    res = 1
    if useCache:
        if not os.path.exists(img_path + iname + '.jpg'):
            res = r.down_image(iname, url=url, path=img_path)
    else:
        res = r.down_image(iname, url=url, path=img_path)

    if res == 1:
        return iname + '.jpg'
    return ""

def getLocalImage(file, factor=0):
    im = Image.open(file)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    if factor:
        im = addTransparency(im, factor)
    return im

def addTransparency(img, factor=0.8):
    img_blender = Image.new('RGBA', img.size, (0,0,0,0))  
    img = Image.blend(img_blender, img, factor)  
    return img  




if __name__ == "__main__":
    # drawText("test")
    # drawText("test\nceshiccec测试  测试  测试\ntest11\nasdasd\naaaaaaaaaaaaa")
    s = """
xxxxxxxxxx
Hanasaka Yui(CV: M.A.O) - Harumachi Clover [MoeMoe] 
Beatmap by Karen 
[ar8 cs4 od7 hp7  bpm142]
[CQ:image,cache=0,file=https://b.ppy.sh/thumb/557733l.jpg]
stars: 4.36*(4.37*) | HD 
74x/148x | 92.52% | F 

92.52%: 39pp(41pp)
94.59%: 82pp(86pp)
100.0%: 113pp(116pp)
3miss，被秀到了呜呜呜
https://osu.ppy.sh/b/1180037
    """
    # https://assets.ppy.sh/beatmaps/557733/covers/cover.jpg
    # downImage("https://assets.ppy.sh/beatmaps/557733/covers/cover.jpg", 557733)
    # drawTextWithCover(s, debug=0)
    s = """
-interesting-
[CQ:image,cache=0,file=https://a.ppy.sh/8505303?1485883146.jpg]
3415pp (1.65/day)
14216pc (6.85/day)
398wtth (280/pc)
--------------------
SS+(0) | SS(0) | S+(1) | S(98) | A(308)
bp1: 206pp,4.1*,97.47%,+NF,DT(4年前)
--------------------
粉丝数: 102
爆肝时长: 12天11小时
最后登录: 2022-02-09 22:05
注册时间: 2016-06-04 (2076天)
    """
    drawTextWithRawCover(s, debug=0)
