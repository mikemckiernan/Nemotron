<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-discover-the-step)=
# Discover The Model Evaluation Step

This guide shows how to find `eval/model_eval` in the step catalog, how to read its contract, and how to decide whether it applies to a given task.

## Prerequisites

- The Nemotron repository synced with `uv sync` complete.
- A local checkout is sufficient for this guide.
  The discovery commands read the local step catalog only, so no network access is required.

## List Eval-Category Steps

Use `nemotron steps list` to enumerate the available steps.
The `--category eval` flag filters the catalog to evaluation steps, and the `--json` flag returns a machine-readable response.

```bash
uv run --no-sync nemotron steps list --category eval --json
```

The response includes one entry per evaluation step.
`eval/model_eval` is the entry that wraps NeMo Evaluator.

## Inspect The Step Contract

Use `nemotron steps show` to print the full step contract from `step.toml`.

```bash
uv run --no-sync nemotron steps show eval/model_eval --json
```

The response contains the fields the contract declares.

| Field | What It Tells You |
| --- | --- |
| `consumes` | Input artifact types the step accepts.  This step accepts `checkpoint_megatron` or `checkpoint_hf`, both optional. |
| `produces` | Output artifact type.  This step produces `eval_results`. |
| `parameters` | Documented parameters.  `benchmarks` is the only parameter, with a metadata default. |
| `strategies` | When-then rules for endpoint type, tokenizer, and reasoning models. |
| `errors` | Named failure modes with recovery guidance, such as `missing_tokenizer_for_logprobs`. |
| `reference` | Upstream documentation and reference example URLs. |

Read `src/nemotron/steps/eval/model_eval/step.toml` in the repository when you need the contract verbatim, including the strategies and error recoveries.

## Read The Sample Files

The step provides two sample configuration files under `src/nemotron/steps/eval/model_eval/config/`.

```{literalinclude} ../../../src/nemotron/steps/eval/model_eval/config/tiny.yaml
:language: yaml
```

The sample `tiny.yaml` file runs one *log-probability* benchmark, `hellaswag`, with `params.limit_samples` set to `20`.
Use it to confirm the endpoint, the credential, and the tokenizer configuration before scaling up.

```{literalinclude} ../../../src/nemotron/steps/eval/model_eval/config/default.yaml
:language: yaml
```

The sample `default.yaml` file runs `mmlu`, `hellaswag`, and `arc_challenge` with `params.limit_samples` set to `null`, which means no cap.

The {doc}`../reference/config-schema` reference documents every field.

## Decide Whether It Applies

`eval/model_eval` applies when the following statements are true.

- The model is already deployed behind an OpenAI-compatible *endpoint*, or you are prepared to deploy it as part of the run.  This step does not deploy checkpoints.
- The benchmarks you need are implemented by NeMo Evaluator or one of the harnesses it integrates with.
- The endpoint type matches the benchmark family.  Chat benchmarks need a chat endpoint, and *log-probability* benchmarks need a completions endpoint with `logprobs` support.

`eval/model_eval` is not the right step when the evaluation needs a custom scorer that NeMo Evaluator does not implement.
Write a dedicated evaluation step in that case, modeled on the contract layout under `src/nemotron/steps/`.

## Related

- `src/nemotron/steps/eval/model_eval/step.toml` for the full step contract.
- {doc}`run-hosted-evaluation` for the first procedural walk-through after discovery.
- {doc}`../reference/config-schema` for field-by-field YAML reference.
- {doc}`../reference/cli-reference` for the flag and override surface.
