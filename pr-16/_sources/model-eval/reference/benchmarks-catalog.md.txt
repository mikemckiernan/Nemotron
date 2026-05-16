<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-benchmarks-catalog)=
# Benchmarks Catalog

This page catalogs the benchmark identifiers accepted by the `benchmarks` field, grouped by family.
The step does not own these benchmarks.
NeMo Evaluator owns the implementations, and this page is a curated map into the upstream catalog.
Refer to the upstream NeMo Evaluator documentation at <https://docs.nvidia.com/nemo/evaluator/latest/> for the authoritative, version-specific list.

## Naming Convention

Benchmark identifiers come in two shapes.

- A short bare name, such as `mmlu`, `hellaswag`, or `arc_challenge`.  Bare names are common for established benchmarks provided by NeMo Evaluator by default.
- A dotted, harness-qualified name, such as `lm-evaluation-harness.ifeval` or `simple_evals.gpqa_diamond`.  The prefix names the harness that hosts the task, and the suffix names the task within it.

Both types are valid in the `benchmarks` field.
Use the exact identifier published by the harness, because the runner passes it through to NeMo Evaluator unchanged.

## Recommended Starting Sets

The recommended starting sets come from the sample YAML files, which are the source of truth for this step.

| Sample file | `benchmarks` value | When to use |
| --- | --- | --- |
| `default.yaml` | `[mmlu, hellaswag, arc_challenge]` | Initial pass against a deployed checkpoint where you want a mix of multiple-choice knowledge and commonsense reasoning. |
| `tiny.yaml` | `[hellaswag]` | Sample run that exercises the endpoint, tokenizer configuration, and result-writing path with one *log-probability* benchmark. |

## Chat And Instruction Benchmarks

These benchmarks need a *chat* endpoint; for the matching rule, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

Representative identifiers provided through NeMo Evaluator harnesses.

| Identifier | Family | Notes |
| --- | --- | --- |
| `lm-evaluation-harness.ifeval` | Instruction following | Verifiable instruction-following tasks. |
| `simple_evals.mmlu_pro` | Multi-task knowledge | Chat-mode evaluation of MMLU Pro. |
| `simple_evals.humaneval` | Code generation | Pass-rate evaluation of HumanEval. |

## Log-Probability Benchmarks

These benchmarks need a *completions* endpoint with `logprobs` support and a matching tokenizer; for the matching rule, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

Representative identifiers.

| Identifier | Family | Notes |
| --- | --- | --- |
| `mmlu` | Multi-task knowledge | Multiple-choice questions across 57 subjects. |
| `hellaswag` | Commonsense completion | Sentence-completion task used by the sample `tiny.yaml` file. |
| `arc_challenge` | Reasoning | Grade-school science questions, challenge split. |
| `piqa` | Physical reasoning | Physical-interaction commonsense. |

Configure `params.extra.tokenizer` to a Hugging Face model ID, a filesystem path, or the `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint.
Set `params.extra.tokenizer_backend` to `huggingface`.

## Reasoning And Math

Reasoning and math benchmarks expect long generations, frequently with a chain-of-thought trace.
For the reasoning-model strategy and the only common reason to deviate from the deterministic defaults, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

Representative identifiers.

| Identifier | Family | Notes |
| --- | --- | --- |
| `simple_evals.gpqa_diamond` | Graduate-level science | Diamond split of GPQA. |
| `simple_evals.math` | Math word problems | MATH benchmark. |
| `simple_evals.aime` | Competition math | American Invitational Mathematics Examination. |

## Tool Calling And Function Calling

Tool-calling benchmarks score whether the model emits structured tool calls in OpenAI format and whether the calls match the expected schema.
These require a chat endpoint that supports tool-calling responses.

Representative identifiers.

| Identifier | Family | Notes |
| --- | --- | --- |
| `lm-evaluation-harness.bfcl_v3` | Tool calling | Berkeley function-calling leaderboard, version 3. |

## Choosing A Benchmark

Three questions decide the benchmark choice.

1. What endpoint type does the deployment expose?  Chat benchmarks need a chat endpoint, log-probability benchmarks need a completions endpoint with `logprobs`.
2. What behavior do you need to score?  Instruction following, multi-task knowledge, commonsense reasoning, math, code, or tool use each map to different families above.
3. Is this a sample run or a production comparison?  Sample runs should stay on the sample `tiny.yaml` file.  Production comparisons should run the same benchmark set across the baseline and the post-training checkpoint, by following {ref}`model-eval-comparing-runs`.

For benchmark-specific configuration parameters, refer to the NeMo Evaluator [documentation](https://docs.nvidia.com/nemo/evaluator/latest/).

## Related

- {doc}`config-schema` for the `benchmarks` field and the `params.extra` mapping.
- {doc}`output-artifacts` for the per-benchmark subdirectory layout.
- {doc}`../explanation/index` for the concept set behind endpoint and benchmark families.
- {doc}`../how-to/evaluate-deployed-checkpoint` for endpoint-type selection in context.
- {ref}`model-eval-comparing-runs` for before-and-after evaluation framing.
