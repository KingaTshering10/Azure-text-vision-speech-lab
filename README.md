# Azure Text, Vision & Speech Lab

A practical collection of **eight notebooks and three runnable scripts** exploring Azure OpenAI and Hugging Face. Start with text generation, add image understanding and receipt extraction, then explore transcription, speech synthesis, and a voice-enabled PDF question-answering workflow.

The examples share one root configuration file and work with repository-relative paths on macOS, Linux, and Windows. This is a learning collection, with supplied sample media and local regression checks.

## Explore the examples

| Area | Example | What it demonstrates |
| --- | --- | --- |
| Text | [Basic requests](02_text/basic_azure_openai.ipynb) | Text generation, translation, and usage information |
| Text | [Prompt design](02_text/prompt_engineering.ipynb) | Tone instructions, short explanations, and few-shot sentiment examples |
| Chat | [Terminal chat](02_text/chat_cli.py), [Streamlit chat](02_text/streamlit_chat.py) | Multi-turn conversation with correct message roles |
| Vision | [Multimodal images](01_vision/multimodal_vision.ipynb) | Receipt reading, label comparison, chart extraction, and screenshot analysis |
| Receipts | [Notebook](01_vision/receipt_analysis.ipynb), [export script](01_vision/receipt_analyzer/receipt_analysis.py) | Image-to-text extraction followed by structured JSON and per-item CSV export |
| Speech recognition | [Azure ASR](03_speech_recognition/azure_asr.ipynb) | Transcription and speech-to-English translation |
| Local speech | [SpeechT5 synthesis](04_text_to_speech/local_speecht5.ipynb) | English speech generation with a supplied speaker embedding |
| Azure speech | [Text-to-speech](05_voice_assistant/azure_tts.ipynb) | Speech synthesis using a separately configured deployment |
| Voice + documents | [Speech translation and PDF retrieval](05_voice_assistant/speech_translation_rag.ipynb) | Spoken question → English query → retrieved PDF context → Swahili answer → spoken reply |

## Quick start on macOS or Linux

Use **Python 3.11** as the common starting point for these examples. Open the extracted or cloned repository folder in Terminal, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and copy the configuration with `Copy-Item .env.example .env`.

Edit the root `.env` with your own Azure resource details. Start with the `AZURE_OAI_*` group for text and vision. Configure the other service groups only when you need them.

| Configuration group | Used by | Deployment requirements |
| --- | --- | --- |
| `AZURE_OAI_*` | Text, chat, vision, receipt extraction, PDF answers | A chat deployment; image examples also need image input support |
| `AZURE_ASR_*` | Transcription and speech-to-English translation | A Whisper-compatible deployment supporting the requested audio operation |
| `AZURE_TTS_*` | Azure speech synthesis | A speech-synthesis deployment supporting the selected voice and language |

Each group has its own endpoint, key, deployment name, and API version. They may belong to different Azure resources. **Use the deployment name you created**, which can differ from the underlying model name. The configured dated APIs follow the original Azure SDK approach; select an API version supported by your resource. Defaults are configurable in `.env.example`.

Azure examples send the selected text, images, or audio to your configured cloud resource and may incur usage charges. The PDF assistant sends retrieved PDF text to the chat deployment. Local SpeechT5 and BGE embeddings download model files on first use and run locally afterward.

## Run an example

### Terminal chat

```bash
python 02_text/chat_cli.py
```

Type `quit` to end the conversation. History remains in memory for the current session.

### Streamlit chat

```bash
streamlit run 02_text/streamlit_chat.py
```

The app displays configuration guidance when settings are missing. It retains successful conversation turns in session state and provides a clear-conversation button.

### Receipt export

```bash
python 01_vision/receipt_analyzer/receipt_analysis.py
```

The default input is the included `test_receipt.jpg`. New results are written to `generated/receipt_result.json` and `generated/receipt_result.csv`. To analyze another image:

```bash
python 01_vision/receipt_analyzer/receipt_analysis.py path/to/receipt.jpg --json generated/custom.json --csv generated/custom.csv
```

Extraction uses two model calls: image reading, then JSON parsing with LangChain. The CSV repeats receipt-level details for each line item. The bundled JSON/CSV files are historical examples matching `test_receipt.jpg`; they are separate from newly generated results. Check values against the image before relying on them.

### Notebooks

Open a notebook in VS Code and select the `.venv` Python interpreter, or launch JupyterLab from the repository root:

```bash
jupyter lab
```

