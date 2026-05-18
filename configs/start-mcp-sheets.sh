#!/bin/bash
# Start MCP Google Sheets server with OAuth2 authentication
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Set OAuth token path for MCP server
# Token file contains client_id, client_secret, refresh_token (all-in-one)
export TOKEN_PATH="${TOKEN_PATH:-$SCRIPT_DIR/google-oauth-token.json}"

exec npx -y mcp-google-sheets
