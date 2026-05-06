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

(sdg-create-greenteme-airlines-dataset)=
# Create a Synthetic Dataset for Greenteme Airlines Customer Service

This guide adapts the bundled SDG pipeline to a custom domain — fictional **Greenteme Airlines** customer-service conversations — using the same `synth/data_designer` step as {doc}`../getting-started`. You copy `default.yaml` to a new config, swap the seed file and category columns for an airline domain, and rewrite the prompts. Customisation lives entirely in YAML; `step.py` stays generic.

The output format stays the same: OpenAI chat-format JSONL, ready for `prep/sft_packing` or AutoModel SFT.

## Prerequisites

- ✅ Completed {doc}`../getting-started` — at least one successful preview and full run of `default.yaml` so you know the pipeline works end-to-end.
- ✅ `NVIDIA_API_KEY` set in your environment.

## How This Differs From `default.yaml`

The bundled `default.yaml` mixes a single category dimension (`persona`) with seed topics. Greenteme adds two more category dimensions (`traveler_segment`, `inquiry_type`, `channel`) on top of seed scenarios so that diversity comes from explicit, controllable axes rather than from temperature alone — the approach the {doc}`../index` and `version-sdg-pipeline` pattern recommend.

A fictional brand (`Greenteme Airlines`) anchors the prompts so generated dialogue does not reference real airline names, real flight numbers, or real loyalty programs — a small but important guardrail when synthetic data may be redistributed.

## Procedure

1. **Create `greenteme.yaml`** starting from a copy of the bundled config:

   ```bash
   cp src/nemotron/steps/sdg/data_designer/config/default.yaml greenteme.yaml
   ```

   Save the file wherever is convenient — the procedure below walks through each change you need to make. The finished config is shown in full in the {ref}`reference section <sdg-greenteme-full-config>` below.

2. **Replace the seed file** with airline scenario hooks. Each row contributes a `scenario` field that anchors the conversation in a concrete situation. Create a JSONL file, such as `greenteme_inquiry_seeds.jsonl`, like the following example:

   ```{literalinclude} ../_snippets/input/greenteme_inquiry_seeds.jsonl
   :language: json
   :caption: greenteme_inquiry_seeds.jsonl (first lines)
   :lines: 1-5
   ```

   In `greenteme.yaml`, point `seed_dataset.path` at your seed file and rename the seed `fields` list:

   ```yaml
   seed_dataset:
     path: /path/to/greenteme_inquiry_seeds.jsonl
     strategy: shuffle
     fields: [scenario]
   ```

3. **Swap the category columns.** Replace the single `persona` column from `default.yaml` with three airline-relevant dimensions:

   ```yaml
   columns:
     - name: traveler_segment
       type: category
       values:
         - frequent_flyer
         - business_traveler
         - family_with_children
         - first_time_international
         - elite_loyalty_member
         - leisure_couple

     - name: inquiry_type
       type: category
       values:
         - rebooking
         - baggage_issue
         - refund_request
         - loyalty_status
         - fare_rules
         - flight_status

     - name: channel
       type: category
       values: [chat, phone, app]
   ```

   Multiple category dimensions multiply combinatorially, so even small lists produce wide coverage. With six segments × six inquiry types × three channels × twelve seed scenarios you have 1,296 distinct slot combinations — well beyond the 100 records this config generates.

4. **Rewrite the LLM-text prompts** for the airline domain. Reference both seed and sampler columns with Jinja2 (`{{ scenario }}`, `{{ traveler_segment }}`, etc.):

   ```yaml
     - name: user_query
       type: llm_text
       model_alias: nvidia-text
       prompt: |
         You are role-playing a {{ traveler_segment }} contacting Greenteme Airlines
         via {{ channel }} about a {{ inquiry_type }}. The scenario is:
         "{{ scenario }}"

         Write the customer's first message. Keep it natural, 1-3 sentences.
         Do not reference any real airline name, real flight number, or real
         loyalty program.

     - name: assistant_response
       type: llm_text
       model_alias: nvidia-text
       prompt: |
         You are a customer-service agent at Greenteme Airlines, a fictional airline.
         Reply to this customer message:

         "{{ user_query }}"

         Provide a concise, professional, compliant response, 2-4 sentences.
         Stay realistic and grounded in standard airline policy. Do not invent
         real airline names, real flight numbers, real PNR codes, or real
         loyalty program details. No markdown.
   ```

   The system-style instruction lives at the top of each prompt rather than as a separate field — `llm_text` columns take a single `prompt`, with the role framing baked in.

