<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

# Translation Configuration Reference

Translation YAML is parsed by `ByobTranslationConfig.from_yaml` in `runtime/config.py`.

## Required keys

| Key | Notes |
| --- | --- |
| `expt_name` | Directory name under `output_dir` for caches and finals. |
| `dataset_path` | Existing `benchmark.parquet` from a generation run. |
| `output_dir` | Parent directory for `expt_name`. |
| `source_language` | BCP-47 style tag (for example `en-US`). |
| `target_language` | Target locale tag (for example `hi-IN`). |
| `translation_model_config` | Dict with `backend_type`, `params`, optional `stage` and `segment_stage`. |
| `backtranslation_quality_metrics` | Non-empty list of dicts with `type` and `threshold`. |

## Quality metrics

Each metric `type` must be one of `sacrebleu`, `chrf`, or `ter` (`AVAILABLE_QUALITY_METRICS` in `runtime/constants.py`).

`threshold` must be a nonnegative number; the translation pipeline interprets scores relative to these cutoffs when labeling rows.

## Optional keys

| Key | Default | Notes |
| --- | --- | --- |
| `remove_low_quality` | `True` in the dataclass, unless YAML overrides it | When true, drops rows failing the aggregated metric gate before export. |

## FAITH evaluation

`from_yaml` asserts `translation_model_config.stage.enable_faith_eval` is not true, because BYOB translation relies on backtranslation metrics instead of FAITH.

## Running translate

The checked-in `translate.yaml` does not set a top-level `stage` key, so pass `--stage translate` through the step script:

```console
uv run nemotron steps run byob -c translate -- --stage translate
```

Update `dataset_path` in YAML (or via dotlist override) so it points at the `benchmark.parquet` you want to translate.
