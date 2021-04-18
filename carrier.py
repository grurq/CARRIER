# -*- coding: utf-8 -*-
import blessed
import re
import time
import numpy 
import datetime
import os
import sys
import pathlib
term = blessed.Terminal()
tile=(' ','.','$','*','@','+','6','7','#','9','A','B','C','D','E','F','!')
"""
移動関数
0:床 半角空白
1:置き場 .
2:荷物 $
3:置かれた荷物 *
4:床の人 @
5:置き場の人 +
8:壁 #
"""
XMAX=32
YMAX=24
ZMAX=20
CONSOLEX=36
fname='stage'

smax=0
px=0
py=0
steps=0
mstep=0

world=[]
scores=numpy.zeros([ZMAX],dtype=int)
stage=0
floor=numpy.zeros([XMAX,YMAX],dtype=int)
class level:
    """
    下記のアトリビュートを代入せよ
    width   :幅
    height  :高さ
    floor[,]:フロア（width,heightで定義）
    hiscore :最小歩数

    ※hiscoreが必要なので、レコードを作る必要がある。
    今はここは無視する
    """
    pass

def chipprint(x,y):
    with term.hidden_cursor():
        print(term.move_xy(x,y)+tile[floor[x,y]])
def initscore(name):
    f=open(str(name)+'r','w',encoding='utf-8')
    for h in range(ZMAX):
        f.write('0|')
    f.close()
def loadscore(name):
    global scores
    try:
        f=open(str(name)+'r','r',encoding='utf-8')
    except FileNotFoundError:
        initscore(name)
    else:
        words=f.read()
        f.close()
        if words.find('|')<0:
            initscore(name)
        words=re.sub('[^0123456789\|]','',words)
        bars=words.count('|')
        words=words.split('|')
        for i in range(bars):
            scores[i]=int(words[i])
def savescores(name):
    global scores
    words=''
    f=open(str(name)+'r','w',encoding='utf-8')
    for h in range(ZMAX):
        words+=str(scores[h])+'|'
    f.write(words)
    f.close()
def loadgame(name):
    f=open(name,'r',encoding='utf-8')
    words = f.read()
    f.close()
    words=re.sub('[^0123456789\|]','',words)
    bars=words.count('|')
    words=words.split('|')

    for z in range(bars):
        xy=words[z]
        if z%2==0:
            wz=level()
            if len(words[z])!=4:
                return z//2
            wz.width=int(xy[0:2])
            wz.height=int(xy[2:4])
            wz.floor=numpy.zeros([wz.width,wz.height],dtype=int)
        else:
            tiles=words[z]
            for x in range(wz.width):
                for y in range(wz.height):
                    wz.floor[x,y]=tiles[x+y*wz.width]
            world.append(wz)
            del(wz)
    return bars//2
def loadlevel(ID):
    global px
    global py
    global floor
    global mstep
    mstep=scores[ID]
    for x in range(XMAX):
        for y in range(YMAX):
            floor[x,y]=world[ID].floor[x,y] if x<world[ID].width and y<world[ID].height else 0 
            if floor[x,y]&4:
                px=x
                py=y
                
def fullprint():
    for x in range(XMAX):
        for y in range(YMAX):
            chipprint(x,y)

def docs(ID):
    # 文字部分の画面を表示する
    # 40から
    # 0:ステップ
    # 1:ステージ
    # 2:解説・クレジット
    global smax
    global stage
    with term.hidden_cursor():
        if ID==0:
            s=str(steps)
            print(term.move_xy(CONSOLEX,5)+'steps:'+s.rjust(8))
            s=str(mstep) if mstep!=0 else 'none'
            print(term.move_xy(CONSOLEX,6)+'best :'+s.rjust(8))
        elif ID==1:
            s=str(stage+1)
            print(term.move_xy(CONSOLEX,2)+'stage:'+s.rjust(2))
            s=str(smax)
            print(term.move_xy(CONSOLEX+5,3)+'/'+s.rjust(2))
        elif ID==2:
            print(term.move_xy(CONSOLEX,8)+'操作方法')
            print(term.move_xy(CONSOLEX,9)+'↑→↓←：移動')
            print(term.move_xy(CONSOLEX,10)+'BS：やりなおし')
            print(term.move_xy(CONSOLEX,11)+'<>：面の移動')
            print(term.move_xy(CONSOLEX,12)+'ESC：終了')
            print(term.move_xy(CONSOLEX,14)+'記号一覧')
            print(term.move_xy(CONSOLEX,15)+'床 空白 置場 . 荷物 $ 置場の荷物 *')
            print(term.move_xy(CONSOLEX,16)+'床の人 @ 置き場の人 + 壁 #')

def changestartpos():
    for x in range(XMAX):
        for y in range(YMAX):
            if floor[x,y]&4!=0:
                if x!=px or y!=py:
                    floor[x,y]-= floor[x,y]&4
                    chipprint(x,y)
def chkclear(ID):
    global steps
    global scores
    for x in range(XMAX):
        for y in range(YMAX):
            if floor[x,y]==1 or floor[x,y]==2 or floor[x,y]==5:
                return False
    if steps<mstep or mstep==0:
        scores[ID]=steps
        savescores(fname)
    return True

