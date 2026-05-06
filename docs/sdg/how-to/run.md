<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

(sdg-run)=
# Run the SDG Pipeline

This guide covers previewing, generating, and customizing output for any bundled or custom config. Run commands from the repository root with `NVIDIA_API_KEY` set.

## Preview Before Generating

Always preview before running a full generation job. Preview mode calls the same pipeline but returns a small number of records without writing the final JSONL:

```console
$ nemotron step run sdg/data_designer -c default preview=true num_records=2
```

Preview with `tiny.yaml` is an alternative for cheap iteration — it limits `max_tokens` as well as record count, so LLM calls are faster:

```console
$ nemotron step run sdg/data_designer -c tiny preview=true num_records=2
```

Use preview to verify:
- Column references in prompts (`{{ column_name }}`) resolve to the expected values.
- Seed fields (`{{ scenario }}`, `{{ prompt }}`, etc.) are populated from the seed file.
- The model returns text that matches the prompt's intent.
- The `output_projection` produces the schema downstream steps expect.

## Generate a Dataset

Default record count is set in the config (`num_records: 1000` in `default.yaml`). Override on the command line:

```console
$ nemotron step run sdg/data_designer -c default num_records=100
```

Output lands at the path configured in `output_path`. For `default.yaml` this is `./output/sdg/sft.jsonl` when no environment variables are set. Override the path directly:

```console
$ nemotron step run sdg/data_designer -c default \
    num_records=100 \
    output_path=/data/my-project/sft.jsonl
```

## Select a Config

The bundled configs cover three output shapes:

| Config | Output | Use for |
|---|---|---|
| `default` | SFT chat (`openai_messages`) | General chat SFT |
| `customer_support_tools` | Tool-call SFT (`structured_messages`) | Tool-use SFT |
| `rl_pref` | Preference pairs (`dpo_preference`) | DPO / RLHF |
| `tiny` | SFT chat, 10 records, short tokens | Fast iteration |

```console
$ nemotron step run sdg/data_designer -c customer_support_tools preview=true num_records=2
```

To use a config file at an arbitrary path, pass the path to `-c`:

```console
$ nemotron step run sdg/data_designer -c /path/to/my-config.yaml preview=true num_records=2
```

## Dry Run

Compile the config and print the resolved job spec without executing anything:

```console
$ nemotron step run sdg/data_designer -c default --dry-run
```

Useful for checking that overrides resolve correctly before submitting to a cluster.

## Run Attached on a Cluster Profile

To dispatch to a Lepton or Slurm profile configured in `env.toml`, use `--run` (attached, streams logs) or `--batch` (detached):

```console
$ nemotron step run sdg/data_designer -c default --run my-lepton-profile num_records=1000
```

For cluster setup, see {doc}`dispatch-to-cluster`.

## Next Steps

- **Adapt to your domain**: {doc}`create-greenteme-airlines-dataset`.
- **Generate tool-call data**: {doc}`tool-call-data`.
- **Generate preference pairs**: {doc}`preference-data`.
- **CLI flags**: {doc}`../reference/cli-reference`.
- **Config schema**: {doc}`../reference/config-schema`.
