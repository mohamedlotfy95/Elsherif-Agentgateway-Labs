[Documentation](https://gateway-api.sigs.k8s.io/)

## We need a Kubernetes cluster

Let's create a Kubernetes cluster to play with, using [kind](https://kind.sigs.k8s.io/docs/user/quick-start/):

```shell
kind create cluster --name gatewayapi --image kindest/node:v1.34.0
```

Test your cluster and make sure `kubectl` is configured for it:

> This creates a one-node Kubernetes cluster that we can use for testing.

```shell
kubectl get nodes
```

```
NAME                       STATUS   ROLES           AGE   VERSION
gatewayapi-control-plane   Ready    control-plane   40s   v1.34.0
```

> AgentGateway needs a Kubernetes cluster, but it also needs the "Gateway API."

## Gateway API CRDs

The Kubernetes Gateway API is not installed on Kubernetes by default.
For now, we can install it from the [Gateway API SIG Guide](https://gateway-api.sigs.k8s.io/guides/#installing-gateway-api):

```shell
kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml
```

This installs the following (Standard Channel):

* Gateway Classes: `kubectl get gatewayclass`
* Gateways: `kubectl get gateway`
* HTTP Routes: `kubectl get httproute`

These APIs are part of the Experimental Channel:

* TLS Routes: `kubectl get tlsroute`
* TCP Routes: `kubectl get tcproute`
* UDP Routes: `kubectl get udproute`

---

## Install AgentGateway

AgentGateway is distributed as two Helm charts: one for its CRDs and one for the control plane.

To find the version you want, check the [AgentGateway GitHub Releases page](https://github.com/agentgateway/agentgateway/releases).
For this guide, we will use 1.1.0.

You can also list the Helm chart versions:

```shell
helm show chart oci://cr.agentgateway.dev/charts/agentgateway-crds
helm show chart oci://cr.agentgateway.dev/charts/agentgateway
```

Set the chart version:

```shell
CHART_VERSION="v1.1.0"
```

### Install the CRDs

```shell
helm upgrade -i agentgateway-crds oci://cr.agentgateway.dev/charts/agentgateway-crds \
  --create-namespace \
  --namespace agentgateway-system \
  --version $CHART_VERSION
```

### Install the control plane

```shell
helm upgrade -i agentgateway oci://cr.agentgateway.dev/charts/agentgateway \
  --namespace agentgateway-system \
  --version $CHART_VERSION \
  --set controller.image.pullPolicy=Always \
  --wait
```

### Check the installation

```shell
# Check that the pods are running
kubectl -n agentgateway-system get pods

# Check the logs
kubectl -n agentgateway-system logs -l app.kubernetes.io/name=agentgateway
```