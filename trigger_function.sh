#!/bin/bash

# Configuration
FUNCTION_APP_NAME="lk-outbound-caller-scheduler-1749797869"
FUNCTION_NAME="mytimer"

# Get master key if not provided
if [ -z "$1" ]; then
  echo "Getting master key..."
  MASTER_KEY=$(az functionapp keys list \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "livekit-outbound-caller-agent" \
    --query "masterKey" -o tsv)
  
  if [ -z "$MASTER_KEY" ]; then
    echo "Error: Could not get master key"
    exit 1
  fi
  echo "Using master key: ${MASTER_KEY:0:10}..."
else
  MASTER_KEY="$1"
fi

# Trigger the function using admin endpoint
echo "=== Triggering function $FUNCTION_NAME..."
curl -v \
  -X POST \
  -d "{}" \
  -H "x-functions-key: $MASTER_KEY" \
  -H "Content-Type: application/json" \
  "https://$FUNCTION_APP_NAME.azurewebsites.net/admin/functions/$FUNCTION_NAME"

echo -e "\n=== Function trigger request sent!"
echo "Check the logs with: task logs"
