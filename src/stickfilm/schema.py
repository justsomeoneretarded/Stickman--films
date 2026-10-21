"""Strict, non-executable creative intermediate representation."""
from __future__ import annotations
import math
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

NICHES = ["Psychology & Human Behavior", "Relatable Comedy", "Money & Business",
          "History & Geopolitics", "What-if & Survival", "Storytelling & Life Lessons",
          "Science Explained", "Self-improvement", "Technology & Cybersecurity", "Mysteries & Scams"]
ENVIRONMENTS = ["bedroom", "classroom", "office", "city", "restaurant", "bank", "forest", "desert", "island", "laboratory", "battlefield", "abstract", "digital"]
ACTIONS = ["idle", "walk", "run", "sprint", "turn", "reach", "pickup", "surprise", "think", "fear", "happy", "angry", "embarrassed", "sad", "excited", "frustrated", "hesitate", "jump", "fall", "stairs", "sit", "stand", "crouch", "point", "celebrate", "shield", "exchange", "inspect"]
CAMERAS = ["wide", "follow", "dolly-in", "dolly-out", "pan", "tilt", "zoom", "reveal", "establishing", "over-shoulder", "close-up", "tracking"]

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

class Cue(Strict):
    at: float = Field(ge=0, le=1)
    kind: Literal["step", "impact", "click", "chime", "whoosh", "tick", "pickup"]
    gain: float = Field(default=0.4, ge=0, le=1)

class Actor(Strict):
    character: Literal["hero", "friend", "office", "student", "scientist", "business", "antagonist", "crowd"] = "hero"
    action: str = "think"
    x: float = Field(default=520, ge=-1000, le=4000)
    travel: float = Field(default=0, ge=-800, le=800)
    facing: Literal[-1, 1] = 1
    emotion: Literal["neutral", "surprise", "confused", "fear", "happy", "angry", "embarrassed", "sad", "excited", "thinking", "frustrated", "hesitant"] = "neutral"
    depth: float = Field(default=1, ge=0.65, le=1.15)
    @field_validator("action")
    @classmethod
    def action_known(cls, v):
        if v not in ACTIONS: raise ValueError(f"Unknown action {v}; use {ACTIONS}")
        return v

class Scene(Strict):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,60}$")
    beat: Literal["hook", "setup", "progression", "conflict", "discovery", "payoff", "closing"]
    narration: str = Field(default="", max_length=1600)
    dialogue: list[str] = Field(default_factory=list, max_length=3)
    label: str = Field(default="", max_length=65)
    environment: str = "abstract"
    actors: list[Actor] = Field(min_length=1, max_length=4)
    prop: Literal["none", "phone", "clock", "box", "coin", "book", "plant", "door", "lock", "planet", "flag", "water", "evidence", "ball", "steps"] = "none"
    prop_label: str = Field(default="", max_length=35)
    camera: str = "wide"
    transition: Literal["cut", "dissolve", "wipe", "match"] = "cut"
    lighting: Literal["day", "night", "warm", "dramatic"] = "day"
    music: Literal["curious", "comic", "tense", "warm", "wonder", "silence"] = "curious"
    cues: list[Cue] = Field(default_factory=list, max_length=20)
    pause: float = Field(default=0.45, ge=0.1, le=2)
    duration: float = Field(default=0, ge=0, le=45)
    start: float = Field(default=0, ge=0)
    end: float = Field(default=0, ge=0)
    @field_validator("environment")
    @classmethod
    def env_known(cls, v):
        if v not in ENVIRONMENTS: raise ValueError(f"Unknown environment {v}")
        return v
    @field_validator("camera")
    @classmethod
    def camera_known(cls, v):
        if v not in CAMERAS: raise ValueError(f"Unknown camera {v}")
        return v

class Source(Strict):
    url: str = Field(pattern=r"^https://", max_length=700)
    claim: str = Field(min_length=10, max_length=1200)

class Plan(Strict):
    version: Literal[1] = 1
    title: str = Field(min_length=1, max_length=180)
    brief: str = Field(min_length=1, max_length=4000)
    niche: str
    requested_minutes: float = Field(gt=0, le=30)
    seed: int = Field(default=42, ge=0, le=2147483647)
    provenance: Literal["authored-example", "reviewed-plan", "local-model"]
    factual_status: Literal["fiction", "source-grounded", "unverified"]
    sources: list[Source] = Field(default_factory=list, max_length=30)
    scenes: list[Scene] = Field(min_length=1, max_length=200)
    @model_validator(mode="after")
    def coherent(self):
        if self.niche not in NICHES: raise ValueError("Unknown niche")
        ids = [s.id for s in self.scenes]
        if len(ids) != len(set(ids)): raise ValueError("Scene IDs must be unique")
        if self.factual_status == "source-grounded" and not self.sources: raise ValueError("Source-grounded plans require sources")
        if self.factual_status == "unverified": raise ValueError("Unverified factual scripts cannot be rendered; supply reviewed sources or clearly label fiction")
        if self.provenance != "authored-example":
            beats = {s.beat for s in self.scenes}
            if not {"hook", "setup", "payoff"} <= beats: raise ValueError("Need hook, setup, payoff")
        return self


def minutes(value: str | float, maximum: float = 10) -> float:
    try: number = float(value)
    except (TypeError, ValueError): raise ValueError("Duration must be a positive number of minutes") from None
    if not math.isfinite(number) or not 0 < number <= maximum:
        raise ValueError(f"Duration must be finite, positive, and at most {maximum} minutes")
    if number * 60 < 8: raise ValueError("Minimum duration is 8 seconds; shorter videos cannot demonstrate a narrative")
    return number


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:90] or "video"
