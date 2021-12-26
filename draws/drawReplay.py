# coding: utf-8

import sys
sys.path.append('./')

import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
from draws import draw_data, drawRank
from commLib import mods
from botappLib import botHandler
from ppyappLib import ppyHandler

pre = 'draws/'
default_skin = '%s/New!+game!' % pre
osu_ui = '%s/osu!ui/Resources' % pre
font_cn = '%s/font/msyh.ttc' % pre
font_alp = '%s/font/Aller_Rg_MODFIED.ttf' % pre




def drawRec(mapjson, recinfo, bestinfo, userjson, **kw):
    """
    kwargs:
        pp, fcpp, acpp

    """

    # skin
    bg_e = draw_data.check_bg(mapjson['beatmap_id'], mapjson['beatmapset_id'])
    bg = '%s.jpg'%mapjson['beatmap_id'] if bg_e else 'newgame_background.png' 
    back_icon = 'menu-back-0.png'
    mod_icon = 'selection-mode.png'
    mods_icon = 'selection-mods.png'
    random_icon = 'selection-random.png'
    options_icon = 'selection-options.png'
    rank_x = 'ranking-%s-small.png'
    maxcb_icon = 'ranking-maxcombo.png'
    acc_icon = 'ranking-accuracy.png'
    ranking_icon = 'ranking-title.png'
    rank_icon = 'ranking-%s.png'
    replay_icon = 'ranking-replay.png'
    score_icon = 'score-%s.png'
    score_x_icon = 'score-x.png'
    score_pp_icon = 'score-p.png' # 自制p字母
    score_dot_icon = 'score-dot.png'
    score_p_icon = 'score-percent.png'
    hit0_icon = 'hit0.png'
    hit50_icon = 'hit50.png'
    hit50k_icon = 'hit50k.png'
    hit100_icon = 'hit100.png'
    hit100k_icon = 'hit100k.png'
    
    mod_icon_map={
        'NF': 'selection-mod-nofail.png',
        'EZ': 'selection-mod-easy.png',
        'NV': 'selection-mod-random.png', # 这个未知
        'HD': 'selection-mod-hidden.png',
        'HR': 'selection-mod-hardrock.png',
        'SD': 'selection-mod-suddendeath.png',
        'DT': 'selection-mod-doubletime.png',
        'Relax': 'selection-mod-relax.png',
        'HT': 'selection-mod-halftime.png',
        'NC': 'selection-mod-nightcore.png',
        'FL': 'selection-mod-flashlight.png',
        'AT': 'selection-mod-autoplay.png',
        'SO': 'selection-mod-spunout.png',
        'AP': 'selection-mod-relax2.png',
        'PF': 'selection-mod-perfect.png',
    }

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
    bpm = kw['bpm'] if kw.get("bpm") else mapjson.get('bpm','')
    max_combo = mapjson.get('max_combo','')
    difficultyrating = kw['star'] if kw.get("star") else round(float(mapjson.get('difficultyrating','')),2)  #star
    diff_size = kw['cs'] if kw.get("cs") else mapjson.get('diff_size','') #CS
    diff_approach = kw['ar'] if kw.get("ar") else mapjson.get('diff_approach','') #AR
    diff_overall = kw['od'] if kw.get("od") else mapjson.get('diff_overall','') #OD
    diff_drain = kw['hp'] if kw.get("hp") else mapjson.get('diff_drain','') #HP
    count_normal = mapjson.get('count_normal', 0)
    count_slider = mapjson.get('count_slider', 0)
    count_spinner = mapjson.get('count_spinner', 0)


    m, s = divmod(int(mapjson.get('total_length')), 60)
    h, m = divmod(m, 60)
    if h != 0:
        hit_length = "%02d:%02d:%02d" % (h, m, s) #sec
    else:
        hit_length = "%02d:%02d" % (m, s) #sec

    # 头像download
    me = userjson.get('user_id', '')
    draw_data.check_img([me])
    
    d = drawRank.DrawRec()

    # 第一层bg
    d.add_items(isresize=True, path='image/bg/%s'%bg, factor=0.95)
    # title黑层
    d.add_items2(songselecttop)
    # 低下大黑条
    d.add_items2(songselect_bottom, 0, 648, isresize=True, width=1366, height=120)
    # 大粉饼
    d.add_items2(osu_icon, 1130, 550, isresize=True, width=300, height=300)
    # 返回
    d.add_items(back_icon, 10, 615)
    
    # 设置项
    d.add_items(mod_icon, 250, 678) # mode
    d.add_items(mods_icon, 340, 678) # mods选择
    d.add_items(random_icon, 430, 678) # random
    d.add_items(options_icon, 520, 678) # options

    # 头像
    d.add_items(x=690, y=675, path='image/userimg/%s.jpg'%me, isresize=True, width=90, height=90)
    # 用户信息
    d.add_items2(umod, 998, 670, factor=0.5)
    d.add_text(968, 710, '# %s'%rank, font_size=16, ttype='en')
    d.add_text(788, 670, uname, font_size=24, ttype='en')
    d.add_text(788, 700, 'Performance:%spp'%pp, font_size=16, ttype='en')
    d.add_text(788, 720, 'Accuracy:%s%%'%acc, font_size=16, ttype='en')
    d.add_text(788, 740, 'Lv%s'%level, font_size=16, ttype='en')
    d.add_items2(level_bar, 840, 745, isresize=True, width=int(lv_left*200), height=14)
    d.add_items2(level_bar_bg, 840, 745)

    # 曲子信息
    d.add_text(35, 0, '%s %s - %s [%s]'%(source,artist,title,version), font_size=25, ttype='cn')
    d.add_items2(selection_approved, 7, 3)
    d.add_text(40, 30, '作者: %s'%(creator), font_size=16, ttype='cn')
    d.add_text(5, 50, '长度: %s  BPM: %s  物件数: %s'%(hit_length,bpm,max_combo), font_size=18, ttype='cn')
    d.add_text(5, 75, '圈数: %s 滑条数: %s 转盘数: %s'%(count_normal,count_slider,count_spinner), font_size=16, ttype='cn')
    d.add_text(5, 100, 'CS:%s AR:%s OD:%s HP:%s Star:%s★'%(diff_size,diff_approach,diff_overall,diff_drain,difficultyrating), font_size=16, ttype='en')

    # 个人最佳成绩区域
    d.add_text(150, 550, '个人最佳成绩', font_size=24, ttype='cn')
    d.draw_rectangle(x=20, y=590, width=460, height=60, fill=(0, 0, 0, 90))

    mds = int(bestinfo['enabled_mods'])
    mds_l = mods.getMod(mds)
    if 'NONE' in mds_l:
        mds_l.remove('NONE')
    m_str = ','.join(mds_l) if mds > 0 else ''
    rank = 'D' if bestinfo['rank'] == 'F' else bestinfo['rank']
    d.add_items(x=20, y=590, path='image/userimg/%s.jpg'%me, isresize=True, width=60, height=60)
    d.add_items(rank_x%rank, 80, 595)
    d.add_text(120, 590, f"{uname}  #{round(float(bestinfo['pp']))}pp", font_size=25, ttype='en')
    d.add_text(120, 620, f"得分: {int(bestinfo['score']):,}    ({int(bestinfo['maxcombo']):,}x)", font_size=20, ttype='cn')
    d.add_text(450-20*len(mds_l), 597, '%s'%(m_str), font_size=20, ttype='en')
    acc = mods.get_acc(bestinfo['count300'], bestinfo['count100'], bestinfo['count50'], bestinfo['countmiss'])
    d.add_text(410, 620, f"{acc:.2f}%", font_size=18, ttype='en')

    # 当前成绩区域
    d.draw_rectangle(x=20, y=160, width=600, height=60, fill=(0, 0, 0, 90))
    d.draw_rectangle(x=20, y=240, width=600, height=300, fill=(0, 0, 0, 90))

    # 分数icon
    d.add_items(hit100_icon, 40, 320)
    d.add_items(hit50_icon, 40, 380)
    d.add_items(hit100k_icon, 350, 320)
    d.add_items(hit0_icon, 350, 350)
    d.add_items(maxcb_icon, 40, 440)
    d.add_items(acc_icon, 330, 440)

    # score
    for idx, s in enumerate(recinfo['score'][::-1]):
        d.add_items(score_icon%s, 550-50*idx, 170)

    for idx, s in enumerate(recinfo['count300']+'x'):
        d.add_items(score_icon%s, 180+idx*35, 260)

    for idx, s in enumerate(recinfo['count100']+'x'):
        d.add_items(score_icon%s, 180+idx*35, 320)

    for idx, s in enumerate(recinfo['count50']+'x'):
        d.add_items(score_icon%s, 180+idx*35, 380)

    for idx, s in enumerate(recinfo['countgeki']+'x'):
        d.add_items(score_icon%s, 490+idx*35, 260)

    for idx, s in enumerate(recinfo['countkatu']+'x'):
        d.add_items(score_icon%s, 490+idx*35, 320)
        
    for idx, s in enumerate(recinfo['countmiss']+'x'):
        d.add_items(score_icon%s, 490+idx*35, 380)

    # cb
    for idx, s in enumerate(recinfo['maxcombo']+'x'):
        d.add_items(score_icon%s, 60+idx*35, 480)
    # acc
    acc2 = mods.get_acc(recinfo['count300'], recinfo['count100'], recinfo['count50'], recinfo['countmiss'])
    acc_str = str(round(acc2, 2))
    acc_start_x = 360
    for idx, s in enumerate(acc_str):
        if s == '.':
            d.add_items(score_dot_icon, acc_start_x+idx*35, 480)
            acc_start_x -= 25 # 去掉间隙
        else:
            d.add_items(score_icon%s, acc_start_x+idx*35, 480)

        if idx + 1 == len(acc_str):
            d.add_items(score_p_icon, acc_start_x+idx*35+35, 480)

    mds2 = int(recinfo['enabled_mods'])
    mds_l2 = mods.getMod(mds2)
    if 'NONE' in mds_l2:
        mds_l2.remove('NONE')
    rank2 = 'D' if recinfo['rank'] == 'F' else recinfo['rank']

    d.add_items(ranking_icon, 1000, 10) # 右上角 ranking
    d.add_items(replay_icon, 920, 470, factor=0.8) # replay
    d.add_items(rank_icon%rank2, 920, 100) # 评分
    # mod
    for idx, mod in enumerate(mds_l2[::-1]):
        m_icon = mod_icon_map.get(mod)
        if not m_icon:
            continue
        d.add_items(m_icon, 1190-70*idx, 390)

    # pp区域
    d.draw_rectangle(x=640, y=590, width=460, height=60, fill=(0, 0, 0, 90))
    d.add_items(score_pp_icon, 650, 600)
    for idx, s in enumerate(str(round(kw["pp"]))):
        d.add_items(score_icon%s, 710+idx*30, 600)

    for idx, s in enumerate(str(round(kw["fcpp"]))):
        d.add_items(score_icon%s, 840+idx*30, 600)

    for idx, s in enumerate(str(round(kw["acpp"]))):
        d.add_items(score_icon%s, 980+idx*30, 600)

    
    # d.RecImg.show()

    uid = userjson.get('user_id', '')
    p = 'rctpp-%s.png' % uid
    pfs = 'rctpp-%s-fs8.png' % uid
    f = '/static/interbot/image/%s' % p
    d.save(f)
    # 压缩
    os.system('pngquant -f %s' % f)
    logging.info('[%s]成绩生成成功!' % pfs)
    return pfs


