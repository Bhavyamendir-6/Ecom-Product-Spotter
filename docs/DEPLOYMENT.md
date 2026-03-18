# Deployment Guide: ecommerce_product_spotter

## Local Deployment

### Prerequisites
- Python 3.11+
- `.env` file with `GOOGLE_API_KEY`

### Run Modes

#### Interactive Web UI
```bash
cd Ecommerce_product_spotter
.\.venv\Scripts\activate
adk web .
# Open http://localhost:8000
```

#### Terminal Mode
```bash
cd Ecommerce_product_spotter
.\.venv\Scripts\activate
adk run .
```

#### REST API Server
```bash
cd parent_directory
adk api_server Ecommerce_product_spotter
# API at http://localhost:8000
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | — | Gemini API key |
| `MODEL` | No | `gemini-2.0-flash` | Sub-agent model |
| `MODEL_PRO` | No | `gemini-2.5-flash` | Report generator model |

## GCP Deployment

Not in scope for this project (local-only per requirements). For future GCP deployment, refer to:
- [ADK Agent Engine docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine)
- [ADK Cloud Run deployment](https://google.github.io/adk-docs/deploy/cloud-run/)
