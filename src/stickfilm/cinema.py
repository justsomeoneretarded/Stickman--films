"""Original cinematic cutout animation: large acting rigs, physical sets and shot keys.

Visual action is authored independently of voice length. A film is a sequence of
changes in position, intention, expression, object state and camera composition.
"""
import math
import numpy as np
import cairocffi as cairo
from .drawing import color,line,ellipse,rect,poly,text,wrap,INK,PAPER
from .motion import smooth,ik,foot

TAU=math.tau
CLOTH={'father':'#54a7a1','daughter':'#f5ba65','boss':'#596579','colleague':'#c08379','partner':'#b3bd87','witness':'#7184cb','mother':'#ba829c','friend':'#6ca595','bully':'#a48a69','crowd':'#738b91'}
SKIN='#f4e8d4';DARK='#192b38';RED='#e27c73';GOLD='#efc377';PINK='#e882c3'


def interpolate(keys,u):
    a,b=keys[-2:]
    for ka,kb in zip(keys,keys[1:]):
        if ka.at<=u<=kb.at:a,b=ka,kb;break
    q=smooth((u-a.at)/max(.0001,b.at-a.at))
    values={k:getattr(a,k)+(getattr(b,k)-getattr(a,k))*q for k in ('x','y','scale','angle','alpha') if hasattr(a,k)}
    if hasattr(a,'zoom'):values['zoom']=a.zoom+(b.zoom-a.zoom)*q
    return a,b,q,values


def silhouette(c,world,palette,t,pan=0,night=False):
    warm=palette=='amber';sky=('#243c54','#66788a') if night else ('#d7a47f','#f3ddbc') if warm else ('#a4afca','#e4dce5')
    g=cairo.LinearGradient(0,0,0,900)
    for stop,co in zip([0,1],sky):g.add_color_stop_rgb(stop,*[int(co[i:i+2],16)/255 for i in (1,3,5)])
    c.set_source(g);c.paint()
    c.save();c.translate(-pan*.12,0)
    if world in ('street','square','park','rooftop','cafe','hospital','home','bedroom','office'):
        ellipse(c,1250,200,70,70,'#f4cf97' if warm else '#f4ead5',alpha=.8)
        for layer in range(2):
            for i in range(12):
                x=-350+i*195+layer*60;h=160+(i*81)%240
                rect(c,x,650-h+layer*60,165,h,'#426276' if night else '#819399',6,alpha=.28+layer*.1)
                for j in range(3):
                    for k in range(3):rect(c,x+20+j*43,675-h+layer*60+k*39,15,22,'#eacc95' if night else '#d0d4ca',2,alpha=.35)
    c.restore()


