# Troubleshooting

- **No workflow button:** ensure `video-generator.yml` is on the default branch and
  GitHub Actions is enabled. If organizational policy disables Actions, ask the repo
  administrator. No program can override that policy.
- **Duration rejected:** enter a finite positive decimal number, between 8 seconds
  and the configured safe maximum (10 minutes by default).
- **Narration too long/short:** read the measured seconds in the error. Revise the
  script, splitting long scenes or adding actual narrative content. Do not pad the
  picture or stretch the voice. The automatic writer has one bounded rewrite.
- **A reviewed plan rejects a different title:** intentional. Change the plan or
  use automatic writing. Authored examples are not generic title-generation engines.
- **Unknown asset/action:** choose an enum from `config/plan.schema.json` or implement
  and qualify the missing action; model-generated executable code is never accepted.
- **Model download failure:** inspect network/logs, disk space and SHA checks.
  Downloads retry three times. Do not disable TLS or checksum verification.
- **llama-cpp wheel unavailable:** Python 3.12 on Ubuntu x86_64 is tested. Use the
  exact pinned CPU wheel index. Reviewed plans need no writer installation/model.
- **QA fails:** download quality-report.json, failure.json, logs and preview. Failed
  outputs are uploaded as diagnostics but are not a successful production result.
- **Job timeout:** lower the explicit quality preset or shorten/review the script.
  Production jobs have a 55-minute timeout and a 40-minute process bound. Monthly
  usage/storage is an account limit; increasing parallelism does not reduce usage.
- **One comparison fails:** `fail-fast: false` preserves the other jobs. Aggregation
  marks missing results; it does not silently promote partial output to a pass.
- **Cache reuse:** local scene cache decode-checks files and hashes renderer sources.
  Delete `output/.../scenes` to force a cold render. Model caches use pinned checksums.
