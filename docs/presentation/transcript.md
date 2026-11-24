# Agentgateway: Simple Presentation Transcript

## 1. Introduction

Hello everyone. In this video, we are going to learn how to use Agentgateway as an AI gateway in Kubernetes.

In many companies, applications and AI agents connect directly to large language model providers. This means that each application may need separate API keys and provider settings. It can also make traffic harder to monitor and secure.

Agentgateway gives us one central endpoint in front of our AI systems. Applications can send their requests to the gateway, and the gateway can route those requests to the right provider.

By the end of this video, you will understand how the gateway works and how to route requests to Gemini and Claude.

```text
+-------------+       +-----------------+       +--------------+
| Application | ----> | Agentgateway    | ----> | AI provider  |
+-------------+       +-----------------+       +--------------+
```

## 2. What is Agentgateway?

Agentgateway is an open source gateway for AI infrastructure. You can think of it as a reverse proxy that sits in front of AI services.

It can route requests to cloud language model providers or to local models. It can also work as an MCP router and manage traffic between AI agents.

The gateway adds another layer for security and monitoring. It is useful because it gives applications one place to connect to AI services.

## 3. Why use a gateway?

Regular HTTP gateways usually route traffic using the URL path or headers. They are often stateless and send traffic to Kubernetes Services or external endpoints.

AI traffic has additional needs. The gateway may need to inspect the request body to choose a model. It may also need to understand which agents are talking to each other.

For MCP servers, the gateway may need to know which tools are available. Agentgateway handles these AI-specific situations as well as normal HTTP routing.

In this video, we will focus on LLM routing.

## 4. Gateway API resources

We will use three main Kubernetes resources.

The **Gateway** opens a listener for incoming traffic. Its listener can use HTTP on port 80.

The **HTTPRoute** controls where incoming requests go. It can match a URL path and connect to a backend.

The **AgentgatewayBackend** describes an AI provider, such as Gemini or Claude. It also contains the provider settings and references the Kubernetes Secret that holds the API key.

In this lab, we will use the `default` namespace for the Gateway and the `agentgateway-system` namespace for the control plane, routes, backends, and Secrets.

```text
Gateway listener :80
        |
HTTPRoute: /ai/gemini
        |
AgentgatewayBackend: gemini ----> Gemini
        |
        +-- uses Secret: gemini-secret
```

## 5. Set up the Kubernetes cluster

We will use Kind to create a local Kubernetes cluster for testing.

```shell
kind create cluster --name gatewayapi
kubectl get nodes
```

The output should show that the cluster node is ready.

## 6. Install the Gateway API resources

Agentgateway needs the Kubernetes Gateway API custom resource definitions, or CRDs.

Set the chart version and install the CRD chart:

```shell
CHART_VERSION="v1.1.0"

helm upgrade -i agentgateway-crds oci://cr.agentgateway.dev/charts/agentgateway-crds \
  --create-namespace \
  --namespace agentgateway-system \
  --version $CHART_VERSION
```

This gives Kubernetes the resources used for Gateways, HTTPRoutes, GatewayClasses, and Agentgateway backends.

Install the Agentgateway control plane next:

```shell
helm upgrade -i agentgateway oci://cr.agentgateway.dev/charts/agentgateway \
  --namespace agentgateway-system \
  --version $CHART_VERSION \
  --set controller.image.pullPolicy=Always \
  --wait
```

The control plane watches Gateway API and Agentgateway resources. When we apply these resources, the control plane creates the gateway configuration and proxy.

Check that the pods are running:

```shell
kubectl -n agentgateway-system get pods
```

## 7. Create the Gateway

Apply the Gateway manifest from the repository:

```shell
kubectl apply -f docs/agent-gateway/kubernetes/manifests/gateway.yaml
```

Check the GatewayClass and Gateway:

```shell
kubectl get gatewayclass agentgateway
kubectl get gateway agentgateway -n default
kubectl get services -n default
```

The Gateway should report `Accepted=True` and `Programmed=True`.

Kind does not provide a public load balancer by default. Start a port forward to make the Gateway available on your computer:

```shell
kubectl -n default port-forward svc/agentgateway 8080:80
```

Keep this command running while you test the routes.

## 8. Configure the Gemini provider

Get a Gemini API key from Google AI Studio and store it in an environment variable:

```shell
export GOOGLE_KEY="<your-gemini-api-key>"
```

Never put a real API key directly in source files or commit it to Git.

Create a Kubernetes Secret for Gemini:

```shell
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: gemini-secret
  namespace: agentgateway-system
type: Opaque
stringData:
  Authorization: $GOOGLE_KEY
EOF
```

Check that the Secret was created:

```shell
kubectl get secrets -n agentgateway-system
```

Next, create the Gemini backend:

