# Agentgateway: Simple Presentation Transcript

## 1. Welcome

Hello, everyone. Today we will learn what an agent gateway does and how to use Agentgateway with Kubernetes.

By the end, you will know how to connect two AI providers and send requests to them through one gateway.

```text
+-------------+       +-----------------+       +--------------+
| Application | ----> | Agentgateway    | ----> | AI provider  |
+-------------+       +-----------------+       +--------------+
```

## 2. The problem

Many applications connect directly to AI providers. One application may use Gemini. Another may use Claude. Each application needs its own provider settings and API key.

This can make it harder to manage keys, understand where requests go, and check errors. When we use a gateway, applications can send requests to one place. The gateway can then send each request to the right provider.

The gateway does not secure or monitor everything automatically. We must configure the right credentials, policies, and monitoring.

```text
Before:                         After:
App A -- API key --> Gemini     App A --\
App B -- API key --> Claude               > Agentgateway --> Gemini or Claude
Agent -- API key --> Provider   App B --/
```

## 3. The main Kubernetes resources

We will use three important resources.

First, a **Gateway** opens a listener for incoming traffic.

Second, an **HTTPRoute** tells the Gateway where to send a request. It can match a URL path, such as `/ai/gemini`.

Third, an **AgentgatewayBackend** describes an AI provider, such as Gemini or Claude. It also refers to the Secret that holds the provider's API key.

In this lab, the Gateway is in the `default` namespace. The routes and provider backends are in the `agentgateway-system` namespace.

```text
Gateway listener :80
        |
HTTPRoute: /ai/gemini
        |
AgentgatewayBackend: gemini ----> Gemini
        |
        +-- uses Secret: gemini-secret
```

## 4. Set up the lab

We will use Kind to create a Kubernetes cluster on our computer. Then we will install the Gateway API resources and the Agentgateway control plane.

The control plane manages the gateway configuration. We will apply a Gateway manifest and check that the Gateway is accepted and ready.

Kind does not provide a public load balancer by default. We will use `kubectl port-forward` to send requests from our computer to the Gateway. Keep the port-forward command running in a separate terminal.

```shell
$ kind create cluster --name gatewayapi
$ kubectl get nodes
NAME                       STATUS
gatewayapi-control-plane   Ready

# After installing the Gateway API and Agentgateway:
$ kubectl apply -f docs/agent-gateway/kubernetes/manifests/gateway.yaml
$ kubectl -n default port-forward svc/agentgateway 8080:80
```

## 5. Add the AI providers

Next, we will create a Kubernetes Secret for each provider API key. We should not put real API keys in source files or commit them to Git.

Then we will create one `AgentgatewayBackend` for Gemini and one for Claude. Each backend uses a model and refers to its provider's Secret. Before routing requests, check that both backends are accepted.

```text
$ kubectl get secrets -n agentgateway-system
NAME               TYPE
gemini-secret      Opaque
anthropic-secret   Opaque

$ kubectl get agentgatewaybackends.agentgateway.dev -n agentgateway-system
NAME     ACCEPTED
gemini   True
claude   True
```

## 6. Route requests

An HTTPRoute connects a request to a backend. A basic route can send all requests to Gemini.

We can also route by URL path. In our example, requests under `/ai/gemini` go to the Gemini backend. Requests under `/ai/claude` go to the Claude backend.

The path prefix is the part at the start of the URL. A request to `/ai/gemini` or to a longer path such as `/ai/gemini/chat` matches the Gemini rule.

After applying the route, check its status. We want to see `Accepted=True` and `ResolvedRefs=True`. This tells us the Gateway accepted the route and found its backend references.

```text
POST /ai/gemini  ----------------> AgentgatewayBackend: gemini
POST /ai/claude  ----------------> AgentgatewayBackend: claude
```

## 7. Test and troubleshoot

Now we can use the curl examples to send one request to Gemini and another to Claude.

```shell
$ curl -sS http://localhost:8080/ai/gemini \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemini-3.5-flash-lite","messages":[{"role":"user","content":"Hello"}]}'

$ curl -sS http://localhost:8080/ai/claude \
  -H 'Content-Type: application/json' \
  -d '{"model":"claude-opus-4-6","messages":[{"role":"user","content":"Hello"}]}'
```

If we see `404 route not found`, check the URL path and make sure the HTTPRoute is attached to the correct Gateway.

If a route is not accepted, check its parent reference and the Gateway listener's allowed namespaces. If a backend reference cannot be resolved, check the backend name and namespace.

If a provider says the model is unavailable, check that the model is available to your API account.

```text
$ kubectl describe httproute provider-routing -n agentgateway-system
# Check the route's parent status for:
# Accepted=True
# ResolvedRefs=True

# If a request returns "404 route not found":
# Check the route path and its parent Gateway.
```

## 8. Review and clean up

Today we learned how a Gateway, an HTTPRoute, and an AgentgatewayBackend work together. We also sent requests to two providers through path-based routes.

When you finish the lab, delete the Kind cluster created for this lesson. This removes its Kubernetes resources, including the Secrets.

```shell
$ kind delete cluster --name gatewayapi
Deleting cluster "gatewayapi" ...
```

Thank you for joining. You can repeat the lab and change the route paths or provider configuration to explore further.
