"""Distance-driven gaits. Stance feet stay fixed in world coordinates.

All coordinates are in a 1600x900 world; joints are computed, never redrawn.
The two-bone solver clamps reach while reporting residuals for QA.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np


def smooth(t):
    t = min(1., max(0., t))
    return t*t*(3-2*t)


def smoother(t):
    t = min(1., max(0., t))
    return t*t*t*(t*(t*6-15)+10)


def mix(a, b, t): return a+(b-a)*t


def ik(a, b, l1, l2, bend=1):
    ax,ay=a; bx,by=b
    dx,dy=bx-ax,by-ay
    raw=math.hypot(dx,dy)
    d=min(l1+l2-0.0001, max(abs(l1-l2)+0.0001, raw))
    ux,uy=(dx/raw,dy/raw) if raw>1e-8 else (0.,1.)
    along=(l1*l1-l2*l2+d*d)/(2*d)
    height=math.sqrt(max(0.,l1*l1-along*along))
    target=(ax+ux*d,ay+uy*d)
    mid=(ax+ux*along-uy*height*bend,ay+uy*along+ux*height*bend)
    return mid,target,max(0.,raw-(l1+l2))


@dataclass
class Pose:
    root: tuple
    joints: dict
    contacts: dict
    facing: float
    lean: float
    emotion: str
    reach_error: float
    prop_hand: tuple
    pickup: float
    ground: float


def trajectory(t, duration, travel):
    """Analytic position/velocity with zero velocity at both endpoints."""
    u=min(1.,max(0.,t/max(duration,1e-6)))
    return travel*smoother(u), travel*30*u*u*(u-1)**2/max(duration,1e-6)


def foot(distance, cycle, side, x0, ground, direction=1, stance=.60, lift=31):
    phase=distance/cycle+side*.5
    k=math.floor(phase); f=phase-k
    planted=x0+direction*((k-side*.5)*cycle+cycle*stance*.5)
    if f<stance:
        return (planted,ground),True,k
    u=(f-stance)/(1-stance)
    return (planted+direction*cycle*smooth(u),ground-lift*math.sin(math.pi*u)**1.35),False,k


def pose(actor, t, duration, ground=710, motion_sample=None):
    action=actor.action
    u=min(1.,max(0.,t/max(duration,1e-6)))
    travel=actor.travel
    distance,velocity=trajectory(t,duration,travel)
    if motion_sample is not None: distance,velocity = motion_sample[:2]
    x=actor.x+distance
    direction=1 if travel>=0 else -1
    facing=actor.facing
    if action=="turn": facing=actor.facing*(1-2*smooth((u-.34)/.32))
    speed=abs(velocity)
    # Blend walk/run by world speed, so acceleration does not reset gait phase.
    # A fixed cycle within a clip avoids discontinuity when speed changes.
    cycle=210 if action in ("run","sprint") else 170
    if motion_sample is not None: cycle=motion_sample[2]
    phase=abs(distance)/cycle
    running=smooth((speed-65)/150) if action in ("run","sprint") else 0
    locomotion=action in ("walk","run","sprint","stairs") and abs(travel)>0
    bob=(3+4*running)*math.sin(phase*4*math.pi) if locomotion else 1.4*math.sin(t*2.2)
    lean=direction*min(.22,speed/1000) if locomotion else .025*math.sin(t*1.5)
    hip_y=ground-103+bob
    compression=0
    if action in ("jump","fall"):
        q=smooth((u-.12)/.14)*(1-smooth((u-.72)/.15))
        arc=math.sin(math.pi*min(1,max(0,(u-.23)/.49)))
        compression=18*math.sin(math.pi*min(1,u/.23)) if u<.23 else 0
        hip_y+=compression-100*max(0,arc)
        lean=-.15*arc if action=="fall" else .05
    if action in ("crouch","pickup","reach","inspect"):
        compression=40*math.sin(math.pi*smooth(u))**2
        hip_y+=compression
        lean=.30*math.sin(math.pi*u)**2*facing
    if action=="sit":
        hip_y+=45*smooth(u/.40); lean=-.08
    if action=="stand": hip_y+=45*(1-smooth(u/.55))
    if action=="stairs": hip_y-=38*smooth(u); ground-=38*smooth(u)
    hip=(x,hip_y)
    neck=(x+lean*155,hip_y-96)
    shoulder=(mix(hip[0],neck[0],.83),mix(hip[1],neck[1],.83))
    joints={"hips":hip,"neck":neck,"shoulders":shoulder,"head":(neck[0]+lean*20,neck[1]-41)}
    contacts={}; reach_error=0
    for side,name in enumerate(("left","right")):
        offset=(-1 if side==0 else 1)*9
        h=(hip[0]+offset,hip[1])
        if locomotion:
            ankle,contact,_=foot(abs(distance),cycle,side,actor.x,ground,direction,
                                 stance=.44 if action in ("run","sprint") else .60,
                                 lift=(31+22*running)*smooth(speed/45))
            # A run has a genuine flight interval. Lift amplitude goes to zero
            # with speed, so an idle/start/stop never holds a foot in the air.
            contact=contact or speed<.001
        else:
            ankle=(x+(-24 if side==0 else 27),ground)
            contact=action not in ("jump","fall") or not .24<u<.73
            if not contact: ankle=(ankle[0]+(-8 if side==0 else 12),ankle[1]-max(0,(ground-103)-hip_y))
        if action=="sit": ankle=(x+35+side*35,ground)
        knee,ankle_solved,err=ik(h,ankle,66,66,bend=-actor.facing)
        reach_error=max(reach_error,err)
        joints[f"hip_{name}"]=h; joints[f"knee_{name}"]=knee
        joints[f"ankle_{name}"]=ankle_solved
        contacts[name]=contact
        swing=math.sin(phase*2*math.pi+side*math.pi)*(36+running*20) if locomotion else 3*math.sin(t*2+side)
        wrist=(shoulder[0]+(-1 if side==0 else 1)*25+swing,
               shoulder[1]+74-abs(swing)*.25)
        if action in ("think","hesitate","frustrated","inspect") and side==1:
            wrist=(neck[0]+facing*31,neck[1]-18)
        if action in ("surprise","fear","excited","celebrate","happy"):
            amount=smooth(u/.18)*(1-.2*smooth((u-.7)/.3))
            wrist=(shoulder[0]+(-1 if side==0 else 1)*(44+12*amount),shoulder[1]+70-145*amount)
        if action in ("reach","pickup","exchange") and side==1:
            a=math.sin(math.pi*smooth(u))**.7
            wrist=(shoulder[0]+facing*mix(25,91,a),shoulder[1]+mix(74,113,a))
        if action in ("point","shield") and side==1:
            a=smooth(u/.25)
            wrist=(shoulder[0]+facing*mix(25,99,a),shoulder[1]+mix(74,-10,a))
        if action=="angry": wrist=(shoulder[0]+(-1 if side==0 else 1)*47,shoulder[1]+35)
        if action=="sad": wrist=(shoulder[0]+(-1 if side==0 else 1)*19,shoulder[1]+98)
        elbow,wrist,err=ik(shoulder,wrist,55,56,bend=1 if side==0 else -1)
        joints[f"elbow_{name}"]=elbow; joints[f"wrist_{name}"]=wrist
    emotion=actor.emotion
    automatic={"think":"thinking","surprise":"surprise","fear":"fear","happy":"happy","angry":"angry","embarrassed":"embarrassed","sad":"sad","excited":"excited","frustrated":"frustrated","hesitate":"hesitant","celebrate":"happy"}
    if emotion=="neutral": emotion=automatic.get(action,"neutral")
    return Pose((x,hip_y),joints,contacts,facing,lean,emotion,reach_error,
                joints["wrist_right"],smooth((u-.48)/.12) if action=="pickup" else 0,ground)
