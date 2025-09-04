#!/bin/zsh
echo "▶️  Attempting to log in and capture token..."
LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}' \
  http://localhost:1010/login)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r .access_token)
if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Login failed. Server response:"
  echo $LOGIN_RESPONSE
  exit 1
fi
echo "✅ Login successful. Token captured."
echo "\n▶️  Attempting to create user 'alice' with the new token..."
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username": "alice", "age": 25, "email": "alice@example.com"}' \
  http://localhost:1010/users
echo "\n"
