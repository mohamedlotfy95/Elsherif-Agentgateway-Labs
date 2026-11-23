# Tech with Lotfy

Learning material and hands-on examples for cloud-native AI infrastructure.

## Agentgateway learning path

This workshop is for learners who know the basics of Kubernetes and want to deploy an AI gateway on a local cluster. By the end, you will be able to explain the gateway's role, deploy it on Kind, connect Gemini and Anthropic backends, and route requests by URL path.

### Prerequisites

- Docker, Kind, `kubectl`, Helm, `curl`, and `jq`
- API keys for Gemini and Anthropic
- Familiarity with Kubernetes namespaces, Secrets, and Services
- Run the command examples from the repository root; do not commit API keys.

### Lessons

1. [Understand the gateway and its responsibilities](docs/agent-gateway/overview.md).
2. [Create a Kind cluster, install Agentgateway, and configure provider backends and routes](docs/agent-gateway/kubernetes/create-cluster.md).
3. [Test Gemini and Claude path-based routing](docs/agent-gateway/kubernetes/curl-examples.md).

The [Gateway manifest](docs/agent-gateway/kubernetes/manifests/gateway.yaml) is applied in the Kubernetes setup guide.

## Documentation checks

The GitHub Actions workflow runs Markdown style checks, link checks, YAML parsing, and shell syntax checks for the examples. To run the same checks locally, install Python 3, Bash, Node.js, PyYAML, `markdownlint-cli2`, and [lychee](https://lychee.cli.rs/), then run:

```shell
python -m pip install PyYAML
npm install --global markdownlint-cli2@0.18.1
markdownlint-cli2
lychee --no-progress --max-retries 2 README.md docs
python scripts/check_docs.py
```

The shell examples are syntax-checked only; they are not executed.
