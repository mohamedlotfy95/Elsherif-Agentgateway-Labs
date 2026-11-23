# Test provider routing

These examples verify the routes from the [Kubernetes setup guide](create-cluster.md). Before running them:

- Create the Gemini and Claude `AgentgatewayBackend` resources.
- Apply the basic `gemini` `HTTPRoute` for the standard endpoint.
- Apply the `provider-routing` `HTTPRoute` to test path-based routing.
- Start a port-forward and leave it running in a separate terminal:

  ```shell
  kubectl -n default port-forward svc/agentgateway 8080:80
  ```

## Send a request to the basic Gemini route

The basic route sends requests to Gemini through the OpenAI-compatible chat completions endpoint:

```shell
curl -sS http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }' | jq
```

## Send a request to Gemini by path

The `/ai/gemini` path prefix routes this request to the Gemini backend:

```shell
curl -sS http://localhost:8080/ai/gemini \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }' | jq
```

## Send a request to Claude

The `/ai/claude` path prefix routes this request to the Claude backend:

```shell
curl -sS http://localhost:8080/ai/claude \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "claude-opus-4-6",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }' | jq
```
