# Setup and operation

The production workflow lives at `.github/workflows/video-generator.yml` and is named
**Cinematic Stickman Video Generator**. It supports only manual launch; test CI runs
on pushes and pull requests. The workflow has read-only repository permissions.

## Exact sample launch

For a full authored sample, select Single Video, minutes `1.25`, quality `production`,
plan_path `examples/plans/00.json`, title:

> The Deadline Has a Sofa

and description:

> A fictional office comedy about avoiding an intimidating assignment; no neuroscience claims.

Leave source_notes_path empty. These exact values are required because the existing
plan is an authored fixture. For a new story, leave plan_path empty and enter a new
brief. The local CPU writer will generate the narration and select executable scenes.

Animation Quality Test ignores single-video duration and produces the 22-second
1080p60 action-only benchmark. Comparison ignores the creative inputs and uses ten
75-second authored examples. Those mode-specific behaviors are intentional and shown
in the workflow descriptions.

## Supply a reviewed plan

Use `config/plan.schema.json`; validate with `stickfilm validate your-plan.json`.
A plan includes title, brief, niche, requested_minutes, provenance, factual_status,
sources and scenes. Scenes carry beat, narration, dialogue, actors, prop, environment,
camera, lighting, music, transitions, sound cues and pauses. Timing is finalized from
measured speech and written back into the delivered `plan.json`.

Use provenance `reviewed-plan` for human/Codex reviewed custom plans. Fiction is
explicit. A source-grounded plan must include sources; unverified plans are rejected.
Scripts with scene speech exceeding 45 seconds must be split into shorter scenes.

Source-notes input for local writing is a JSON list:

```json
[
  {
    "url": "https://www.cisa.gov/secure-our-world/turn-mfa",
    "claim": "Multi-factor authentication adds protection beyond a password."
  }
]
```

This is user-reviewed context. Automatic retrieval and verification of arbitrary
claims is not implemented. Source presence does not prove narration correctness.

## Artifacts

`animation-benchmark-1080p60` is generated before production jobs. In comparison mode,
`cinematic-00` through `cinematic-09` correspond to the ten niche order shown in the
workflow. `ten-niche-comparison-report` includes missing and failed entries.
`cinematic-single` is the normal generated video. Download the ZIP and open its final
MP4; `motion-preview.mp4` is only an excerpt.

The root report JSON distinguishes objectively measured checks from pending artistic
review. `resources.json` reports wall time, Python peak RAM, disk and encode timing.
Check monthly Actions minutes/storage in GitHub billing; this program cannot infer
an account's remaining quota. Public repositories may receive free standard runner
minutes subject to GitHub policy. Nothing here provisions a paid runner.

Intermediate scene MP4s and voice WAVs are retained locally for reruns. Scene keys
include content, renderer sources, resolution and FPS. They are decode-checked before
reuse. GitHub's model cache survives separate runs; scene caches currently do not.
Only model/dependency caches are restored automatically on fresh Actions runners.

## Repair and consolidation

If one niche fails, correct its plan or voice and launch a Single Video run with
that reviewed plan's exact title/brief. Run **Consolidate Comparison Reports**,
entering the original comparison run ID and the newer repair run ID. It downloads
read-only artifacts, prefers the explicitly supplied repair, and fails unless all
ten niches have passing quality reports. The original failure remains visible.

Authored action-only scenes can set an explicit scene duration with empty narration;
that directed timing is retained. They are not automatically padded to a target.