def set_art(c,world,palette,t,night=False):
    warm=palette=='amber';wall='#e4d3b8' if warm else '#d3cbd5';shadow='#283b4d' if night else '#a6a7a0'
    if world in ('home','bedroom','office','hospital','cafe','mirror'):
        # A real room with a window through to the separate distant-city plane.
        poly(c,[(-1000,-500),(3000,-500),(3000,300),(-1000,300)],wall)
        rect(c,-1000,290,1470,430,wall);rect(c,1170,290,1850,430,wall);rect(c,470,650,700,100,wall)
        rect(c,463,284,716,376,shadow,8,DARK,7)
        for x in [483,828]:rect(c,x,301,325,330,'#345164' if night else '#b1c8c4',1,alpha=.17)
        line(c,[(820,296),(820,650)],DARK,6);line(c,[(470,477),(1170,477)],DARK,5)
        rect(c,-1000,702,4000,18,'#927e72' if warm else '#898090')
    ground='#8b8781' if night else '#b7a28c' if warm else '#aaa6b4'
    rect(c,-1400,720,4500,900,ground)
    for y in [780,900,1080]:line(c,[(-1400,y),(3100,y)],DARK,2,alpha=.12)
    for x in range(-1500,3600,240):line(c,[(800+(x-800)*.4,720),(x,1300)],DARK,2,alpha=.12)
    if world=='home':
        rect(c,35,556,390,147,'#849d8e',26,DARK,4);rect(c,22,619,430,74,'#779482',15)
        rect(c,80,535,112,72,'#c7b88e',15);rect(c,270,535,100,74,'#b4c4b2',15)
        line(c,[(1320,712),(1320,370)],DARK,12);poly(c,[(1220,432),(1415,432),(1376,326),(1263,326)],'#e8be80')
        rect(c,1260,650,200,30,'#9e7e63',8)
        rect(c,180,265,150,170,PAPER,8,DARK,4);object_art(c,'drawing',255,421,.7,0,0,'OUR SHOW',GOLD)
    if world=='bedroom':
        rect(c,120,585,650,125,'#697e95',30,DARK,5);rect(c,110,559,200,74,PAPER,25);rect(c,310,571,470,126,'#a99cab',24)
        rect(c,850,585,160,130,'#9f846f',12,DARK,4);object_art(c,'clock',930,599,.7,t,0,'',GOLD)
        rect(c,1370,300,105,410,'#8d7b78',8,DARK,5)
    if world=='office':
        for x in (130,980):
            rect(c,x,574,480,22,'#a4866c',7,DARK,4)
            for dx in (25,440):line(c,[(x+dx,596),(x+dx,735)],DARK,9)
            rect(c,x+210,429,170,112,'#44586a',9,DARK,4);rect(c,x+221,439,148,88,'#b5d0cd',4)
            line(c,[(x+293,540),(x+293,573)],DARK,9)
        rect(c,39,250,210,110,'#f1e5ca',8,DARK,3);text(c,'TEAM FIRST',65,318,29,DARK,True)
    if world in ('street','square'):
        for x in (-150,1270):
            rect(c,x,295,310,425,'#6a7c87' if not warm else '#bc987f',10,DARK,5)
            rect(c,x+55,445,105,270,'#3e5964',8,DARK,4)
            rect(c,x+200,400,77,105,'#d8c697',5,DARK,3)
        if world=='square':
            rect(c,560,570,480,150,'#8f8c98',10,DARK,5);rect(c,750,421,145,170,'#686e88',8,DARK,5)
            rect(c,300,190,1000,103,'#313d58',12)
            text(c,'THE TRUTH IS SHOWING',443,260,45,PAPER,True)
        else:
            for x in [350,1130]:
                line(c,[(x,718),(x,255)],DARK,13);line(c,[(x,260),(x+83,260)],DARK,9)
                ellipse(c,x+93,270,39,15,'#f6d08e')
    if world in ('stage','backstage'):
        rect(c,-1000,-500,4000,1200,'#2a3248');rect(c,180,570,1240,142,'#a87c67',4,DARK,5)
        for x in (-90,1300):
            rect(c,x,0,390,670,'#8b5261',25)
            for j in range(5):line(c,[(x+30+j*70,0),(x+30+j*70,650)],'#603d51',13,alpha=.6)
        for x in [530,1070]:
            poly(c,[(x,150),(x-220,700),(x+240,700)],'#f7dba0',.10)
        for i in range(9):object_art(c,'chair',80+i*180,1040,.9,t,0,'', '#394355')
        if world=='backstage':rect(c,1000,250,350,470,'#7e6374',7,DARK,7)
    if world=='hospital':
        rect(c,800,543,600,125,'#acc1c4',20,DARK,5);rect(c,813,515,185,70,PAPER,15)
        line(c,[(814,670),(814,748)],DARK,13);line(c,[(1373,670),(1373,748)],DARK,13)
        rect(c,1240,322,200,132,'#405466',11,DARK,5)
        beat=[(1260,391),(1300,391),(1310,375),(1323,410),(1335,360),(1348,391),(1420,391)];line(c,beat,'#8ccfc1',4)
        line(c,[(1510,710),(1510,260),(1450,260)],DARK,8);rect(c,1425,275,67,105,'#d1dce0',10,DARK,3)
    if world=='cafe':
        for x in [400,1130]:
            ellipse(c,x,590,225,35,'#b18c6b',DARK,4);line(c,[(x,620),(x,740)],DARK,14)
        rect(c,40,300,280,310,'#486b73',10,DARK,4);text(c,'OPEN',92,400,47,PAPER,True)
    if world=='mirror':
        rect(c,550,210,500,550,'#6a778b',45,DARK,9);rect(c,572,233,456,500,'#adbdc5',33)
        line(c,[(600,270),(940,650)],PAPER,15,alpha=.12)
    if world in ('park','rooftop'):
        if world=='rooftop':rect(c,-1000,600,4000,120,'#6e7986',3,DARK,6)
        else:
            for x in (40,1370):
                line(c,[(x,735),(x+30,350)],'#6f746b',30)
                for dx,dy in [(-60,410),(60,390),(0,310)]:ellipse(c,x+dx,dy,110,120,'#758e83',DARK,3)
            rect(c,1000,590,380,30,'#967963',8,DARK,4);rect(c,1010,500,360,60,'#b69372',10,DARK,4)
            for x in [1040,1330]:line(c,[(x,620),(x,740)],DARK,10)
    if world=='void':
        rect(c,-1500,-1000,4500,2800,'#252f49' if not warm else '#514650')
        for i in range(9):ellipse(c,120+i*190,400+math.sin(i*2)*150,80,95,'#a995ac',alpha=.04)


