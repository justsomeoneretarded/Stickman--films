# Asset and model licensing

All character drawings, procedural environment geometry, props, scripts and generated
music/foley in this repository are original project code/assets under the root MIT
license. No stock footage, copied channel artwork, cloned voice profiles or scraped
sound library is included. Model weights are downloaded separately, never committed.

Reviewed 2026-10-21:

| Component | Upstream declaration | Use |
|---|---|---|
| Kokoro-82M v1.0 weights/voices | Apache-2.0, [model card](https://huggingface.co/hexgrad/Kokoro-82M/blob/f3ff3571791e39611d31c381e3a41a3af07b4987/README.md) | Local narrator; stock voices, no cloning |
| kokoro-onnx 0.4.9 | MIT, [source](https://github.com/thewh1teagle/kokoro-onnx) | ONNX runtime adapter |
| Qwen2.5-1.5B-Instruct GGUF | Apache-2.0, [pinned repository](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/91cad51170dc346986eccefdc2dd33a9da36ead9) | Optional CPU story writer |
| llama-cpp-python | MIT | CPU inference |
| Cairo | LGPL-2.1/MPL-1.1 dual terms | System rendering library |
| FFmpeg | LGPL/GPL depending build; libx264 build is GPL | Encoding executable; not distributed here |
| DejaVu fonts | Bitstream Vera / DejaVu font terms | System text rendering |

Kokoro's card explicitly declares Apache-licensed model weights and commercial usage,
not merely an open-source inference library. It also describes training sources and
attributions: retain upstream notices when redistributing the model. We download and
verify the ONNX conversion from the upstream adapter's versioned model-files-v1.0
release and record checksums in config/models.json. Upstream declarations are not an
independent audit of all training data or rights in every jurisdiction.

Piper was considered but not integrated: current OHF piper1-gpl code is GPL-3.0, and
voice model licenses vary by voice; code licensing alone cannot qualify a voice.
Kokoro was actually run on this project's CPU environment; Piper was not performance
or listening-tested. No claims of a head-to-head voice-quality evaluation are made.

Kokoro offers voice identity and speaking-rate controls here, not convincing reliable
emotional direction. Compare delivered samples by listening before commercial use.
Narrative sources are listed separately in each plan and do not license unrelated
assets. Generated outputs need user factual and artistic review before publishing.
