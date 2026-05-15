<!--
  Working notes for the docs/model-eval section. Not for publication.
  Drop this file before final PR if it has not already been removed.
-->
# Model Evaluation Documentation Plan

## Summary

This plan adds a Nemotron documentation section under `docs/model-eval/` for the `eval/model_eval` step.
The step is a thin wrapper around NeMo Evaluator that hits an OpenAI-compatible endpoint with one or more benchmark suites.
Because the surface area is narrow, the layout mirrors the existing `docs/sdg/` and `docs/translation/` sections: an *About* index, a hands-on *Getting Started*, a *Using Skills* page for agent-driven workflows, a *How-To* directory for task guides, and a *Reference* directory for lookup material.
An `explanation/` directory holds three concept pages plus a landing page.
The concept pages cover the artifact-flow architecture, the chat-versus-completions endpoint decision coupled to benchmark families, and the tokenizer-alignment requirement for log-probability benchmarks.
Deep coverage of NeMo Evaluator internals, checkpoint deployment, and the eval-bookends pattern is still cross-linked rather than re-explained.

## Inspiration Review

Source studied: `/local/var/tmp/mike/speaker/docs/source/evaluate-models/`.

Conventions adopted from Speaker:

- A clear concepts versus how-to versus reference split, with how-to as the spine and reference as the lookup surface.
- *Before You Start* prerequisite blocks at the top of each how-to.
- Per-page *Related Documentation* or *Next Steps* footer, in place of dense in-line links.
- Troubleshooting drilled into named failure modes with one paragraph on cause and one on fix.

Conventions intentionally deviated from:

- Speaker carries one reference page per benchmark.
  The Nemotron step does not own those benchmarks, NeMo Evaluator does, so a single `reference/benchmarks-catalog.md` summarizes the families and cross-links upstream NeMo Evaluator pages.
- Speaker uses MyST grid cards, octicons, and badges heavily on the landing pages.
  The Nemotron peers `docs/sdg/` and `docs/translation/` use grid cards more sparingly and pair them with a tab-set table of contents.
  Follow the Nemotron pattern.
- Speaker has rich `explanation/` pages because it owns multiple benchmark families.
  This section does not, so concept content is folded into the index and the relevant how-to pages.
- Speaker uses emoji checkmarks for success criteria.
  Use plain sentences instead, per project style.
- Speaker uses bold freely for emphasis.
  Switch to italic on first use for new terms, and reserve bold for UI element names.

## Proposed Directory Tree

```
docs/model-eval/
  index.md                              About + map; folds a small How It Works subsection
  getting-started.md                    First successful sample run against a hosted endpoint
  using-skills.md                       Driving the step from a coding agent (EVAL-004 flow)
  how-to/
    index.md                            Landing for task guides
    discover-the-step.md                steps list / steps show, reading the step contract
    run-hosted-evaluation.md            Hosted endpoint, tiny config, parameter overrides
    evaluate-deployed-checkpoint.md     Pick a deployment path, then point eval at the endpoint
  reference/
    index.md                            Landing for lookup pages
    config-schema.md                    YAML field reference for default.yaml and tiny.yaml
    cli-reference.md                    nemotron steps run eval/model_eval flags and overrides
    output-artifacts.md                 eval_results contract; on-disk layout of results dir
    benchmarks-catalog.md               Benchmark task IDs grouped by family; endpoint guidance
  explanation/
    index.md                            Landing for concept pages, grouped by theme
    pipeline-overview.md                Artifact flow and what is owned by Nemotron versus NeMo Evaluator
    endpoint-types-and-benchmarks.md    Chat versus completions endpoints and the benchmark-family match
    tokenizer-alignment.md              Why log-probability benchmarks need a tokenizer that matches the served model
```

A troubleshooting page is intentionally deferred for the initial release.
When it is added, it lives at `reference/troubleshoot.md`, not under `how-to/`, since the content reads as lookup material keyed to the `errors` block in `step.toml`.

## Page-By-Page Plan

### `index.md`

Purpose: About page and section map, with a short conceptual primer.

Headings, in title case:

- About Model Evaluation
- When To Use
- Pipeline At A Glance
- How It Works
- Documentation
- All Documentation
- Before You Start
- Limitations And Considerations

