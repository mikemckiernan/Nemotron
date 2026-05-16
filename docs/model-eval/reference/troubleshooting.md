<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-troubleshooting)=
# Troubleshooting

This page is the canonical reference for recognizing a failed `eval/model_eval` run and deciding what to change before rerunning.
A *named error* is an entry in the `[[errors]]` table of `src/nemotron/steps/eval/model_eval/step.toml`.
The runner uses these names to identify common misconfigurations and reports them with their recovery guidance.

## How A Failed Run Surfaces

A failure in `eval/model_eval` arrives in one of two shapes.

- The `check_endpoint` probe fails before the benchmark loop starts.
  This catches a typo in `deployment.url`, a mismatch between the URL path and `deployment.endpoint_type`, and an endpoint that does not advertise the configured `deployment.model_id`.
  For where the probe sits in the pipeline, refer to {doc}`../explanation/pipeline-overview`.
- A configuration that the probe cannot detect surfaces as a named error from `step.toml`.
  Each named error is keyed to a specific misconfiguration and ships with a recovery string that the runner reports alongside the name.

The Validation Behavior section of {doc}`config-schema` summarizes both shapes from the configuration side.

## Named Errors

The three errors in `step.toml` today are listed below in the order they appear in the contract.
The recovery prose is quoted verbatim from the `[[errors]]` table, so that the reference page and the contract cannot drift.
If the contract changes, update the matching subsection here.

### Missing Tokenizer For Log-Probability Benchmarks

The runner reports the `missing_tokenizer_for_logprobs` named error when a log-probability benchmark is requested without a tokenizer the run can resolve.
The most common cause is a `params.extra` block that omits `tokenizer` or `tokenizer_backend`, or a `tokenizer` value that points at a placeholder path.
The recovery, from `step.toml`:

> Provide tokenizer and tokenizer_backend for log-probability tasks, using checkpoint/tokenizer for Megatron Bridge or the Hugging Face model ID or path for checkpoint_hf.

For why log-probability benchmarks require a matching tokenizer and the three accepted shapes for `params.extra.tokenizer`, refer to {doc}`../explanation/tokenizer-alignment`.

### Mismatched Endpoint Type And Benchmark Family

The runner reports the `wrong_endpoint_type` named error when `deployment.endpoint_type` does not match the family of every benchmark in the `benchmarks` list.
The most common cause is a chat endpoint paired with a log-probability benchmark such as `mmlu`, `hellaswag`, `arc_challenge`, or `piqa`, or a completions endpoint paired with an instruction benchmark.
The recovery, from `step.toml`:

> Use chat endpoints for instruction/chat benchmarks and completions endpoints with logprobs for multiple-choice log-probability tasks.

For the chat versus completions decision and the per-family endpoint requirements, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

### Bad Megatron Bridge Checkpoint Path

The runner reports the `bad_megatron_checkpoint_path` named error when the evaluation deployment is pointed at the parent run output folder rather than at a specific `iter_*` checkpoint directory.
The most common cause is reusing the training output path without descending into the iteration directory that holds the weights and the `tokenizer/` subdirectory.
The recovery, from `step.toml`:

> Point evaluation deployment at the specific iter_* checkpoint directory rather than only the parent output folder.

For the Megatron Bridge tokenizer convention that goes with this path shape, refer to {doc}`../explanation/tokenizer-alignment`.

## Quick Lookup Table

| Error Name | Most Common Cause | Read More |
| --- | --- | --- |
| `missing_tokenizer_for_logprobs` | A log-probability benchmark is requested with no resolvable `params.extra.tokenizer`. | {doc}`../explanation/tokenizer-alignment` |
| `wrong_endpoint_type` | The `deployment.endpoint_type` value does not match the family of every benchmark in the list. | {doc}`../explanation/endpoint-types-and-benchmarks` |
| `bad_megatron_checkpoint_path` | The deployment path stops at the parent output folder instead of descending into an `iter_*` directory. | {doc}`../explanation/tokenizer-alignment` |

`step.toml` is the source of truth for this table.
If a new `[[errors]]` block is added to the contract, add the matching subsection above and a row here.

## Endpoint Probe Failures

The `check_endpoint` probe is not itself a named error, but it is the most common reason a run halts before any benchmark dispatches.
The probe checks three things.

- The URL is reachable and returns a successful response from the configured path.
- The configured `endpoint_type` agrees with the URL path inside `deployment.url`.
- The endpoint advertises the configured `deployment.model_id` as a model identifier.

A failure in the first check surfaces as a connection error or a hypertext transfer protocol (HTTP) status error from `check_endpoint`.
A failure in the second check surfaces as the `wrong_endpoint_type` named error.
A failure in the third check surfaces as a model-not-found error from `check_endpoint`, with the configured `model_id` named in the message.

For the configuration side, refer to the Validation Behavior section of {doc}`config-schema`.
For the endpoint and benchmark pairing rule, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

## When Scores Look Wrong After A Successful Run

A run can complete successfully and still produce scores that are not meaningful.
The case the docs already name is a tokenizer that resolves but does not match the served model.
The `check_endpoint` probe does not detect this case, because the probe only inspects the endpoint and not the local tokenization output.
Symptoms are unstable scores across reruns, or implausibly poor scores on a benchmark where the model is known to do well.

Detect this case by comparing scores against a known baseline rather than reading a single run in isolation.
The {ref}`model-eval-comparing-runs` framing in {doc}`output-artifacts` describes the comparison pattern.

## Related Pages

- {doc}`config-schema` for the field-by-field schema and the Validation Behavior section.
- {doc}`output-artifacts` for the on-disk layout and the {ref}`model-eval-comparing-runs` framing.
- {doc}`../explanation/tokenizer-alignment` for why log-probability benchmarks need a matching tokenizer.
- {doc}`../explanation/endpoint-types-and-benchmarks` for the chat versus completions decision.
- `src/nemotron/steps/eval/model_eval/step.toml` for the full step contract, including the `[[errors]]` table that this page mirrors.