if __name__ == "__main__":
    
    mapjson = {'beatmapset_id': '1086772', 'beatmap_id': '2272608', 'approved': '1', 'total_length': '86', 'hit_length': '85', 'version': 'Angel', 
    'file_md5': 'a3689f6595911caf32ab8329c6d9c378', 'diff_size': '4', 'diff_overall': '8', 'diff_approach': '9.1', 'diff_drain': '5.7', 
    'mode': '0', 'count_normal': '247', 'count_slider': '120', 'count_spinner': '0', 'submit_date': '2019-12-31 15:21:07', 'approved_date': '2020-03-28 17:02:07', 
    'last_update': '2020-03-19 13:59:55', 'artist': 'HoneyWorks', 'artist_unicode': 'HoneyWorks', 'title': 'Watashi no Tenshi feat. Narumi Sena (CV: Amamiya Sora)', 
    'title_unicode': 'ワタシノテンシ feat. 成海聖奈（CV：雨宮天）', 'creator': 'C O N N E R', 'creator_id': '3222353', 'bpm': '168', 'source': '', 
    'tags': 'short ver my little angel very very cute sister imouto mona gom [_lost_] conner c_o_n_n_e_r frozz fzl_17 hikan xen xenon- xehn serizawa haruki j_a_c_k jack japanese jpop pop j-pop', 
    'genre_id': '5', 'language_id': '3', 'favourite_count': '285', 'rating': '9.3888', 'storyboard': '0', 'video': '0', 'download_unavailable': '0', 
    'audio_unavailable': '0', 'playcount': '235053', 'passcount': '42534', 'packs': 'S876', 'max_combo': '487', 'diff_aim': '2.38286', 'diff_speed': '2.23119', 
    'difficultyrating': '4.79777'}

    recinfo = {'score_id': '3727585910', 'score': '2238828', 'username': 'interbot', 'maxcombo': '487', 'count50': '0', 
    'count100': '6', 'count300': '361', 'countmiss': '0', 'countkatu': '6', 'countgeki': '67', 'perfect': '1', 'enabled_mods': '1', 
    'user_id': '11788070', 'date': '2021-06-19 09:50:36', 'rank': 'S', 'pp': '133.597', 'replay_available': '0'}

    userjson = {'user_id': '11788070', 'username': 'interbot', 'join_date': '2018-02-22 07:51:46', 'count300': '1587854', 
        'count100': '339607', 'count50': '44451', 'playcount': '5319', 'ranked_score': '2038490047', 'total_score': '4678155119', 
        'pp_rank': '143495', 'level': '88.9205', 'pp_raw': '3196.72', 'accuracy': '95.25702667236328', 'count_rank_ss': '0', 
        'count_rank_ssh': '0', 'count_rank_s': '44', 'count_rank_sh': '0', 'count_rank_a': '267', 'country': 'CN', 
        'total_seconds_played': '496736', 'pp_country_rank': '2356', 'events': []}

    kwargs = {
        "pp": 133.597,
        "fcpp": 135.604,
        "acpp": 180.514,
    }

    drawRec(mapjson, recinfo, recinfo, userjson, **kwargs)

