<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-using-skills)=
# Use The Model Evaluation Skill With Confidence

This page is for newcomers who plan to drive `eval/model_eval` from a coding agent.
The goal is to make the chat productive: less back-and-forth, fewer clarifying questions, and a clear handoff between what you decide and what the agent edits or runs in the repository.

Use an agent to translate your intent about endpoints, benchmarks, and tokenizers into the right `nemotron steps run eval/model_eval` invocation and YAML overrides.

## Keeping An Agent Session Productive

The agent needs four pieces of information to make progress without guessing.

- The evaluation endpoint URL.
- The model identifier the endpoint advertises.
- The name of the environment variable that holds the bearer token.  Not the secret value.
- A tokenizer location, either as a Hugging Face model ID, a filesystem path, or the `tokenizer/` subdirectory of a Megatron Bridge `iter_*` checkpoint.

Until the agent has these four, ask it to wait rather than to invent values.

## What The Agent Needs From You

Tell the agent the kind of run you want, then let it select the sample file that matches.

- A sample run, to confirm the endpoint, credential, and tokenizer configuration.  The agent should select the sample `tiny.yaml` file and add `params.limit_samples=1`.
- A production benchmark run, to compare against a baseline.  The agent should select the sample `default.yaml` file and include a date or run identifier in the `output_dir` override.

Ask the agent to start from the sample files and the {doc}`getting-started` flow unless there is a strong reason to invent a new configuration.
Reasoning models, custom benchmark families, and chat-only benchmarks are the common reasons to deviate.

## A Reusable Opening Brief

Copy the following block into the chat and fill in the bracketed lines before sending.

```text
Context: [one sentence on the model and what you want to score]
Goal for this session: [one outcome, for example a one-sample HellaSwag run that finishes with files on disk]
Endpoint URL: [full URL with path segment, or "I do not have this yet, please ask"]
Model identifier: [as the endpoint advertises it]
API key environment variable: [name only, for example NVIDIA_API_KEY]
Tokenizer: [Hugging Face model ID, filesystem path, or Megatron Bridge tokenizer/ subdirectory]
Hard limits: [for example, do not change endpoint type, do not invent values]
Please: [one request]. Use Nemotron eval/model_eval defaults from the repo unless something blocks that.
```

The agent should ask for any field you marked as missing rather than guess.

## What Success Looks Like

A reasonable first success is the one-sample evaluation described in {doc}`getting-started`.
The session reaches that point when three things have happened.

- The agent has issued one `nemotron steps run eval/model_eval -c tiny ...` command with overrides built from the brief.
- The runner's `check_endpoint` probe has succeeded, which means the URL, endpoint type, and model identifier are aligned.
- A per-benchmark subdirectory exists under the `output_dir` you chose, with files written by NeMo Evaluator inside it.

If the probe fails, the agent should report the failure verbatim and ask which field to correct.
It should not retry with different values it invented.

## Next Steps

- Run the tutorial: {doc}`getting-started`.
- Pick a deployment path and configure the endpoint: {doc}`how-to/evaluate-deployed-checkpoint`.
- Run a hosted evaluation with custom benchmarks: {doc}`how-to/run-hosted-evaluation`.
- Look up flags and YAML fields when the agent names them: {doc}`reference/cli-reference` and {doc}`reference/config-schema`.
