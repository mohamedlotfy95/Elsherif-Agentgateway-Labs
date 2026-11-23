# Agentgateway overview

## What is an agent gateway?

An **agent gateway** is a proxy that can provide a managed entry point between applications or agents and AI providers. The capabilities available depend on the gateway product and how it is configured.

### Why use one?

When applications and agents call providers directly, each client may need its own provider configuration and credentials. This can make it harder to apply consistent controls, understand usage, and investigate failures.

```text
[User] -------------> [OpenAI]      (Limited visibility)
[Mobile App] -------> [Anthropic]   (Credentials managed per client)
[AI Agent] ---------> [Gemini]      (Unmanaged Traffic)
[Automated Script] -> [Llama 3]     (Fragmented API Keys)
```

An agent gateway can give clients a common endpoint and central place to configure provider access. Depending on the implementation and policies enabled, it can provide:

- **Centralized credentials:** Keep provider credentials out of individual clients. Protecting them still requires appropriate Secret access controls and cluster security.
- **Traffic controls:** Configure request routing, rate limits, and model selection where supported.
- **Observability:** Collect request, usage, and performance data when telemetry is configured.

These controls are not automatic; they must be enabled and configured for the deployment.

```text
[User] -------------\                                  +--> [OpenAI]
[Mobile App] --------\                                 +--> [Anthropic]
[AI Agent] ------------> [ AGENT GATEWAY ] ------------+--> [Gemini]
[Automated Script] --/   (Policies and telemetry)      +--> [Llama 3]
```

**Result:** With the relevant credentials, policies, and telemetry configured, requests can be managed through a common gateway.

---

### [Agentgateway](https://github.com/agentgateway/agentgateway)

Agentgateway is an open-source proxy for AI and agent traffic. It supports integrations for protocols such as [MCP](https://modelcontextprotocol.io/introduction) and [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/). See the [official project documentation](https://agentgateway.dev/docs/) for supported features and configuration requirements.

---

## Key Features

Depending on the configured deployment, Agentgateway can provide features such as:

1. **LLM routing:** Route requests to supported providers through compatible APIs.
2. **Inference routing:** Route traffic to supported self-hosted or local model backends.
3. **MCP connectivity:** Connect agents to configured MCP servers and tools.
4. **A2A connectivity:** Support communication between agents using the A2A protocol.
5. **Policy enforcement:** Apply configured authentication, rate limits, and access controls.

Check the [official feature list](https://github.com/agentgateway/agentgateway#key-features) for current capabilities and requirements.

---

### Agent gateways and traditional gateways

Watch the official introduction: [Introducing Agent Gateway: AI-Native Connectivity & Security](https://www.youtube.com/watch?v=SomP92JWPmE).

Traditional gateways can handle many HTTP routing tasks, and some can be extended for AI workloads. An agent gateway may offer AI-provider integrations or protocol-specific features without requiring the same custom extensions. Compare products by the protocols, policies, and observability they support rather than assuming a traditional gateway cannot provide them.

AI requests also do not automatically make a connection stateful. Conversation history is commonly sent by the client with each request; streaming, session affinity, or other stateful behavior depends on the application and gateway configuration.

## LLM Gateway Overview

An LLM gateway can let applications use a consistent client interface while the gateway routes requests to configured providers. Provider-specific features and request compatibility vary.

Agentgateway supports integrations for providers such as **OpenAI**, **Anthropic**, and **Gemini**. Consult the [provider documentation](https://agentgateway.dev/docs/kubernetes/latest/integrations/llm/providers/) for supported APIs, models, and setup details.
