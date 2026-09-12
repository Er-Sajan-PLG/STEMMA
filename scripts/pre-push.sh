#!/bin/bash
echo "[STEMMA] Delegating pre-push verification to STEMMA's n8n Orchestrator..."

# Attempt to trigger the local STEMMA n8n webhook (port 5679)
RESPONSE=$(curl -s -w "%{http_code}" -X POST http://127.0.0.1:5679/webhook/stemma-ci)
STATUS_CODE=${RESPONSE: -3}
BODY=${RESPONSE::-3}

if [ "$STATUS_CODE" -eq 000 ]; then
    echo "⚠️ STEMMA n8n orchestrator not reachable on port 5679."
    echo "Falling back to local execution..."
    python3 scripts/verify_all.py
    if [ $? -ne 0 ]; then
        echo "❌ Local verification failed!"
        exit 1
    fi
    exit 0
fi

if [ "$STATUS_CODE" -ne 200 ]; then
    echo "❌ n8n Orchestrator rejected the push (Verification Failed)!"
    echo "Response: $BODY"
    exit 1
fi

echo "✅ n8n Orchestrator approved the push."
exit 0
