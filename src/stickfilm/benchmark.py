"""A single continuous performance, not a sequence of unrelated pose cards."""
from .schema import Actor, Scene, Plan, NICHES
from .motion import pose, smooth, smoother, ik

DURATION=22

def travel(t):
    # Continuous position, speed and acceleration across idle/walk/run/stop.
    # Integral smoothstep: integral_0^u (3u²-2u³) = u³ - u⁴/2.
    if t<2:return 0,0
    if t<5:
        u=(t-2)/3;return 210*(u**3-.5*u**4),70*smooth(u)
    if t<7:return 105+70*(t-5),70
    if t<9:
        u=(t-7)/2;return 245+140*u+240*(u**3-.5*u**4),70+120*smooth(u)
    if t<12:return 505+190*(t-9),190
    if t<15:
        u=(t-12)/3;return 1075+570*(u-u**3+.5*u**4),190*(1-smooth(u))
    return 1360,0


def benchmark_pose(t):
    dist,v=travel(t)
    a=Actor(action="run",x=290,travel=700)
    p=pose(a,t,DURATION,motion_sample=(dist,v,170))
    if t>15:
        # Keep the actual planted end feet while the torso turns and reaches.
        facing=1-2*smooth((t-15.6)/1.2)
        action="turn" if t<17 else "pickup" if t<20.3 else "surprise"
        local=t-17 if action=="pickup" else t-20.3 if action=="surprise" else t-15
        duration=3.3 if action=="pickup" else 1.7 if action=="surprise" else 2
        q=pose(Actor(action=action,x=1650,facing=-1),max(0,local),duration)
        # Blend body transforms over the settling interval; no root jump.
        blend=smooth((t-15)/.65)
        for key in q.joints:
            if key.startswith(("ankle","knee","hip_")):continue
            p.joints[key]=tuple(p.joints[key][i]*(1-blend)+q.joints[key][i]*blend for i in (0,1))
        p.root=p.joints["hips"];p.facing=facing;p.emotion=q.emotion;p.lean=q.lean*blend
        p.prop_hand=p.joints["wrist_right"];p.pickup=1 if t>=20.3 else q.pickup
        for side in ("left","right"):
            h=(p.root[0]+(-9 if side=="left" else 9),p.root[1]);ankle=p.joints["ankle_"+side]
            knee,_,err=ik(h,ankle,66,66,bend=-1)
            p.joints["hip_"+side]=h;p.joints["knee_"+side]=knee;p.reach_error=max(p.reach_error,err)
    return p


def benchmark_plan():
    s=Scene(id="benchmark",beat="hook",label="A LITTLE MOMENTUM",environment="forest",actors=[Actor(action="run",x=290,travel=700)],camera="tracking",music="wonder",duration=DURATION,start=0,end=DURATION)
    return Plan(title="A Little Momentum — Animation Benchmark",brief="Continuous idle, walk, acceleration, run, deceleration, turn, pickup and surprise in a layered forest.",niche=NICHES[5],requested_minutes=DURATION/60,provenance="authored-example",factual_status="fiction",scenes=[s])


def benchmark_camera(t,focus):
    pan=.8*(focus-290)*smoother((t-2)/4)
    return 800+pan,450,1
