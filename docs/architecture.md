# Architecture and engineering tradeoffs

Python orchestrates a CPU Cairo vector renderer rather than a slideshow generator.
Character frames derive from a skeletal pose with neck, shoulders, hips, elbows,
wrists, knees and ankles. A two-bone IK solver fixes the length of each segment.
Walking/running phases derive from distance, and planted feet have fixed world-space
coordinates. Smooth integrated speed ramps drive the uninterrupted benchmark.

Original archetypes have consistent proportions and different palettes/accessories:
hero, friend, office worker, student, scientist, businessperson, antagonist, crowd.
Faces carry eyes/brows/mouth expressions; torso tilt, arm overlap, compression,
breathing and anticipation support acting. The run is contact-aware and grounded,
but level-ground walking/running is substantially more mature than stairs/falling.
No general collision or dynamics solver is claimed.

The camera projects a 1600×900 design world into 16:9 output. Actor depth scales the
whole rig around its ground anchor, while distant architecture and foreground
vegetation move at different fractions of the camera displacement. Perspective
floor grids, ambient occlusion and foot shadows ground the figures. Layered parallax
is not a full 3D simulation. Original geometry replaces stock background photographs.
Thirteen environments use reusable procedural architecture rather than photo assets.

Cairo supplies anti-aliased round strokes. BGRA frames stream directly into FFmpeg
without frame PNGs or a disk-heavy intermediate. H.264 CRF18, yuv420p, 60 FPS and AAC
192 kb/s are the production targets. Interpolation is in the animation timeline;
optical flow is not used to hide bad motion. A development quality preset is explicit.

The local writer uses Apache-2.0 Qwen2.5-1.5B Q4_K_M with JSON grammar constraints.
It generates new narration and executable shot choices for title/brief. The small
CPU model is not an expert screenwriter or researcher. Bounded scene batches keep
context/memory requirements practical; every generated scene passes the same strict
schema. The fixed comparison examples are separate and identify their provenance.
A reviewed-plan path is the practical higher-quality alternative without paid APIs.

Kokoro ONNX INT8 is the chosen speech backend: modest memory, fast CPU inference and
upstream Apache-2.0 weights. Segment durations are measured from the real WAVs.
A modest 0.92–1.12 delivery-rate correction can synthesize again. If the timeline still
falls outside ±25%, the model may rewrite once based on measured duration. Reviewed
plans fail with a clear content-revision instruction. Audio is never time-stretched.
Scene frame rounding is at most half a frame each; the finalized timeline has no gaps.
Word-caption positions and authored cue fractions are estimates, not forced alignment.

Music and effects are generated with deterministic oscillators/noise, not scraped
assets. Footsteps derive from IK contact changes. Speech-envelope ducking, fades,
headroom and two-pass EBU loudness normalization precede stereo AAC mastering.
TTS emotional control and the procedural score are limited; listening remains required.

Blender is available in development but is not required in Actions. Full mesh lighting,
free 3D camera or physically simulated props could justify a Blender backend. The
current renderer targets restrained drawn storytelling with low startup/RAM costs.
See `docs/validation.md` for measured rendering work rather than an assumed throughput.
