# Rebuild after visual-storytelling feedback

The user rejected the earlier narrated explainers: movement was too small, frames
barely changed, scripts lacked emotional force, and the voice carried the story.
Those earlier downloads remain historical, not the current delivery.

We studied the supplied 171-second reference through a 35-frame shot overview. The
useful principles were emotional reactions, motivated framing, physical choices and
consequences that remain readable without narration. Its footage, characters, plot,
recording and music are not included in these original productions.

## The new films

- **They Loved Him More When He Was Useful**: a father trades a promise to his daughter
  for praise at work. An empty reserved seat, a damaged star and a repaired home stage
  carry the story. The climax is a refusal that costs him approval.
- **What If Every Lie Left a Mark on Your Face?**: a young man enjoys exposing lies,
  then a child's tears and his mother's fear reveal the limits of his moral certainty.
  His own public confession completes the opening image.

Both stories are fiction. Each contains 50 authored shots and a 300-second directed
timeline. Psychology has 128 spoken words; what-if has 214. Voice length no longer
sets the length of an action. These are separately authored story plans, not claims
that a small local model independently directed them.

## Animation changes

New large cutout rigs have filled costumes, distinct hair silhouettes, head tilts,
12 facial states, gaze, crying, reaching, collapse, kneeling, refusal and embraces.
Position, scale, angle, expression and pose follow explicit keys. Characters cross
up to 1,100 world units in a shot. Props fall, pass between people, are put down,
and change meaning across scenes. New physical interiors and exterior layers support
close-ups, tracking, reaction cuts, depth and lighting changes. Continuous headings
and paragraph captions are removed. Dialogue appears only in its directed window.

The first complete drafts and the revised character-voice drafts passed media checks at exactly 300 seconds. All 94 tests passed locally and in GitHub CI. Frame review
led to correcting seated gestures, the father's kneeling embrace, caption widths,
movement-facing direction and the height of the child's home stage. Both final 1080p60 artifacts were then downloaded. Their individual passing reports
were checked, formats independently probed, and six four-frame sequences extracted
from each actual MP4 and visually inspected. Final checks are in
[v2-production-validation.json](v2-production-validation.json).

## Honest qualification

The cinematic rigs have their own directed-action audit; the old planted-foot metric
is not applied to them and no zero-sliding claim is inferred. Locomotion uses cyclic
IK with distance-driven stance targets; a general collision solver is not implemented.
Sound effects are authored at action times and footsteps follow traveled distance.
The original procedural score differs between the two films. Speech is local synthetic
voice and does not offer studio-level emotional performance control.

A technical pass verifies the media, timing and authored direction. It cannot certify
a great script, emotional impact or reference-level artistry. Review covers all
storyboard shots, complete draft renders, and sampled sequences from final MP4s;
it is not represented as a complete human watch-and-listen session.

## Measurable change from the rejected versions

| Film | Earlier narrated words / shots | Rebuilt spoken words / shots |
|---|---:|---:|
| Psychology | 832 / 20 | 128 / 50 |
| What-if | 905 / 20 | 214 / 50 |

The rebuilt films each have a complete 300-second timeline. Silent time contains
directed action and reactions rather than narration stretched to reach a duration.
The revised drafts use six distinct character/narrator voices for psychology and
five for what-if. These counts describe the implementation, not an artistic score.
