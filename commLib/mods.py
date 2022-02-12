# -*- coding: utf-8 -*-
import logging


mod_list={
    0: 'NONE',
    1: 'NF',
    2: 'EZ',
    3: 'NV',
    4: 'HD',
    5: 'HR',
    6: 'SD',
    7: 'DT',
    8: 'RX',
    9: 'HT',
    10: 'NC',
    11: 'FL',
    12: 'AT',
    13: 'SO',
    14: 'AP',
    15: 'PF',
    16: 'PF',
    
}

def getMod(num=16504):
    '''NC出现的话删除DT，PF出现的话删除SD'''
    mods = []
    num = int(num)
    i=1
    while num:
        if num&0x1:
            mods.append(mod_list.get(i))
        num=num>>1
        i+=1
    if not mods:
        return ['NONE']
    if 'NC' in mods:
        mods.remove('DT')
    if 'PF' in mods:
        mods.remove('SD')
    
    return mods

def get_acc(c300, c100, c50, cmiss):
    c300 = int(c300)
    c100 = int(c100)
    c50 = int(c50)
    cmiss = int(cmiss)

    tph = c50 * 50 + c100 * 100 + c300 * 300
    tnh = cmiss + c50 + c100 + c300
    acc = tph / tnh / 3
    return round(acc, 2)


def get_mods_name(bitset):
    mods = getMod(int(bitset))
    name = ""
    for m in mods:
        name = name + m

    return name