5. **Update `output_projection`** so the metadata fields reflect the new column names:

   ```yaml
   output_projection:
     type: openai_messages
     user_field: user_query
     assistant_field: assistant_response
     metadata_fields: [traveler_segment, inquiry_type, channel, scenario]
   ```

6. **Update `output_path`** so the JSONL file does not collide with `default.yaml`'s output:

   ```yaml
   output_path: ${output_dir}/greenteme_sft.jsonl
   ```

7. **Run a preview.** As with `default.yaml`, override `preview=true num_records=2` to verify the pipeline before scaling:

   ```console
   $ nemotron step run sdg/data_designer -c greenteme preview=true num_records=2
   ```

   ```{literalinclude} ../_snippets/output/greenteme/preview.txt
   :language: text
   :caption: preview output
   ```

   ::: {tip}
   Preview is the cheapest place to catch a prompt that asks the model to do something that does not match the column wiring (typo'd column references, missing seed fields, or a system instruction that conflicts with the user-message framing). Iterate here before scaling `num_records`.
   :::

8. **Generate the dataset.** Default is 100 records; raise `num_records` once preview output looks correct:

   ```console
   $ nemotron step run sdg/data_designer -c greenteme num_records=100
   ```

   ```{literalinclude} ../_snippets/output/greenteme/sft_first_record.jsonl
   :language: json
   :caption: first record from output/sdg/greenteme_sft.jsonl
   ```

(sdg-greenteme-full-config)=
## Reference: Full `greenteme.yaml`

```{literalinclude} ../_snippets/input/greenteme.yaml
:language: yaml
:caption: greenteme.yaml
```

## Going Further

**Locale-aware persona profiles.** The current YAML schema supports category, seed, and LLM column types. To replace the static `traveler_segment` category with Census-grounded persona profiles via Data Designer's [person sampler](https://nvidia-nemo.github.io/DataDesigner/latest/concepts/person_sampling/) — including locale, age range, and synthetic-personas integration — the YAML schema needs a `type: person` extension in `step.py`'s `build_columns()`. Track this enhancement in the {doc}`../reference/config-schema` reference.

**Multi-turn conversations.** The example above generates a single user → assistant exchange. For multi-turn dialogue, swap the two `llm_text` columns for one `llm_structured` column whose `output_format` is a Pydantic conversation schema. See `customer_support_tools.yaml` in the step directory for the structured-output pattern.

**Dispatch to a cluster.** Generation runs locally against the NVIDIA-hosted endpoint by default. To run on Lepton or Slurm, see {doc}`dispatch-to-cluster` — env.toml profiles, container images, and the gotchas that bite first-time cluster runs.

## Schema and Downstream Use

The `openai_messages` projection emits records with a `messages` array plus the metadata fields you list. These flow directly into:

- `prep/sft_packing` for Megatron-Bridge-style training, or
- AutoModel SFT, which consumes the chat format directly.

For a full reference of available projection shapes, see {doc}`../reference/output-projections`.

## Next Steps

- **Generate preference pairs for DPO**: {doc}`preference-data` — the `rl_pref.yaml` pattern.
- **Generate tool-calling SFT data**: {doc}`tool-call-data` — multi-turn with `output_format=Conversation`.
- **CLI flags and overrides**: {doc}`../reference/cli-reference`.
- **Config schema**: {doc}`../reference/config-schema` — full reference for column types, samplers, and projections.
- **Pipeline overview**: {doc}`../index`.
