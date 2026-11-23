# Deploying Gateway API and Agentgateway on Kubernetes

[Gateway API documentation](https://gateway-api.sigs.k8s.io/)

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

## 4. Agentgateway Deployment Modes

According to the [Agentgateway documentation](https://agentgateway.dev/docs/), Agentgateway can be deployed in two ways:

1. **Standalone:** Run the Agentgateway binary or a Docker container on a local machine or server. This approach is suitable for development, testing, and standalone deployments.

2. **On Kubernetes:** Deploy Agentgateway to Kubernetes and manage its configuration through the built-in control plane and Kubernetes Gateway API.

### Example: Gateway Resource

The following example is taken from the official [Kubernetes Gateway API documentation](https://kubernetes.io/docs/concepts/services-networking/gateway/#api-kind-gateway).

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: example-gateway
  namespace: example-namespace
spec:
  gatewayClassName: example-class
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      hostname: "www.example.com"
      allowedRoutes:
        namespaces:
          from: Same
```

> Before applying this example, make sure the referenced `GatewayClass` and namespace exist.

### Deploy the Gateway

The following Gateway listens for HTTP traffic and allows routes from any namespace:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: agentgateway
  namespace: default
spec:
  gatewayClassName: agentgateway
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: All
```

Apply the manifest and verify the Gateway and its service:

```shell
kubectl apply -f docs/agent-gateway/kubernetes/manifests/gateway.yaml
kubectl get pods
kubectl get services
kubectl get gateway

# Kind does not provide a LoadBalancer by default, so use port-forwarding.
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
  name: google-secret
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

```
NAME                       TYPE     DATA   AGE
google-secret              Opaque   1      102s
```

Create an `AgentgatewayBackend` resource that configures the Gemini provider and references the API key Secret:

```shell
kubectl apply -f - <<EOF
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayBackend
metadata:
  name: google
  namespace: agentgateway-system
spec:
  ai:
    provider:
      gemini:
        model: gemini-3.5-flash-lite
  policies:
    auth:
      secretRef:
        name: google-secret
EOF
```

Verify that the backend is accepted:

```shell
kubectl get agentgatewaybackends.agentgateway.dev -n agentgateway-system
```

Example output:

```text
NAME     ACCEPTED   AGE
google   True       47s
```

Create an `HTTPRoute` to route incoming requests to the `AgentgatewayBackend`.

> Agentgateway rewrites the endpoint to the chat completions endpoint appropriate for the configured provider.

```shell
kubectl apply -f - <<EOF
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: google
  namespace: agentgateway-system
spec:
  parentRefs:
    - name: agentgateway
      namespace: default
  rules:
    - backendRefs:
        - name: google
          namespace: agentgateway-system
          group: agentgateway.dev
          kind: AgentgatewayBackend
EOF
```

### Example: Route to providers by path

Use separate `HTTPRoute` rules to send requests under `/ai/gemini` to the Gemini backend and requests under `/ai/claude` to the Claude backend. This example assumes an `AgentgatewayBackend` named `claude` already exists in the `agentgateway-system` namespace.

> follow here to create the [Anthropic](https://agentgateway.dev/docs/kubernetes/latest/integrations/llm/providers/anthropic/) AgentgatewayBackend 
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
        - name: google
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

Send a chat completion request through the port-forward:

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