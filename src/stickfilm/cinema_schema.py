"""Declarative keyframes for shot-led films. No executable expressions."""
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class Key(Strict):
    at:float=Field(ge=0,le=1)
    x:float=Field(ge=-2500,le=3500)
    y:float=Field(default=760,ge=-1000,le=2000)
    scale:float=Field(default=1.35,gt=.1,le=5)
    angle:float=Field(default=0,ge=-180,le=180)
    alpha:float=Field(default=1,ge=0,le=1)
    pose:Literal['rest','walk','run','reach','offer','hold','clutch','plead','angry','point','sit','slump','kneel','hug','cheer','cover','write','push','wave','fall','listen','sit_offer','sit_cover','sit_hold','kneel_hug','kneel_hold','kneel_write','kneel_reach']='rest'
    emotion:Literal['neutral','joy','hope','tired','sad','cry','angry','shock','smug','fear','tender','guilty']='neutral'
    facing:Literal[-1,1]=1
    mark:float=Field(default=0,ge=0,le=1)
class Performer(Strict):
    name:str=Field(max_length=50)
    look:Literal['father','daughter','boss','colleague','partner','witness','mother','friend','bully','crowd']='father'
    keys:list[Key]=Field(min_length=2,max_length=14)
    carry:Literal['none','paper','ticket','box','star','bouquet','cup','phone','drawing','scissors','money','pencil']='none'
    @model_validator(mode='after')
    def ordered(self):
        if self.keys[0].at!=0 or self.keys[-1].at!=1 or any(a.at>=b.at for a,b in zip(self.keys,self.keys[1:])):raise ValueError('Actor keys must increase from 0 to 1')
        return self
class ObjectKey(Strict):
    at:float=Field(ge=0,le=1)
    x:float=Field(ge=-3000,le=4000)
    y:float=Field(default=600,ge=-1500,le=2500)
    scale:float=Field(default=1,gt=.01,le=8)
    angle:float=Field(default=0,ge=-360,le=360)
    alpha:float=Field(default=1,ge=0,le=1)
class Item(Strict):
    kind:Literal['paper','ticket','box','star','bouquet','cup','phone','drawing','scissors','chair','clock','heart','thread','spotlight','confetti','mark','sign','photo','cake','door','money','rain','leaves','pencil','balloon','tear','curtain','platform']
    keys:list[ObjectKey]=Field(min_length=2,max_length=12)
    label:str=Field(default='',max_length=50)
    color:str=Field(default='#eecb79',pattern='^#[0-9a-fA-F]{6}$')
    @model_validator(mode='after')
    def ordered(self):
        if self.keys[0].at!=0 or self.keys[-1].at!=1 or any(a.at>=b.at for a,b in zip(self.keys,self.keys[1:])):raise ValueError('Object keys must increase from 0 to 1')
        return self
class CameraKey(Strict):
    at:float=Field(ge=0,le=1)
    x:float=Field(default=800,ge=-1000,le=2600)
    y:float=Field(default=450,ge=-500,le=1400)
    zoom:float=Field(default=1,ge=.5,le=3)
class Cinema(Strict):
    world:Literal['home','office','street','stage','backstage','hospital','square','cafe','bedroom','park','mirror','rooftop','void']
    palette:Literal['amber','violet']='amber'
    time:Literal['morning','day','sunset','night']='day'
    performers:list[Performer]=Field(min_length=1,max_length=12)
    items:list[Item]=Field(default_factory=list,max_length=30)
    lens:list[CameraKey]=Field(min_length=2,max_length=6)
    caption:str=Field(default='',max_length=90)
    caption_at:float=Field(default=.1,ge=0,le=1)
    caption_end:float=Field(default=.9,ge=0,le=1)
    voice:Literal['narrator','father','daughter','boss','colleague','partner','witness','mother','friend','bully','crowd']='narrator'
    caption_speaker:int=Field(default=-1,ge=-1,le=11)
    note:str=Field(min_length=10,max_length=1200)
    @model_validator(mode='after')
    def ordered(self):
        if self.lens[0].at!=0 or self.lens[-1].at!=1 or any(a.at>=b.at for a,b in zip(self.lens,self.lens[1:])):raise ValueError('Camera keys must increase from 0 to 1')
        if self.caption_speaker>=len(self.performers):raise ValueError('Caption speaker does not exist')
        return self
