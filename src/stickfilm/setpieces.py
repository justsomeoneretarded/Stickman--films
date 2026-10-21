"""Directed animated set pieces for independently authored long-form films.

These are visual actions, not replacement slides. Art sits in world space and
responds continuously to the shot timeline and character positions.
"""
import math
from .drawing import *
from .motion import smooth

SETPIECES=['none','goal_wall','goal_backpack','tug_of_war','attention_loop','tiny_staircase','progress_meter','identity_mirror','city_network','cable_cut','offline_checkout','paper_map','supply_chain','notice_board','radio_desk','writing_desk','calendar','repair_links']

def draw_setpiece(c,kind,t,duration,poses,variant=0):
    u=min(1,max(0,t/max(.01,duration)));e=smooth(u);p=poses[0];hx,hy=p.joints['head'];wx,wy=p.joints['wrist_right']
    if kind=='none':return
    if kind=='goal_wall':
        for i,label in enumerate(['PERFECT BODY','NEW LANGUAGE','PROMOTION','SIDE BUSINESS','ALWAYS CALM','NEVER FAIL']):
            x=890+(i%2)*235;y=400+(i//2)*100
            dy=70*(1-smooth((u-i*.06)/.25))
            rect(c,x,y+dy,213,77,PAPER,9,INK,3);text(c,label,x+15,y+44+dy,17,INK,True,max_width=184)
        if variant==1:
            line(c,[(1134,516),(1318,551)],CORAL,7,alpha=smooth((u-.5)/.3))
    elif kind=='goal_backpack':
        x,y=p.joints['hips'];bx=x-49
        rect(c,bx-25,y-82,68,81,'#ad8064',13,INK,4)
        line(c,[(bx+25,y-76),(x+7,y-91),(x+14,y-21)],GOLD,7)
        for i,label in enumerate(['MY REASON'] if variant==2 else ['STATUS','SHOULD','PROVE IT']):
            dy=12*math.sin(t*2+i)
            draw_prop(c,'box',bx-10+i*9,y-90-i*62+dy,scale=.65)
            text(c,label,bx-36,y-106-i*62+dy,10,INK,True)
    elif kind=='tug_of_war':
        anchor=(1185,610);line(c,[(wx,wy),anchor],GOLD,10)
        draw_prop(c,'mountain',1220,710,scale=1.3)
        for i in range(4):line(c,[(810+i*65,680),(850+i*65,680)],PAPER,4,alpha=.5)
    elif kind=='attention_loop':
        draw_prop(c,'phone',1060,660,scale=1.5)
        for i in range(4):
            a=t*.8+i*math.pi/2;x=1060+165*math.cos(a);y=500+96*math.sin(a)
            ellipse(c,x,y,24,24,CORAL if i%2 else GOLD,INK,2)
            text(c,['!','+','?','!'][i],x-7,y+9,25,INK,True)
        line(c,[(855,650),(970,590)],CORAL,6)
    elif kind=='tiny_staircase':
        for i in range(4):
            x=900+i*100;h=26*(i+1)
            rect(c,x,710-h,100,h,'#83a997',3,INK,3)
            if u>i*.15:ellipse(c,x+49,697-h,9,9,GOLD)
        text(c,'OPEN THE FILE',903,570,18,INK,True)
        text(c,'ONE ROUGH LINE',1100,540,18,INK,True)
    elif kind=='progress_meter':
        rect(c,875,495,430,155,PAPER,16,INK,4)
        text(c,'A REPEATABLE NEXT STEP',900,535,20,INK,True)
        for i in range(7):
            filled=i<int(u*7) if variant==0 else i in [0,1,3,4,6]
            rect(c,902+i*54,573,39,39,MINT if filled else '#d8d8cb',7)
            if filled:line(c,[(911+i*54,593),(919+i*54,600),(931+i*54,583)],INK,3)
    elif kind=='identity_mirror':
        rect(c,980,330,224,360,'#9fb9ac',24,INK,6)
        ellipse(c,1092,420,37,41,PAPER,INK,3)
        line(c,[(1092,461),(1092,570)],'#627f78',23)
        for d in [-1,1]:line(c,[(1092,568),(1092+d*36,658)],INK,10)
        text(c,'WORTH IS NOT A SCORE',932,745,16,INK,True)
    elif kind in ('city_network','cable_cut','repair_links'):
        points=[(865,460),(1090,365),(1335,465),(1290,650),(965,650)]
        for i,(x,y) in enumerate(points):
            draw_prop(c,'laptop' if i%2 else 'phone',x,y,scale=.65)
            nx,ny=points[(i+1)%len(points)]
            dead=kind=='cable_cut' and u>.35
            repaired=kind=='repair_links' and i<int(u*6)
            if kind=='repair_links':dead=not repaired
            line(c,[(x,y-40),(nx,ny-40)],MINT if not dead or repaired else '#526c79',4,alpha=.9 if not dead or repaired else .3)
            if not dead or repaired:
                q=(t*.23+i*.2)%1;ellipse(c,x+(nx-x)*q,y-40+(ny-y)*q,7,7,GOLD)
        if kind=='cable_cut':
            a=smooth((u-.25)/.2)
            for dx in [-16,16]:line(c,[(1085+dx,500-25*a),(1085-dx,545+25*a)],CORAL,8,alpha=a)
    elif kind=='offline_checkout':
        draw_prop(c,'desk',1080,710,scale=1.2);draw_prop(c,'laptop',1080,563,scale=.8)
        rect(c,1037,505,86,30,CORAL,5);text(c,'OFFLINE',1045,525,13,INK,True)
        draw_prop(c,'coin',1230,710,scale=.7)
        draw_prop(c,'box',1300,710,scale=.8)
    elif kind=='paper_map':
        poly(c,[(850,430),(1030,405),(1210,430),(1370,400),(1370,645),(1205,675),(1030,650),(850,675)],PAPER)
        for x in [1030,1210]:line(c,[(x,420),(x,655)],'#bab6a5',2)
        route=[(910,600),(1030,525),(1150,590),(1300,480)]
        for a,b in zip(route,route[1:]):line(c,[a,b],CORAL,6)
        for i,(x,y) in enumerate(route):ellipse(c,x,y,9,9,GOLD,INK,2)
        q=e*(len(route)-1);i=min(2,int(q));f=q-i;a,b=route[i],route[i+1]
        ellipse(c,a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,15,15,MINT,INK,3)
    elif kind=='supply_chain':
        for i,label in enumerate(['SUPPLIER','WAREHOUSE','SHOP']):
            x=880+i*175;rect(c,x,490,130,145,'#819d9d',6,INK,3)
            rect(c,x+44,572,43,63,PAPER,3);text(c,label,x-3,665,16,PAPER if variant else INK,True)
            if i<2:
                line(c,[(x+134,565),(x+171,565)],GOLD,5)
                q=(t*.23+i*.23)%1;draw_prop(c,'box',x+145+q*30,553,scale=.25)
        if variant:line(c,[(1040,510),(1070,600)],CORAL,8)
    elif kind=='notice_board':
        rect(c,900,350,410,340,'#a98d65',12,INK,6)
        for i,label in enumerate(['WATER / EAST HALL','MEDICINE / ASK HERE','DELIVERIES / 4 PM','CHECKED BY A PERSON']):
            y=378+i*71;rect(c,923,y,365,53,PAPER,4);ellipse(c,934,y+8,4,4,CORAL)
            text(c,label,942,y+33,18,INK,True,max_width=324)
    elif kind=='radio_desk':
        draw_prop(c,'desk',1100,710)
        rect(c,1020,490,160,94,'#8a9c8b',12,INK,4)
        ellipse(c,1065,537,28,28,INK);ellipse(c,1144,538,15,15,GOLD)
        line(c,[(1150,488),(1193,401)],INK,4)
        for i in range(3):
            r=42+i*17+(t*12)%17
            c.new_path();c.arc(1190,415,r,-.65,.65);color(c,GOLD,1-i*.2);c.set_line_width(3);c.stroke()
    elif kind=='writing_desk':
        x,y=p.root;top=560
        rect(c,x+48,top,325,15,'#927c62',5,INK,3)
        for dx in (73,341):line(c,[(x+dx,top+15),(x+dx,710)],INK,8)
        poly(c,[(x+62,top-4),(x+178,top-12),(x+207,top-2),(x+75,top+4)],PAPER)
        for i in range(5):
            if u>i*.14:line(c,[(x+84,top-5+i*.8),(x+116+40*smooth((u-i*.14)*4),top-5+i*.8)],'#79948e',1.4)
        line(c,[(wx-8,wy-23),(wx+5,wy+9)],GOLD,5)
        if variant!=2:
            rect(c,x+230,top-44,36,44,PAPER,5,INK,2)
            c.new_path();c.arc(x+268,top-21,13,-1.5,1.5);color(c,INK);c.set_line_width(3);c.stroke()
            for i in range(2):line(c,[(x+239+i*12,top-57),(x+242+i*12+3*math.sin(t*2),top-75)],PAPER,2,alpha=.6)
        if variant==1:draw_prop(c,'phone',x+340,top-3,scale=.45)
    elif kind=='calendar':
        rect(c,910,370,360,290,PAPER,17,INK,4);rect(c,910,370,360,61,CORAL,14)
        text(c,'THIRTY DAYS OFFLINE',936,410,22,INK,True)
        for i in range(30):
            x=936+i%7*46;y=458+i//7*38
            text(c,str(i+1),x,y,16,INK)
            if i<int(u*30):line(c,[(x-4,y-15),(x+24,y+3)],CORAL,3)
