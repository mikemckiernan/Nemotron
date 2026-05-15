---
license: Apache-2.0
copyright: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
description: "Why log-probability benchmarks in eval/model_eval require a tokenizer that matches the served model, and the shapes accepted by params.extra.tokenizer."
topics: ["Model Evaluation", "Tokenizer"]
tags: ["Explanation", "Model Evaluation"]
content:
  type: "Explanation"
  difficulty: "Beginner"
  audience: ["ML Engineer", "Data Scientist"]
---

(model-eval-tokenizer-alignment)=
# Tokenizer Alignment

*Log-probability* benchmarks score candidate answers by token, so the run must tokenize the same strings the served model tokenizes, by using the same vocabulary and the same merge rules.
This page explains why that requirement exists, the shapes the step accepts for the tokenizer, and how the failure surfaces when alignment breaks.

## Why The Tokenizer Is Needed

Log-probability benchmarks request log-probabilities for specific candidate token sequences from the completions endpoint.
The requesting client tokenizes each candidate locally before issuing the call, so the endpoint can score those exact token sequences in a single forward pass.
The value of `params.extra.tokenizer` is the loader the client uses to perform that local tokenization.

Generation-based benchmarks do not need a tokenizer because they read produced text rather than candidate token probabilities.
The tokenizer requirement is specific to the log-probability family.

## Why It Must Match The Served Model

The tokenizer that the client uses must produce the same sequence of integer identifiers that the served model expects.
When the two tokenizers diverge, the client sends one sequence of token identifiers and the model interprets a different sequence, which yields probabilities for the wrong tokens.
Candidate scores computed under mismatched tokenizers are not meaningful, and small mismatches can produce small but persistent score errors that are easy to miss in aggregate.

## Accepted Shapes

The `params.extra.tokenizer` field accepts three shapes.

- A Hugging Face model ID, for example `meta-llama/Llama-3.1-8B`, resolved through the Hugging Face Hub by the loader.
- A filesystem path that contains the tokenizer files, for use when the tokenizer is not published on the hub or when the run executes offline.
- The `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint, for runs that evaluate a Megatron Bridge training output.

The companion field `params.extra.tokenizer_backend` is documented for this step as `huggingface`.
Other values exist upstream in NeMo Evaluator and are not exercised by this step by default.

## The Megatron Bridge Tokenizer Convention

Megatron Bridge writes a self-contained `tokenizer/` subdirectory inside each `iter_*` checkpoint, alongside the model weights for that iteration.
Pointing `params.extra.tokenizer` at that subdirectory is the recommended pattern for Megatron Bridge deployments, because the tokenizer travels with the weights and matches them by construction.

Pointing `params.extra.tokenizer` at the parent run output folder instead of at a specific `iter_*/tokenizer` subdirectory is a configuration error.
That mistake surfaces as the `bad_megatron_checkpoint_path` named error in `src/nemotron/steps/eval/model_eval/step.toml`.
For the recovery, refer to {doc}`../reference/troubleshooting`.

## Failure Modes

- An absent tokenizer for a log-probability benchmark surfaces as the `missing_tokenizer_for_logprobs` named error in `step.toml`, raised before any benchmark dispatches.
  For the recovery, refer to {doc}`../reference/troubleshooting`.
- A tokenizer that resolves but does not match the served model produces unstable or implausibly poor scores, and is not caught by the `check_endpoint` probe.
  Detect this case by comparing scores against a known baseline; the {ref}`model-eval-comparing-runs` framing in the output-artifacts reference describes the comparison pattern.

## Related Pages

- {doc}`endpoint-types-and-benchmarks` for the endpoint side of the log-probability case.
- {doc}`pipeline-overview` for where the tokenizer load sits in the run.
- {doc}`../reference/config-schema` for the field-by-field documentation of `params.extra`.
- {doc}`../reference/troubleshooting` for the named error modes and their recovery guidance.
- {doc}`../how-to/evaluate-deployed-checkpoint` for choosing the tokenizer value in context.
