# Delivered videos and evaluation

> Historical short samples. The current two independent five-minute films are
> available in [the film delivery page](episodes/README.md).

All ten final niche videos pass technical QA at **1920×1080, 60 FPS**, H.264/yuv420p,
stereo AAC 48 kHz. Each requested 75 seconds; all final durations are within ±25%.
Each artifact includes its actual MP4, six-second preview, contact sheet, measured
scene plan and JSON/Markdown quality report. Downloads expire after 14 days.

[Consolidated report artifact](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39623335826/artifacts/12355228433)
— the consolidation workflow passed and requires ten passing reports.

| Niche | Measured duration | Technical QA | Artifact |
|---|---|---|---|
| Psychology & Human Behavior | 73.68s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12335679764) |
| Relatable Comedy | 77.93s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336635617) |
| Money & Business | 79.03s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336098882) |
| History & Geopolitics | 82.45s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12335739764) |
| What-if & Survival | 73.97s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336626682) |
| Storytelling & Life Lessons | 82.05s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12337355418) |
| Science Explained | 81.65s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39581843861/artifacts/12337431762) |
| Self-improvement | 82.88s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336377573) |
| Technology & Cybersecurity | 80.13s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336437626) |
| Mysteries & Scams | 80.38s | PASS | [Download](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336294433) |

## Benchmark and automatic writing

- [1080p60 animation benchmark](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336570119): 22.00 seconds; idle, walk, acceleration, run/flight, stop, turn, pickup, reaction and tracking.
- [Automatic title-to-video result](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39582095213/artifacts/12337991561): title/brief generated a new six-scene fictional office story using local Qwen3-4B. Measured 29.50 seconds against 36 requested, within the permitted 27–45 seconds. This is separate from the ten authored fixtures.

The original comparison run has nine successful videos and one failed science job.
The science voice was too slow: its measured 118-second timeline was correctly
rejected before rendering. The repaired science run uses a different stock Kokoro
voice at a normal rate and passes at 81.65 seconds. The consolidated report explicitly
combines those runs; the failed diagnostics were preserved, not relabelled a success.
Earlier baseline runs were stopped after visual defects were identified and corrected.

## Visual review and production fit

Contact sheets from all ten final videos, plus benchmark stride frames and the
separate generated story, were visually inspected. This supports conclusions about
composition, proportions, leg contacts, props and continuity. It does not establish
full human playback/listening approval, emotional impact or professional artistry.
The downloaded final files were also checked for decoding independently of their
hosted reports.

As an engineering judgment, psychology, money, habit and small character stories fit
the current visual vocabulary best. The three money buckets and carried objects now
communicate concrete ideas. Comedy still needs more precise reactions and ensemble
choreography. Science needs bespoke diagrams beyond these simple demonstrations;
history needs reviewed research, maps and specialized scenes for factual documentaries.
The history and survival comparison stories are explicitly fictional.

No invented artistic scores or audience rankings are assigned. Remaining limits:
finite actions/props, simplified collisions and head turns, approximate word-level
alignment, one narration voice per video, limited TTS emotion, basic procedural score,
and no autonomous source-entailment or ASR fidelity verification. Some model-selected
props/actions remain symbolic and need review against the spoken story.

Priorities before publishing: bespoke scene direction and acting, more exact phrase
alignment, a listening/ASR pass, richer contextual sound and source review. Higher
FPS alone does not solve those issues.
