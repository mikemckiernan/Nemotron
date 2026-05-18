<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-config-schema)=
# Configuration Reference

This page documents the YAML schema accepted by `nemotron steps run eval/model_eval`.
The reference is anchored on the sample `default.yaml` file.
The sample `tiny.yaml` file shares the same schema and overrides only `output_dir`, `benchmarks`, and `params.limit_samples`.

## Top-Level Structure

The step loads a single OmegaConf document and reads four top-level keys.

```{literalinclude} ../../../src/nemotron/steps/eval/model_eval/config/default.yaml
:language: yaml
:class: scrollable
```

| Key | Type | Required | Purpose |
| --- | --- | --- | --- |
| `output_dir` | string | yes | Directory under which one subdirectory is created per benchmark. |
| `deployment` | mapping | yes | OpenAI-compatible *endpoint* that NeMo Evaluator targets. |
| `benchmarks` | list of strings | yes | NeMo Evaluator task identifiers to run, one after the other. |
| `params` | mapping | yes | Generation parameters passed to `nemo_evaluator.api.api_dataclasses.ConfigParams`. |

The runner loads the document, applies Hydra-style dotlist overrides, and resolves OmegaConf interpolations before constructing the NeMo Evaluator request objects.

## Output Directory

`output_dir` is treated as a base directory.
For each benchmark named in `benchmarks`, the runner writes results to `output_dir/<benchmark>/`.
The runner does not stamp a date, run ID, or experiment name into the path.
Include a run identifier in the override you pass on the command line if you want to keep multiple runs side by side on disk.

## Deployment

The `deployment` block describes the HTTP endpoint that NeMo Evaluator calls.

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `model_id` | string | yes | Model identifier as the endpoint advertises it.  This is the value placed in the `model` field of each request. |
| `url` | string | yes | Full URL of the chat or completions endpoint, including the path segment.  Examples are `http://0.0.0.0:8080/v1/completions/` and `https://integrate.api.nvidia.com/v1/chat/completions`. |
| `endpoint_type` | string | no | Either `completions` or `chat`.  Defaults to `completions` when omitted.  Pair this with the benchmark family. |
| `api_key_name` | string | no | Name of the environment variable that holds the bearer token.  This is the variable name, not the secret value. |

Set the value for the `api_key_name` variable in your shell before launching the step.
The sample `default.yaml` file names `NGC_API_KEY`; the getting started tutorial uses `NVIDIA_API_KEY` for the NVIDIA-hosted endpoint.

## Benchmarks

`benchmarks` is a list of NeMo Evaluator task identifiers.
The runner iterates the list in order and writes one subdirectory per benchmark under `output_dir`.

The sample files set the recommended starting points.

| Sample file | `benchmarks` value | Intended use |
| --- | --- | --- |
| `default.yaml` | `[mmlu, hellaswag, arc_challenge]` | Production runs against a deployed checkpoint. |
| `tiny.yaml` | `[hellaswag]` | Sample runs that exercise the endpoint and the result-writing path. |

The `[[parameters]] benchmarks` entry in `step.toml` is metadata used by the discovery commands.
Treat it as documentation, not as the recommended starting set.
Refer to `benchmarks-catalog.md` for benchmark families and endpoint pairing guidance.

## Params

The `params` block is passed verbatim to `ConfigParams(**cfg.get("params", {}))`.
The fields used by the sample files are documented below.
Other fields exist upstream in NeMo Evaluator and are not exercised by this step by default.

| Field | Type | Purpose |
| --- | --- | --- |
| `temperature` | float | Sampling temperature.  The sample files set `0` for deterministic generation. |
| `top_p` | float | Top-p nucleus sampling.  The sample files set `0`. |
| `parallelism` | int | Concurrent requests issued by the runner. |
| `request_timeout` | int | Per-request timeout in seconds. |
| `limit_samples` | int or `null` | Cap on the number of samples evaluated per benchmark.  Set to `null` in `default.yaml` and to `20` in `tiny.yaml`. |
| `extra` | mapping | Pass-through for fields specific to the chosen benchmark, such as the tokenizer. |

### Params Extra

`params.extra` carries fields that the benchmark implementation requires.
The two fields exercised by the sample files are the tokenizer location and its backend.

| Field | Type | Purpose |
| --- | --- | --- |
| `tokenizer` | string | Tokenizer to load.  Accepts a Hugging Face model ID, a filesystem path, or the `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint. |
| `tokenizer_backend` | string | The tokenizer loader to use.  This step documents `huggingface`.  Other values exist upstream and are not exercised here. |

For why *log-probability* benchmarks require a tokenizer that matches the served model, refer to {doc}`../explanation/tokenizer-alignment`.

## Validation Behavior

The runner performs one explicit check before iterating the benchmark list.
It calls `nemo_evaluator.api.check_endpoint` with the configured `url`, `endpoint_type`, and `model_id`.
A failing probe stops the run before any benchmark is dispatched, which protects against typos in the endpoint URL and against an endpoint that does not advertise the configured `model_id`.

Misconfigurations beyond the endpoint probe surface as the named error modes in `step.toml`.
For each named error, the most common cause, and the recovery, refer to {doc}`troubleshooting`.
Read `src/nemotron/steps/eval/model_eval/step.toml` in the repository for the full list of error names.

## Related

- {doc}`cli-reference` for command-line flags and Hydra override syntax.
- {doc}`benchmarks-catalog` for benchmark identifiers grouped by family.
- {doc}`output-artifacts` for the `eval_results` contract and the on-disk layout.
- {doc}`troubleshooting` for the named error modes and their recovery guidance.
- {doc}`../explanation/index` for the concept set behind tokenizer alignment and endpoint families.
- `src/nemotron/steps/eval/model_eval/step.toml` for the full step contract.
