"""Cairo art direction: rounded ink, warm paper faces, mineral palette."""
import math
import cairocffi as cairo

INK="#182938"; PAPER="#f4eddb"; MINT="#7fbdad"; CORAL="#e89079"; GOLD="#e7be6b"
PALETTES={"hero":(MINT,PAPER),"friend":(CORAL,"#f3d8bb"),"office":("#8c9eb6",PAPER),
"student":(GOLD,PAPER),"scientist":("#e4e9df","#e7d6be"),"business":("#6f8b9d",PAPER),
"antagonist":("#9e7e9d","#dfc9b6"),"crowd":("#7e9994",PAPER)}


def color(c, value, alpha=1):
    if isinstance(value,str): value=tuple(int(value[i:i+2],16)/255 for i in (1,3,5))
    c.set_source_rgba(*value[:3],alpha)


def line(c, points, stroke=INK, width=8, alpha=1):
    c.new_path(); c.move_to(*points[0])
    for p in points[1:]: c.line_to(*p)
    c.set_line_width(width); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    color(c,stroke,alpha); c.stroke()


def ellipse(c,x,y,rx,ry,fill,stroke=None,width=3,alpha=1):
    c.save(); c.translate(x,y); c.scale(rx,ry); c.new_path(); c.arc(0,0,1,0,2*math.pi); c.restore()
    color(c,fill,alpha); c.fill_preserve()
    if stroke: color(c,stroke,alpha); c.set_line_width(width); c.stroke()
    else: c.new_path()


def rect(c,x,y,w,h,fill,r=0,stroke=None,width=3,alpha=1):
    c.new_path()
    if r:
        r=min(r,w/2,h/2)
        for cx,cy,a in [(x+w-r,y+r,-math.pi/2),(x+w-r,y+h-r,0),(x+r,y+h-r,math.pi/2),(x+r,y+r,math.pi)]: c.arc(cx,cy,r,a,a+math.pi/2)
        c.close_path()
    else: c.rectangle(x,y,w,h)
    color(c,fill,alpha); c.fill_preserve()
    if stroke: color(c,stroke,alpha); c.set_line_width(width); c.stroke()
    else: c.new_path()


def poly(c,points,fill,alpha=1):
    c.new_path(); c.move_to(*points[0])
    for p in points[1:]:c.line_to(*p)
    c.close_path(); color(c,fill,alpha); c.fill()


