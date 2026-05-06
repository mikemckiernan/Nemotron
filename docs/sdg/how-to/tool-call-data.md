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

(sdg-tool-call-data)=
# Generate Tool-Calling SFT Data

This guide walks through `customer_support_tools.yaml`, which generates multi-turn ecommerce support conversations that include an OpenAI-style tool call and tool response. Output is training-ready JSONL with `messages` and `tools` arrays.

## How It Works

Unlike the single-turn `default.yaml`, this config uses one `llm_structured` column to generate the entire conversation in a single LLM call. The column's `output_format` is a JSON schema that enforces the message shape — roles, tool call structure, and turn count — so the model cannot produce malformed records:

```{literalinclude} ../../src/nemotron/steps/sdg/data_designer/config/customer_support_tools.yaml
:language: yaml
:caption: src/nemotron/steps/sdg/data_designer/config/customer_support_tools.yaml
```

Each record in the seed file contributes five fields that anchor the conversation: `customer_name`, `issue`, `order_id`, `product`, and `policy_hint`. Two category columns (`urgency`, `channel`) add further variety without requiring seed rows for every combination.

## Prerequisites

- `NVIDIA_API_KEY` set in your environment.
- The bundled seed file `data/customer_support_tool_seeds.jsonl` ships with the step. Add rows to it or swap the path for your own seed file.

## Procedure

1. Preview two records to verify the structured output matches the schema:

   ```console
   $ nemotron step run sdg/data_designer -c customer_support_tools preview=true num_records=2
   ```

   Inspect the preview for:
   - Exactly one `tool_calls` message from the assistant.
   - Exactly one `tool` message with a matching `tool_call_id`.
   - `function.arguments` is a JSON **string**, not a JSON object.
   - The assistant's final message references the tool result.
   - No markdown in message `content` fields.

2. Generate the dataset:

   ```console
   $ nemotron step run sdg/data_designer -c customer_support_tools num_records=200
   ```

   Output is written to `./output/sdg/customer_support_tool_sft.jsonl`.

3. Inspect the output. Each record has a `messages` array and a `tools` array plus metadata:

   ```json
   {
     "messages": [
       {"role": "system", "content": "You are a helpful ecommerce support agent..."},
       {"role": "user", "content": "Hi, I haven't received my headphones yet..."},
       {"role": "assistant", "content": "I'd be happy to help. Could you share your order number?"},
       {"role": "user", "content": "It's ORD-10492."},
       {"role": "assistant", "content": "", "tool_calls": [{"id": "call_001", "type": "function", "function": {"name": "lookup_order", "arguments": "{\"order_id\":\"ORD-10492\"}"}}]},
       {"role": "tool", "tool_call_id": "call_001", "name": "lookup_order", "content": "{\"status\":\"delayed\",\"eta\":\"tomorrow\"}"},
       {"role": "assistant", "content": "Your order is delayed and should arrive tomorrow. Per our policy, I can arrange an expedited replacement if you prefer."}
     ],
     "tools": [{"type": "function", "function": {"name": "lookup_order", "description": "...", "parameters": {...}}}],
     "customer_name": "Priya", "issue": "late delivery", "urgency": "frustrated", "channel": "web_chat"
   }
   ```

## Adapt to Your Domain

To target a different domain:

1. Replace or extend the seed file with rows covering your domain's entities — the five fields (`customer_name`, `issue`, `order_id`, `product`, `policy_hint`) can be renamed to anything as long as the prompt references them by the same names.
2. Update `seed_dataset.fields` in the YAML to match the new field names.
3. Rewrite the `prompt` to describe your domain's scenario and available tool functions.
4. Update `output_format` if the message structure differs (for example, multiple tool calls per conversation).

Keep the `output_projection` as `structured_messages` — it extracts `messages` and `tools` from the structured column and merges the category metadata into the top-level record.

## Validation Checklist

Before using generated records for training, sample at least 50 records and check:

- [ ] Every `tool_calls` entry has a corresponding `tool` message with a matching `tool_call_id`.
- [ ] `function.arguments` values are JSON strings, not nested objects.
- [ ] The assistant's final reply references the tool result (not a generic canned response).
- [ ] No markdown in `content` fields if the trainer doesn't expect it.
- [ ] The `tools` array is present and non-empty in every record.

## Downstream Use

```text
customer_support_tool_sft.jsonl  →  prep/sft_packing  →  SFT training
```

The `structured_messages` projection writes `messages` and `tools` at the top level, matching the format expected by AutoModel SFT and Megatron-Bridge-style training. Verify with `prep/sft_packing`'s dry run before launching a training job.

## Next Steps

- **Output projection reference**: {doc}`../reference/output-projections` — `structured_messages` schema.
- **Config schema**: {doc}`../reference/config-schema` — `llm_structured` column type and `output_format`.
- **Dispatch to a cluster**: {doc}`dispatch-to-cluster`.
