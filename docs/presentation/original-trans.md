# Chapter 1: Intro

In many companies, users call large language models directly, and AI agents do the same. This usually means many API keys for many providers. It also means limited visibility, weak monitoring, and weaker security.

What if we placed one gateway in front of all AI systems?

This would give us one endpoint, one set of central API keys, traffic visibility, and monitoring. This is what Agent Gateway provides.

In this video, we will cover what Agent Gateway is, why it is useful, and how it works. We will install it on a Kubernetes cluster, configure it, and learn how to route traffic to different language models.

Let's begin.

Chapter 2: What is Agent Gateway

Agent Gateway is an infrastructure gateway for AI systems. It acts like a reverse proxy in front of all AI services.

It helps you connect, secure, and monitor AI infrastructure.

It can sit in front of language models and route requests to cloud providers or local models.

It can work as an MCP router, routing traffic to internal or external MCP servers.

It can also manage traffic between AI agents. This makes Agent Gateway another layer for security and monitoring.

Agent Gateway is open source on GitHub under the Apache 2.0 license.

On GitHub, you can find a video that explains the differences between Agent Gateway and a normal gateway.

If you use the Kubernetes Gateway API, you may know gateways such as NGINX Gateway Fabric, kgateway, Envoy Gateway, Istio, or Linkerd.

The main difference is that normal HTTP traffic is usually stateless.

Chapter 3: The LLM Gateway

Normal HTTP gateways route traffic by URL path and sometimes by headers. They may also balance traffic across several backend services.

This approach has limits in AI workflows.

An AI gateway may need to inspect the HTTP request body to choose a language model, rather than using only the URL.

It may also need to understand an agent-to-agent conversation. It should not send an agent's request to a random agent. It should know which agent sessions are connected.

The gateway should be aware of the session between Agent A and Agent B.

When routing traffic to MCP servers, the gateway may need to know which tools each server provides.

It may need to collect those tools and present them to the client in a useful way.

Agent Gateway has many features. In this video, we will focus on its LLM gateway features.

Chapter 4: Challenge using HTTP Gateways

These features let applications switch providers without changing their code.

The gateway can route requests to OpenAI, Anthropic, Gemini, Google AI, Amazon, and other providers.

It also works with most OpenAI-compatible providers through chat completions and streaming responses.

If you use Kubernetes Gateway API, you can manage this traffic with normal Gateway API resources.

Chapter 5: LLM Gateway Overview

On this channel, you can find a Gateway API playlist. It includes an introduction and videos about several gateway implementations.

Agent Gateway uses Kubernetes Gateway API resources, so it is important to understand Gateway API for this video.

Chapter 6: The Gateway API Series

To start, we need a Kubernetes cluster. In my Gateway API introduction, I showed how to create a cluster with kind.

Let's copy that command and run it in the terminal.

It creates a one-node Kubernetes cluster for testing.

Run `kubectl get nodes` to confirm that the node is ready.

Chapter 7: Create a Kubernetes Cluster

Agent Gateway also needs the Gateway API custom resource definitions, or CRDs.

We can get these from the Gateway API guide or from their GitHub repository.

We will use the Gateway API 1.4 CRDs.

Run `kubectl apply` to install them.

We can then use commands for Gateway, GatewayClass, HTTPRoute, TLSRoute, TCPRoute, and UDPRoute.

Chapter 8: Gateway API CRDs

Scroll to the tutorial section on the Agent Gateway website.

The tutorials cover a standalone installation and Kubernetes installations for LLM and MCP routing.

The documentation also explains how to install Agent Gateway with Helm, Argo CD, and Flux.

In this video, we will use Helm and install the gateway in our local cluster.

Chapter 9: The Docs

Agent Gateway is easy to install with Helm.

It uses one chart for the CRDs and one chart for the control plane.

When this video was recorded, we used chart version 1.1.0.

You can check chart versions with `helm show chart`.

Save the version in an environment variable.

Then install the CRD chart and the control plane chart.

Chapter 10: Installation

The CRD chart adds Agent Gateway resources to the cluster.

Next, install the control plane.

The control plane watches Gateway API and Agent Gateway resources.

It also creates the proxy that receives traffic.

After the installation, clear the terminal and find a namespace called `agent-gateway-system`.

This namespace contains the control plane.

The control plane watches resources such as GatewayClass, Gateway, and HTTPRoute. It creates the matching data plane, just like a normal Gateway API implementation.

Chapter 11: Gateway Class

The first resource Agent Gateway creates is a GatewayClass.

A GatewayClass is a YAML resource that infrastructure engineers use to control which gateways can run in a cluster.

Engineers can choose gateways such as NGINX Gateway Fabric, kgateway, Envoy Gateway, or Agent Gateway.

If this guide is useful, please like and subscribe so you do not miss the next episode.

Chapter 12: Gateways

In the Gateway API series, we explained that a Gateway is a YAML object.

A Gateway describes how traffic enters the cluster and which GatewayClass it uses.

