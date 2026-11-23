# Gateway API and Agentgateway on Kubernetes

[Gateway API Documentation](https://gateway-api.sigs.k8s.io/)

## 1. Create a Kubernetes Cluster

Let's create a Kubernetes cluster for testing using [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/):

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

> This creates a single-node Kubernetes cluster that we can use for testing.

### Optional: kubectl Autocomplete

For more details, see the [kubectl Quick Reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/#kubectl-autocomplete).

For Bash, enable autocomplete and create a short `k` alias:

```shell
source <(kubectl completion bash)
alias k=kubectl
complete -o default -F __start_kubectl k
```

> **Note:** Agentgateway requires a running Kubernetes cluster and the Kubernetes Gateway API CRDs to be installed.

## 2. Install Gateway API CRDs

The Kubernetes Gateway API is not installed by default in Kubernetes.

Install the Standard Channel CRDs by following the [Gateway API installation guide](https://gateway-api.sigs.k8s.io/guides/#installing-gateway-api):

```shell
kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml
```

This installs the following resources (Standard Channel):

- GatewayClasses: `kubectl get gatewayclass`
- Gateways: `kubectl get gateway`
- HTTPRoutes: `kubectl get httproute`

The following resources are part of the Experimental Channel and are not included in the Standard Channel installation:

- TLSRoutes: `kubectl get tlsroute`
- TCPRoutes: `kubectl get tcproute`
- UDPRoutes: `kubectl get udproute`

## 3. Install Agentgateway

Agentgateway is distributed through two Helm charts:

1. **CRDs chart:** Installs the custom resource definitions required by Agentgateway.
2. **Control plane chart:** Deploys the control plane pods responsible for watching and reconciling Kubernetes Gateway API resources, as well as Agentgateway-specific resources.

To select the version you want to install, check the [Agentgateway GitHub Releases](https://github.com/agentgateway/agentgateway/releases).

For this guide, we will use version `v1.1.0`.

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

```shell
k get gatewayclasses.gateway.networking.k8s.io 
```
here where you define wht gateways can be implemented. so you can controll what gateways can be implemented in your cluster. 

Check the control plane logs:

```shell
kubectl -n agentgateway-system logs -l app.kubernetes.io/name=agentgateway
```

## 4. Agentgateway Deployment Modes

According to the [Agentgateway documentation](https://agentgateway.dev/docs/), Agentgateway can be deployed in two ways:

1. **Standalone:** Run the Agentgateway binary or a Docker container on your local machine or server. This approach is suitable for development, testing, and standalone deployments.

2. **On Kubernetes:** Deploy Agentgateway on Kubernetes and manage its configuration dynamically through the built-in control plane and Kubernetes Gateway API.

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

> Note: Before applying it, ensure that the referenced `GatewayClass` exists and that the target namespace is created.



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
