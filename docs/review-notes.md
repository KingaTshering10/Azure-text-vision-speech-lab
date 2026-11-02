# Preparation and validation notes

## Original collection

The source archive contains 44 substantive files: eight notebooks, three Python scripts, four `.env` files, four requirements files, seven image files (including a duplicate receipt), thirteen audio files, two receipt-result files, an Arrow speaker-vector file and its metadata, and one PDF.

The package reorganizes the four original top-level directories into five learning sections. The original `6TTS/project` material is now `05_voice_assistant/`. Eight notebooks and three scripts have been rebuilt or revised around a shared root helper. No original source credentials or saved notebook outputs are included.

## Changes

1. Removed all four original `.env` files. Replaced hardcoded notebook keys, resource endpoints, and deployment assumptions with root `.env.example` settings. Configuration does not print keys, and key values are excluded from the settings object's representation. Existing keys must be rotated separately if real.
2. Cleared notebook outputs, execution counts, and original notebook metadata. This removes stored API responses, errors, inline media, and environment-specific details. Historical receipt files remain explicitly labeled as supplied examples.
3. Replaced the missing `receipt.png` reference with an existing JPEG. Image request MIME types now follow the selected file type. Corrected a duplicated dictionary key that overwrote the system role in the VPN request. Each optional image task has an explicit paired image and question.
4. Corrected generated CLI replies from `system` to `assistant` messages. Chat history records successful requests; failed requests do not leave an unmatched user turn. The Streamlit app now presents a general chat demo with consistent labels and configuration guidance.
5. Centralized separate chat/vision, ASR, and TTS credentials. SDK calls use configured deployment names. Chat and ASR default to the documented `2024-10-21` API; the TTS example retains the Azure sample's configurable `2025-03-01-preview` approach. Resource support must be checked before use.
6. Audio files are opened with context managers. Transcription and translation are distinct operations; translation is described as speech-to-English text. Streaming synthesis writes new MP3s under `generated/` without replacing supplied samples.
7. Replaced the private Windows Hugging Face cache path with a portable JSON file containing the one speaker embedding used by the notebook. The local SpeechT5 notebook checks the selected speaker vector's `(1, 512)` shape. It uses a supplied speaker embedding; no speaker training or personal voice cloning is implemented.
8. Replaced older LangChain aggregate imports and `get_relevant_documents` with current integration packages, `InMemoryVectorStore`, and `invoke`. Replaced full-page embedding with overlapping text chunks. Added page metadata and a source-grounded answer prompt. Retrieval still has no calibrated relevance threshold.
9. Receipt CLI defaults to `test_receipt.jpg`, matching the supplied JSON and CSV. New output paths live under `generated/`. It validates the top-level parsed object and line-item structure before writing the output files. This is not a strict receipt schema or financial reconciliation system.
10. Replaced inconsistent module requirement files with root base and optional dependency groups. Removed unused TensorFlow and obsolete DocArray/legacy-chain requirements. The Hugging Face integration's `full` extra requires Sentence Transformers below version 6, so the optional assistant requirements reflect that bound.

## Excluded call recordings

The following source files are not in the public-ready package:

- `4AzureASR/Call1_separated_16k_health_insurance.wav`
- `4AzureASR/Call3_separated_16k_pharmacy_call.wav`
- `4AzureASR/Call6_mono_16k_az_apply_loan.wav`

Their filenames suggest potentially sensitive call scenarios, and the spoken contents were not reviewed. This is a packaging precaution, not a finding that the recordings contain personal information. They remain available in the original source archive and are not needed by the rebuilt notebooks.

## Verification completed

- Parsed every Python file and notebook code cell as Python; validated all eight notebooks with `nbformat` and confirmed cleared outputs/counts.
- Ran seven offline regression tests with the actual OpenAI SDK and LangChain parser. API requests were intercepted by `httpx.MockTransport`; no Azure credentials or real network calls were used by these tests.
- Versions used for those checks: OpenAI SDK `3.26.0`, LangChain OpenAI `1.6.7`, LangChain Core `1.7.3`, nbformat `5.11.1`, and PyArrow `26.0.0`.
- Smoke-tested the Streamlit app with AppTest for missing configuration, a mock chat reply, and clearing conversation history; no real API calls were made.
- Read the supplied Arrow stream: 7,931 rows, with a 512-value vector at index 7306. Exported that selected vector and filename to `speaker_embedding.json` and verified every value against the original; preserved the source dataset metadata. The full Arrow cache is excluded to keep the repository small and stay within the upload service's request limit. It remains in the original ZIP.
- Extracted text from the six-page Margie's Travel PDF and exercised the real PDF splitting/retrieval code with deterministic test embeddings: 13 chunks, three retrieved results, and expected New York page retrieval for an English test query. This checks the pipeline mechanics, not BGE semantic quality.
- Checked all seven images for decodability and inspected an image contact sheet. The receipt outputs correspond to the industrial-parts test image, not the East Repair receipt. The source receipt image contains sample address/payment fields; these were retained as training-image content.
- Probed all thirteen source audio files for format/duration/channel metadata; ten are retained. Audio contents were not transcribed or fully reviewed. No speech accuracy or quality assessment was performed.
- Preserved retained binary/sample assets unchanged and recorded SHA-256 hashes in `source-assets.json`.
- Scanned the finished text and notebooks for the original credential values and common credential patterns. Real `.env` files, original notebook outputs, and macOS archive metadata are excluded.

## Not executed

No live Azure requests, deployment provisioning, model downloads, real BGE inference, SpeechT5 generation, or live Streamlit chat session were performed. Requirements are compatibility ranges with selected pins, not a complete lockfile validated across all platforms. The collection has no measured end-to-end accuracy, translation quality, latency, or cost results.

## Attribution

The original archive supplies training examples and sample assets, not a complete authorship or license manifest. The included PDF identifies Margie's Travel as its sample context. Public model/dataset cards are linked in the README; the bundled dataset metadata itself has an empty license field. The source cards list MIT, but this does not imply a collection-wide license for other assets. No additional ownership claim or blanket license was added.
