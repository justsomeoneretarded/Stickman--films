"""Layered, depth-scaled architecture with ground perspective and parallax."""
import math
import cairocffi as cairo
from .drawing import *
from .motion import smooth

OUTDOOR={"city","forest","desert","island","battlefield"}


def background(c,env,lighting,t,pan=0,design="classic"):
    night=lighting in ("night","dramatic")
    top="#152c40" if night else "#c8d7cd"
    bottom="#45616c" if night else "#eee5d0"
    if design=="psychology" and not night:top="#ddd5c5";bottom="#f5e8ce"
    if design=="outage":top="#183747" if night else "#9eb6bc";bottom="#496874" if night else "#d8dfd2"
    g=cairo.LinearGradient(0,0,0,900)
    for v,col in [(0,top),(1,bottom)]: g.add_color_stop_rgb(v,*tuple(int(col[i:i+2],16)/255 for i in (1,3,5)))
    c.set_source(g);c.paint()
    # Far silhouettes move at a fraction of the camera displacement.
    c.save();c.translate(-pan*.13,0)
    if env in OUTDOOR:
        ellipse(c,1250,215,70,70,PAPER,alpha=.65 if night else .9)
        for layer in range(3):
            color_= ["#7c9e9b","#638c8a","#507c7c"][layer]
            points=[(-500,670)]
            for i in range(12):points.append((-500+i*230,450+layer*52+math.sin(i*1.8+layer)*75))
            points.extend([(2400,900),(-500,900)])
            poly(c,points,color_,.35)
        if env=="city":
            for i in range(15):
                x=-200+i*155;h=100+(i*73)%200
                rect(c,x,610-h,110,h,"#577e82",5,alpha=.5)
                for j in range(3):rect(c,x+15+j*28,635-h,10,18,PAPER,2,alpha=.5)
        if env in ("forest","island"):
            for i in range(8):
                x=-150+i*290
                line(c,[(x,650),(x+12,390)],"#53746a",15)
                for dx,dy in [(-35,410),(35,390),(0,350)]:ellipse(c,x+dx,dy,58,69,"#608e7e",alpha=.8)
        if env=="desert":poly(c,[(-300,660),(450,520),(970,650),(1700,550),(1900,900),(-300,900)],"#c5b48a")
    elif env=="digital":
        for i in range(16):
            rect(c,i*130-160,280+(i%3)*60,92,120,"#79a7a4",7,alpha=.18)
            for j in range(3):line(c,[(i*130-143,310+j*22),(i*130-88,310+j*22)],MINT,3,alpha=.27)
        for i in range(8):ellipse(c,140+i*205,390+math.sin(i*2)*90,7,7,MINT,alpha=.7)
    elif env=="abstract" and design=="psychology":
        for i in range(5):ellipse(c,150+i*360,420+math.sin(i*2)*70,160,180,"#c2b7a0",alpha=.13)
        line(c,[(-300,635),(2100,635)],"#b4a793",2,alpha=.3)
    else:
        # Interior verticals, recessed windows and deliberately simple architecture.
        for x in (-200,440,1080,1720):
            rect(c,x,230,290,325,"#789b98",14,alpha=.24)
            rect(c,x+15,245,260,295,"#b9cebf" if not night else "#224052",9)
            line(c,[(x+145,245),(x+145,540)],"#73918c",6)
            line(c,[(x+15,396),(x+275,396)],"#73918c",6)
        if env in ("office","classroom","laboratory","bank"):
            for i in range(4):
                x=i*500-150
                rect(c,x,565,295,17,"#71928c",5)
                line(c,[(x+25,582),(x+25,658)],"#71928c",8)
                line(c,[(x+269,582),(x+269,658)],"#71928c",8)
                draw_prop(c,"book" if env=="classroom" else "phone",x+160,565,scale=.6)
        elif env=="bedroom":
            rect(c,70,568,310,80,"#9bb7a6",14);rect(c,60,548,90,32,PAPER,12)
        elif env=="restaurant":
            for x in (130,1120):
                ellipse(c,x,570,100,22,"#a5a78a");line(c,[(x,590),(x,650)],"#7e897a",10)
    c.restore()


def ground(c,env,t,pan=0,design="classic"):
    outdoor=env in OUTDOOR
    fill="#b6bda4" if outdoor else "#d0c9b5"
    if env=="digital":fill="#537780"
    if design=="psychology":fill="#c9bda1"
    if design=="outage":fill="#94a8a5" if env!="digital" else "#43616d"
    poly(c,[(-1000,650),(3000,650),(3000,1400),(-1000,1400)],fill)
    line(c,[(-1000,650),(3000,650)],INK,2,alpha=.12)
    for i in range(-3,14):
        x=i*260-pan*.35
        line(c,[(800+(x-800)*.42,650),(x,1000)],INK,1.2,alpha=.10)
    for y in (710,804,943):line(c,[(-1000,y),(3000,y)],INK,1,alpha=.09)
    if outdoor:
        for i in range(18):
            x=(i*193+31)%2000-200
            line(c,[(x,738+(i%3)*24),(x+5,726+(i%3)*24)],"#6d8c75",3,alpha=.45)


def foreground(c,env,t,pan=0,design="classic"):
    c.save();c.translate(-pan*1.17,0)
    if env in ("forest","island","abstract"):
        for x in (-60,1640):
            line(c,[(x,1020),(x+30,803)],"#547d72",12,alpha=.65)
            for j in range(4):ellipse(c,x+(-1 if j%2 else 1)*24,850-j*22,44,12,"#547d72",alpha=.7)
    elif env in ("office","classroom","laboratory","restaurant"):
        for x in (-100,1670):
            poly(c,[(x-85,885),(x+75,862),(x+122,900),(x-95,950)],"#557b78",.32)
    c.restore()


def camera(scene,t,duration,focus_x=650):
    u=min(1,max(0,t/max(duration,1e-6)));e=smooth(u)
    mode=scene.camera
    zoom=1.;cx=800;cy=450
    if mode in ("dolly-in","zoom"):zoom=1+.12*e;cy=465
    if mode=="dolly-out":zoom=1.16-.16*e
    if mode in ("follow","tracking"):cx=800+(focus_x-650)*.65;zoom=1.06
    if mode=="pan":cx=730+120*e
    if mode=="tilt":cy=490-55*e
    if mode=="reveal":cx=690+170*e;zoom=1.08-.08*e
    if mode=="establishing":zoom=.94+.06*e
    if mode=="wide":zoom=1
    if mode=="close-up":zoom=1.30;cx=focus_x+120;cy=490
    if mode=="over-shoulder":zoom=1.16;cx=focus_x+180;cy=475
    if scene.design!="classic":
        if mode=="close-up":zoom=1.85;cx=focus_x+65;cy=520
        if mode=="over-shoulder":zoom=1.4;cx=focus_x+180;cy=505
        if mode=="dolly-in":zoom=1.02+.32*e;cx=720+80*e;cy=475
        if mode=="dolly-out":zoom=1.32-.32*e;cy=475
    return cx,cy,zoom
