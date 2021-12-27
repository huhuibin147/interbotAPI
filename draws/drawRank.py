# coding: utf-8

import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
from draws import draw_data 
from commLib import mods
from botappLib import botHandler
from ppyappLib import ppyHandler

pre = 'draws/'
default_skin = '%s/New!+game!' % pre
osu_ui = '%s/osu!ui/Resources' % pre
font_cn = '%s/font/msyh.ttc' % pre
font_alp = '%s/font/Aller_Rg_MODFIED.ttf' % pre


class DrawRec():
    def __init__(self, **kw):
        self.width = kw.get('width', 1366)
        self.height = kw.get('height', 768)
        self.skin = kw.get('skin', default_skin)
        self.ui = kw.get('ui', osu_ui)
        self.RecImg = Image.new('RGBA', (self.width, self.height), 0) 
        self.font_cn = kw.get('font', font_cn)
        self.font_alp = kw.get('font2', font_alp)

    def get_img(self, iname, path=None, factor=0):
        fpath = '%s/%s' % (self.skin, iname) if not path else path
        # 没头像的临时处理，通用方法都暂时指向default
        if not os.path.exists(fpath):
            fpath = 'image/userimg/default.jpg'
        im = Image.open(fpath)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        if factor:
            im = self.addTransparency(im, factor)
        return im

    def draw_title_bg(self):
        im2 = Image.new('RGBA', (self.width, self.height))
        ImageDraw.Draw(im2).rectangle((0, 0, self.width, 200), fill=(0, 0, 0, 170)) #左上右下
        self.RecImg.paste(im2, (0, 0), mask=im2)

    def draw_rectangle(self, x, y, width, height, fill=(0, 0, 0, 170)):
        im2 = Image.new('RGBA', (width, height))
        ImageDraw.Draw(im2).rectangle((0, 0, width, height), fill=fill) #左上右下
        self.RecImg.paste(im2, (x, y), mask=im2)

    def add_items(self, fname=None, x=0, y=0, **kwargs):
        # 默认皮肤
        itemImg = self.get_img(fname, path=kwargs.get('path', None), factor=kwargs.get('factor', 0))
        if kwargs.get('isresize', False):
            itemImg = itemImg.resize((kwargs.get('width', self.width), kwargs.get('height', self.height)))
        mask = itemImg if kwargs.get('ismask', 1) else None
        self.RecImg.paste(itemImg, (x, y), mask=mask)

    def add_items2(self, fname, x=0, y=0, **kwargs):
        # UI元素或者使用默认路径外的 
        path_pref = self.ui if not kwargs.get('path', None) else kwargs['path']
        path = '%s/%s' % (path_pref, fname)
        self.add_items(x=x, y=y, path=path, **kwargs)

    def add_text(self, x, y, text, font_size=28, color='white', font_path=None, ttype='en'):
        if font_path:
            f = font_path
        else:
            f = self.font_alp if ttype == 'en' else self.font_cn
        font = ImageFont.truetype(f, font_size)
        ImageDraw.Draw(self.RecImg).text((x, y), text, font=font, fill=color)

    def addTransparency(self, img, factor=0.8):
        img_blender = Image.new('RGBA', img.size, (0,0,0,0))  
        img = Image.blend(img_blender, img, factor)  
        return img  

    def save(self, name='rec.png'):
        self.RecImg.save(name)


