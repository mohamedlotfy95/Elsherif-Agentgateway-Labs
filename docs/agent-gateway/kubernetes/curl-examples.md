curl "localhost:8080/v1beta/openai/chat/completions" -H content-type:application/json  -d '{
  "model": "",
  "messages": [
   {"role": "user", "content": "Explain how AI works in simple terms."}
 ]
}' | jq

curl -sS http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-2.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }' | jq