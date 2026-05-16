<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

(model-eval-evaluate-deployed-checkpoint)=
# Evaluate A Deployed Checkpoint

This guide bridges between training output and benchmark scores.
The work falls into two halves.
First, you choose a deployment path and deploy an OpenAI-compatible *endpoint* to serve the checkpoint.
Second, you point `eval/model_eval` at that endpoint, exactly the way {doc}`run-hosted-evaluation` describes.

## Prerequisites

- A trained checkpoint in one of the supported formats.
  Hugging Face safetensors and Megatron Bridge `iter_*` directories both work.
- A host or workspace that can serve the checkpoint.
  Supported environments include your workstation, a Slurm cluster, a vLLM container, and a managed NVIDIA DGX Cloud Lepton endpoint.
- A reachable network path from the machine that runs `nemotron steps run` to the host that serves the model.
- A tokenizer that matches the served model.

## Choose A Deployment Path

Four documented paths cover the common deployments.
Choose the path that matches your environment and the level of orchestration you want.

| Path | Where It Runs | Who Orchestrates | Reference |
| --- | --- | --- | --- |
| Self-hosted vLLM Docker container | Local workstation or remote host | You start `vllm serve`, you stop it | <https://docs.vllm.ai/> and the launcher example at `Evaluator/packages/nemo-evaluator-launcher/examples/local_vllm_logprobs.yaml` |
| NeMo Export-Deploy with Ray Serve or PyTriton | Local or Slurm host with NeMo Framework container | You run the Export-Deploy scripts | <https://github.com/NVIDIA-NeMo/Export-Deploy> and `Evaluator/docs/deployment/nemo-fw/` |
| DGX Cloud Lepton managed endpoint | Lepton workspace | Lepton dashboard or command-line interface | <https://docs.nvidia.com/dgx-cloud/lepton/get-started/endpoint/> |
| NeMo Evaluator Launcher orchestration | Local, Slurm, or Lepton | One launcher command deploys and evaluates | `Evaluator/docs/deployment/launcher-orchestrated/` |

:::{admonition} Lepton Example
:class: tip

Deploy the model by using the NVIDIA DGX Cloud Lepton dashboard, then collect three values: the endpoint URL, the served-model name, and the environment variable name that holds your Lepton API key.
Export the key under that variable name, then point `eval/model_eval` at the endpoint.

```bash
export LEPTON_API_KEY="<your-lepton-api-key>"

uv run --no-sync nemotron steps run eval/model_eval \
  -c tiny \
  output_dir=./output/eval-lepton \
  deployment.url="https://<your-endpoint>.lepton.run/v1/completions/" \
  deployment.model_id="<served-model-name>" \
  deployment.api_key_name=LEPTON_API_KEY \
  params.extra.tokenizer="<hf-model-id-or-path>"
```

For Lepton endpoint setup, refer to <https://docs.nvidia.com/dgx-cloud/lepton/get-started/endpoint/>.
:::

## Choose The Endpoint Type

The endpoint type must match the benchmark family: a *chat* endpoint for chat and instruction-following benchmarks, and a *completions* endpoint with `logprobs` support for *log-probability* benchmarks such as `mmlu`, `hellaswag`, `arc_challenge`, and `piqa`.
For the matching rule and the recovery from a mismatch, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

Set `deployment.endpoint_type` to `chat` or `completions` to match the family, and point `deployment.url` at the chat-completions path or the completions path that the endpoint exposes.

## Configure A Hugging Face Checkpoint

For the tokenizer field shapes and why log-probability benchmarks require a matching tokenizer, refer to {doc}`../explanation/tokenizer-alignment`.

For a Hugging Face checkpoint, the deployment configuration looks like the following.

```yaml
deployment:
  model_id: my-hf-checkpoint
  url: http://0.0.0.0:8080/v1/completions/
  endpoint_type: completions
  api_key_name: NVIDIA_API_KEY

params:
  extra:
    tokenizer: meta-llama/Llama-3.1-8B
    tokenizer_backend: huggingface
```

## Configure A Megatron Bridge Checkpoint

For the tokenizer field shapes and the Megatron Bridge `tokenizer/` convention, refer to {doc}`../explanation/tokenizer-alignment`.

For a Megatron Bridge `iter_*` checkpoint, the same fields apply, with the tokenizer pointing at the `tokenizer/` subdirectory of the specific iteration.

```yaml
deployment:
  model_id: my-megatron-checkpoint
  url: http://0.0.0.0:8080/v1/completions/
  endpoint_type: completions
  api_key_name: NVIDIA_API_KEY

params:
  extra:
    tokenizer: /path/to/run/iter_0010000/tokenizer
    tokenizer_backend: huggingface
```

Point the deployment script at the specific `iter_*` directory, not at the parent run output folder.

## Reasoning Models

Reasoning models produce long chains of thought and need different generation parameters than the sample-file deterministic defaults.

- Raise `params.max_new_tokens` to fit the typical chain-of-thought trace.
- Enable reasoning-trace processing for benchmarks that score the final answer rather than the trace.
- Use the temperature and top-p values from the model card.  Many reasoning models recommend non-zero sampling.

For the rationale and the only common reason to deviate from the deterministic defaults, refer to {doc}`../explanation/endpoint-types-and-benchmarks`.

## Run The Evaluation

After the endpoint is running, the run command is the same as the one in {doc}`run-hosted-evaluation`.
A sample run with the sample `tiny.yaml` file is the right first step against any new deployment.

```bash
uv run --no-sync nemotron steps run eval/model_eval \
  -c tiny \
  output_dir=./output/eval-deployed-sample \
  deployment.url="$EVAL_URL" \
  deployment.model_id="$EVAL_MODEL_ID" \
  deployment.api_key_name="$EVAL_API_KEY_NAME" \
  params.limit_samples=1 \
  params.extra.tokenizer="$EVAL_TOKENIZER"
```

After the sample run succeeds, replace `-c tiny` with `-c default` and remove `params.limit_samples=1` to run the production benchmark set.

## Related

- {doc}`run-hosted-evaluation` for the procedural walk-through this guide builds on.
- {doc}`../explanation/index` for the concept set behind endpoint type, tokenizer alignment, and reasoning-model strategies.
- {ref}`model-eval-comparing-runs` for the before-and-after framing this guide enables.
- {doc}`../../deployment-guides` for the broader catalog of Nemotron deployment options.
- {doc}`../reference/config-schema` for the YAML field reference.
- {doc}`../reference/benchmarks-catalog` for benchmark families and endpoint-type guidance.