def drawR(mapjson, rankjson, userjson):
    # skin
    bg_e = draw_data.check_bg(mapjson['beatmap_id'], mapjson['beatmapset_id'])
    bg = '%s.jpg'%mapjson['beatmap_id'] if bg_e else 'newgame_background.png' 
    back_icon = 'menu-back-0.png'
    mod_icon = 'selection-mode.png'
    mods_icon = 'selection-mods.png'
    random_icon = 'selection-random.png'
    options_icon = 'selection-options.png'
    rank_x = 'ranking-%s-small.png'

    # ous ui
    songselecttop = 'songselect-top.png'
    uptips = 'selection-update.png'
    osu_icon = 'menu-osu.png'
    songselect_bottom = 'songselect-bottom.png'
    level_bar = 'levelbar.png'
    level_bar_bg = 'levelbar-bg.png'
    selection_approved = 'selection-approved.png'

    # 用户信息
    uname = userjson.get('username', '')
    pp = f"{float(userjson.get('pp_raw', 0)):,.0f}"
    acc = round(float(userjson.get('accuracy', 0)), 2)
    lv = float(userjson.get('level', 0))
    level = int(lv)
    lv_left = lv - level # 小数位，经验条
    rank = userjson.get('pp_rank', 0)
    umod = 'mode-osu-small.png'

    #曲子信息
    title = mapjson.get('title_unicode','')
    source = mapjson.get('source','')
    artist = mapjson.get('artist_unicode','')
    version = mapjson.get('version','')
    creator = mapjson.get('creator','')
    bpm = mapjson.get('bpm','')
    max_combo = mapjson.get('max_combo','')
    difficultyrating = round(float(mapjson.get('difficultyrating','')),2)  #stars
    diff_size = mapjson.get('diff_size','') #CS
    diff_approach = mapjson.get('diff_approach','') #AR
    diff_overall = mapjson.get('diff_overall','') #OD
    diff_drain = mapjson.get('diff_drain','') #HP
    count_normal = int(mapjson.get('count_normal', 0))
    count_slider = int(mapjson.get('count_slider', 0))
    count_spinner = int(mapjson.get('count_spinner', 0))

    m, s = divmod(int(mapjson.get('total_length')), 60)
    h, m = divmod(m, 60)
    if h != 0:
        hit_length = "%02d:%02d:%02d" % (h, m, s) #sec
    else:
        hit_length = "%02d:%02d" % (m, s) #sec

    # 头像download
    uids = [list(r.keys())[0] for r in rankjson]
    check_uids = uids[:12]
    me = userjson.get('user_id', '')
    if me not in uids:
        check_uids.append(me)
        me_idx = -1
    else:
        me_idx = uids.index(me)
    draw_data.check_img(check_uids)


    d = DrawRec()

    # 第一层bg
    # d.add_items(isresize=True, path='image/bg/default.jpg')
    d.add_items(isresize=True, path='image/bg/%s'%bg)
    # title黑层
    d.add_items2(songselecttop)
    # 更新提示
    # d.add_items2(uptips, 20, 200)
    # 低下大黑条
    d.add_items2(songselect_bottom, 0, 648, isresize=True, width=1366, height=120)
    # 大粉饼
    d.add_items2(osu_icon, 1130, 550, isresize=True, width=300, height=300)
    # 返回
    d.add_items(back_icon, 10, 615)
    
    # mode
    d.add_items(mod_icon, 250, 678)
    # mods选择
    d.add_items(mods_icon, 340, 678)
    # random
    d.add_items(random_icon, 430, 678)
    # options
    d.add_items(options_icon, 520, 678)

    # 头像
    d.add_items(x=690, y=675, path='image/userimg/%s.jpg'%me, isresize=True, width=90, height=90)
    # 用户信息
    d.add_items2(umod, 998, 670, factor=0.5)
    d.add_text(968, 710, '# %s'%rank, font_size=16, ttype='en')
    d.add_text(788, 670, uname, font_size=24, ttype='en')
    d.add_text(788, 700, 'Performance:%spp'%pp, font_size=16, ttype='en')
    d.add_text(788, 720, 'Accuracy:%s%%'%acc, font_size=16, ttype='en')
    d.add_text(788, 740, 'Lv:%s'%level, font_size=16, ttype='en')
    if lv_left > 0.1:
        d.add_items2(level_bar, 840, 745, isresize=True, width=int(lv_left*200), height=14)
    d.add_items2(level_bar_bg, 840, 745)

    # 曲子信息
    d.add_text(35, 0, '%s (%s) - %s [%s]'%(source,artist,title,version), font_size=25, ttype='cn')
    d.add_items2(selection_approved, 7, 3)
    d.add_text(40, 30, '作者: %s'%(creator), font_size=16, ttype='cn')
    d.add_text(5, 50, '长度: %s  BPM: %s  物件数: %s'%(hit_length,bpm,count_normal+count_slider+count_spinner), font_size=18, ttype='cn')
    d.add_text(5, 75, '圈数: %s 滑条数: %s 转盘数: %s'%(count_normal,count_slider,count_spinner), font_size=16, ttype='cn')
    d.add_text(5, 100, 'CS:%s AR:%s OD:%s HP:%s Star:%s★'%(diff_size,diff_approach,diff_overall,diff_drain,difficultyrating), font_size=16, ttype='en')

    bid = mapjson['beatmap_id']
    d.add_text(1180, 30, f"bid: {bid}", font_size=25, ttype='en')

    # 榜区域
    nums = len(uids)
    o = botHandler.botHandler()
    res = o.get_usernames_by_uid(uids)
    udict = {r['osuid']:r['osuname'] for r in res}
    if nums > 6:
        r1 = 6
        r2 = nums - 6
    else:
        r1 = nums
        r2 = 0
    offset1 = 65
    for i in range(r1):
        r = rankjson[i]
        u = uids[i]
        mds = int(r[u][5])
        mds_l = mods.getMod(mds)
        m = ','.join(mds_l) if mds > 0 else ''
        rank = 'D' if r[u][4] == 'F' else r[u][4]
        d.draw_rectangle(x=20, y=160+i*offset1, width=460, height=60, fill=(0, 0, 0, 50))
        d.add_items(x=20, y=160+i*offset1, path='image/userimg/%s.jpg'%u, isresize=True, width=60, height=60)
        d.add_items(rank_x%rank, 80, 170+i*offset1)
        d.add_text(120, 160+i*offset1, '%s'%(udict.get(u, 'None')), font_size=25, ttype='en')
        d.add_text(120, 190+i*offset1, '得分: %s'%(format(int(r[u][0]),',')), font_size=20, ttype='cn')
        d.add_text(300, 190+i*offset1, '(%sx)'%(format(int(r[u][1]),',')), font_size=20, ttype='en')
        d.add_text(450-20*len(mds_l), 165+i*offset1, '%s'%(m), font_size=20, ttype='en')
        d.add_text(400, 190+i*offset1, '%s%%'%(r[u][3]), font_size=18, ttype='en')

    d.add_text(150, 550, '个人最佳成绩', font_size=24, ttype='cn')
    d.draw_rectangle(x=20, y=590, width=460, height=60, fill=(0, 0, 0, 50))
    if me_idx != -1:
        r = rankjson[me_idx]
        u = uids[me_idx]
        mds = int(r[u][5])
        mds_l = mods.getMod(mds)
        m = ','.join(mds_l) if mds > 0 else ''
        rank = 'D' if r[u][4] == 'F' else r[u][4]
        d.add_items(x=20, y=590, path='image/userimg/%s.jpg'%me, isresize=True, width=60, height=60)
        d.add_items(rank_x%rank, 80, 595)
        d.add_text(120, 590, '%s'%(udict.get(u, 'None')), font_size=25, ttype='en')
        d.add_text(120, 620, '得分: %s'%(format(int(r[u][0]),',')), font_size=20, ttype='cn')
        d.add_text(300, 620, '(%sx)'%(format(int(r[u][1]),',')), font_size=20, ttype='en')
        d.add_text(450-20*len(mds_l), 600, '%s'%(m), font_size=20, ttype='en')
        d.add_text(410, 620, '%s%%'%(r[u][3]), font_size=18, ttype='en')
    else:
        d.add_text(130, 600, '你倒是快刚榜啊', font_size=25, ttype='cn')


    # copy
    for i in range(r2):
        if i == 6:
            break
        oi = i + 6
        r = rankjson[oi]
        u = uids[oi]
        mds = int(r[u][5])
        mds_l = mods.getMod(mds)
        m = ','.join(mds_l) if mds > 0 else ''
        rank = 'D' if r[u][4] == 'F' else r[u][4]
        d.draw_rectangle(x=620, y=160+i*offset1, width=460, height=60, fill=(0, 0, 0, 50))
        d.add_items(x=620, y=160+i*offset1, path='image/userimg/%s.jpg'%u, isresize=True, width=60, height=60)
        d.add_items(rank_x%rank, 680, 170+i*offset1)
        d.add_text(720, 160+i*offset1, '%s'%(udict.get(u, 'None')), font_size=25, ttype='en')
        d.add_text(720, 190+i*offset1, '得分: %s'%(format(int(r[u][0]),',')), font_size=20, ttype='cn')
        d.add_text(900, 190+i*offset1, '(%sx)'%(format(int(r[u][1]),',')), font_size=20, ttype='en')
        d.add_text(1050-20*len(mds_l), 165+i*offset1, '%s'%(m), font_size=20, ttype='en')
        d.add_text(1010, 190+i*offset1, '%s%%'%(r[u][3]), font_size=18, ttype='en')

    n = random.randint(0, 100)
    p = 'rank%s.png' % n
    pfs = 'rank%s-fs8.png' % n
    f = '/static/interbot/image/%s' % p
    d.save(f)
    # 压缩
    os.system('pngquant -f %s' % f)
    logging.info('[%s]榜单生成成功!' % pfs)
    return pfs

def start(bid='847314', groupid='614892339', hid=1, mods=-1, uid='8505303'):
    mapjson,rankjson = draw_data.map_ranks_info(str(bid), groupid, hid, mods)
    ppyIns = ppyHandler.ppyHandler()
    userjson = ppyIns.getOsuUserInfo(uid)[0]
    mapjson = ppyIns.getOsuBeatMapInfo(bid)[0]
    return drawR(mapjson,rankjson,userjson)
