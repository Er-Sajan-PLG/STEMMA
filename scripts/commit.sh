#!/usr/bin/env bash
# commit.sh - Atomic commit helper with validation and doc sync
# Usage: ./scripts/commit.sh "type(scope): description" [files...]

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

TYPE_SCOPE="${1:-}"
shift || true

if [[ -z "$TYPE_SCOPE" ]]; then
    echo "Usage: $0 \"type(scope): description\" [files...]"
    echo "Types: feat, fix, docs, refactor, chore, test, ci"
    exit 1
fi

FILES=("$@")
if [[ ${#FILES[@]} -eq 0 ]]; then
    FILES=($(git diff --name-only))
fi

echo "📦 Staging files: ${FILES[*]}"
git add "${FILES[@]}"

echo "🔍 Running validation..."
if [[ " ${FILES[*]} " =~ (content|connections|sources|schema)/ ]]; then
    echo "  → Running validate.py..."
    python3 scripts/validate.py || { echo "❌ Validation failed"; exit 1; }
fi

if [[ " ${FILES[*]} " =~ (scripts/|webapp/|ingestion_webapp/) ]]; then
    echo "  → Running verify_all.py..."
    python3 scripts/verify_all.py || { echo "❌ verify_all failed"; exit 1; }
fi

# Check for version bump reminder
if git diff --cached --name-only | grep -qE "^schema/.*\.json$|^schema/VERSION\.yaml$"; then
    echo "⚠️  Schema changed — ensure schema/VERSION.yaml is bumped"
fi

# Auto-update AGENTS.md timestamp if docs changed
if git diff --cached --name-only | grep -qE "\.md$|AGENTS\.md$"; then
    echo "📝 Docs changed — updating AGENTS.md timestamp"
    sed -i "s/^# Last updated:.*/# Last updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)/" AGENTS.md 2>/dev/null || true
    git add AGENTS.md
fi

# Show diff
echo "📋 Staged changes:"
git diff --cached --stat

# Commit
git commit -m "$TYPE_SCOPE"

echo "✅ Committed: $TYPE_SCOPE"
git log --oneline -1