def object_art(c,kind,x,y,s,t,angle=0,label='',co=GOLD):
    c.save();c.translate(x,y);c.rotate(math.radians(angle));c.scale(s,s)
    if kind in ('paper','ticket','drawing','photo'):
        rect(c,-60,-115,120,115,PAPER,5,DARK,3)
        if kind in ('drawing','photo'):
            for dx in [-25,25]:ellipse(c,dx,-69,12,13,GOLD if dx<0 else '#7db4ad',DARK,2);line(c,[(dx,-55),(dx,-29),(dx-9,-10),(dx,-29),(dx+10,-10)],'#669a9a',4)
            line(c,[(-27,-37),(27,-37)],RED,4)
        elif kind=='ticket':
            text(c,'OUR SHOW',-49,-79,14,DARK,True);poly(c,[(0,-61),(8,-37),(34,-37),(14,-22),(21,0),(0,-13),(-21,0),(-14,-22),(-34,-37),(-8,-37)],GOLD)
        else:
            for i in range(4):line(c,[(-40,-85+i*19),(36,-85+i*19)],'#8a9e9e',3)
        if label:text(c,label,-51,-10,12,DARK,True,max_width=102)
    elif kind=='star':
        points=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5;r=65 if i%2==0 else 30;points.append((math.cos(a)*r,math.sin(a)*r-55))
        poly(c,points,co);line(c,points+[points[0]],DARK,3)
    elif kind=='platform':
        rect(c,-180,-100,360,100,'#b78f72',7,DARK,5)
        rect(c,-175,-100,350,12,'#e0bd88',4)
        text(c,'JUNE’S STAGE',-120,-40,24,DARK,True)
    elif kind=='box':
        rect(c,-75,-125,150,125,'#b78f72',7,DARK,4);rect(c,-13,-124,26,124,'#dec296',2);line(c,[(-75,-94),(75,-94)],DARK,3)
    elif kind=='cup':
        rect(c,-30,-62,60,62,PAPER,10,DARK,3);c.new_path();c.arc(33,-33,20,-1.5,1.5);color(c,DARK);c.set_line_width(4);c.stroke()
        for dx in [-11,12]:line(c,[(dx,-78),(dx+5*math.sin(t*3),-110)],PAPER,3,alpha=.6)
    elif kind=='phone':
        rect(c,-30,-110,60,110,DARK,10);rect(c,-24,-99,48,81,'#a4c0c8',6)
        for i in range(3):rect(c,-17,-90+i*22,34,15,RED if i==0 else PAPER,3)
    elif kind=='chair':
        rect(c,-65,-185,130,115,co,15,DARK,5);rect(c,-80,-85,160,25,co,8,DARK,4)
        for dx in [-57,57]:line(c,[(dx,-61),(dx+dx*.15,0)],DARK,8)
    elif kind=='clock':
        ellipse(c,0,-82,75,75,PAPER,DARK,5)
        for i in range(12):
            a=i*TAU/12;line(c,[(math.sin(a)*59,-82-math.cos(a)*59),(math.sin(a)*65,-82-math.cos(a)*65)],DARK,3)
        a=t*.5;line(c,[(0,-82),(math.sin(a)*57,-82-math.cos(a)*57)],RED,5);line(c,[(0,-82),(-31,-99)],DARK,6)
    elif kind=='bouquet':
        poly(c,[(-45,-57),(35,-57),(8,23)],'#c2a385')
        for i in range(5):
            xx=-36+i*18;yy=-85-20*math.sin(i*2)
            for j in range(5):ellipse(c,xx+math.cos(j*TAU/5)*10,yy+math.sin(j*TAU/5)*10,10,10,RED)
            ellipse(c,xx,yy,6,6,GOLD)
    elif kind=='scissors':
        for dx in [-13,13]:ellipse(c,dx,0,15,22,RED,DARK,3)
        line(c,[(-12,-12),(29,-87)],'#c4d2d4',7);line(c,[(12,-12),(-29,-87)],'#c4d2d4',7)
    elif kind=='money':
        for i in range(3):rect(c,-65+i*9,-68-i*7,120,60,'#99b995',5,DARK,3)
        ellipse(c,15,-48,19,19,PAPER,DARK,2)
    elif kind=='pencil':line(c,[(-4,-83),(4,0)],GOLD,9);poly(c,[(-2,0),(7,-1),(4,13)],PAPER)
    elif kind=='heart':
        c.move_to(0,2);c.curve_to(-110,-60,-60,-130,0,-76);c.curve_to(60,-130,110,-60,0,2);color(c,co);c.fill()
    elif kind in ('sign','door'):
        w,h=(280,130) if kind=='sign' else (190,400)
        rect(c,-w/2,-h,w,h,co,12,DARK,5)
        if kind=='door':ellipse(c,65,-180,8,8,GOLD)
        if label:
            for i,v in enumerate(wrap(c,label,w-30,25,3)):text(c,v,-w/2+16,-h+43+i*33,25,DARK,True)
    elif kind=='cake':
        rect(c,-80,-65,160,65,'#c18d9b',15,DARK,4);rect(c,-80,-67,160,21,PAPER,10)
        for dx in [-40,0,40]:line(c,[(dx,-70),(dx,-115)],GOLD,6);ellipse(c,dx,-128,5+math.sin(t*8)*2,13,GOLD)
    elif kind=='mark':line(c,[(-30,-65),(-5,-40),(-18,-15),(14,9)],PINK,11)
    elif kind=='tear':ellipse(c,0,-14,9,16,'#9fc5d7',alpha=.8)
    elif kind=='balloon':ellipse(c,0,-150,65,80,co,DARK,4);line(c,[(0,-70),(9,80)],PAPER,2)
    c.restore()


