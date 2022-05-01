# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
import requests



class mpHandler():


    def __init__(self):
        pass

    def test(self):
        url = "https://osu.ppy.sh/community/matches/96490509"
        rs = requests.get(url)
        print(rs.text)




if __name__ == "__main__":
    b = mpHandler()
    b.test()



