<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

# Output Files

All paths below are relative to `output_dir` from your YAML and the string `expt_name`.

## Prepare

| File | Description |
| --- | --- |
| `seed.parquet` | Few-shot rows plus domain chunks produced by `McqByobDataset.sample_and_dump` in `runtime/benchmark_families/mcq/dataset.py`. |

## Generate (`stage_cache/`)

| File | Stage |
| --- | --- |
| `generated_questions.parquet` | GENERATION |
| `judged_questions.parquet` | JUDGEMENT |
| `semantic_deduplicated_questions.parquet` | SEMANTIC_DEDUPLICATION |
| `expanded_distractors.parquet` | DISTRACTOR_EXPANSION (only when `do_distractor_expansion` is true) |
| `coverage_check.parquet` | COVERAGE_CHECK (only when `do_coverage_check` is true) |
| `valid_distractors.parquet` | DISTRACTOR_VALIDITY_CHECK |
| `semantic_outlier_detection.parquet` | SEMANTIC_OUTLIER_DETECTION |
| `filtered_questions.parquet` | HALLUCINATION_EASINESS_DETECTION |

## Generate (experiment root)

| File | Description |
| --- | --- |
| `benchmark_raw.parquet` | Snapshot immediately before column renaming for the final schema. |
| `benchmark.parquet` | Final MCQ schema with columns `question_id`, `question`, `options`, `answer_index`, `answer`, `cot_content`, `src`, and `category` (see `references/benchmark-schema.md` in the source tree). |

## Translate (`stage_cache/`)

| File | Stage |
| --- | --- |
| `translated_questions.parquet` | TRANSLATION |
| `backtranslated_questions.parquet` | BACKTRANSLATION |
| `quality_metrics.parquet` | QUALITY_METRICS |

## Translate (experiment root)

| File | Description |
| --- | --- |
| `benchmark_raw.parquet` | Intermediate snapshot prior to optional quality filtering. |
| `benchmark.parquet` | Final translated MCQ with the same column names as generation, after renaming translated fields back to `question` / `options` / `answer_index` / `answer`. |

Intermediate translation Parquet files can include additional columns such as `question_translated`, `options_translated`, backtranslation fields, and metric scores; those are documented inline in `references/benchmark-schema.md`.