def shape(pose,t,facing=1):
    if '_' in pose:
        base,gesture=pose.split('_',1)
        r=shape(base,t,facing);g=shape(gesture,t,facing)
        dy=r['neck'][1]-g['neck'][1]
        for key in ('lw','rw'):r[key]=(g[key][0],g[key][1]+dy)
        return r
    # Feet, pelvis and wrists are explicit acting targets; elbows/knees use IK.
    d={'hip':(0,-154),'neck':(0,-248),'head':(0,-293),'lf':(-31,0),'rf':(34,0),'lw':(-50,-159),'rw':(50,-159),'tilt':0}
    if pose in ('walk','run'):
        amp=49 if pose=='walk' else 69;phase=t*6 if pose=='walk' else t*9
        d['hip']=(0,-147+5*math.cos(phase*2));d['neck']=(facing*13,-244+5*math.cos(phase*2));d['head']=(facing*19,-289+5*math.cos(phase*2))
        for side,k in [(0,'lf'),(1,'rf')]:
            a=phase+side*math.pi;d[k]=(math.cos(a)*amp,-max(0,math.sin(a))*(30 if pose=='walk' else 55))
        d['lw']=(-facing*math.cos(phase)*53,-162);d['rw']=(facing*math.cos(phase)*53,-162)
    targets={
    'reach':((20,-154),(35,-245),(42,-291),(-42,-158),(103,-215)),
    'offer':((0,-154),(3,-248),(6,-293),(-38,-170),(98,-190)),
    'hold':((0,-154),(0,-248),(0,-293),(-40,-210),(52,-217)),
    'clutch':((0,-154),(-6,-248),(-11,-293),(-20,-224),(25,-233)),
    'plead':((0,-144),(-10,-237),(-16,-282),(47,-239),(61,-244)),
    'angry':((0,-151),(18,-246),(27,-287),(-66,-198),(82,-263)),
    'point':((0,-154),(4,-248),(10,-293),(-45,-164),(109,-252)),
    'sit':((0,-100),(-5,-191),(-10,-237),(-49,-121),(42,-130)),
    'slump':((0,-104),(25,-175),(51,-219),(-18,-116),(68,-129)),
    'kneel':((0,-76),(14,-164),(28,-208),(-16,-100),(73,-142)),
    'hug':((0,-150),(14,-240),(25,-282),(64,-240),(84,-225)),
    'cheer':((0,-158),(0,-251),(0,-297),(-84,-312),(84,-312)),
    'cover':((0,-151),(-10,-244),(-17,-287),(-28,-285),(36,-287)),
    'write':((0,-154),(14,-245),(22,-285),(41,-187),(84,-190)),
    'push':((-12,-145),(21,-233),(40,-274),(87,-238),(98,-228)),
    'wave':((0,-154),(0,-248),(0,-293),(-42,-166),(70,-314)),
    'fall':((0,-90),(49,-150),(77,-180),(-67,-160),(115,-145)),
    'listen':((0,-154),(4,-248),(9,-293),(-40,-166),(35,-269))}
    if pose in targets:
        hip,neck,head,lw,rw=targets[pose];d.update(hip=hip,neck=neck,head=head,lw=lw,rw=rw)
        if pose in ('sit','slump'):d['lf']=(50,0);d['rf']=(89,0)
        if pose=='kneel':d['lf']=(-60,0);d['rf']=(66,0)
        if pose=='write':d['rw']=(rw[0]+5*math.sin(t*9),rw[1]+2*math.sin(t*13))
        if pose=='wave':d['rw']=(rw[0]+14*math.sin(t*6),rw[1])
        if pose in ('cheer','cover'):d['head']=(head[0],head[1]+2*math.sin(t*3))
    if pose not in ('walk','run'):
        for k in ('hip','neck','head','lw','rw'):d[k]=(d[k][0],d[k][1]+1.2*math.sin(t*2.5))
    return d


