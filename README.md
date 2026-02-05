# 🧬 Darwin - AI Growth Engineer

> **Autonomous Multi-Agent System for UX Optimization**

Darwin is an AI-powered system that monitors your product analytics, detects user friction, analyzes root causes, and automatically creates Pull Requests to fix issues.

## 🎯 What Darwin Does

```
📊 PostHog Analytics → 🕵️ Watcher Agent → 🧠 Analyst Agent → 👩‍💻 Engineer Agent → 🔀 GitHub PR
```

1. **Watcher Agent (Eyes)** - Monitors PostHog for rage clicks, drop-offs, and friction signals
2. **Analyst Agent (Brain)** - Diagnoses root causes and recommends specific code fixes
3. **Engineer Agent (Hands)** - Generates code changes and creates GitHub Pull Requests

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- PostHog account with Personal API Key
- GitHub Personal Access Token
- Gemini API Key

### Setup

```bash
# Clone the repository
git clone https://github.com/heenakousarm-cloud/darwin-multi-agent.git
cd darwin-multi-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run Darwin

```bash
# Full pipeline: Watcher → Analyst → Engineer
python scripts/run_darwin.py

# Or run specific modes
python scripts/run_darwin.py --mode analyze   # Skip to analysis
python scripts/run_darwin.py --mode engineer  # Skip to engineering
```

## 📁 Project Structure

```
darwin-multi-agent/
├── src/
│   ├── config/         # Settings and configuration
│   ├── models/         # Pydantic data models
│   ├── db/             # MongoDB connection
│   ├── tools/          # CrewAI custom tools
│   ├── agents/         # Agent definitions
│   ├── tasks/          # Task definitions
│   └── crew/           # Crew orchestration
├── scripts/            # Entry point scripts
├── data/mock/          # Mock data for testing
├── requirements.txt
└── .env.example
```

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `POSTHOG_API_KEY` | PostHog Personal API Key (phx_*) |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GEMINI_API_KEY` | Google Gemini API Key |
| `MONGODB_URI` | MongoDB connection string |

## 🤝 Team

- **heenakousarm-cloud**
- **anand-shirahatti**

## 📄 License

MIT License - Built for WeKan Hackathon 2026
