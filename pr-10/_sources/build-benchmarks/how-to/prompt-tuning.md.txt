<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

# Tune Prompts for BYOB MCQ

When `prompt_config` is `null`, `ByobConfig.from_yaml` loads the built-in templates from `runtime/benchmark_families/mcq/prompts/utils.py#get_prompts`.

## Provide a YAML file

Set `prompt_config` to a path on disk.
The loader opens that file, replaces `prompt_config` with the parsed mapping, and asserts every required stage exists with `system_prompt` and `prompt` strings.

Required top-level keys match the stages in `get_prompts()`:

- `qa_generation`
- `question_judge`
- `hallucination_filter`
- `easiness_filter`
- `distractor_expansion`
- `distractor_validity`

## Format strings

Some templates call `.format(...)` inside `runtime/benchmark_families/mcq/stages.py`.
Keep the same placeholder names the defaults use, for example `num_questions` for QA generation, or the `{{num_choices}}` / `{{choices_text}}` placeholders used by easiness and hallucination filters.

## Try it

```yaml
prompt_config: /path/to/my_prompts.yaml
```

Then run:

```console
uv run nemotron steps run byob -c /path/to/config.yaml
```

If a key is missing or a value is not a string, validation raises before the pipeline starts.