Section summaries:

- *About Model Evaluation*: Two to three sentences naming `eval/model_eval` and explaining that it points at, or assumes someone has deployed, an OpenAI-compatible endpoint and runs benchmark suites through NeMo Evaluator.
- *When To Use*: Three or four bullets covering scoring a trained checkpoint, comparing a new run against a baseline, and one-shot sample runs against a hosted endpoint.
  Italicize *NeMo Evaluator* on first use.
- *Pipeline At A Glance*: A small Mermaid diagram following `docs/sdg/index.md` and `docs/translation/index.md`, showing checkpoint or hosted endpoint, then `eval/model_eval`, then `eval_results`.
- *How It Works*: A short paragraph covering chat versus completions endpoint, the tokenizer requirement for log-probability benchmarks, and deterministic generation defaults.
  Italicize *log-probability* on first use.
- *Documentation*: Grid cards linking to Getting Started, Using Skills, How-To, and Reference.
- *All Documentation*: Tab-set, one table per top tab.
- *Before You Start*: Synced Nemotron environment, the credential exported under the variable named in `deployment.api_key_name`, and a reachable evaluation endpoint with a model identifier.
- *Limitations And Considerations*: Cost, rate limits, that this step does not deploy the checkpoint, and that scores are comparable only when endpoint type and generation parameters are held constant.

Cross-links the page relies on:

- `docs/model-eval/getting-started.md`, `using-skills.md`, `how-to/index.md`, `reference/index.md`.
- `src/nemotron/steps/eval/model_eval/step.toml` for the full step contract, by repository path only.
- The new in-section *Comparing Runs* anchor in `reference/output-artifacts.md` for before-and-after-training framing.
- Upstream NeMo Evaluator docs at `https://docs.nvidia.com/nemo/evaluator/latest/get-started/quickstart/launcher.html`.

### `getting-started.md`

Purpose: A 15- to 30-minute tutorial that ends with a successful or clearly diagnosed one-sample evaluation against a hosted endpoint.
Mirrors EVAL-002 and EVAL-003 from `QA_CUSTOMIZE_MODEL_SCOPE.md`.

Headings, in title case:

- Getting Started With Model Evaluation
- What You Will Build
- Prerequisites
- Discover The Step
- Inspect The Tiny Config
- Run A One-Sample Evaluation
- Inspect The Results
- Summary
- Next Steps

Section summaries:

- *Getting Started With Model Evaluation*: One short paragraph naming the outcome: one benchmark, one sample, hosted endpoint, results on disk.
- *What You Will Build*: A grid card with a one-line goal, a numbered list of three to four steps, and an approximate time budget.
- *Prerequisites*: Synced repo, exported credential, a reachable evaluation URL and model identifier, and a tokenizer path or handle the run can resolve.
  Name the environment variables exactly: `NVIDIA_API_KEY`, `EVAL_URL`, `EVAL_MODEL_ID`, `EVAL_TOKENIZER`.
- *Discover The Step*: Run `uv run --no-sync nemotron steps list --category eval --json` and `uv run --no-sync nemotron steps show eval/model_eval --json`.
- *Inspect The Tiny Config*: `literalinclude` of `src/nemotron/steps/eval/model_eval/config/tiny.yaml`.
  Call out `params.limit_samples` and `params.extra.tokenizer`.
- *Run A One-Sample Evaluation*: The EVAL-003 command, with overrides for `deployment.url`, `deployment.model_id`, `deployment.api_key_name`, `params.limit_samples=1`, and `params.extra.tokenizer`.
- *Inspect The Results*: A `find` over `EVAL_ROOT/results-tiny`.
  Describe the per-benchmark subdirectory shape and point at `reference/output-artifacts.md`.
- *Summary*: Three bullets recapping what was learned.
- *Next Steps*: Links to `how-to/evaluate-deployed-checkpoint.md`, `reference/config-schema.md`, and `using-skills.md`.

Notes:

- Use the `tiny.yaml` benchmark, `hellaswag`, for the first command and call out that the recommended starting set for production runs is the `default.yaml` list: `mmlu`, `hellaswag`, and `arc_challenge`.
- The `step.toml` `[[parameters]] benchmarks` default is treated as metadata only.
  The configs are the source of truth for the recommended starting set.

