# STEMMA n8n Orchestrator

This repository hosts its own independent n8n orchestration plane to ensure strict isolation from other ecosystem projects (like JARVIS).

## Architecture

1. **n8n Container**: Runs locally via `docker-compose.yml` on port `5679` (to avoid conflicts with standard `5678` instances).
2. **STEMMA CI Bridge**: `scripts/ci_bridge_server.py` runs on port `8771`. It securely executes `verify_all.py` on behalf of n8n.
3. **Pre-Push Hook**: `.git/hooks/pre-push` intercepts `git push` commands and delegates execution to the n8n webhook.

## Getting Started

1. **Start the n8n Orchestrator**:
   ```bash
   docker compose up -d
   ```
2. **Access n8n**: Open [http://127.0.0.1:5679](http://127.0.0.1:5679)
3. **Import Workflow**: Import `workflows/stemma-ci-local.json` and set it to **Active**.
4. **Start the Bridge**: (in a separate terminal)
   ```bash
   python3 scripts/ci_bridge_server.py
   ```

Now, every `git push` is gated safely through n8n!