def text(c,value,x,y,size=24,fill=PAPER,bold=False,max_width=None):
    c.select_font_face("DejaVu Sans",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    if max_width:
        while c.text_extents(value)[2]>max_width and size>9:
            size-=1; c.set_font_size(size)
    color(c,fill); c.move_to(x,y); c.show_text(value)


def wrap(c,value,width,size=32,max_lines=3):
    c.select_font_face("DejaVu Sans"); c.set_font_size(size)
    words=value.split(); lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        if c.text_extents(trial)[2]>width and current: lines.append(current); current=word
        else: current=trial
    if current: lines.append(current)
    return lines[:max_lines]


def draw_character(c,p,character="hero",talk=0,depth=1):
    j=p.joints; shirt,skin=PALETTES[character]
    # Contact shadows follow ankles; broad occlusion fixes the body to the floor.
    ellipse(c,p.root[0],p.ground+5,75,13,INK,alpha=.14)
    for side in ("left","right"):
        a=j["ankle_"+side]
        opacity=max(0,1-(p.ground-a[1])/85)*.18
        ellipse(c,a[0]+4,p.ground+4,27,5,INK,alpha=opacity)
    for i,side in enumerate(("left","right")):
        limb="#526777" if i==0 else INK
        line(c,[j["hip_"+side],j["knee_"+side],j["ankle_"+side]],limb,13)
        ax,ay=j["ankle_"+side]
        line(c,[(ax-7,ay-1),(ax+15,ay-1)],limb,15)
    # Back arm, then torso, then foreground arm preserves silhouette.
    line(c,[j["shoulders"],j["elbow_left"],j["wrist_left"]],"#526777",12)
    line(c,[j["hips"],j["neck"]],INK,31)
    line(c,[(j["hips"][0],j["hips"][1]-7),(j["neck"][0],j["neck"][1]+12)],shirt,24)
    line(c,[j["neck"],(j["head"][0],j["head"][1]+22)],INK,11)
    if character in ("office","business"):
        nx,ny=j["neck"]; poly(c,[(nx-4,ny+16),(nx+7,ny+27),(nx+4,ny+67),(nx-4,ny+59)],CORAL)
    if character=="scientist":
        line(c,[(j["neck"][0]-8,j["neck"][1]+19),(j["hips"][0]-10,j["hips"][1]-5)],PAPER,6)
    line(c,[j["shoulders"],j["elbow_right"],j["wrist_right"]],INK,13)
    for side in ("left","right"):
        wx,wy=j["wrist_"+side]; ellipse(c,wx,wy,7,7,skin,INK,2)
    hx,hy=j["head"]
    c.save(); c.translate(hx,hy); c.rotate(p.lean*.6)
    ellipse(c,0,0,35,39,skin,INK,4)
    # Signature two-stroke forelock; archetypes carry distinct accessories.
    if character in ("hero","student"):
        line(c,[(-19,-32),(-10,-44),(-4,-34),(4,-43),(11,-34)],INK,4)
    elif character=="friend":
        ellipse(c,-28,-21,15,19,CORAL,INK,3); line(c,[(-29,-31),(16,-33)],CORAL,11)
    elif character=="business": line(c,[(-32,-31),(28,-31)],INK,7)
    elif character=="antagonist": line(c,[(-25,-31),(15,-42),(26,-29)],INK,7)
    elif character=="scientist":
        for ex in (-13,13): ellipse(c,ex,-3,11,11,skin,INK,2)
        line(c,[(-2,-3),(2,-3)],INK,2)
    face=p.facing
    exshift=6*face; eye_y=-3
    blink=math.sin(hx*.007+hy*.019+talk*2)>0.997
    for ex in (-12,12):
        ellipse(c,ex+exshift,eye_y,3,1 if blink else 5,INK)
    emotion=p.emotion
    if emotion in ("surprise","fear","excited"):
        for ex in (-12,12): line(c,[(ex-6+exshift,-18),(ex+5+exshift,-20)],INK,3)
        ellipse(c,exshift,18,7,9,INK)
    elif emotion in ("angry","frustrated"):
        line(c,[(-21,-19),(-5,-13)],INK,3); line(c,[(7,-13),(23,-20)],INK,3)
        line(c,[(-8+exshift,20),(9+exshift,18)],INK,3)
    elif emotion in ("sad","confused","thinking","hesitant"):
        line(c,[(-21,-14),(-5,-20)],INK,3); line(c,[(8,-20),(23,-15)],INK,3)
        c.new_path(); c.arc(exshift,28,11,math.pi*1.12,math.pi*1.9);color(c,INK);c.set_line_width(3);c.stroke()
    elif emotion in ("happy","embarrassed"):
        c.new_path();c.arc(exshift,10,12,.15,math.pi-.15);color(c,INK);c.set_line_width(3);c.stroke()
        if emotion=="embarrassed":
            ellipse(c,-24,11,7,4,CORAL,alpha=.65);ellipse(c,26,11,7,4,CORAL,alpha=.65)
    else:
        line(c,[(-20,-17),(-6,-17)],INK,3);line(c,[(8,-17),(22,-17)],INK,3)
        line(c,[(-7+exshift,19),(8+exshift,18)],INK,3)
    if talk>.15: ellipse(c,exshift,19,6,3+talk*4,INK)
    c.restore()
    if emotion in ("confused","thinking","hesitant"):
        for idx in range(3): ellipse(c,hx+48+idx*12,hy-39-idx*11,3+idx,3+idx,PAPER,alpha=.8)


def draw_prop(c,kind,x,y,t=0,scale=1,label="",progress=0):
    c.save();c.translate(x,y);c.scale(scale,scale)
    if kind=="phone":
        rect(c,-31,-100,62,108,INK,11);rect(c,-24,-90,48,76,"#a3cec2",5)
        for i in range(3):rect(c,-16,-80+i*21,32,12,PAPER,3)
        ellipse(c,0,-2,4,4,PAPER)
    elif kind=="clock":
        ellipse(c,0,-70,57,57,PAPER,INK,4)
        for i in range(12):
            a=i*math.pi/6;line(c,[(math.sin(a)*44,-70-math.cos(a)*44),(math.sin(a)*48,-70-math.cos(a)*48)],INK,2)
        line(c,[(0,-70),(26*math.sin(t*.7),-70-26*math.cos(t*.7))],CORAL,4)
        line(c,[(0,-70),(-19,-81)],INK,4)
    elif kind in ("box","evidence"):
        poly(c,[(-48,-66),(18,-86),(61,-60),(-4,-40)],"#e4c591")
        poly(c,[(-48,-66),(-4,-40),(-4,9),(-48,-17)],"#bb9564")
        poly(c,[(-4,-40),(61,-60),(61,-11),(-4,9)],"#d6ad79")
        line(c,[(9,-82),(37,-64),(37,-19)],PAPER,7)
        if kind=="evidence":text(c,"?",9,-20,32,INK,True)
    elif kind=="coin":
        for i in range(4):ellipse(c,0,6-i*11,47,16,GOLD,INK,2)
        text(c,"$",-13,-26,35,INK,True)
    elif kind=="book":
        rect(c,-49,-86,98,94,CORAL,6,INK,3);line(c,[(-36,-78),(-36,2)],PAPER,4)
        for i in range(3):line(c,[(-21,-63+i*16),(29,-63+i*16)],PAPER,3)
    elif kind=="plant":
        poly(c,[(-30,-40),(30,-40),(22,9),(-21,9)],CORAL);line(c,[(0,-40),(0,-133)],MINT,7)
        for side,dy in [(-1,-78),(1,-108),(-1,-127)]:ellipse(c,side*18,dy,24,10,MINT)
    elif kind in ("door","lock"):
        if kind=="door":
            rect(c,-49,-185,98,195,"#587c80",4,INK,4);poly(c,[(-38,-175),(38*(1-progress)-38*progress,-175+20*progress),(38*(1-progress)-38*progress,-4-14*progress),(-38,-4)],"#a0b6a4");ellipse(c,25-60*progress,-81,6,6,GOLD)
        else:
            c.new_path();c.arc(0,-80,32,math.pi,2*math.pi);color(c,INK);c.set_line_width(12);c.stroke()
            rect(c,-45,-84,90,82,GOLD,9,INK,3);ellipse(c,0,-53,8,9,INK);rect(c,-3,-49,6,19,INK)
    elif kind=="planet":
        ellipse(c,0,-84,60,60,"#80b5bd",INK,3)
        c.save();c.translate(0,-84);c.rotate(-.35);ellipse(c,0,0,96,19,INK,alpha=.15);c.restore()
        ellipse(c,-19,-99,20,14,MINT);ellipse(c,18,-64,15,21,MINT)
    elif kind=="flag":
        line(c,[(-29,7),(-29,-163)],INK,6);poly(c,[(-26,-163),(55,-145),(-26,-108)],CORAL)
    elif kind=="water":
        rect(c,-38,-115,76,124,PAPER,9,INK,3);rect(c,-31,-72+25*progress,62,72-25*progress,"#80b5bd",4)
    elif kind=="ball":ellipse(c,0,-27,27,27,CORAL,INK,3)
    elif kind=="steps":
        for i in range(3):rect(c,-65+i*45,-(i+1)*29,45,(i+1)*29,"#779b99",2,INK,2)
    elif kind=="desk":
        poly(c,[(-135,-119),(111,-134),(140,-112),(-112,-96)],"#a98058")
        line(c,[(-115,-103),(-115,2)],INK,9);line(c,[(120,-113),(120,2)],INK,9)
        line(c,[(-115,-96),(120,-111)],INK,8)
    elif kind=="chair":
        line(c,[(-33,3),(-33,-169),(24,-169),(24,-68)],"#657f7a",10)
        rect(c,-39,-72,83,14,"#9eb3a0",5,INK,3)
        line(c,[(34,-58),(34,3)],INK,8)
    elif kind=="laptop":
        rect(c,-55,-79,110,74,INK,5);rect(c,-48,-72,96,58,"#9dc6b8",3)
        for i in range(3):line(c,[(-35,-60+i*16),(30+8*math.sin(t+i),-60+i*16)],PAPER,3)
        poly(c,[(-55,-5),(55,-5),(75,8),(-75,8)],"#728c92")
    elif kind=="letter":
        rect(c,-57,-75,114,73,PAPER,4,INK,3)
        line(c,[(-53,-72),(0,-32),(53,-72)],"#9a9c8c",3)
        ellipse(c,1,-30,10,10,CORAL)
    elif kind=="receipt":
        poly(c,[(-33,-125),(34,-125),(34,0),(21,-7),(10,0),(0,-7),(-11,0),(-23,-7),(-33,0)],PAPER)
        for i in range(5):line(c,[(-20,-110+i*18),(20,-110+i*18)],"#8b998e",3)
    elif kind=="mountain":
        poly(c,[(-137,7),(-20,-225),(136,7)],"#688e8e")
        poly(c,[(-20,-225),(17,-166),(-10,-181),(-37,-150),(-51,-166)],PAPER)
        poly(c,[(-137,7),(-20,-225),(-48,7)],"#7fa39b")
    elif kind=="bridge":
        line(c,[(-150,-29),(150,-29)],"#8b7d66",15)
        for side in (-1,1):
            line(c,[(side*118,0),(side*118,-137)],INK,7)
            line(c,[(side*118,-137),(0,-48)],INK,3)
        for i in range(9):line(c,[(-120+i*30,-35),(-120+i*30,-69)],INK,3)
    elif kind=="umbrella":
        line(c,[(0,-15),(0,-151)],INK,5)
        c.new_path();c.arc(0,-144,87,math.pi,2*math.pi);c.close_path();color(c,CORAL);c.fill()
        for dx in (-43,43):line(c,[(0,-231),(dx,-144)],PAPER,2)
        c.new_path();c.arc(-9,-17,9,0,math.pi);color(c,INK);c.set_line_width(5);c.stroke()
    elif kind=="bottle":
        rect(c,-15,-145,30,20,INK,4);rect(c,-24,-126,48,127,"#b4d6ca",9,INK,3)
        rect(c,-19,-73,38,66,"#76adb6",6);line(c,[(-13,-111),(-13,-88)],PAPER,4)
    elif kind=="shoe":
        poly(c,[(-47,-31),(-7,-31),(9,-16),(49,-9),(52,4),(-50,4)],CORAL)
        line(c,[(-49,5),(51,5)],INK,6)
        for i in range(3):line(c,[(-14+i*13,-24),(-22+i*13,-12)],PAPER,3)
    elif kind=="pump":
        rect(c,-18,-103,36,107,"#789c92",6,INK,3);line(c,[(0,-93),(49,-93),(49,-66)],INK,8)
        line(c,[(-3,-107),(-43,-151)],INK,7);ellipse(c,-48,-156,10,7,CORAL)
        ellipse(c,0,9,37,9,INK,alpha=.22)
    elif kind=="boat":
        poly(c,[(-118,-37),(118,-37),(78,9),(-79,9)],"#a5815c")
        line(c,[(0,-38),(0,-192)],INK,5);poly(c,[(6,-186),(6,-54),(98,-54)],PAPER)
    if label:
        lines=wrap(c,label,200,17,2)
        for i,v in enumerate(lines):text(c,v,-min(90,len(v)*4.6),42+i*23,17,INK,True)
    c.restore()