def walk(x,y):
    global px
    global py
    global steps
    m1=-1
    m2=-1
    if x<0:
        if px==0:
        	return
        m1=floor[px+x,py]
        if px>1:
        	m2=floor[px+x+x,py] 
        if m1>=8:
        	return
        if m1>1 and m2>1:
        	return
        if m1&2!=0 and m2>=0 and m2<2:
            m1-=2
            m2+=2
        if m1<2:
            m1+=4
        if m1<4:
            return
        floor[px+x,py]=m1
        floor[px,py]-=4
        chipprint(px,py)
        chipprint(px+x,py)
        if m2>=0:
            floor[px+x+x,py]=m2
            chipprint(px+x+x,py)
        px+=x
        m1=-1
        m2=-1
    if x>0:
        if px==XMAX-1:
            return
        m1=floor[px+x,py]
        if m1>=8:
        	return
        if px<XMAX-2:
            m2=floor[px+x+x,py]
        if m1>=8:
        	return
        if m1>1 and m2>1:
        	return
        if m1&2!=0 and m2>=0 and m2<2:
            m1-=2
            m2+=2
        if m1<2:
            m1+=4
        if m1<4:
            return
        floor[px+x,py]=m1
        floor[px,py]-=4
        chipprint(px,py)
        chipprint(px+x,py)
        if m2>=0:
            floor[px+x+x,py]=m2
            chipprint(px+x+x,py)
        px+=x
        m1=-1
        m2=-1
    if y<0:
        if py==YMAX-1:
            return
        m1=floor[px,py+y]
        if m1>=8:
        	return
        if py<YMAX-2:
            m2=floor[px,py+y+y]
        if m1>1 and m2>1:
        	return
        if m1&2!=0 and m2>=0 and m2<2:
            m1-=2
            m2+=2
        if m1<2:
            m1+=4
        if m1<4:
            return
        floor[px,py+y]=m1
        floor[px,py]-=4
        chipprint(px,py)
        chipprint(px,py+y)
        if m2>=0:
            floor[px,py+y+y]=m2
            chipprint(px,py+y+y)
        py+=y
        m1=-1
        m2=-1
    if y>0:
        if py==YMAX-1:
            return
        m1=floor[px,py+y]
        if m1>=8:
        	return
        if py<YMAX-2:
            m2=floor[px,py+y+y]
        if m1>=8:
        	return
        if m1>1 and m2>1:
        	return
        if m1&2!=0 and m2>=0 and m2<2:
            m1-=2
            m2+=2
        if m1<2:
            m1+=4
        if m1<4:
            return
        floor[px,py+y]=m1
        floor[px,py]-=4
        chipprint(px,py)
        chipprint(px,py+y)
        if m2>=0:
            floor[px,py+y+y]=m2
            chipprint(px,py+y+y)
        py+=y
        m1=-1
        m2=-1
    steps+=1
    docs(0)
def getch():
    with term.cbreak():
        val = ''
        while val=='':
            val = term.inkey(timeout=0.1)
        
    return val

def getxmax():
	rm=0
	x=XMAX-1
	while x>=0:
		for y in range(YMAX):
			if floor[x,y]>0:
				rm=x
				break
		if rm>0:
			break
		x-=1
	return rm+1
def getymax():
	cm=0
	y=YMAX-1
	while y>=0:
		for x in range(XMAX):
			if floor[x,y]>0:
				cm=y
				break
		if cm>0:
			break
		y-=1
	return cm+1
def play(ID):
    loadlevel(ID)
    fullprint()
    docs(0)
    docs(1)
    docs(2)
    while chkclear(ID)==False:
        keypress=getch()
        if keypress.name=='KEY_ESCAPE':
            return -100
        elif keypress.name=='KEY_BACKSPACE':
            return 0
        elif keypress.name=='KEY_UP':
            walk(0,-1)
        elif keypress.name=='KEY_RIGHT':
            walk(1,0)
        elif keypress.name=='KEY_DOWN':
            walk(0,1)
        elif keypress.name=='KEY_LEFT':
            walk(-1,0)
        elif keypress.is_sequence==False:
            if keypress=='>':
                return 1
            elif keypress=='<':
                return -1
    savescores(fname)
    return 1
def select():
    wlist=list(pathlib.Path(os.path.dirname(sys.argv[0])+'/dat').glob('*.cr'))
    n=0
    keypress=''
    while 1:
        print(term.move_xy(0,0)+term.clear_eol+'ファイルを選んでください（↑↓：選択　SPACE：決定）')
        print(term.move_xy(0,1)+term.clear_eol+str(wlist[n]))
        keypress=getch()
        if keypress.name=='KEY_UP':
            n-=1
        if keypress.name=='KEY_DOWN':
            n+=1
        if n>=len(wlist):
            n=0
        if n<0:
            n=len(wlist)-1
        if keypress==' ':
            return str(os.path.basename(wlist[n]))
    

def main():
    global smax
    global stage
    global steps
    global fname
    with term.hidden_cursor():
        print(term.enter_fullscreen+term.clear_eol)
        fname=select()
        os.chdir(os.getcwd()+'/dat/')
        smax=loadgame(fname)
        loadscore(fname)
        print(term.move_xy(0,0)+term.clear())

        while stage>=0 and stage<smax:
            steps=0
            stage+=play(stage)
        print(term.exit_fullscreen+term.move_xy(0,0)+term.clear_eol)
        print(term.move_xy(0,0)+'アプリを終了しました')
        getch()
    return 0

if __name__ == '__main__':
    main()