### `using-skills.md`

Purpose: Equivalent of `docs/sdg/using-skills.md` and `docs/translation/using-skills.md`, scoped to `eval/model_eval` and the EVAL-004 agent-driven flow.

Headings, in title case:

- Use The Model Evaluation Skill With Confidence
- Keeping An Agent Session Productive
- What The Agent Needs From You
- A Reusable Opening Brief
- What Success Looks Like
- How SKILL.md Fits Your Session
- Next Steps

Notes:

- The skill path to cite is `src/nemotron/steps/eval/model_eval/SKILL.md`.
  The skill name is `nemotron-eval-model-eval`.

### `how-to/index.md`

Purpose: Landing for task-focused guides.
Mirrors `docs/sdg/how-to/index.md` and `docs/translation/how-to/index.md`.

Headings: *Model Evaluation How-To Guides*, *Choose A Guide*.

### `how-to/discover-the-step.md`

Purpose: How to find the step, read its contract, and decide whether it applies to the task.

Headings, in title case:

- Discover The Model Evaluation Step
- Prerequisites
- List Eval-Category Steps
- Inspect The Step Contract
- Read The Sample Files
- Decide Whether It Applies
- Related

Notes:

- Anchored on `step.toml` and `step.py`.
- Cross-link `src/nemotron/steps/eval/model_eval/step.toml` by repository path only.

### `how-to/run-hosted-evaluation.md`

Purpose: Run an evaluation against an already-running hosted endpoint.

Headings, in title case:

- Run A Hosted Evaluation
- Prerequisites
- Pick A Starting Config
- Override Endpoint, Credential, And Model
- Choose Benchmarks
- Set Generation Parameters
- Run And Stream Output
- Validate Output Artifacts
- Related

Notes:

- `nemotron steps run` accepts `-c/--config`, `-r/--run`, `-b/--batch`, `-d/--dry-run`, and `--force-squash`.
  These are confirmed at `src/nemotron/cli/commands/steps/run_cmd.py`.
- `api_key_name` is the name of an environment variable, not the secret itself.

### `how-to/evaluate-deployed-checkpoint.md`

Purpose: Bridge between training output and benchmark scores.
Covers picking a deployment path, then pointing `eval/model_eval` at the resulting endpoint.

Headings, in title case:

- Evaluate A Deployed Checkpoint
- Prerequisites
- Pick A Deployment Path
- Pick The Endpoint Type
- Configure A Hugging Face Checkpoint
- Configure A Megatron Bridge Checkpoint
- Reasoning Models
- Run The Evaluation
- Related

Pick A Deployment Path section content:

A comparison table with one row per documented option:

| Path | Where It Runs | Who Orchestrates | Reference |
| --- | --- | --- | --- |
| Self-hosted vLLM Docker container | Local workstation or remote host | You start `vllm serve`, you stop it | `https://docs.vllm.ai/` and the launcher example at `Evaluator/packages/nemo-evaluator-launcher/examples/local_vllm_logprobs.yaml` |
| NeMo Export-Deploy with Ray Serve or PyTriton | Local or Slurm host with NeMo Framework container | You run the Export-Deploy scripts | `https://github.com/NVIDIA-NeMo/Export-Deploy` and `Evaluator/docs/deployment/nemo-fw/` |
| DGX Cloud Lepton managed endpoint | Lepton workspace | Lepton dashboard or CLI | `https://docs.nvidia.com/dgx-cloud/lepton/get-started/endpoint/` |
| NeMo Evaluator Launcher orchestration | Local, Slurm, or Lepton | Single launcher command deploys and evaluates | `Evaluator/docs/deployment/launcher-orchestrated/` |

A short *Lepton mini-recipe* callout sits below the table.
Three or four lines plus a code block.
Inputs: endpoint URL from the Lepton dashboard, served-model name as `deployment.model_id`, and the environment variable name for the Lepton API key.

Endpoint type section:

- *Chat* for chat and instruction-following benchmarks.
- *Completions* with `logprobs` support for log-probability benchmarks.

Configure A Hugging Face Checkpoint:

- `deployment.model_id`, `deployment.url`, and `params.extra.tokenizer` set to the HF handle or path.
- `params.extra.tokenizer_backend: huggingface`.

Configure A Megatron Bridge Checkpoint:

- Same fields, with `params.extra.tokenizer` pointing at the `tokenizer/` subdirectory of the iter_* checkpoint.
- Mention the `bad_megatron_checkpoint_path` error name from `step.toml`.

Reasoning Models:

- Higher `params.max_new_tokens`.
- Reasoning-trace processing on.
- Model-card temperature and top-p.

Related:

- `run-hosted-evaluation.md`, the in-section *Comparing Runs* anchor in `reference/output-artifacts.md`, and `docs/deployment-guides.md` for the broader deployment catalog.

### `reference/index.md`

Purpose: Lookup landing.
Mirrors `docs/sdg/reference/index.md`.

### `reference/config-schema.md`

Purpose: Field-by-field reference for the YAML accepted by `eval/model_eval`, anchored on `default.yaml`.

Headings, in title case:

- Configuration Reference
- Top-Level Structure
- Output Directory
- Deployment
- Benchmarks
- Params
- Validation Behavior
- Related

Notes:

- `params` is opaquely passed to `nemo_evaluator.api.api_dataclasses.ConfigParams(**cfg.get("params", {}))`.
  The reference page documents the fields actually used by `default.yaml` and `tiny.yaml`: `temperature`, `top_p`, `parallelism`, `request_timeout`, `limit_samples`, and the `extra` mapping including `tokenizer` and `tokenizer_backend`.
- `params.extra.tokenizer` accepts a Hugging Face handle, a filesystem path, or a Megatron Bridge `tokenizer/` subdirectory.
- `params.extra.tokenizer_backend` is documented as `huggingface`; other values exist upstream and are not exercised here.

### `reference/cli-reference.md`

Purpose: Command-line reference for `nemotron steps run eval/model_eval` and its discovery siblings.

Headings, in title case:

- CLI Reference
- Syntax
- Flags
- Hydra Overrides
- Discovery Commands
- Examples
- Related

Notes:

- Flags: `-c/--config`, `-r/--run`, `-b/--batch`, `-d/--dry-run`, `--force-squash`.
- Hydra overrides table: `output_dir`, `deployment.url`, `deployment.model_id`, `deployment.api_key_name`, `params.limit_samples`, `params.extra.tokenizer`.

### `reference/output-artifacts.md`

Purpose: Describe `eval_results` as a contract and on disk.

Headings, in title case:

- Output Artifacts
- The `eval_results` Contract
- Directory Layout
- Per-Benchmark Files
- Reading And Comparing Runs
- Related

Notes:

- Contract is loose.
  `step.toml` declares only `produces.type = "eval_results"`.
  The runner writes one subdirectory per benchmark under `output_dir`, and the contents are whatever NeMo Evaluator writes for that benchmark.
- No `expt_name` convention exists.
  Recommend operators include a date or run ID in their `output_dir` override if they want runs side by side.

### `reference/benchmarks-catalog.md`

Purpose: Catalog of the benchmark IDs accepted by `benchmarks:`, grouped by family with endpoint guidance.

Headings, in title case:

- Benchmarks Catalog
- Naming Convention
- Chat And Instruction Benchmarks
- Log-Probability Benchmarks
- Reasoning And Math
- Tool Calling And Function Calling
- Choosing A Benchmark
- Related

Notes:

- The recommended starting set comes from the sample YAML files: `default.yaml` for production runs, `tiny.yaml` for sample runs.
- The `step.toml` `[[parameters]] benchmarks` default is treated as metadata only and is not promoted as the recommended set.

## Cross-Links And Reuse

Content that lives in this section:

- The CLI surface specific to `eval/model_eval`.
- The YAML schema of `default.yaml` and `tiny.yaml`.
- The hosted-evaluation, deployed-checkpoint, and troubleshooting how-tos.
- The agent-driven flow that maps to QA EVAL-004.

Content that lives elsewhere and is cross-linked:

