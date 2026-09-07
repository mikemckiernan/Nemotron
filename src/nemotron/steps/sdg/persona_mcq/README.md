# Persona MCQ SDG

`sdg/persona_mcq` is a config-driven, resumable Nemotron step for generating
persona-grounded multiple-choice SFT data. It generates India-grounded English
and Hindi questions, removes lexical and semantic duplicates, asks three
teachers to answer each question, applies agreement and quality gates, and
writes aligned SFT JSONL for teacher ablations.

The reusable Data Designer column lives in `sdg/plugins/persona_mcq`; future SDG
steps can consume it without copying the pipeline.

## Install

```bash
uv sync --extra data-sdg
uv run data-designer download personas --locale en_IN
uv run data-designer download personas --locale hi_Deva_IN
```

Set `QWEN_API_BASE`, `OSS_API_BASE`, `GEMMA_API_BASE`, and `NVIDIA_API_KEY`.
Resolved credentials are never written to committed configs or run metadata;
endpoint URLs are retained in the redacted run configuration for provenance.

## Run

The generic Nemotron step CLI discovers Persona MCQ from its `step.toml` manifest:

```bash
uv run nemotron steps list --category sdg
uv run nemotron steps show sdg/persona_mcq
```

Start with the smoke profile:

```bash
uv run nemotron steps run sdg/persona_mcq -c tiny \
  pipeline.experiment_name=my-smoke
```

Run production-shaped defaults only after inspecting the smoke artifacts:

```bash
uv run nemotron steps run sdg/persona_mcq -c default \
  pipeline.experiment_name=my-run
```

Run or resume selected stages with an OmegaConf list override:

```bash
uv run nemotron steps run sdg/persona_mcq -c default \
  pipeline.experiment_name=my-run 'pipeline.stages=[answers,build_sft,sample]'
```

Stages always follow this order: `questions`, `lexical_dedup`,
`semantic_dedup`, `answer_seed`, `answers`, `build_sft`, `sample`. Inputs for a
selected stage must already exist. Reusing an experiment name with a different
configuration is rejected unless `pipeline.overwrite=true` is explicit.

Use `sdg/persona_mcq` for persona-grounded MCQ-shaped **SFT training data**. Use
`byob/mcq` instead when the output is a held-out benchmark or evaluation set.

## Artifacts

Artifacts are rooted at `<output_root>/<experiment_name>/`:

- `questions/`, `lexical/`, `semantic/`, and `answer_seed/` preserve generation
  and deduplication provenance.
- `answers/<model>/<language>/` contains append-safe successes and retryable
  failures.
- `sft/<teacher>/<language>.jsonl` contains quality-gated records.
- `final/<teacher>.jsonl` contains aligned English/Hindi samples.
- `run.json` records the redacted configuration and dependency/source versions;
  `summary.json` records stage yields and rejection reasons.

The final schema is `{messages, metadata}`. Reasoning-on records include
`assistant.reasoning_content`; the deterministic reasoning-off subset omits it.

## Guardrails

- Never commit generated data, resolved secrets, or endpoint-specific configs.
- Preserve the same model list across answering, voting, and aligned sampling.
- Configure teacher aliases to use distinct model endpoints in production;
  pointing several aliases at one endpoint is suitable only for smoke testing.
- Treat teacher agreement as a consistency gate, not factual verification;
  fact-check or separately judge generated examples before training on them.
- Treat a low shared-teacher intersection as a quality signal, not something to
  bypass silently.
- Use a GPU for production semantic deduplication; the tiny profile uses CPU for
  portability only.
