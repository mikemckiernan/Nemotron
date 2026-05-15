<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-getting-started)=
# Getting Started With Model Evaluation

::::{grid} 2

:::{grid-item-card}
:columns: 8

**What You'll Build**: A one benchmark result for a single sample of HellaSwag, written under a writable `output_dir` by `eval/model_eval` against an OpenAI-compatible hosted endpoint.

^^^

**In this tutorial, you will**:

1. Discover the `eval/model_eval` step from the local catalog.
2. Inspect the sample `tiny.yaml` file.
3. Run a one-sample evaluation against a hosted endpoint.
4. List the result files on disk and locate the per-benchmark subdirectory.

{octicon}`clock;1.5em;sd-mr-1` This tutorial requires between fifteen and thirty minutes to complete, depending on endpoint latency.
:::

:::{grid-item-card}
:columns: 4

{octicon}`flame;1.5em;sd-mr-1` **Sample Prompt**

^^^

Run a one-sample HellaSwag evaluation against my hosted endpoint by using `eval/model_eval` with `tiny.yaml`, then show me the result files.
:::
::::

## Start Here

- Run all commands from the repository root so paths in the procedure resolve correctly.
- The sample `tiny.yaml` file is at `src/nemotron/steps/eval/model_eval/config/tiny.yaml`.
  Two fields control this tutorial: `params.limit_samples` caps samples per benchmark (the file sets `20`; this tutorial overrides to `1`), and `params.extra.tokenizer` identifies the tokenizer for the served model.

  ```{literalinclude} ../../src/nemotron/steps/eval/model_eval/config/tiny.yaml
  :language: yaml
  ```

## Prerequisites

- The Nemotron repository synced and `uv sync` complete.  Refer to the {doc}`../index` page if you have not done this yet.
- A reachable evaluation endpoint URL and a model identifier the endpoint advertises.
- A bearer token exported as the environment variable referenced by `deployment.api_key_name`.
- A tokenizer that matches the served model.  This can be a Hugging Face model ID, a filesystem path, or the `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint.

## Procedure

1. Export the environment variables used throughout this tutorial.
   `EVAL_ROOT` is a directory you choose; it is the parent of the per-run `output_dir`.

   ```console
   $ export NVIDIA_API_KEY="<your-api-key>"
   $ export EVAL_URL="<full-endpoint-url-with-path>"
   $ export EVAL_MODEL_ID="<model-identifier-from-the-endpoint>"
   $ export EVAL_TOKENIZER="<hf-dataset-or-tokenizer-path>"
   $ export EVAL_ROOT="$(pwd)/output/eval-getting-started"
   ```

1. Confirm that the local catalog exposes `eval/model_eval` before running it.

   ```console
   $ uv run nemotron steps show eval/model_eval
   ```

   The command prints the step contract, including the input artifact types, the output artifact type, the documented parameters, the strategies for endpoint and tokenizer choices, and the named error modes.
   For a walk-through of the contract, refer to {doc}`how-to/discover-the-step`.

1. Run the sample `tiny.yaml` file with five overrides: the output directory, the three endpoint fields, the sample cap, and the tokenizer.

   ```console
   $ uv run --no-sync nemotron steps run eval/model_eval \
       -c tiny \
       output_dir="$EVAL_ROOT/results-tiny" \
       deployment.url="$EVAL_URL" \
       deployment.model_id="$EVAL_MODEL_ID" \
       deployment.api_key_name=NVIDIA_API_KEY \
       params.limit_samples=1 \
       params.extra.tokenizer="$EVAL_TOKENIZER"
   ```

   The runner validates the endpoint first by calling `check_endpoint` with the configured URL, endpoint type, and model identifier.
   A typo or an unreachable endpoint surfaces immediately, before any benchmark runs.

   If you want to inspect the merged configuration without dispatching the run, add `--dry-run`.

1. List the files written under `EVAL_ROOT/results-tiny`.

   ```console
   $ find "$EVAL_ROOT/results-tiny" -maxdepth 5 -type f | sort
   ```

   The runner writes one subdirectory per benchmark.
   For the sample `tiny.yaml` file, the only subdirectory is `hellaswag/`, because `tiny.yaml` sets `benchmarks: [hellaswag]`.

   The file set inside the subdirectory is written by NeMo Evaluator and varies with the benchmark version.
   A typical run produces a summary file with aggregate metrics, a per-sample predictions file, and a configuration record.
   For the contract and the on-disk layout, refer to {doc}`reference/output-artifacts`.

## Next Steps

- Run the standard benchmark set against a deployed checkpoint: {doc}`how-to/evaluate-deployed-checkpoint`.
- Look up the full YAML schema: {doc}`reference/config-schema`.
- Drive the step from a coding agent: {doc}`using-skills`.
- Run hosted evaluations with a custom benchmark list and generation parameters: {doc}`how-to/run-hosted-evaluation`.
