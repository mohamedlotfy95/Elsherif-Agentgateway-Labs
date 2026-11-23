# Deploying Gateway API and Agentgateway on Kubernetes

[Gateway API documentation](https://gateway-api.sigs.k8s.io/)

## Learning goals

By the end of this lab, you will be able to:

- Explain how a Gateway, HTTPRoute, and AgentgatewayBackend work together.
- Deploy Agentgateway on a local Kubernetes cluster.
- Configure Gemini and Anthropic backends and route requests to each by URL path.

## Prerequisites

- Docker, Kind, `kubectl`, Helm, `curl`, and `jq`
- Gemini and Anthropic API keys
- Basic familiarity with Kubernetes resources, namespaces, and Secrets

## 1. Create a Kubernetes Cluster

Create a test Kubernetes cluster with [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/):

```shell
kind create cluster --name gatewayapi --image kindest/node:v1.34.0
```

Verify that the cluster is running and that `kubectl` is configured correctly:

```shell
kubectl get nodes
```

Expected output:

```text
NAME                       STATUS   ROLES           AGE   VERSION
gatewayapi-control-plane   Ready    control-plane   40s   v1.34.0
```

> This command creates a single-node Kubernetes cluster for testing.

### Optional: kubectl Autocomplete

For details, see the [kubectl Quick Reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/#kubectl-autocomplete).

For Bash, enable autocomplete and create a short `k` alias:

```shell
source <(kubectl completion bash)
alias k=kubectl
complete -o default -F __start_kubectl k
```

> **Note:** Agentgateway requires a running Kubernetes cluster and the Kubernetes Gateway API CRDs to be installed.

## 2. Install Gateway API CRDs

The Kubernetes Gateway API is not installed by default.

Install the Standard Channel CRDs by following the [Gateway API installation guide](https://gateway-api.sigs.k8s.io/guides/#installing-gateway-api):

```shell
kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml
```

The Standard Channel includes these resources:

- GatewayClasses: `kubectl get gatewayclasses`
- Gateways: `kubectl get gateways`
- HTTPRoutes: `kubectl get httproutes`

The following resources are part of the Experimental Channel and are not included in the Standard Channel installation:

- TLSRoutes: `kubectl get tlsroutes`
- TCPRoutes: `kubectl get tcproutes`
- UDPRoutes: `kubectl get udproutes`

## 3. Install Agentgateway

Agentgateway is distributed through two Helm charts:

1. **CRDs chart:** Installs the custom resource definitions required by Agentgateway.
2. **Control plane chart:** Deploys the pods that watch and reconcile Kubernetes Gateway API and Agentgateway resources.

Choose a version from the [Agentgateway GitHub releases](https://github.com/agentgateway/agentgateway/releases).

This guide uses version `v1.1.0`.

You can also inspect the available Helm chart metadata:

```shell
helm show chart oci://cr.agentgateway.dev/charts/agentgateway-crds
helm show chart oci://cr.agentgateway.dev/charts/agentgateway
```

Set the chart version:

```shell
CHART_VERSION="v1.1.0"
```

### 3.1. Install the CRDs

```shell
helm upgrade -i agentgateway-crds oci://cr.agentgateway.dev/charts/agentgateway-crds \
  --create-namespace \
  --namespace agentgateway-system \
  --version $CHART_VERSION
```

### 3.2. Install the Control Plane

The Agentgateway control plane consists of pods that watch and reconcile Gateway API objects and Agentgateway-specific custom resources.

These components observe the Kubernetes API and ensure that the deployed gateway configuration reflects the desired state defined by the resources.

```shell
helm upgrade -i agentgateway oci://cr.agentgateway.dev/charts/agentgateway \
  --namespace agentgateway-system \
  --version $CHART_VERSION \
  --set controller.image.pullPolicy=Always \
  --wait
```

### 3.3. Verify the Installation

Check that the Agentgateway pods are running:

```shell
kubectl -n agentgateway-system get pods
```

List the available GatewayClasses:

```shell
kubectl get gatewayclasses.gateway.networking.k8s.io
```

GatewayClasses define which gateway implementations are available in the cluster.

Check the control plane logs:

```shell
kubectl -n agentgateway-system logs -l app.kubernetes.io/name=agentgateway
```

## 4. Deploy the Gateway

The [Gateway manifest](manifests/gateway.yaml) creates an HTTP listener in the `default` namespace and allows routes from any namespace.

Apply it and check the Gateway status:

```shell
kubectl apply -f docs/agent-gateway/kubernetes/manifests/gateway.yaml
kubectl get gatewayclass agentgateway
kubectl get gateway agentgateway -n default
kubectl get services -n default
```

The Gateway should report `Accepted=True` and `Programmed=True`. Start a port-forward in a separate terminal and leave it running while you test requests:

```shell
kubectl -n default port-forward svc/agentgateway 8080:80
```

## 5. Configure Gemini

Follow the [Gemini provider guide](https://agentgateway.dev/docs/kubernetes/latest/integrations/llm/providers/gemini/#set-up-access-to-gemini) to create an API key, then set it in an environment variable:

```shell
export GOOGLE_KEY="<your-gemini-api-key>"
```

Create a Kubernetes Secret containing the key:

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

Verify that the Secret was created:

```shell
kubectl get secrets -n agentgateway-system
```

Example output:

```text
NAME                       TYPE     DATA   AGE
gemini-secret              Opaque   1      102s
```

Create an `AgentgatewayBackend` resource that configures the Gemini provider and references the API key Secret:

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

Verify that the backend is accepted:

```shell
kubectl get agentgatewaybackends.agentgateway.dev -n agentgateway-system
```

Example output:

```text
NAME     ACCEPTED   AGE
gemini   True       47s
```

## 6. Configure Claude

Follow the [Anthropic provider guide](https://agentgateway.dev/docs/kubernetes/latest/integrations/llm/providers/anthropic/) to create an API key, then store it in an environment variable:

```shell
export ANTHROPIC_API_KEY="<your-anthropic-api-key>"
```

Create a Secret for the API key. The gateway uses it to authenticate with Anthropic:

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

## 7. Route requests to providers

### Basic route to Gemini

An `HTTPRoute` connects a Gateway listener to a backend. With no path matches, this rule sends all requests to Gemini; use it as a simple starting point.

> Agentgateway rewrites the endpoint to the chat completions endpoint appropriate for the configured provider.

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

### Route by URL path

This second route sends requests under `/ai/gemini` to Gemini and requests under `/ai/claude` to Claude. `PathPrefix` also matches paths nested under each prefix.

You can keep the basic Gemini route as a fallback. When both routes are attached to the Gateway, the more-specific path matches in this route take precedence for `/ai/gemini` and `/ai/claude`.

The route assumes both backends have been created and accepted in `agentgateway-system`.

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

Check that the route is accepted and its backend references are resolved:

```shell
kubectl describe httproute provider-routing -n agentgateway-system
```

Look for `Accepted=True` and `ResolvedRefs=True` under the route's parent status. Use the [curl examples](curl-examples.md) to test each provider path.

## 8. Troubleshoot common issues

| Symptom | What to check |
| --- | --- |
| `404 route not found` | The request path matches a route rule, and the HTTPRoute is attached to `default/agentgateway`. |
| HTTPRoute is not accepted | Check the Gateway listener's `allowedRoutes`, the HTTPRoute `parentRefs`, and the conditions in `kubectl describe httproute`. |
| Backend reference is unresolved | Confirm the `AgentgatewayBackend` exists in `agentgateway-system` and is accepted. |
| Provider reports that a model is unavailable | Check that the model configured in the backend is available to your API account. |
| Port-forward cannot connect | Confirm the `agentgateway` Service exists in `default` and the port-forward command is still running. |

## 9. Clean up

This removes the Kind cluster created in step 1, including its Kubernetes resources and Secrets:

```shell
kind delete cluster --name gatewayapi
```
