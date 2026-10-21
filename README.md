# Small Worlds — Cinematic Stickman Engine

An original CPU animation engine with a manually launched GitHub Actions pipeline.
It produces real H.264/AAC videos from validated scene plans, local Kokoro voiceover,
contact-aware skeletal motion, layered environments, procedural sound and measured QA.

**Status: working development engine, not professionally qualified autonomous filmmaking.**
The finite action library cannot visualize every arbitrary brief. Technical acceptance
and professional artistic acceptance are deliberately separate. See
[quality standards](docs/quality-standards.md) and [validation results](docs/validation.md).

## Run on GitHub

Open **Actions → Cinematic Stickman Video Generator → Run workflow**.

1. Enter **video_title**, **video_description** (your creative brief), and **minutes**.
   Decimals such as `1.5`, `2.5`, `7.5` are accepted; default is 3, safe maximum 10.
2. Leave **niche** at Auto-detect or choose one of ten niches.
3. Choose **Single Video**, **Ten-Niche Comparison**, or **Animation Quality Test**.
4. Keep **quality: production** for 1920×1080 / 60 FPS. Preview is 1280×720 / 24 FPS;
   draft is 640×360 / 24 FPS. The mandatory benchmark always runs at 1080p60.
5. Download the artifacts near the bottom of the completed run.

**Single Video** uses a genuine local Qwen2.5-1.5B quantized model, not a fixed script
lookup. No paid API, account, key or credit card is required by the engine. The small
model's writing quality is limited, and it can fail validation. A bounded rewrite is
attempted if measured narration cannot fit the duration. No audio stretching or filler.
GitHub account Actions quotas and artifact storage limits still apply.

Without source notes the writer creates a **clearly labelled fictional story**. It does
not pretend to know real historical/scientific facts. For factual material, commit a
reviewed source-notes JSON file and supply **source_notes_path**, or use a reviewed full
plan via **plan_path**. Sources are supplied context, not an autonomous fact-checker.
Review any factual output before publication.

**Reviewed plan:** commit your `Plan` JSON and enter its relative path in `plan_path`.
Title and brief must match the plan exactly; its story is not relabelled to masquerade
as newly generated content. The duration input is still measured and enforced.
See [setup](docs/setup.md) for an exact runnable example.

**Ten-Niche Comparison** runs ten independent matrix jobs, using the **ten distinct,
Codex-authored review fixtures** in `examples/plans/`. Title and brief are ignored in this
mode, and duration defaults to **75 seconds each**, configured separately from the
single-video duration. These examples qualify rendering, not arbitrary-title writing.
The history/survival stories are fiction, not real events or emergency instructions.
The science/security/scam examples include reviewed source notes.

Each successful job supplies the final MP4, six-second motion preview, contact sheet,
measured plan, narration manifest, technical report and resource report. Failed jobs
preserve diagnostics. Artifacts expire after 14 days (failure details: 7 days).
No generated videos are committed to this repository.

Repository variables: `MAX_MINUTES=10`, `COMPARISON_MINUTES=1.25`, `MAX_PARALLEL=2`.
The optional parallel_jobs input selects 2, 4 or 10 jobs (default 2) and takes
precedence over MAX_PARALLEL. Queued runners are normal.
Changing comparison duration significantly requires rewriting sample scripts. The
pipeline fails instead of stretching the same content to arbitrary length.

## Local setup

Python 3.12, FFmpeg/FFprobe, libcairo2 and DejaVu fonts. Linux is the tested platform.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
pip install -e . --no-deps
pytest -q
stickfilm benchmark --out output/benchmark
stickfilm models
stickfilm produce --plan examples/plans/00.json --minutes 1.25 --out output/psychology
```

For automatic writing:

```sh
pip install -r requirements-writer.lock --only-binary llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
stickfilm models --local
stickfilm produce --title 'The Door That Only Opened After Lunch' \
  --brief 'A fictional office comedy. Milo thinks a door is broken. Ada finds a sign saying pull. A simple misunderstanding escalates, then has a visual payoff. Use the door prop and no factual claims.' \
  --minutes 0.6 --niche 'Relatable Comedy' --out output/door --preset preview
```

The local writer's 1.1 GB model and 115 MB speech models are versioned and checksum
verified, cached in Actions, never checked into Git. The writer runs on two CPU
threads; larger models may improve writing but are not assumed available on hosted runners.

## Design

- `src/stickfilm/schema.py`: strict production IR and JSON schema.
- `motion.py`, `benchmark.py`: two-bone IK, distance gait, continuous benchmark.
- `drawing.py`, `world.py`, `render.py`: original rounded characters, 13 settings,
  three depth layers, camera tools, direct Cairo → FFmpeg stream, scene cache.
- `writer.py`: local-model JSON generation; `examples/plans`: authored fixtures.
- `voice.py`, `audio.py`: measured speech, narration ducking, original score/foley.
- `quality.py`: encoding, decode, duration, sound and motion gates; review images.
- `pipeline.py`, `cli.py`: production, preserved failure state, bounded retries.
- `.github/workflows/video-generator.yml`: manual production, benchmark, matrix,
  report aggregation and artifacts. `animation-tests.yml`: unit + real media tests.

[Architecture](docs/architecture.md) · [Setup](docs/setup.md) ·
[Troubleshooting](docs/troubleshooting.md) · [Licenses](assets/licenses/README.md)