def actor_state(actor,u,t):
    a,b,q,v=interpolate(actor.keys,u);pa,pb=shape(a.pose,t,a.facing),shape(b.pose,t,b.facing)
    # Pose transitions run over the authored interval: a reach or collapse can
    # occupy a full shot rather than snapping to a generic preset gesture.
    rig={k:tuple(pa[k][j]*(1-q)+pb[k][j]*q for j in (0,1)) for k in pa if k!='tilt'}
    if a.pose in ('walk','run') or b.pose in ('walk','run'):
        initial=actor.keys[0].x;distance=(v['x']-initial)/v['scale'];direction=1 if b.x>=a.x else -1
        f=a.facing if q<.5 else b.facing
        if abs(b.x-a.x)>10:
            for side,key in enumerate(('lf','rf')):
                ankle,_,_=foot(abs(distance),160,side,0,0,direction,stance=.6,lift=36)
                rig[key]=((ankle[0]-distance)/f,ankle[1])
            root=rig['hip'];target_y=root[1]
            for side,key in enumerate(('lf','rf')):
                dx=rig[key][0]-(root[0]+(-12 if side==0 else 12))
                target_y=max(target_y,rig[key][1]-math.sqrt(max(1,163**2-dx**2)))
            delta=target_y-root[1]
            for key in ('hip','neck','head','lw','rw'):rig[key]=(rig[key][0],rig[key][1]+delta)
    v.update(rig=rig,emotion=b.emotion if q>.52 else a.emotion,facing=a.facing if q<.5 else b.facing,mark=a.mark+(b.mark-a.mark)*q)
    return v


