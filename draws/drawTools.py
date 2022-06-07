# -*- coding: utf-8 -*-
from enum import auto
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

MAP_COVER_FILE = "map_cover_{sid}"
MAP_THUMB_FILE = "map_thumb_{sid}"


class DrawTool:


    def __init__(self, **kw):
        # cover图原size(900,250)，这里除掉一半
        self.width = kw.get('width', 425)
        self.height = kw.get('height', 475)
        self.exheight = kw.get('exheight', 3)
        self.font_cn = kw.get('font_cn', font_cn) # 字体
        self.font_size = kw.get('font_size', 14) # 文字大小
        self.font_color = kw.get('font_color', 'black') # 文字颜色
        self.doffset = kw.get('doffset', (3, 1)) # 绘制间隙
        self.img_mode = kw.get('img_mode', 'RGB') # 可选RGBA
        self.img_color = kw.get('img_color', 'white') # 背景颜色
        self.save_path = kw.get('save_path', img_path)
        self.autoDraw = [] # 保存绘制路径
        self.FreeTypeFont = None
        self.initImageObj()

    def initImageObj(self):
        self.img = Image.new(self.img_mode, (self.width, self.height), self.img_color)
        self.drawer = ImageDraw.Draw(self.img)

    def autoDrawText(self, s):
        if not self.FreeTypeFont:
            self.FreeTypeFont = ImageFont.truetype(font_cn, self.font_size)
        font_size = get_str_size(s, self.FreeTypeFont) # 宽，高
        d = {
            "func": self.drawText,
            "kwargs": {"s": s, "FreeTypeFont": self.FreeTypeFont},
            "offset": self.doffset,
            "size": font_size
        }
        self.autoDraw.append(d)
    
    def autoDrawImage(self, fname=None, url=None, save_name=None, autoResizeW=0):
        # autoResizeW: cover图记得设置
        if url:
            fname = downImage(url, save_name)
            if not fname:
                logging.error("图片下载失败!")
                return

        ImageObj = self.openImage(fname)
        if autoResizeW:
            x, y = self.calResizeToImgWidth(ImageObj)

        d = {
            "func": self.drawImage,
            "kwargs": {"fname": fname, "ImageObj": ImageObj, "resize_xy": (x, y)},
            "size": (x, y)
        }
        self.autoDraw.append(d)

    def drawText(self, s, offset=(0, 0), color=None, font_size=None, font_type=None, FreeTypeFont=None):
        if not FreeTypeFont:
            if not font_type:
                font_type = self.font_cn
            if not font_size:
                font_size = self.font_size
            FreeTypeFont = ImageFont.truetype(font_cn, font_size)
        if not color:
            color = self.font_color
        self.drawer.text(offset, s, font=FreeTypeFont, fill=color)

    def drawImage(self, fname=None, path=None, file=None, ImageObj=None, offset=(0, 0), 
                            factor=None, resize_xy=None, resize_rate=None, autoResizeW=0, mask=None):
        if not ImageObj:
            ImageObj = self.openImage(fname, path, file)
        # resize_xy:(w,h)
        if resize_xy:
            ImageObj = ImageObj.resize(resize_xy)
        # 按图片宽度比例自动缩放 0/1
        if autoResizeW:
            size = self.calResizeToImgWidth(ImageObj)
            ImageObj = ImageObj.resize(size)
        if resize_rate:
            x = ImageObj.size[0] * resize_rate
            y = ImageObj.size[1] * resize_rate
            ImageObj = ImageObj.resize((x, y))
        if factor:
            ImageObj = addTransparency(ImageObj, factor)
        self.img.paste(ImageObj, offset, mask=mask)
    
    def calResizeToImgWidth(self, ImageObj):
        # 计算缩放size
        x = self.width
        y = int(x/ImageObj.size[0]*ImageObj.size[1])
        return x, y
    
    def openImage(self, fname=None, path=None, file=None, conv=None):
        # conv: RBGA/RGB
        if not file:
            if not path:
                path = self.save_path
            file = path + fname
        im = Image.open(file)
        if conv and im.mode != conv:
            im = im.convert(conv)
        return im

    def save(self, name="", debug=0, fs8=1):
        # fs8 压缩
        if debug == 1:
            self.img.show()
        else:
            if not name:
                name = '%s.png' % uuid.uuid4()
            fname = self.save_path + name
            self.img.save(fname)
            name = f"tmp/{name}"
            logging.info('生成图片[%s]' % fname)

            # 压缩
            if fs8:
                os.system('pngquant -f %s' % fname)
                name = name.replace(".png", "-fs8.png")
                logging.info('生成压缩图片[%s]' % name)

        return name

    def startDraw(self):
        # 先计算图大小
        autoY = 0
        for r in self.autoDraw:
            yy = r.get('offset', (0, 0))[1]
            autoY += r['size'][1] + yy

        self.height = autoY + self.exheight

        x = 0
        y = 0
        self.initImageObj()
        for r in self.autoDraw:
            xx = r.get('offset', (0, 0))[0]
            yy = r.get('offset', (0, 0))[1]
            r['kwargs']['offset'] = (x+xx, y+yy)
            r['func'](**r['kwargs'])
            y += r['size'][1] + yy

        return self.save()


