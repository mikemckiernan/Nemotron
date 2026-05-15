<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-cli-reference)=
# CLI Reference

This page documents the command-line interface (CLI) surface for `nemotron steps run eval/model_eval`.
The flags listed here are shared by every step.
The Hydra override examples are specific to this step's YAML schema.

## Syntax

```bash
uv run nemotron steps run eval/model_eval [FLAGS] [HYDRA_OVERRIDES...]
```

Run the command from the repository root after `uv sync`.
Pass the configuration name with `-c`, the per-step overrides as `key=value` dotlists, and any optional flags described below.

## Flags

These flags are accepted by `nemotron steps run` for every step.
The implementation lives in `src/nemotron/cli/commands/steps/run_cmd.py`.

| Flag | Long form | Purpose |
| --- | --- | --- |
| `-c` | `--config` | Configuration name inside the step's `config/` directory, such as `default` or `tiny`.  Accepts an explicit path to a `*.yaml` file. |
| `-r` | `--run` | Attached execution by using an environment profile defined in `env.toml`.  Streams logs back to the terminal. |
| `-b` | `--batch` | Detached execution by using an environment profile defined in `env.toml`. |
| `-d` | `--dry-run` | Compile the merged configuration and exit without dispatching the run. |
| | `--force-squash` | Force re-squash of the container image when the executor builds one. |

Invoking the command without `-c` resolves the runspec default, which is `default.yaml`.

## Hydra Overrides

Anything passed after the flags as `key=value` is merged into the loaded YAML by using OmegaConf dotlist semantics.
The fields documented here are the ones operators override most often.

| Override | Purpose |
| --- | --- |
| `output_dir=<path>` | Directory under which each benchmark gets a subdirectory.  Include a run identifier when keeping multiple runs side by side. |
| `deployment.url=<url>` | Full URL of the chat or completions endpoint, with the path segment. |
| `deployment.model_id=<id>` | Model identifier as the endpoint advertises it. |
| `deployment.endpoint_type=<type>` | `chat` or `completions`.  Defaults to `completions` when omitted. |
| `deployment.api_key_name=<env-var-name>` | Name of the environment variable holding the bearer token.  This is the variable name, not the secret. |
| `benchmarks=[<id>,<id>,...]` | Override the benchmark list.  Quote the value so the shell does not interpret the brackets. |
| `params.limit_samples=<int>` | Cap the number of samples per benchmark.  Use `1` for a one-sample run. |
| `params.temperature=<float>` | Sampling temperature.  Hold this constant across runs that you want to compare. |
| `params.top_p=<float>` | Top-p nucleus sampling. |
| `params.parallelism=<int>` | Concurrent requests issued by the runner. |
| `params.request_timeout=<int>` | Per-request timeout in seconds. |
| `params.extra.tokenizer=<handle-or-path>` | Hugging Face handle, filesystem path, or *Megatron Bridge* `tokenizer/` subdirectory. |
| `params.extra.tokenizer_backend=huggingface` | Documented tokenizer backend for this step. |

## Discovery Commands

The discovery commands surface the step contract from `step.toml` without running the step.

```bash
uv run --no-sync nemotron steps list --category eval --json
uv run --no-sync nemotron steps show eval/model_eval --json
```

`nemotron steps list --category eval` filters the catalog to the evaluation category.
`nemotron steps show eval/model_eval --json` prints the full step contract, including `consumes`, `produces`, `parameters`, `strategies`, and `errors`.
The {doc}`../how-to/discover-the-step` guide walks through both commands.

## Examples

### Sample Run Against A Hosted Endpoint

Run a one-sample evaluation by using the sample `tiny.yaml` file and four overrides for the endpoint, model, credential variable, and tokenizer.

```bash
uv run --no-sync nemotron steps run eval/model_eval \
  -c tiny \
  output_dir=./output/eval-sample \
  deployment.url="$EVAL_URL" \
  deployment.model_id="$EVAL_MODEL_ID" \
  deployment.api_key_name=NVIDIA_API_KEY \
  params.limit_samples=1 \
  params.extra.tokenizer="$EVAL_TOKENIZER"
```

### Production Run Against A Self-Hosted vLLM Endpoint

Use the sample `default.yaml` file to score against the three-benchmark starting set.
Set `deployment.url` to the local vLLM endpoint and `params.parallelism` to a higher value if the endpoint can serve concurrent requests.

```bash
uv run --no-sync nemotron steps run eval/model_eval \
  -c default \
  output_dir=./output/eval-2026-05-14 \
  deployment.url=http://0.0.0.0:8080/v1/completions/ \
  deployment.model_id=my-checkpoint \
  deployment.api_key_name=NVIDIA_API_KEY \
  params.parallelism=4 \
  params.extra.tokenizer=/path/to/checkpoint/tokenizer
```

### Dry Run

Compile the merged configuration and exit.
Use this to confirm overrides land where you expect before issuing a real run.

```bash
uv run --no-sync nemotron steps run eval/model_eval -d -c tiny \
  deployment.url="$EVAL_URL" \
  deployment.model_id="$EVAL_MODEL_ID"
```

## Related

- {doc}`config-schema` for the YAML schema accepted by `-c` and dotlist overrides.
- {doc}`output-artifacts` for the on-disk layout produced under `output_dir`.
- {doc}`../how-to/run-hosted-evaluation` for a procedural walk-through.
- {doc}`../how-to/discover-the-step` for the step-contract discovery commands.
