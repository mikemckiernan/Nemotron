<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-run-hosted-evaluation)=
# Run A Hosted Evaluation

This guide runs `eval/model_eval` against an already-running, OpenAI-compatible endpoint.

## Prerequisites

- The Nemotron repository synced with `uv sync` complete.
- A reachable evaluation endpoint URL and a model identifier the endpoint advertises.
- A credential exported as an environment variable.
- A tokenizer that matches the served model.
  Accept a Hugging Face model ID, a filesystem path, or the `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint.

## Choose A Starting Sample File

Two sample files cover most hosted-evaluation runs.

| Sample file | Use |
| --- | --- |
| `tiny.yaml` | Sample run with `limit_samples: 20` on the `hellaswag` benchmar.  Confirms endpoint, credential, and tokenizer configuration. |
| `default.yaml` | Production run with `mmlu`, `hellaswag`, and `arc_challenge`, with no sample cap. |

Pass the configuration file name with `--config`.
You can also specify `--config` with a path to a YAML configuration file outside the step's `config/` directory.

## Override Endpoint, Credential, And Model

Three deployment fields almost always need to be overridden on the command line.

| Override | Value |
| --- | --- |
| `deployment.url` | Full URL of the chat or completions endpoint, including the path segment. |
| `deployment.model_id` | Model identifier as the endpoint advertises it. |
| `deployment.api_key_name` | Name of the environment variable that holds the bearer token.  This is the variable name, not the secret. |

## Choose Benchmarks

The sample files include benchmark lists that match the file's intent.
Override the list when you want a different selection.

```yaml
benchmarks:
  - mmlu
  - hellaswag
```

The benchmark identifiers come from NeMo Evaluator.
Refer to {doc}`../reference/benchmarks-catalog` for families and endpoint-type guidance.

## Set Generation Parameters

The sample files set deterministic generation, which is the right choice for *log-probability* benchmarks and for runs you want to compare side by side.

| Parameter | Default | When to change |
| --- | --- | --- |
| `params.temperature` | `0` | Match the model card for reasoning or chat benchmarks. |
| `params.top_p` | `0` | Match the model card for reasoning or chat benchmarks. |
| `params.parallelism` | `1` | Raise when the endpoint can serve concurrent requests. |
| `params.request_timeout` | `3600` | Raise for long-generation benchmarks. |
| `params.limit_samples` | `null` in `default.yaml`, `20` in `tiny.yaml` | Set to `1` for a one-sample run. |

The tokenizer fields under `params.extra` are required for *log-probability* benchmarks.

```bash
params.extra.tokenizer=<hf-model-id-or-path>
params.extra.tokenizer_backend=huggingface
```

## Run And Stream Output

The following command runs the sample `tiny.yaml` file against a hosted endpoint and limits to one sample.

```bash
: "${NVIDIA_API_KEY:?Set NVIDIA_API_KEY for the hosted eval}"
: "${EVAL_URL:?Set EVAL_URL for the eval endpoint}"
: "${EVAL_MODEL_ID:?Set EVAL_MODEL_ID for the eval endpoint}"
: "${EVAL_TOKENIZER:?Set EVAL_TOKENIZER to a tokenizer path visible to the run}"

uv run --no-sync nemotron steps run eval/model_eval \
  -c tiny \
  output_dir=./output/eval-sample \
  deployment.url="$EVAL_URL" \
  deployment.model_id="$EVAL_MODEL_ID" \
  deployment.api_key_name=NVIDIA_API_KEY \
  params.limit_samples=1 \
  params.extra.tokenizer="$EVAL_TOKENIZER"
```

For a longer production run against the same endpoint, replace `-c tiny` with `-c default`, remove the `params.limit_samples=1` override, and choose an `output_dir` value that includes a date or run identifier.

To compile and inspect the merged configuration without dispatching the run, pass `-d` or `--dry-run`.

```bash
uv run --no-sync nemotron steps run eval/model_eval -d -c tiny \
  deployment.url="$EVAL_URL" \
  deployment.model_id="$EVAL_MODEL_ID"
```

## Validate Output Artifacts

After the run completes, list the files written under `output_dir`.

```bash
find ./output/eval-sample -maxdepth 5 -type f | sort
```

The runner writes one subdirectory per benchmark.
For the sample `tiny.yaml` file, the only subdirectory is `hellaswag/`.
For the sample `default.yaml` file, three subdirectories are written: `mmlu/`, `hellaswag/`, and `arc_challenge/`.

The file set inside each subdirectory comes from NeMo Evaluator.
A typical run produces a summary file with aggregate metrics, a per-sample predictions file, and a configuration record.
For the contract and the on-disk layout, refer to {doc}`../reference/output-artifacts`.

## Related

- {doc}`discover-the-step` for the discovery commands that confirm the step contract.
- {doc}`evaluate-deployed-checkpoint` for picking a deployment path and pointing this step at the resulting endpoint.
- {doc}`../reference/cli-reference` for the full flag and override surface.
- {doc}`../reference/config-schema` for the YAML field reference.
- {ref}`model-eval-comparing-runs` for before-and-after evaluation framing.
