# -*- coding: utf-8 -*-
import sys
sys.path.append('./')


from ppyappLib import ppyAPI
from draws import score



def get_rec_tmp():
    t = {"beatmap_id": "", "score": "", "maxcombo": "", "count50": "", "count100": "", 
    "count300": "", "countmiss": "", "countkatu": "", "countgeki": "", "perfect": "", 
    "enabled_mods": "", "user_id": "", "date": "", "rank": "", "score_id": ""}
    return t


# mp_res = {
#     'match': {'match_id': '100252592', 'name': '新人群:25届群赛A组', 'start_time': '2022-05-01 11:57:50', 'end_time': None}, 
#     'games': [
#         {'game_id': '511271295', 'start_time': '2022-05-01 12:12:26', 'end_time': '2022-05-01 12:16:24', 'beatmap_id': '2300502', 'play_mode': '0', 'match_type': '0', 'scoring_type': '3', 'team_type': '0', 'mods': '0', 
#         'scores': [
#             {'slot': '0', 'team': '0', 'user_id': '26300418', 'score': '43276', 'maxcombo': '71', 'rank': '0', 'count50': '59', 'count100': '132', 'count300': '164', 'countmiss': '26', 'countgeki': '11', 'countkatu': '33', 'perfect': '0', 'pass': '0', 'enabled_mods': None}, 
#             {'slot': '2', 'team': '0', 'user_id': '29552621', 'score': '443024', 'maxcombo': '475', 'rank': '0', 'count50': '3', 'count100': '72', 'count300': '305', 'countmiss': '1', 'countgeki': '42', 'countkatu': '49', 'perfect': '0', 'pass': '1', 'enabled_mods': None}, 
#             {'slot': '3', 'team': '0', 'user_id': '28203001', 'score': '390819', 'maxcombo': '470', 'rank': '0', 'count50': '6', 'count100': '77', 'count300': '296', 'countmiss': '2', 'countgeki': '42', 'countkatu': '45', 'perfect': '0', 'pass': '1', 'enabled_mods': None}, 
#             {'slot': '4', 'team': '0', 'user_id': '16275637', 'score': '372413', 'maxcombo': '309', 'rank': '0', 'count50': '4', 'count100': '57', 'count300': '319', 'countmiss': '1', 'countgeki': '49', 'countkatu': '41', 'perfect': '0', 'pass': '1', 'enabled_mods': None}, 
#             {'slot': '5', 'team': '0', 'user_id': '28494479', 'score': '94171', 'maxcombo': '165', 'rank': '0', 'count50': '44', 'count100': '158', 'count300': '173', 'countmiss': '6', 'countgeki': '14', 'countkatu': '43', 'perfect': '0', 'pass': '1', 'enabled_mods': None}, 
#             {'slot': '6', 'team': '0', 'user_id': '25131253', 'score': '567660', 'maxcombo': '539', 'rank': '0', 'count50': '6', 'count100': '44', 'count300': '331', 'countmiss': '0', 'countgeki': '56', 'countkatu': '32', 'perfect': '0', 'pass': '1', 'enabled_mods': None}, 
#             {'slot': '15', 'team': '0', 'user_id': '11537994', 'score': '0', 'maxcombo': '0', 'rank': '0', 'count50': '0', 'count100': '0', 'count300': '0', 'countmiss': '381', 'countgeki': '0', 'countkatu': '0', 'perfect': '0', 'pass': '0', 'enabled_mods': None}]
#             }
#         ]
#     }


# 25届
# A
# https://osu.ppy.sh/community/matches/100252592
# B 
# https://osu.ppy.sh/community/matches/100252563
# C
# https://osu.ppy.sh/community/matches/100252957
# D
# https://osu.ppy.sh/community/matches/100252329
# E
# https://osu.ppy.sh/community/matches/100252448
# F
# https://osu.ppy.sh/community/matches/100252520
# G
# https://osu.ppy.sh/community/matches/100252686
# A 补图1，重算
# https://osu.ppy.sh/community/matches/100255761




def main():
    hid = 25
    # mids = [100252592, 100252563, 100252957, 100252448, 100252520, 100252686]
    mids = [100255761]
    admins = ['11537994', '11355787', '7003013', '9580470', '7183040', '6073139', '12398775', '24010320']
    for mid in mids:
        add_maprank(hid, mid, admins)


def add_maprank(hid=25, mid=100252592, admins=[]):
    hid = 25
    groupid = hid
    mp_res = ppyAPI.apiRoute("mp", mid=mid)

    print(f"match: {mid} run...")
    for game in mp_res["games"]:
        beatmap_id = game["beatmap_id"]
        end_time = game["end_time"]
        print(f"bid: {beatmap_id} run...")
        for s in game["scores"]:
            if s['user_id'] in admins:
                continue
            print(f"uid: {s['user_id']} run...")
            if not s["enabled_mods"]:
                s["enabled_mods"] = 0
            s["beatmap_id"] = beatmap_id
            s["date"] = end_time
            s["rank"] = "S"
            score.map_rank([s], groupid, hid, rtype=1, topslimit=200)

    print(f"match: {mid} finish...")




if __name__ == "__main__":
    main()
