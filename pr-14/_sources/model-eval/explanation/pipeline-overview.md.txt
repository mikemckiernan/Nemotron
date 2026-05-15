---
license: Apache-2.0
copyright: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
description: "How nemotron eval/model_eval flows from a checkpoint or hosted endpoint, through NeMo Evaluator, into eval_results on disk."
topics: ["Model Evaluation", "Pipeline"]
tags: ["Explanation", "Architecture"]
content:
  type: "Explanation"
  difficulty: "Beginner"
  audience: ["ML Engineer", "Data Scientist"]
---

(model-eval-pipeline-overview)=
# Pipeline Overview

The `eval/model_eval` step is the evaluation stage of the Nemotron pipeline.
Its artifact flow begins at a *Hugging Face* checkpoint or a *Megatron Bridge* checkpoint, passes through an OpenAI-compatible endpoint that some other process deploys, runs through `eval/model_eval`, and ends as an `eval_results` directory on disk.

## Architecture

```{mermaid}
%%{init: {'theme': 'base', 'themeVariables': { 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'primaryTextColor': '#333333', 'clusterBkg': '#ffffff', 'clusterBorder': '#333333'}}}%%
flowchart LR
    ckpt["Hugging Face or<br/>Megatron Bridge checkpoint"] --> deploy["OpenAI-compatible<br/>endpoint"]
    hosted["Hosted endpoint"] --> deploy
    deploy --> step["eval/model_eval<br/>(NeMo Evaluator)"]
    step --> results["output_dir/&lt;benchmark&gt;/<br/>per-benchmark subdirs"]
```

## Input Artifacts

The step declares two optional input artifacts in `src/nemotron/steps/eval/model_eval/step.toml`.

- `checkpoint_megatron` is a *Megatron Bridge* checkpoint directory, usually an `iter_*` directory, deployed by a separate process before the step runs.
- `checkpoint_hf` is a *Hugging Face* checkpoint or model path, deployed by a separate process before the step runs.

Both are marked `required = false` because the step does not deploy the checkpoint.
A third case is also supported: the user points the step at an already-running hosted endpoint, in which case no checkpoint artifact is consumed and only the `deployment` configuration is needed.

## Endpoint Validation

Before the runner dispatches any benchmark, it issues a single `check_endpoint` probe.
The runner passes three arguments to that probe: the URL, the endpoint type, and the model identifier.
A failing probe stops the run before any benchmark is dispatched, which catches a typo in the URL, a mismatch between the URL path and the endpoint type, and an endpoint that does not advertise the configured model identifier.

## Per-Benchmark Loop

The runner iterates the `benchmarks` list in declaration order and writes each benchmark's results to `output_dir/<benchmark>/`.
No merge step combines results across benchmarks.
Each subdirectory contains whatever *NeMo Evaluator* writes for that benchmark, treated as a per-benchmark contract that the step does not normalize.

## Output Artifact

The step produces a single `eval_results` artifact, which is the `output_dir` directory together with its per-benchmark subdirectories.
This is a loose contract: `step.toml` declares only `produces.type = "eval_results"`, and the on-disk layout is whatever the underlying *NeMo Evaluator* benchmark writes.
For the layout details and the recommended pattern for comparing runs, refer to {doc}`../reference/output-artifacts`.

## What Is Owned Where

| Owned by Nemotron | Owned by NeMo Evaluator |
| --- | --- |
| The YAML schema for `output_dir`, `deployment`, `benchmarks`, and `params`. | The implementation of each benchmark task and its scoring code. |
| The `check_endpoint` call site and the named error modes in `step.toml`. | The wire format of requests issued to the chat or completions endpoint. |
| Hydra-style command-line overrides and the discovery commands. | The structure of files written into each per-benchmark subdirectory. |
| The deterministic-by-default generation parameters in the sample files. | The accepted set of benchmark identifiers and their version handling. |

Use this split to decide where a given parameter lives.
Parameters that live in the YAML and are documented in this section are owned by Nemotron; everything below the YAML surface sits upstream in *NeMo Evaluator*.

## Related Pages

- {doc}`endpoint-types-and-benchmarks` for the chat-versus-completions decision.
- {doc}`tokenizer-alignment` for why log-probability benchmarks need a matching tokenizer.
- {doc}`../reference/output-artifacts` for the on-disk layout and the {ref}`model-eval-comparing-runs` framing.
- {doc}`../how-to/discover-the-step` for reading the step contract before configuring a run.