def face(c,x,y,emotion,look,t,mark=0,gaze=1):
    c.save();c.translate(x,y)
    tilt={'sad':-.12,'cry':-.15,'smug':.12,'hope':.08,'tender':-.06,'fear':-.08}.get(emotion,0)
    c.rotate(tilt)
    ellipse(c,0,0,45,49,SKIN,DARK,4)
    # Distinct silhouettes and hair for the ensemble.
    if look in ('father','witness','friend','boss','colleague','bully'):
        hair='#5b554f' if look=='father' else '#343c57' if look=='witness' else '#8a6c55' if look=='friend' else '#686875'
        poly(c,[(-41,-17),(-38,-42),(-13,-54),(12,-51),(38,-31),(40,-12),(24,-31),(8,-28),(-8,-35),(-28,-24)],hair)
    if look in ('daughter','mother','partner'):
        hair='#66514f' if look=='daughter' else '#6a5664' if look=='mother' else '#6b5c51'
        poly(c,[(-46,4),(-45,-28),(-26,-48),(12,-52),(40,-31),(49,27),(34,30),(32,-14),(11,-27),(-20,-12),(-34,17)],hair)
        if look=='daughter':ellipse(c,-50,-10,18,22,hair);ellipse(c,-48,-24,12,7,RED)
    ex=16;ey=-2
    blink=1 if (t*1.07+len(look)*.73)%4.6<.13 else 0
    if emotion in ('joy','tender'):
        for dx in [-ex,ex]:
            c.new_path();c.arc(dx,ey+2,7,math.pi,TAU);color(c,DARK);c.set_line_width(3);c.stroke()
    elif blink:
        for dx in [-ex,ex]:line(c,[(dx-6,ey),(dx+6,ey)],DARK,3)
    else:
        ry=10 if emotion in ('shock','fear','hope') else 6 if emotion in ('tired','sad','guilty','smug') else 8
        for dx in [-ex,ex]:ellipse(c,dx+gaze*2,ey,5.7,ry,DARK);ellipse(c,dx-1+gaze*2,ey-2,1.4,2,PAPER)
    brows={'angry':((-26,-22),(-9,-15),(9,-15),(26,-22)),'sad':((-27,-17),(-10,-25),(10,-25),(27,-17)),'cry':((-27,-15),(-10,-25),(10,-25),(27,-15)),'fear':((-27,-23),(-10,-28),(10,-28),(27,-23)),'guilty':((-27,-17),(-10,-23),(10,-23),(27,-19)),'smug':((-27,-22),(-10,-15),(10,-22),(27,-25))}
    pts=brows.get(emotion,((-27,-20),(-10,-22),(10,-22),(27,-20)))
    line(c,pts[:2],DARK,3);line(c,pts[2:],DARK,3)
    if emotion in ('shock','fear'):ellipse(c,0,24,8,11,DARK)
    elif emotion in ('joy','smug','hope','tender'):
        c.new_path();c.arc(0,13,15,.15,math.pi-.15);color(c,DARK);c.set_line_width(3);c.stroke()
        if emotion=='joy':ellipse(c,-30,17,8,5,RED,alpha=.35);ellipse(c,30,17,8,5,RED,alpha=.35)
    elif emotion in ('cry','sad','guilty','tired'):
        c.new_path();c.arc(0,35,12,math.pi+.25,TAU-.25);color(c,DARK);c.set_line_width(3);c.stroke()
    elif emotion=='angry':line(c,[(-12,26),(13,21)],DARK,4)
    else:line(c,[(-9,25),(10,25)],DARK,3)
    if emotion=='cry':
        for dx in [-17,17]:ellipse(c,dx,17+((t*26+dx)%28),4,8,'#8ebcd0',alpha=.85)
    if mark:
        line(c,[(25,-5),(17,7),(29,15),(20,29)],PINK,5,alpha=mark)
        ellipse(c,32,9,9,15,PINK,alpha=mark*.12)
    c.restore()