In this example, the Gateway uses Agent Gateway.

It can also define the number of proxy replicas, the load balancer type, and other settings.

The Gateway is in the `default` namespace and is named `agent-gateway`.

It uses the `agent-gateway` GatewayClass and listens on port 80.

It allows HTTPRoutes to attach to it.

Install the Gateway by applying its YAML file.

Check the Gateway status with `kubectl get gateway`.

Make sure that the Gateway is accepted.

A data plane pod and service should appear. The pod has one replica, and the service uses the load balancer type by default.

You can change the replica count, load balancer type, and other settings with Gateway parameters.

Kind does not provide a load balancer, so we will use port forwarding.

The port-forward command sends local port 80 traffic to the Gateway API service.

Leave this command running while testing.

Chapter 13: Agent Gateway Backends

Agent Gateway has a few interesting features.

In Gateway API, you usually route traffic to Kubernetes Services, external URLs, or internal URLs.

Agent Gateway can also use MCP servers, agents, and LLM providers as backends.

A backend can be a provider such as Gemini or Claude. It can also be a local LLM in or outside the Kubernetes cluster.

The setup follows a similar pattern.

Create a Kubernetes Secret that contains the provider API key.

Then create an Agent Gateway Backend and attach it to the Gateway with an HTTPRoute.

Chapter 14: LLM Routing

This is how Agent Gateway performs LLM routing.

The CRD chart adds a resource called `AgentGatewayBackend`.

This resource represents an LLM provider as a routable backend.

In this example, we will create a backend for Gemini.

First, get a Gemini API key from Google AI Studio.

Then create a Kubernetes Secret for the key.

This Secret will be used when traffic is routed to the Gemini backend.

A Gateway normally needs an upstream Kubernetes Service.

Agent Gateway uses an `AgentGatewayBackend` instead.

Chapter 15: Creating a Backend

An `AgentGatewayBackend` has a name and a `spec`.

The `spec` contains the AI provider name and the default model.

It also contains authentication settings that reference the Secret.

Apply the backend with `kubectl apply`.

Use `kubectl get` to confirm that the backend was accepted.

You can use `kubectl describe` to troubleshoot it.

Chapter 16: HTTP Route

Next, create an HTTPRoute to send traffic to the backend.

The HTTPRoute is attached to the Gateway.

It sends all traffic on that Gateway to the Gemini backend.

Apply the HTTPRoute and check it with `kubectl get httproute`.

Chapter 17: Testing HTTPRoute

Test the route with `curl` on `localhost:8080`.

The route sends traffic to Gemini for every path.

Send a prompt that asks, "What is Kubernetes in one sentence?"

The Gemini model returns an answer.

The response may also include token usage details.

This setup is useful, but it sends every request to one provider.

Chapter 18: Route by Path

In real applications, we may need to route by URL path.

Update the existing HTTPRoute while keeping the same Gateway.

Create rules that control which paths are accepted.

Requests to `/ai/gemini` will have that prefix removed before they reach Gemini.

This gives us control over the public URL.

Apply the updated route and test it.

The Gateway can now send requests to different models based on their paths.

Chapter 19: Route to other Models

We can also route to several providers through one endpoint.

The same method can create an Anthropic backend.

Create an API key and a Secret for Anthropic.

Save the Anthropic API key in an environment variable.

Create the Kubernetes Secret, as we did for Gemini.

Now define an `AgentGatewayBackend` named `anthropic`.

Set the provider, default model, and authentication Secret.

Apply the backend and check both backends with `kubectl get`.

Update the existing HTTPRoute with two rules.

The first rule sends `/ai/claude` traffic to the Anthropic backend.

It removes the `/ai/claude` prefix before forwarding the request.

The second rule sends `/ai/gemini` traffic to the Gemini backend.

It removes the `/ai/gemini` prefix before forwarding the request.

Apply the updated HTTPRoute.

Requests to `/ai/gemini` now use Gemini Flash.

Requests to `/ai/claude` now use Claude Sonnet.

Send a request to the Claude endpoint with `curl`.

Claude Sonnet returns the answer and token details.

This may look like normal Gateway API URL routing.

However, Agent Gateway can also inspect the HTTP request body and use token information.

It becomes more useful for MCP routing and agent-to-agent traffic.

These features go beyond what standard HTTP gateways typically support.

Chapter 20: The Source Code

The source code for this series is available in the GitHub repository linked in the description.

In the repository, open the Kubernetes folder and then the Gateway API folder.

Agent Gateway examples are in the `agent-gateway` folder.

The README explains the installation and LLM routing steps shown in this video.

Follow the link in the description to try the examples.

In a later video, we will look at MCP routing.

MCP servers are becoming more common. DevOps engineers will need to manage MCP servers and route their traffic in Kubernetes.

Check out the Ultimate DevOps Roadmap and course if you want to start learning DevOps.

If you want to support the channel, join as a YouTube member.

Thanks for watching. See you next time.