```shell
kubectl apply -f - <<EOF
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayBackend
metadata:
  name: gemini
  namespace: agentgateway-system
spec:
  ai:
    provider:
      gemini:
        model: gemini-3.5-flash-lite
  policies:
    auth:
      secretRef:
        name: gemini-secret
EOF
```

Check that the backend is accepted:

```shell
kubectl get agentgatewaybackends.agentgateway.dev -n agentgateway-system
```

## 9. Configure the Claude provider

Create an Anthropic API key and save it in an environment variable:

```shell
export ANTHROPIC_API_KEY="<your-anthropic-api-key>"
```

Create a Kubernetes Secret for Claude:

```shell
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: anthropic-secret
  namespace: agentgateway-system
type: Opaque
stringData:
  Authorization: $ANTHROPIC_API_KEY
EOF
```

Create the Claude backend:

```shell
kubectl apply -f - <<EOF
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayBackend
metadata:
  name: claude
  namespace: agentgateway-system
spec:
  ai:
    provider:
      anthropic:
        model: claude-opus-4-6
  policies:
    auth:
      secretRef:
        name: anthropic-secret
EOF
```

Check that both provider backends are accepted:

```shell
kubectl get agentgatewaybackends.agentgateway.dev -n agentgateway-system
```

## 10. Create a basic route to Gemini

An HTTPRoute connects a Gateway listener to a backend. The following route sends all requests to Gemini:

```shell
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: gemini
  namespace: agentgateway-system
spec:
  parentRefs:
    - name: agentgateway
      namespace: default
  rules:
    - backendRefs:
        - name: gemini
          namespace: agentgateway-system
          group: agentgateway.dev
          kind: AgentgatewayBackend
EOF
```

Agentgateway rewrites the request to the chat completions endpoint for the selected provider.

Test the Gemini route:

```shell
curl -sS http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }'
```

The route should return an answer from Gemini. The response may also include token usage details.

## 11. Route requests by URL path

Next, we will update the routing rules so that different paths select different providers.

Create an HTTPRoute named `provider-routing`:

```shell
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: provider-routing
  namespace: agentgateway-system
spec:
  parentRefs:
    - name: agentgateway
      namespace: default
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /ai/gemini
      backendRefs:
        - name: gemini
          namespace: agentgateway-system
          group: agentgateway.dev
          kind: AgentgatewayBackend
    - matches:
        - path:
            type: PathPrefix
            value: /ai/claude
      backendRefs:
        - name: claude
          namespace: agentgateway-system
          group: agentgateway.dev
          kind: AgentgatewayBackend
EOF
```

A `PathPrefix` match also accepts longer paths below the same prefix. For example, `/ai/gemini/chat` will use the Gemini rule.

If you keep the basic Gemini route, the more specific path rules take precedence for `/ai/gemini` and `/ai/claude`.

```text
POST /ai/gemini  ----> AgentgatewayBackend: gemini
POST /ai/claude  ----> AgentgatewayBackend: claude
```

## 12. Test provider routing

Send a request to Gemini through the Gemini path:

```shell
curl -sS http://localhost:8080/ai/gemini \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-3.5-flash-lite",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }'
```

Send a request to Claude through the Claude path:

```shell
curl -sS http://localhost:8080/ai/claude \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "claude-opus-4-6",
    "messages": [
      {"role": "user", "content": "Explain how AI works in simple terms."}
    ]
  }'
```

Both providers are now available through one gateway endpoint.

## 13. Check the route status

Check that the HTTPRoute was accepted and that its backend references were resolved:

```shell
kubectl describe httproute provider-routing -n agentgateway-system
```

Look for `Accepted=True` and `ResolvedRefs=True`. These statuses show that the Gateway accepted the route and found the referenced backends.

If you receive `404 route not found`, check the URL path and confirm that the HTTPRoute is attached to the correct Gateway.

If a backend is unresolved, confirm that the `AgentgatewayBackend` exists in `agentgateway-system` and has been accepted.

If a provider reports that a model is unavailable, confirm that the model is available to your API account.

## 14. Review

Today we learned how a Gateway, an HTTPRoute, and an AgentgatewayBackend work together.

We installed Agentgateway in Kubernetes, created provider backends, and routed requests to Gemini and Claude through one endpoint.

Agentgateway can also use the request body and provider-specific data for more advanced routing. This makes it useful for MCP routing and agent-to-agent traffic, which require more than basic URL-based routing.

## 15. Source code and next steps

You can find the source code for this lesson in the repository description. The Kubernetes examples are in the `docs/agent-gateway/kubernetes` folder.

The setup guide explains how to install the Gateway and configure provider routing. The curl examples show how to test the basic and path-based routes.

In a later video, we will look at MCP routing. MCP servers are becoming more common, and DevOps engineers need to know how to manage and route traffic to them in Kubernetes.

You can also explore the Ultimate DevOps Roadmap and course if you want to learn more about starting a career in DevOps.

Thank you for watching. See you next time.
