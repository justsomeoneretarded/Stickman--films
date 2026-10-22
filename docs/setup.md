# Setup and operation

Two independent manual workflows are available:

- **Psychology — Independent Film** (`.github/workflows/psychology.yml`)
- **What-if Scenarios — Independent Film** (`.github/workflows/what-if.yml`)

Both call the shared renderer, but have distinct creative inputs, niche, concurrency
group, job and artifact. Launch both to produce both films concurrently. Neither
waits on the other. Infrastructure tests run separately on pushes and pull requests.
Repository permissions for the film workflows are read-only.

## Exact first-film launches

Use the title and creative brief in [psychology-inputs.json](episodes/psychology-inputs.json)
or [what-if-inputs.json](episodes/what-if-inputs.json). Each file supplies all the exact
workflow fields, including `minutes: "5"`, production quality, and its own reviewed plan.
The finished duration for a requested five-minute film must be four to six minutes.

The current defaults reproduce the authored 50-shot films. For a new episode, enter its own title and creative brief and leave
`reviewed_plan_path` blank. The experimental local CPU writer will generate a new story and
executable scene plan; it does not promise the same shot direction as the reviewed films. Supply reviewed source notes for factual claims; otherwise
it writes labelled fiction. The first two stories are separately authored review
plans, not claims that the small local model independently authored these scripts.

The earlier comparison workflows are archived under `docs/archive/workflows/`.
For the continuous movement benchmark, run `stickfilm benchmark` locally; tests also
exercise a real short video. There is no cross-niche benchmark job blocking either
production workflow.

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

The two production artifacts are `psychology-film-1080p60` and
`what-if-film-1080p60`. Each has its own final MP4, script, storyboard, measured plan,
voice manifest, contact sheet, six-second motion excerpt, technical QA and resource
reports. Download the ZIP and open the long title-named MP4. `motion-preview.mp4`
is only an excerpt. Successful and partial production artifacts are retained for
30 days; failure diagnostics are retained for seven days.

The root report JSON distinguishes objectively measured checks from pending artistic
review. `resources.json` reports wall time, Python peak RAM, disk and encode timing.
Check monthly Actions minutes/storage in GitHub billing; this program cannot infer
an account's remaining quota. Public repositories may receive free standard runner
minutes subject to GitHub policy. Nothing here provisions a paid runner.

Intermediate scene MP4s and voice WAVs are retained locally for reruns. Scene keys
include content, renderer sources, resolution and FPS. They are decode-checked before
reuse. GitHub's model cache survives separate runs; scene caches currently do not.
Only model/dependency caches are restored automatically on fresh Actions runners.

## Repair one film

If a film fails, open its own run and inspect `failure.json`, the technical report,
and the diagnostics artifact. Correct that film's plan and rerun its workflow with
the matching title and brief. The other niche is unaffected and keeps its own
artifact. A passing technical report is not an artistic score.

Authored action-only scenes can set an explicit scene duration with empty narration;
that directed timing is retained. They are not automatically padded to a target.
