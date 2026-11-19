## What is an Agent Gateway?

An **Agent Gateway** is a single entry point that sits between your users/AI agents and the LLM models.

**The Problem**
When users and AI agents call LLM models directly:
* **No Visibility:** You cannot easily see who is making requests or how many tokens are being used.
* **No Observability:** It is hard to track errors, slow responses, or agent behavior.
* **Security Risks:** API keys are spread across different apps and agents, making them hard to protect and manage.
```text
[User] -------------> [OpenAI]      (No Visibility)
[Mobile App] -------> [Anthropic]   (No Security)
[AI Agent] ---------> [Gemini]      (Unmanaged Traffic)
[Automated Script] -> [Llama 3]     (Fragmented API Keys)
```
**The Solution**
An Agent Gateway gives you **one single endpoint** for all LLM requests. From one central place, you get:
* **Centralized API Keys:** Store and manage all your LLM keys safely in one spot.
* **Traffic Control:** Manage rate limits, route requests, and switch models easily.
* **Visibility & Observability:** Monitor usage, costs, logs, and performance in real time.

```text
[User] -------------\
[Mobile App] --------\                                      +--> [OpenAI]
[AI Agent] --------------> [ AGENT GATEWAY ]                +--> [Anthropic]
[Automated Script] --/     (Keys, Logs,Rate Limits)         +--> [Gemini]
                                                            +--> [Llama 3]
```

based on that: All traffic is centralized, logged, secured, and rate-limited.

---

### [Agentgateway](https://github.com/agentgateway/agentgateway) 
is an open source proxy built on AI-native protocols ([MCP](https://modelcontextprotocol.io/introduction) & [A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)) that provides drop-in security, observability, and governance for agent-to-LLM, agent-to-tool, and agent-to-agent communication across any framework and environment.

Official Intro to Agentgateway [Video](https://www.youtube.com/watch?v=SomP92JWPmE)

---

## [Key Features](https://github.com/agentgateway/agentgateway#key-features) 

It acts like a gateway for your infrastructure, think of it like a **reverse proxy** that sits in front of your AI system.

Here is what you get:

1. **LLM Gateway:** Route traffic to major LLM models with budget and spend controls through one unified, OpenAI-compatible API.
2. **Inference Routing:** Intelligently route traffic to your self-hosted models or local LLM workloads.
3. **MCP Gateway:** Connect your LLMs to tools, external data sources, and internal or external MCPs.
4. **A2A (Agent-to-Agent):** Enable secure, standardized communication and task handoffs between different AI agents.
5. **Security:** Protect your AI system with centralized API keys, authentication, rate limiting, and access control.