- Step contract, by repository path only: `src/nemotron/steps/eval/model_eval/step.toml`.
- Before-and-after evaluation framing: inlined in `reference/output-artifacts.md` under the `(model-eval-comparing-runs)=` anchor, with a one-line pointer to the source pattern at `src/nemotron/steps/patterns/eval-bookends.md`.
- Deployment recipes: `docs/deployment-guides.md` and upstream NeMo Evaluator and Lepton URLs.
- NeMo Evaluator internals and benchmark catalog upstream.
- Artifact graph mechanics in `docs/train-models/explanation/artifact-graph.md` when that page is the canonical home.

Constraint: `docs/customize/` is out of scope for this section.
Do not cross-link any page under `docs/customize/`.
Cross-link source paths under `src/nemotron/` for contract material, and inline the needed guidance for cross-cutting patterns.

Style rules to surface for every drafter:

- Title case for every heading on every page.
- No bold for anything other than UI element names.
- Italicize a new term on first use, for example *log-probability* and *endpoint*.
- Expand acronyms on first use, for example "supervised fine-tuning (SFT)" and "hypertext transfer protocol (HTTP)".
- Replace "e.g." with "for example", "etc." with "and so on", and "via" with "by using".
- Avoid parenthetical text.
  Prefer commas or a follow-up sentence.
- Use complete sentences.
- One sentence per line in Markdown, except inside tables, code blocks, and other constructs where line breaks would break formatting.
- Prefer positive scope.

## Resolved Decisions

These items are settled and drive the authoring work.

1. Deployment doc to link.
   Documented as three first-class paths plus an orchestrated alternative: self-hosted vLLM container, NeMo Export-Deploy, DGX Cloud Lepton managed endpoint, NeMo Evaluator Launcher.
   Captured in the `how-to/evaluate-deployed-checkpoint.md` comparison table.
2. `--run` and `--batch` support.
   Confirmed in `src/nemotron/cli/commands/steps/run_cmd.py`.
   `nemotron steps run` accepts `-c/--config`, `-r/--run`, `-b/--batch`, `-d/--dry-run`, and `--force-squash` for every step.
3. Accepted `params.extra.tokenizer` shapes.
   Hugging Face handle, filesystem path, and Megatron Bridge `tokenizer/` subdirectory are all valid.
   Documented `tokenizer_backend` value is `huggingface`.
4. `eval_results` contract.
   Loose.
   One subdirectory per benchmark under `output_dir`, contents are whatever NeMo Evaluator writes.
5. Recommended benchmark set.
   The YAML configs are the source of truth.
   Sample runs use the sample `tiny.yaml` file, which sets `benchmarks: [hellaswag]`.
   Standard runs use `default.yaml`, which sets `benchmarks: [mmlu, hellaswag, arc_challenge]`.
   The `step.toml` `[[parameters]] benchmarks` default is treated as metadata only.
6. `expt_name` convention.
   Not present.
   Operators include date or run ID in `output_dir`.
7. Reasoning model guidance.
   Canonical in `step.toml` strategies and `SKILL.md`.
   Higher `max_new_tokens`, reasoning-trace processing on, and model-card temperature and top-p.
8. SKILL.md path.
   `src/nemotron/steps/eval/model_eval/SKILL.md`.
   Skill name `nemotron-eval-model-eval`.
9. Troubleshooting page.
   Deferred for the initial release.
   When added later, the page lives at `reference/troubleshoot.md`, keyed to the `errors` block in `step.toml`.

## Authoring Order

1. `reference/config-schema.md`.
2. `reference/cli-reference.md`.
3. `reference/output-artifacts.md`.
4. `reference/benchmarks-catalog.md`.
5. `explanation/pipeline-overview.md`, `explanation/endpoint-types-and-benchmarks.md`, `explanation/tokenizer-alignment.md`, and `explanation/index.md`.
   In the next pass, the explanation pages are written before the how-to pages so the how-to pages can cross-link them and stay short.
6. `how-to/discover-the-step.md`.
7. `how-to/run-hosted-evaluation.md`.
8. `how-to/evaluate-deployed-checkpoint.md`.
9. `getting-started.md`.
10. `using-skills.md`.
11. `how-to/index.md` and `reference/index.md`.
12. `index.md`.

Deferred: `reference/troubleshoot.md` is written in a follow-up pass.
