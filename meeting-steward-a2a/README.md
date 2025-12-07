# Meeting Steward A2A

**Intelligent, Fully Local Multi-Agent Meeting Analysis System**

Meeting Steward A2A is a sophisticated meeting analysis tool that runs entirely on your local machine. It uses LangGraph for multi-agent orchestration, Ollama for LLM inference, Whisper for transcription, and WhisperX for speaker diarization—all without requiring external APIs.

## Features

- **📁 Flexible Input**: Upload audio files (.wav, .mp3, .m4a) or paste text transcripts
- **🎙️ Local Transcription**: Whisper-based speech-to-text with speaker diarization
- **🤖 Multi-Agent Analysis**: LangGraph orchestrates specialized agents:
  - Transcriber (audio processing)
  - Summarizer (executive summary generation)
  - Decision Extractor (key decisions identification)
  - Action Item Agent (task extraction with owners and due dates)
- **💾 Persistent Storage**: SQLite database for meeting history
- **🖥️ Web UI**: Beautiful Streamlit interface for easy interaction
- **⚡ CLI Tools**: Standalone scripts for automation

## Architecture

```
meeting-steward-a2a/
├── a2a_protocol/      # Agent-to-Agent communication protocol
├── agents/            # Individual agent implementations
├── llm_providers/     # Ollama client and prompts
├── services/          # Pipeline orchestration and storage
├── ui/                # Streamlit web interface
├── scripts/           # CLI utilities
└── data/              # Database and uploads
```

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running

### Installing Ollama

Download from [ollama.ai](https://ollama.ai/) and install.

Pull a model:
```bash
ollama pull llama3.2
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

## Installation

1. **Clone/Navigate to the project**:
```bash
cd meeting-steward-a2a
```

2. **Create virtual environment**:
```bash
python -m venv venv
```

3. **Activate virtual environment**:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -e .
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

5. **Create .env file** (optional):
```bash
copy .env.template .env
```

Edit `.env` to customize settings (Ollama host, model name, etc.).

## Usage

### Streamlit Web UI

Launch the web interface:
```bash
streamlit run ui/streamlit_app.py
```

Then:
1. Open your browser to http://localhost:8501
2. Select **Audio File** or **Text Transcript** input
3. Upload/paste your meeting data
4. Click **Run Meeting Steward**
5. View results: summary, decisions, action items, agent logs, and transcript

### CLI Tools

**Transcribe audio only**:
```bash
python scripts/transcribe_audio.py path/to/audio.wav
```

**Analyze text transcript**:
```bash
python scripts/run_text_meeting.py path/to/transcript.txt
```

## Configuration

Edit `.env` or modify `app_config/settings.py`:

- `OLLAMA_HOST`: Ollama API endpoint (default: http://localhost:11434)
- `MODEL_NAME`: LLM model to use (default: llama3.2)
- `WHISPER_MODEL`: Whisper model size (base/small/medium/large)
- `USE_WHISPERX`: Enable WhisperX for diarization (default: True)
- `DB_PATH`: SQLite database location

## How It Works

### Audio Path
1. **Upload** → Audio file uploaded
2. **Transcribe** → Whisper converts speech to text
3. **Diarize** → WhisperX identifies speakers
4. **Summarize** → LLM generates executive summary
5. **Extract Decisions** → LLM identifies key decisions
6. **Extract Actions** → LLM finds action items with owners
7. **Store** → Results saved to SQLite
8. **Display** → Results shown in UI

### Text Path
1. **Paste** → Text transcript provided
2. **Summarize** → LLM generates executive summary
3. **Extract Decisions** → LLM identifies key decisions
4. **Extract Actions** → LLM finds action items
5. **Store** → Results saved to SQLite
6. **Display** → Results shown in UI

## A2A Protocol

The system implements an Agent-to-Agent (A2A) communication protocol:

- **Roles**: STEWARD, TRANSCRIBER, SUMMARIZER, DECISION_EXTRACTOR, ACTION_ITEM_AGENT
- **Messages**: Structured AgentMessage objects track inter-agent communication
- **Routing**: Predefined message flows ensure correct agent sequencing
- **State**: Shared GraphState object maintains meeting data throughout pipeline

## Data Models

### MeetingState
Central state object containing:
- Transcript (raw text and diarized segments)
- Summary (executive bullet points)
- Decisions (with owners and rationale)
- Action items (with owners, due dates, priority)
- Agent messages (communication log)

### Database Schema
- `meetings`: Core meeting data
- `decisions`: Key decisions (linked to meetings)
- `action_items`: Tasks (linked to meetings)

## Troubleshooting

### Ollama connection errors
Ensure Ollama is running:
```bash
ollama serve
```

### Model not found
Pull the required model:
```bash
ollama pull llama3.2
```

### Whisper/diarization errors
For WhisperX diarization issues, set `USE_WHISPERX=False` in `.env` to use basic Whisper without diarization.

### Memory issues
Use smaller models:
- Whisper: Change to `WHISPER_MODEL=tiny` or `base`
- LLM: Use a smaller Ollama model

## Development

Run tests:
```bash
pytest tests/ -v
```

Code formatting:
```bash
black .
ruff check .
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Roadmap

- [ ] Real-time streaming transcription
- [ ] Multi-language support
- [ ] Export to various formats (PDF, DOCX, Markdown)
- [ ] Advanced search and filtering
- [ ] Meeting templates and custom prompts
- [ ] Integration with calendar applications

---

Built with ❤️ using LangGraph, Ollama, Whisper, and Streamlit