def performer(c,actor,u,t):
    v=actor_state(actor,u,t);r=v['rig'];s=v['scale'];f=v['facing'];look=actor.look;shirt=CLOTH[look]
    # Each pose casts a foot-relative, depth-scaled shadow.
    ellipse(c,v['x'],v['y']+8,88*s,13*s,DARK,alpha=.16*v['alpha'])
    c.save();c.translate(v['x'],v['y']);c.scale(s,s);c.rotate(math.radians(v['angle']))
    # Horizontal posing mirrors targets, but faces remain readable in profile.
    def pt(k):return (r[k][0]*f,r[k][1])
    hip=pt('hip');neck=pt('neck');shoulder=(hip[0]*.15+neck[0]*.85,hip[1]*.15+neck[1]*.85)
    for side,foot in enumerate(('lf','rf')):
        h=(hip[0]+(-12 if side==0 else 12),hip[1]);a=pt(foot);knee,ankle,_=ik(h,a,82,82,bend=-f)
        line(c,[h,knee,ankle],'#506374' if side==0 else '#263a4b',20)
        line(c,[(ankle[0]-10,ankle[1]-2),(ankle[0]+18,ankle[1]-2)],DARK,18)
    # Filled costume follows the tilted torso; no floating head or loose shirt.
    dx=neck[0]-hip[0];dy=neck[1]-hip[1];length=math.hypot(dx,dy)
    c.save();c.translate(hip[0],hip[1]);c.rotate(math.atan2(dy,dx)+math.pi/2)
    rect(c,-31,-length,62,length+12,shirt,25,DARK,4)
    rect(c,-19,-length+17,5,length-17,PAPER,2,alpha=.22)
    if look=='boss':poly(c,[(-15,-length),(0,-length+27),(14,-length),(0,-length+8)],PAPER);line(c,[(0,-length+13),(0,-length+66)],'#a77479',8)
    c.restore()
    wrists={}
    for side,key in enumerate(('lw','rw')):
        sh=(shoulder[0]+(-18 if side==0 else 18),shoulder[1]+4);w=pt(key);elbow,w,_=ik(sh,w,60,62,bend=1 if side==0 else -1)
        line(c,[sh,elbow,w],DARK,19);line(c,[sh,elbow,w],shirt,13)
        ellipse(c,w[0],w[1],12,13,SKIN,DARK,2);wrists[key]=w
    head=pt('head');line(c,[(neck[0],neck[1]+7),(head[0],head[1]+40)],SKIN,18)
    face(c,*head,v['emotion'],look,t,v['mark'],f)
    if actor.carry!='none':
        w=wrists['rw'];object_art(c,actor.carry,w[0]+f*4,w[1]+14,.58,t,0,'',GOLD)
    c.restore()
    return v


