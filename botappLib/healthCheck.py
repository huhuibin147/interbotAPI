# -*- coding: utf-8 -*-

import math

def health_check(user, bp):
    '''健康指数2'''
    pp = float(user['pp_raw'])
    pc = int(user['playcount'])
    tth = int(user['count300'])+int(user['count100'])+int(user['count50'])
    bp1 = float(bp[0]['pp'])
    bp5 = float(bp[4]['pp'])
    acc_list = []
    for b in bp:
        c50 = float(b['count50'])
        c100 = float(b['count100'])
        c300 = float(b['count300'])
        cmiss = float(b['countmiss'])
        acc = round((c50*50+c100*100+c300*300)/(c50+c100+c300+cmiss)/300,2)
        acc_list.append(acc)
    acc_list = sorted(acc_list,reverse=True)
    acc1 = acc_list[0]
    acc2 = acc_list[1]
    acc3 = acc_list[2]
    # print(pp,pc,tth,bp1,bp5,acc1,acc2,acc3)
    v = pp*pc*tth*bp1*bp5*acc1*acc2*acc3
    if v == 0:
        return "%s 数据不正常" % uid
    else:
        A1 = pp/(4*bp1-3*bp5)
        A2 = math.log(tth/pc)/math.log(15.5)
        if pp < 1000:
            A31 = 1000*pc/(1.2*pp)-400
        elif pp < 7000:
            A31 = 1000*pc/(0.0008*pp*pp+0.4*pp)-400
        else:
            A31 = 1000*pc/(6*pp)-400
        if A31 > 1:
            A3 = math.log(A31)/math.log(24.5)
        else:
            A3 = 0
        A4 = math.pow((acc1+acc2+acc3)/3,5)
        total = A1*A2*A3*A4
        
        if pp < 300:
            level = "该号pp较低，不作出评价"
        elif total >= 55: 
            level = "该号成绩卓越，同分段中的王者!"
        elif total >= 44:
            level = "该号成绩优秀，标准的正常玩家!"
        elif A3 < 1 or A1 < 3:
            level = "基本断定是小号或者离线党!"
        elif A3 < 1.7: 
            if A1 < 9:
                level = "要么天赋超群，要么小号或者离线党,总之这个pp严重虚低!"
            else:
                if A4 < 0.75:
                    level = "虽然天赋超群,但是求你别糊图了!"
                elif A4 < 0.88: 
                    level = "虽然天赋超群，但是建议花些pc好好练习一下acc吧!"
                elif A2 < 1.7: 
                    level = "是一个有天赋的超级pp刷子,求求你不要re了!"
                elif A2 < 1.9: 
                    level = "是一个有天赋的高级pp刷子,建议降低re图次数!"
                else:
                    level = "是一个有天赋又认真的pp刷子,建议多打点综合图!"
            
        
        elif A3 < 1.9:
            if A1 < 9 and A4 > 0.75: 
                level = "有一定天赋，将来一定时间内还是可以飞升一波的!"
            if A1 < 11 and A4 > 0.75: 
                level = "有一定天赋，将来一定时间内还是可以小幅涨一点的!"
            else:
                if A4 < 0.75: 
                    level = "虽然有一些天赋,但是求你别糊图了!"
                elif A4 < 0.88: 
                    level = "虽然有一些天赋，但是建议花些pc好好练习一下acc吧!"
                elif A2 < 1.7: 
                    level = "是一个标准pp刷子,求求你不要re了!"
                elif A2 < 1.9: 
                    level = "是一个标准pp刷子,建议降低re图次数!"
                elif A2 < 2.1: 
                    level = "是一个标准pp刷子,建议多打点综合图!"
                else: 
                    level = "这种情况比较罕见，你应该和各种类型的人都不一样!"
            
        
        elif A3 < 2.1:
            if A1 < 9 and A4 > 0.75: 
                level = "看样子正渡过瓶颈期了，将来一定时间内还是可以飞升一波的!"
            if A1 < 11 and A4 > 0.75: 
                level = "要么即将渡过瓶颈期，要么之前飞太快即将进入瓶颈期!"
            else:
                if A4 < 0.75: 
                    level = "你啥都不错,但是求你别糊图了!"
                elif A4 < 0.88: 
                    level = "比较正常，但是建议好好练习一下acc吧!"
                elif A2 < 1.7: 
                    level = "是一个没天赋的pp刷子,求求你不要re了!"
                elif A2 < 1.9: 
                    level = "是一个没天赋的pp刷子,建议降低re图次数!"
                else:
                    level = "比较正常，但是可能某些方面有所欠缺，请参考指标!"
            
        
        elif A3 < 2.4:
            if A1 < 9 and A4 > 0.75: 
                level = "相信自己，你正在飞升!"
            if A1 < 11 and A4 > 0.75: 
                level = "也许在瓶颈期附近，但是相信你能克服它!"
            else:
                if A4 < 0.75: 
                    level = "你真的很强,但是求你别糊图了!"
                elif A4 < 0.88: 
                    level = "你真的很强，但是建议好好练习一下acc吧!"
                elif A2 < 1.7: 
                    level = "是一个没救了的pp刷子,求求你不要re了!"
                elif A2 < 1.9: 
                    level = "是一个没救了的pp刷子,建议降低re图次数!"
                else:
                    level = "这孩子瓶颈了!"
            
        else:
            if A1 < 10 and A4 > 0.75: 
                level = "打图经验充足，不飞升没理由!"
            else:
                if A2 < 1.8: 
                    level = "你这么个re图毫无用处，好好考虑下吧!"
                else:
                    level = "你不适合屙屎，删游戏吧!"
            
        
        msg = '%s\nBP指标:%.2f 参考值12.00\nTTH指标:%.2f 参考值2.00\nPC指标:%.2f 参考值2.00\nACC指标:%.4f 参考值0.9000\n综合指标:%.2f\n结论:%s' %(user['username'],A1,A2,A3,round(A4,4),round(total,2),level)
        return msg
