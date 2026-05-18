---
license: Apache-2.0
copyright: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
description: "Why eval/model_eval couples endpoint type to benchmark family, and how the chat versus completions decision is made."
topics: ["Model Evaluation", "Endpoints"]
tags: ["Explanation", "Model Evaluation"]
content:
  type: "Explanation"
  difficulty: "Beginner"
  audience: ["ML Engineer", "Data Scientist"]
---

(model-eval-endpoint-types-and-benchmarks)=
# Endpoint Types And Benchmark Families

The step reads two coupled fields from the `deployment` block: the `endpoint_type` and the URL path inside `url`.
Both fields must agree with the benchmark family for the benchmarks named in the `benchmarks` list.
The step itself does not validate the match.
A mismatch surfaces when NeMo Evaluator dispatches a benchmark, not during the preflight probe.

## Two Endpoint Types

`eval/model_eval` supports two endpoint shapes.

- A *chat endpoint* exposes the path `/v1/chat/completions` and accepts a structured `messages` payload.
  The endpoint returns the assistant's reply as generated text.
- A *completions endpoint* exposes the path `/v1/completions` and accepts a raw prompt string.
  The endpoint returns generated text and, when requested, the per-token log-probabilities of the response.

The configured `endpoint_type` value must match the URL path you place in `deployment.url`.

## Two Benchmark Families

Benchmarks split into two families based on how they score the model.

- *Generation-based* benchmarks issue a prompt to the endpoint and score the produced text against a reference answer, a verifier, or a judge model.
  These benchmarks use a chat endpoint.
- *Log-probability* benchmarks request token-level probabilities from the model for each candidate answer, then select the candidate with the highest likelihood.
  These benchmarks use a completions endpoint with `logprobs` support and require a tokenizer that the run can resolve locally.

## Why The Match Matters

The step does not enforce the matching rule itself.
The `check_endpoint` probe in `src/nemotron/steps/eval/model_eval/step.py` calls NeMo Evaluator with the URL, the endpoint type, and the model identifier only, so it reports reachability and authentication failures but does not see the benchmark list.
When the endpoint type does not match the benchmark family, the failure surfaces later, inside the per-benchmark `evaluate` call from NeMo Evaluator.

The `wrong_endpoint_type` entry in `src/nemotron/steps/eval/model_eval/step.toml` documents this class of mistake and points to the recovery guidance.
That entry is documentation rather than an enforcement check.
For the recovery, refer to {doc}`../reference/troubleshooting`.

## Decision Table

| Benchmark family | Required `endpoint_type` | Required URL shape | Extra requirements |
| --- | --- | --- | --- |
| Chat and instruction benchmarks | `chat` | A chat-completions URL ending in `/v1/chat/completions` | None beyond deterministic generation defaults. |
| Log-probability benchmarks | `completions` | A completions URL ending in `/v1/completions` | A tokenizer that matches the served model and `logprobs` support on the endpoint. |
| Reasoning benchmarks | `chat` | A chat-completions URL ending in `/v1/chat/completions` | Non-deterministic generation parameters from the model card. |

## Reasoning Models

Reasoning benchmarks are the one common reason to deviate from the deterministic defaults.
The `step.toml` strategy entry for reasoning models calls for three changes: a higher `params.max_new_tokens` value to fit the typical chain-of-thought trace, reasoning-trace processing on so the scorer sees the final answer rather than the trace, and model-card temperature and top-p values instead of the deterministic `0` defaults.
Outside of reasoning models, the recommendation is to keep generation deterministic so that scores remain comparable across runs.

## Related Pages

- {doc}`tokenizer-alignment` for the tokenizer side of the log-probability case.
- {doc}`pipeline-overview` for where the endpoint sits in the artifact flow.
- {doc}`../how-to/evaluate-deployed-checkpoint` for choosing an endpoint type in context.
- {doc}`../reference/benchmarks-catalog` for the benchmark identifiers in each family.
- {doc}`../reference/troubleshooting` for the named error modes and their recovery guidance.