def draw(scene,t,width,height):
    shot=scene.cinema;u=min(1,t/max(.001,scene.duration));surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height);c=cairo.Context(surface);c.scale(width/1600,height/900)
    a,b,q,_=interpolate(shot.lens,u);cx=a.x+(b.x-a.x)*q;cy=a.y+(b.y-a.y)*q;z=a.zoom+(b.zoom-a.zoom)*q
    night=shot.time=='night';silhouette(c,shot.world,shot.palette,t,cx-800,night)
    c.save();c.translate(800,450);c.scale(z,z);c.translate(-cx,-cy)
    set_art(c,shot.world,shot.palette,t,night)
    states=[]
    for obj in shot.items:
        aa,bb,qq,v=interpolate(obj.keys,u)
        if obj.kind in ('rain','leaves','confetti'):
            for i in range(45 if obj.kind=='rain' else 25):
                x=v['x']+(i*173)%1800-900+(math.sin(t+i)*13 if obj.kind!='rain' else -t*35%90);y=v['y']+((i*97+t*(310 if obj.kind=='rain' else 80))%1000)-500
                if obj.kind=='rain':line(c,[(x,y),(x-12,y+34)],'#c7d5dc',2,alpha=.28*v['alpha'])
                else:rect(c,x,y,8,17,obj.color,2,alpha=v['alpha']*.6)
        elif obj.kind=='thread':
            end=(v['x']+math.cos(math.radians(v['angle']))*v['scale']*200,v['y']+math.sin(math.radians(v['angle']))*v['scale']*200)
            line(c,[(v['x'],v['y']),end],obj.color,4,alpha=v['alpha'])
        elif obj.kind=='spotlight':poly(c,[(v['x'],v['y']-500),(v['x']-260*v['scale'],v['y']),(v['x']+260*v['scale'],v['y'])],obj.color,.13*v['alpha'])
        elif obj.kind=='curtain':rect(c,v['x'],v['y']-750,600*v['scale'],750,obj.color,15)
        else:
            c.save();c.push_group();object_art(c,obj.kind,v['x'],v['y'],v['scale'],t,v['angle'],obj.label,obj.color);c.pop_group_to_source();c.paint_with_alpha(v['alpha']);c.restore()
    for actor in sorted(shot.performers,key=lambda a:actor_state(a,u,t)['y']):
        v=actor_state(actor,u,t)
        if v['alpha']<1:c.push_group()
        states.append(performer(c,actor,u,t))
        if v['alpha']<1:c.pop_group_to_source();c.paint_with_alpha(v['alpha'])
    # Foreground architecture supplies occlusion and near-plane parallax.
    if shot.world in ('home','office','hospital','cafe','bedroom'):
        rect(c,-230,845,440,220,'#314952',18,alpha=.4);rect(c,1550,815,300,280,'#314952',18,alpha=.35)
    c.restore()
    grade=cairo.RadialGradient(800,420,220,800,420,1050)
    grade.add_color_stop_rgba(0,.04,.07,.12,0)
    grade.add_color_stop_rgba(1,.04,.07,.12,.34 if night else .12)
    c.set_source(grade);c.paint()
    # Dialogue is sparse and timed to an action, never a continuous prose overlay.
    if shot.caption and shot.caption_at<=u<=shot.caption_end:
        lines=wrap(c,shot.caption,1280,34,2)
        for i,ln in enumerate(lines):
            c.select_font_face('DejaVu Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(34);w=c.text_extents(ln)[2];rect(c,800-w/2-25,765+i*48,w+50,47,DARK,14,alpha=.92);text(c,ln,800-w/2,800+i*48,34,PAPER,True)
    # Cinema framing; no explainer heading competing with the character's face.
    rect(c,0,0,1600,42,'#172433');rect(c,0,858,1600,42,'#172433')
    surface.flush();return surface,[],(cx,cy,z)


def report(plan,fps=60):
    """Measure authored changes, not fake legacy foot-contact qualification."""
    travel=[];expressions=set();object_moves=0;empty=[];shots=[]
    for scene in plan.scenes:
        s=scene.cinema
        if s is None:continue
        distances=[sum(math.hypot(b.x-a.x,b.y-a.y) for a,b in zip(p.keys,p.keys[1:])) for p in s.performers]
        pose_changes=sum(sum(a.pose!=b.pose or a.emotion!=b.emotion for a,b in zip(p.keys,p.keys[1:])) for p in s.performers)
        expressions.update(k.emotion for p in s.performers for k in p.keys)
        moving=sum(any(abs(a.x-b.x)+abs(a.y-b.y)+abs(a.angle-b.angle)+abs(a.alpha-b.alpha)>.1 for a,b in zip(o.keys,o.keys[1:])) for o in s.items)
        if not pose_changes and max(distances,default=0)<30 and not moving:empty.append(scene.id)
        shots.append(dict(id=scene.id,seconds=scene.duration,largest_actor_travel=max(distances,default=0),acting_changes=pose_changes,moving_objects=moving))
        travel+=distances;object_moves+=moving
    return dict(samples_per_second=fps,passes_direction_gate=not empty,contact_gate_applicable=False,qualification='Cinematic cutout rigs use keyframed physical acting. Legacy planted-foot gate is not applicable; no no-sliding claim is inferred.',shots=len(shots),expression_states=sorted(expressions),largest_actor_travel=max(travel,default=0),moving_object_tracks=object_moves,shots_without_authored_change=empty,shot_details=shots,limitations=['No general collision solver.','Keyframed cutout locomotion uses cyclic IK; it is not the legacy contact-qualified gait.','Narrative and emotional readability require visual review.'])
