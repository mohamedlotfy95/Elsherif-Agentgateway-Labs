## What is an Agent Gateway?

An **Agent Gateway** is a single entry point that sits between your users/AI agents and the LLM models.

**The Problem**
When users and AI agents call LLM models directly:
- **No Visibility:** You cannot easily see who is making requests or how many tokens are being used.
- **No Observability:** It is hard to track errors, slow responses, or agent behavior.
- **Security Risks:** API keys are spread across different apps and agents, making them hard to protect and manage.

```text
[User] -------------> [OpenAI]      (No Visibility)
[Mobile App] -------> [Anthropic]   (No Security)
[AI Agent] ---------> [Gemini]      (Unmanaged Traffic)
[Automated Script] -> [Llama 3]     (Fragmented API Keys)
```

**The Solution**
An Agent Gateway gives you **one single endpoint** for all LLM requests. From one central place, you get:
- **Centralized API Keys:** Store and manage all your LLM keys safely in one spot.
- **Traffic Control:** Manage rate limits, route requests, and switch models easily.
- **Visibility & Observability:** Monitor usage, costs, logs, and performance in real time.

```text
[User] -------------\                                  +--> [OpenAI]
[Mobile App] --------\                                 +--> [Anthropic]
[AI Agent] ------------> [ AGENT GATEWAY ] ------------+--> [Gemini]
[Automated Script] --/   (Keys, Logs, Rate Limits)     +--> [Llama 3]
```

**Result:** All traffic is centralized, logged, secured, and rate-limited.

---

### [Agentgateway](https://github.com/agentgateway/agentgateway)
An open-source proxy built on AI-native protocols ([MCP](https://modelcontextprotocol.io/introduction) & [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)) that provides drop-in security, observability, and governance for agent-to-LLM, agent-to-tool, and agent-to-agent communication across any framework and environment.

---

## Key Features

Think of it like a gateway for your infrastructure that sits in front of your AI system. Here is what you get:

1. **LLM Gateway:** Route traffic to major LLM models with budget and spend controls through one unified, OpenAI-compatible API.
2. **Inference Routing:** Intelligently route traffic to your self-hosted models or local LLM workloads.
3. **MCP Gateway:** Connect your LLMs to tools, external data sources, and internal or external MCPs.
4. **A2A (Agent-to-Agent):** Enable secure, standardized communication and task handoffs between different AI agents.
5. **Security:** Protect your AI system with centralized API keys, authentication, rate limiting, and access control.

Ref: Official [repo](https://github.com/agentgateway/agentgateway#key-features)

---

### Agent Gateway vs. Traditional Gateways
Official intro video: [Introducing Agent Gateway: AI-Native Connectivity & Security](http://www.youtube.com/watch?v=SomP92JWPmE)

This video explains the key differences between an Agent Gateway and traditional gateways/reverse proxies (like NGINX, Envoy, and Traefik)—specifically why **stateful** protocols and **multiplexing** across tools (MCP) and long-running agent tasks (A2A) need a purpose-built data plane [[02:46](https://www.youtube.com/watch?v=SomP92JWPmE&t=166)], [[06:29](https://www.youtube.com/watch?v=SomP92JWPmE&t=389)], [[07:52](https://www.youtube.com/watch?v=SomP92JWPmE&t=472)], [[09:49](https://www.youtube.com/watch?v=SomP92JWPmE&t=589)], [[10:13](https://www.youtube.com/watch?v=SomP92JWPmE&t=613)].

## Challenges

Traditional gateways (like NGINX, Envoy, and Traefik) are built for standard web traffic, and general HTTP traffic is considered stateless. This creates challenges for AI systems:

1. **Limits of Basic HTTP Routing:** Regular gateways usually route traffic based only on the URL path or headers. AI workflows often need routing based on what is inside the HTTP body (such as model names or prompts).
2. **Session Awareness (Agent-to-Agent):** Standard load balancers send traffic to random servers. When Agent A talks to Agent B, the gateway must be session-aware so requests stay connected to the right agent.
3. **Smart MCP Tool Discovery:** When connecting to multiple internal MCP servers, the gateway needs to discover available tools across them and present them cleanly to the client.

> **Note:** **Stateless** treats each request on its own without remembering past interactions, while **stateful** keeps context or session history across requests and ongoing tasks.