Run cells from top to bottom. Notebook root discovery works when the kernel's working directory is anywhere inside the repository. All stored outputs and execution counts have been cleared.

## Optional local-model dependencies

For local English speech synthesis:

```bash
python -m pip install -r requirements-local-tts.txt
```

For the voice-enabled PDF assistant:

```bash
python -m pip install -r requirements-voice-assistant.txt
```

These files include the base requirements. Local SpeechT5 uses `microsoft/speecht5_tts` and the selected vector from entry 7306 of the 7,931-row source speaker-vector dataset. The selected vector has 512 values. Model weights are not included.

The PDF assistant uses `BAAI/bge-small-en-v1.5` for English retrieval and LangChain's `InMemoryVectorStore`. It splits the six-page sample PDF into overlapping text chunks, retrieves three matches, requests a source-grounded Swahili answer, and synthesizes that answer. It is a file-based demonstration with no microphone capture or live streaming conversation.

Dependency files specify compatible ranges and selected model-library pins; they are not a fully locked environment. See [review notes](docs/review-notes.md) for the versions exercised during preparation.

## Local checks

From the repository root, after installing base requirements:

```bash
python -m unittest discover -s tests -v
```

Seven offline checks exercise configuration, image MIME types, SDK request construction, speech routes, streamed file writing, chat history, and receipt parsing/flattening. Requests use an in-process mock transport, not Azure.

Notebook syntax and structure, sample image integrity, audio metadata, PDF text extraction, and the selected speaker-vector file were also checked during preparation. PDF retrieval was exercised with deterministic test embeddings. Streamlit AppTest checks passed for missing configuration, a mock chat reply, and clearing history. **Live Azure requests, real embedding inference, SpeechT5 synthesis, and live Streamlit chat were not run end to end.** No new accuracy, latency, transcription, or speech-quality results are claimed.

## Sample assets and scope

- `01_vision/` includes five sample images plus receipt analyzer images and historical receipt outputs. The chart is a historical screenshot, not a current performance comparison.
- `03_speech_recognition/` contains `rr.mp3` and `german.mp3`. Audio names are retained from the source archive; spoken content was not fully reviewed or transcribed during preparation.
- `04_text_to_speech/` includes supplied short audio samples and the selected speaker embedding as JSON, with original dataset metadata.
- `05_voice_assistant/` includes supplied Hindi/Swahili sample audio and a six-page Margie's Travel training PDF. The PDF is historical sample context, not a current travel service listing.
- Three call recordings whose names refer to insurance, pharmacy, and loan scenarios were excluded from this public-ready package because their contents were not reviewed for sensitive information. They remain in the original ZIP.

The original `.env` files and hardcoded resource credentials are excluded. If any original keys are real, rotate them; removing them from this package does not revoke them. Keep your own `.env` private. Generated files are ignored by Git.

## Limitations

- A model can misread images, produce invalid fields, or invent unsupported details. JSON parsing does not establish factual accuracy.
- The audio translation example requests **English text**. The Swahili answer is a later chat-generation step, not an arbitrary-language audio translation endpoint.
- Nearest-neighbor retrieval returns matches even when the PDF cannot answer a question. Review the retrieved context and citations.
- Speaker separation, call analytics, medical advice, and production-grade validation are outside this collection's implemented scope.
- Azure deployment availability, API support, regional access, quotas, and supported voices depend on your resource.

## Sources and attribution

Prepared from the supplied `7text vision and speech.zip` training materials. See [review notes](docs/review-notes.md) for changes and [asset provenance](docs/source-assets.json) for original-to-packaged asset mappings and hashes.

Reference documentation:

- [Microsoft: vision-enabled chat models](https://learn.microsoft.com/en-us/azure/ai-services/openai/gpt-v-quickstart)
- [Microsoft: Azure image and audio REST API reference](https://learn.microsoft.com/en-US/azure/cognitive-services/openai/reference)
- [Microsoft: Azure transcription quickstart](https://learn.microsoft.com/en-us/azure/foundry/openai/whisper-quickstart)
- [Microsoft: Azure OpenAI TTS samples](https://github.com/Azure-Samples/azure-openai-tts-demo)
- [Microsoft SpeechT5 model card](https://huggingface.co/microsoft/speecht5_tts)
- [Matthijs/cmu-arctic-xvectors dataset card](https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors)
- [BAAI BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)

The SpeechT5 and speaker-vector source cards list MIT licensing. Other supplied training assets do not include a complete collection-wide license or authorship record. Original material is not claimed as newly authored work, and no blanket license has been assigned to the collection.
