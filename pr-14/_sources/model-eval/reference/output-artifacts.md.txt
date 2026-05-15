<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-output-artifacts)=
# Output Artifacts

This page describes the artifact produced by `eval/model_eval`, both as a contract and as a directory on disk.

## The `eval_results` Contract

`step.toml` declares a single produced artifact.

| Field | Value |
| --- | --- |
| `type` | `eval_results` |
| `description` | Benchmark metrics, artifacts, and evaluation summaries produced by NeMo Evaluator. |

The contract is intentionally loose.
The step does not constrain the file set inside each benchmark subdirectory.
NeMo Evaluator writes whatever the benchmark implementation chooses, which keeps the step a thin wrapper.

## Directory Layout

The runner writes one subdirectory per benchmark under `output_dir`.
The subdirectory name matches the benchmark identifier from the `benchmarks` list verbatim.

For a run with the sample `default.yaml` file, the layout looks like the following.

```text
${output_dir}/
  mmlu/
    <files written by nemo-evaluator for mmlu>
  hellaswag/
    <files written by nemo-evaluator for hellaswag>
  arc_challenge/
    <files written by nemo-evaluator for arc_challenge>
```

For the sample `tiny.yaml` file, only one benchmark subdirectory exists.

```text
${output_dir}/
  hellaswag/
    <files written by nemo-evaluator for hellaswag>
```

The runner does not stamp a date, run identifier, or experiment name into the path.
Include a run identifier in the `output_dir` override you pass on the command line if you want multiple runs to coexist on disk.

## Per-Benchmark Files

The file set inside each benchmark subdirectory comes from NeMo Evaluator.
The exact names and structure can vary across benchmark versions.
A typical run produces three kinds of files.

- A summary file with aggregate metrics, such as accuracy and confidence intervals.
- A per-sample predictions file with the prompt, the model response, and the score for each sample.
- A configuration record that captures the benchmark version, the endpoint metadata, and the generation parameters used for the run.

List the directory after a run completes to see the exact file set for the benchmark and version you ran.

```bash
find "$EVAL_ROOT/results-tiny" -maxdepth 5 -type f | sort
```

For benchmark-specific file layouts, refer to the upstream NeMo Evaluator documentation at <https://docs.nvidia.com/nemo/evaluator/latest/>.

(model-eval-comparing-runs)=
## Comparing Runs

Most evaluations only have meaning when paired with another evaluation.
A trained checkpoint is scored against a baseline, a new prompt format is scored against an older one, a quantized export is scored against the unquantized weights.
The comparison is only honest when the surrounding configuration is held constant.

Apply the following practices before treating any single evaluation as a result.

- Run a lightweight baseline against the starting checkpoint *before* the training, conversion, or quantization step you are measuring.
  Use the same benchmark set, endpoint type, tokenizer, and generation parameters you plan to use afterward.
- Snapshot the exact evaluation configuration: the sample file name, the `output_dir`, every `deployment` and `params` override, and the benchmark version.
  The simplest snapshot is the merged YAML produced by `nemotron steps run eval/model_eval -d`.
- Place a date or run identifier in `output_dir` so the before-and-after directories live side by side.
  For example, `output_dir=./output/eval-2026-05-14-baseline` and `output_dir=./output/eval-2026-05-14-postsft`.
- Keep `params.temperature`, `params.top_p`, `params.extra.tokenizer`, and the benchmark version identical between the two runs.
  A benchmark version bump, a tokenizer replacement, or a chat-template change can make the comparison misleading.
- Rerun the baseline benchmark set first before exploring new benchmarks.
  Keeping the first comparison tightly controlled is more valuable than adding breadth.

The cross-cutting pattern that informs this guidance is recorded at `src/nemotron/steps/patterns/eval-bookends.md` in the repository.

## Related

- {doc}`config-schema` for the YAML keys that influence what is written.
- {doc}`benchmarks-catalog` for the benchmark identifiers that become subdirectory names.
- `src/nemotron/steps/eval/model_eval/step.toml` for the full step contract, including the named error modes.