def drawText(s, fontsize=14, debug=0, offset=(3,1)):
    font = ImageFont.truetype(font_cn, fontsize)
    img_size = get_str_size(s, font)

    img = Image.new('RGB', (img_size[0]+offset[0]+5, img_size[1]), "white")
    drawer = ImageDraw.Draw(img)
    drawer.text(offset, s, font=font, fill='black')

    return save_or_show(img, debug)

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
    if img_size[0] < 375:
        img_size[0] = 375
    y = 0
    
    if cqImgs:
        osuid = cqImgs[0].split("?")[0].split("/")[-1]
        fname = downImage(cqImgs[0], f'headimg_cover_{osuid}')
        if fname:
            bg = getLocalImage(img_path+fname)
            x = bg.size[0]
            y = bg.size[1]
            img = Image.new('RGB', (img_size[0], img_size[1]+y), "white")
            img.paste(bg, (img_offset[0], img_offset[1]), mask=None)
        else:
            img = Image.new('RGB', (img_size[0], img_size[1]), "white")
            logging.error("图片下载失败!")
    else:
        return drawText(text_s)
            
    drawer = ImageDraw.Draw(img)
    drawer.text((offset[0], offset[1]+y), text_s, font=font, fill='black')

    return save_or_show(img, debug)

def drawTextWithCover(s, fontsize=14, debug=0, offset=(5,5)):
    cqImgs = getCqImage(s)
    text_s = rm_cq_image(s)

    font = ImageFont.truetype(font_cn, fontsize)
    img_size = get_str_size(text_s, font)
    img_size[0] += offset[0] + 5
    if img_size[0] < 425:
        img_size[0] = 425

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
    else:
        return drawText(text_s)
            
    drawer = ImageDraw.Draw(img)
    drawer.text((offset[0], offset[1]+y), text_s, font=font, fill='black')

    return save_or_show(img, debug)


def save_or_show(img, debug=0):
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

    if res == 1 and ".jpg" not in iname:
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
    # drawTextWithRawCover(s, debug=0)

    # d = DrawTool()
    # d.drawImage(fname='map_cover_771159.jpg', autoResizeW=1)
    # d.drawText("test", (10, 200))
    # d.save("test5.png")

    # d = DrawTool()
    # d.autoDrawText("interbot's bp!!")
    # d.autoDrawImage(save_name=MAP_COVER_FILE.format(sid="96103"), autoResizeW=1, url=MAP_COVER.format(sid="96103"))
    # d.autoDrawText("bp1, 216pp,98.69%,S,+NF")
    # d.autoDrawImage(save_name=MAP_COVER_FILE.format(sid="952409"), autoResizeW=1, url=MAP_COVER.format(sid="952409"))
    # d.autoDrawText("bp2, 185pp,94.82%,S,+NF")
    # d.autoDrawImage(save_name=MAP_COVER_FILE.format(sid="992231"), autoResizeW=1, url=MAP_COVER.format(sid="992231"))
    # d.autoDrawText("bp3, 176pp,95.23%,S,+NF")
    # d.startDraw()
