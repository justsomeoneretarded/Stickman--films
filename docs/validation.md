# Validation record

The current independent productions passed all 90 tests and both final 1080p60
media gates. See [production validation](episodes/production-validation.json),
[parallel-run evidence](episodes/parallel-proof.json), and [film downloads](episodes/README.md).
The earlier results below describe prior engine versions and short samples.

Development: 3-vCPU Linux, Python 3.12.14, FFmpeg 7.1.5. Hosted tests run on
ubuntu-24.04. Technical acceptance is separate from professional artistic acceptance.

## Benchmark

[Corrected production run](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572)
[1080p60 benchmark artifact](https://github.com/justsomeoneretarded/Stickman--films/actions/runs/39580002572/artifacts/12336570119)

The hosted benchmark measures **22.00 seconds**, 1920×1080, 60 FPS, H.264/yuv420p,
stereo AAC 48 kHz. It passes all technical gates: full decode, duration, contiguous
timeline, black/freeze detection and headroom. At 60 motion samples/second:

- Maximum planted-foot speed: **0.00 design pixels/second**.
- Leg reach error and ground penetration: **0.00 pixels**.
- Maximum leg length error: less than **0.000001 pixels**.
- Peak camera acceleration: **76.0 design units/second²** (after fixing tracking onset).
- The run includes a flight interval and finishes with both feet down.

Contact sheets and a 12-frame stride sequence were visually inspected. This checks
composition, proportions, contacts and prop continuity; it is not a claim of full
human playback/listening review. The rig remains stylized, with limited head-turn
projection and relatively restrained secondary motion. The final output is ready
for artistic evaluation, not automatically certified professional animation.

## Tests

86 tests pass locally, including actual MP4 encoding/decoding, every action and prop,
strict plan validation, duration bounds, continuous speed ramps, bone lengths,
foot contacts, running flight, stopping, camera acceleration and narration guards.
The production and test workflow YAMLs pass actionlint 1.7.12. Hosted CI also passed.
The final download links and per-niche results are in [deliverables.md](deliverables.md).

## Complete media and writing

An initial 75-second reviewed psychology fixture rendered to **73.416667 seconds**
at 1080p60 and passed all technical gates. Its storyboard was inspected and improved
with a seated desk composition and a visible mountain metaphor.

Ten distinct authored comparison scripts are reviewed fixtures, not arbitrary-title
writer output. They use separate narration, voices, moods, actions and shot choices.
All ten final niche videos pass after one separately documented science-voice repair.
The consolidated report workflow passed. See [the final artifact index](deliverables.md).

The first small Qwen2.5-1.5B trials showed repetitive/unresolved storytelling. Those
failures motivated outline planning, bounded JSON lengths and repetition/completeness
guards, and adoption of a larger free Apache-2.0 Qwen3-4B model. No model is described
as a professionally qualified writer. Single-title writing was tested separately on GitHub: the generated office story
passes at 29.50 seconds against 36 requested (1080p60). Human creative/listening review
and longer automatic productions remain unqualified.

## Renderer cost probe

Three 1080p Cairo frames including PNG output took **1.08 seconds**. Three simple
mesh proxy frames in CPU Cycles, four samples, one thread, took **51.60 seconds**.
The proxy scene is not equivalent art, and this is a tiny CPU cost probe, not a full
Blender-versus-vector quality or throughput study. Reproduce the optional Blender
probe with `blender -b -t 1 -P scripts/blender_cost_probe.py -- work/blender-probe`.
Actual cold/warm encode timings are recorded in each artifact's resources.json.

## Remaining evaluation

No human listening panel, ASR fidelity gate, audience study, autonomous source
entailment checker, general collision system or universal scene compiler is claimed.
Word timings are estimates within measured utterances. Factual scripts need source
review; the history/survival fixtures are explicitly fictional. Complex science,
historical maps, combat and elaborate interactions need additional authored clips.
