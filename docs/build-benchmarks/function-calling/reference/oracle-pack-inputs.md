<!--
  SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
  SPDX-License-Identifier: Apache-2.0
-->

# Oracle Pack Inputs

This page is the operator-facing map of the files generation reads. It answers which
files to create, which declarations must agree, and where to look up their fields.
The complete normative contract remains
`src/nemotron/steps/byob/references/bfcl-oracle-pack.md`; when this summary and that
contract disagree, the normative contract is authoritative.

## Keep Three Input Layers Separate

The BFCL workflow has three kinds of input, used at different times:

1. **Authoring inputs**, such as a domain brief, probe plan, or reviewed supplement,
   help a manual or model-assisted flow produce a pack. Generation does not read them.
2. **Oracle Pack inputs** define executable domain truth. Stage 1 loads and fingerprints
   these files.
3. **Run configuration** selects `prepare`, `generate`, `translate`, or `eval` and sets
   paths, budgets, optional model roles, and publication policy. See
   {doc}`generate-config`.

`manifest.yaml` and `task_templates.yaml` are pack declarations, not generation
configuration files. Editing either changes the pack fingerprint and therefore the
identity of every benchmark generated from it.

## Canonical Pack Layout

```text
oracle-pack/
├── manifest.yaml             required
├── tools.json                required
├── backend.py                choose this ...
├── endpoint_config.yaml      ... or this, never both
├── fixtures.json             optional by schema, normally used for domain data
├── task_templates.yaml       required
├── assertions.py             required
├── validation_cases.yaml     required
└── held_out.yaml             optional
```

| File | What it establishes | Who normally writes it |
| --- | --- | --- |
| `manifest.yaml` | Pack identity, languages, paths, fixture keys, shared assistant text, and confirmation vocabulary. | Pack author or assisted assembler. |
| `tools.json` | The public function interface a candidate model may call. | Domain/tool owner; assisted authoring treats it as reviewed evidence. |
| `backend.py` | A deterministic local implementation of the tools. | Domain owner. See {doc}`python-backend`. |
| `endpoint_config.yaml` | A pinned HTTPS BFCL Oracle HTTP v1 service instead of local Python. | Service owner. Mutually exclusive with `backend.py`. |
| `fixtures.json` | Reset state and values that template slots bind. | Domain owner. Optional only when the pack needs no fixture-backed state or slots. |
| `task_templates.yaml` | Conversation intents, slot sources, turn policies, milestones, and claimed success. | Pack author or reviewed assisted-authoring supplement. See {doc}`task-templates`. |
| `assertions.py` | Deterministic predicates that decide whether replay meant success. | Domain/benchmark author. |
| `validation_cases.yaml` | Direct probes of known successful and rejected tool behavior. | Domain/benchmark author. |
| `held_out.yaml` | Fixture primary ids and template ids reserved from ordinary generation. | Benchmark owner, when a held-out policy applies. |

Exactly one oracle is allowed. A pack with both `backend.py` and
`endpoint_config.yaml`, or neither one, is refused rather than resolved by precedence.

## Recommended Fill Order

Each file constrains the next:

1. Declare the public interface in `tools.json`.
2. Implement that exact interface in `backend.py`, or pin an existing HTTP oracle.
3. Put deterministic reset state and slot inventory in `fixtures.json`.
4. Declare identity, paths, languages, primary keys, and shared text in
   `manifest.yaml`.
5. Author conversation shapes in `task_templates.yaml`.
6. Write the assertions those templates name.
7. Probe every tool's success and negative behavior in `validation_cases.yaml`.
8. Add `held_out.yaml` only after deciding which real ids or templates must be
   reserved.

Run `validate_oracle_pack` throughout this sequence; do not wait until every file looks
finished. The scaffold command in {doc}`../how-to/author-a-pack` writes a runnable
starter containing the complete layout.

## Create And Validate The Files

There are two validation levels:

- A **file or source pre-check** catches local shape and consistency problems where a
  dedicated command exists.
- **Whole-pack validation** is authoritative for Gold. It checks how all files work
  together and executes representative behavior.

Create a complete manual starter:

```bash
python -m nemotron.steps.byob.scripts.scaffold_oracle_pack \
  --domain my_domain \
  --target /srv/bfcl/packs/my_domain \
  --transport python \
  --language en \
  --version 0.1.0
```

Use `--transport endpoint` instead of `python` to create
`endpoint_config.yaml`, or add `--include-held-out` to include a held-out policy
example. The target must not already exist.

Validate the complete pack without generating rows:

```bash
python -m nemotron.steps.byob.scripts.validate_oracle_pack \
  --config /srv/bfcl/packs/my_domain/validate.yaml \
  --output-dir /tmp/bfcl-my-domain-validation
```

The pipeline form runs the same preparation contract:

```bash
nemotron steps run byob/bfcl \
  -c /srv/bfcl/packs/my_domain/validate.yaml \
  stage=prepare \
  family=bfcl
```

| File | Supported creation path | Earliest validation path |
| --- | --- | --- |
| `manifest.yaml` | `scaffold_oracle_pack`; assisted assembly derives it from certified evidence and the reviewed supplement. | Whole-pack validation; there is no standalone manifest CLI. |
| `tools.json` | Pack scaffold, or a human-reviewed existing tool catalog. Assisted drafting never rewrites it. | `check_source_package` checks catalog/backend alignment before intake; whole-pack validation is authoritative. |
| `backend.py` | Pack scaffold; or `scaffold_source_package` from an existing catalog. The optional model lane emits declarative behavior that code compiles rather than accepting raw model-written Python. | `check_source_package`, source-intake probes, then whole-pack validation. |
| `fixtures.json` | Pack scaffold or source-package scaffold; the optional model lane can propose fixture content before certification. | `check_source_package` performs static checks; whole-pack validation checks reset and slot use. |
| `task_templates.yaml` | Pack scaffold; assisted drafting may propose templates, but reviewed supplement semantics decide the assembled pack. | No standalone CLI; assembly checks references and whole-pack validation builds representative conversations. |
| `assertions.py` | Pack scaffold; assisted drafting compiles bounded declarative assertion specs into Python. | No standalone CLI; draft compilation and whole-pack `assertions_importable` validation. |
| `validation_cases.yaml` | Pack scaffold; assisted drafting may propose cases that a human reviews in the supplement. | No standalone CLI; assembly checks references and whole-pack validation executes the cases. |
| `endpoint_config.yaml` | `scaffold_oracle_pack --transport endpoint`, then replace the placeholder URL and identity pins with reviewed service metadata. | No standalone CLI; intake/whole-pack validation verifies HTTPS contract and remote identity. |
| `held_out.yaml` | `scaffold_oracle_pack --include-held-out`, then replace the example ids and policy. | Whole-pack validation checks ids, overlap, and reservation behavior. |

Where no standalone validator exists, do not infer that a file is unchecked. Its
meaning depends on sibling files: for example, a template tool name is valid only
relative to `tools.json`, and an assertion name is valid only relative to
`assertions.py`. Run whole-pack validation after each meaningful edit.

### Model-Assisted Creation Boundaries

Model assistance is opt-in and artifact-specific:

- `backend.py` and `fixtures.json`: `scaffold_source_package --draft-with-model`
  accepts a structured source draft, compiles it, marks unresolved decisions, never
  overwrites existing reviewed files, and still requires human review and intake
  probes before certification.
- `task_templates.yaml` and `validation_cases.yaml`: `bfcl_author draft` creates
  proposals outside the pack. Reviewed supplement content and assembly checks decide
  what enters the candidate pack.
- `assertions.py`: the model proposes a bounded declarative assertion specification;
  the pipeline compiles it and refuses unsupported specifications.
- `manifest.yaml`, `tools.json`, `endpoint_config.yaml`, `held_out.yaml`, and the
  candidate supplement are not free-form model outputs.

No model-generated artifact can certify itself, approve exposure or release, or bypass
whole-pack validation.

## Supporting File Workflows

### `tools.json` And `fixtures.json`

The whole-pack scaffold writes both. For an existing catalog used by assisted
authoring, place `tools.json` inside the source directory before running
`scaffold_source_package`; that command reads but does not copy the catalog. It creates
a fixture skeleton alongside the backend.

Pre-check the source pair with:

```bash
python -m nemotron.steps.byob.scripts.check_source_package \
  --source /srv/sources/my-domain
```

This checks static catalog/backend agreement and fixture shape. Only intake probes and
whole-pack validation establish runtime behavior.

### `assertions.py`

The manual scaffold writes assertion functions, the `ASSERTIONS` export, and
`ASSERTION_CAPABILITIES`. Add deterministic functions with the required
`(*, state, trace, task, ctx)` signature and name them from template
`success_assertions`.

Assisted drafting does not accept arbitrary assertion Python from a model. It accepts
bounded declarative specifications and compiles supported predicates. Compilation
refusals remain blockers, and assembly permits only compiled assertion names.

There is no standalone assertions validator. Whole-pack validation imports the module
in the process worker, verifies signatures and capability declarations, checks every
template reference, and then executes the assertions during representative replay.

### `validation_cases.yaml`

The manual scaffold writes successful and structured-error cases. A typical case is:

```yaml
- id: unknown_book
  tool: get_book_status
  arguments: {book_id: BK-ABSENT-1}
  expect:
    result_class: structured_error
    error_code: not_found
  reset_before: true
```

Use stable case ids, name a catalog tool, provide one arguments object, and state the
expected result class and error code where applicable. Assisted drafting may propose
cases, but a human reviews the final cases in the supplement.

There is no standalone case validator. Whole-pack validation executes declared cases
against the backend or endpoint and uses the observations for schema alignment,
mutation, error-shape, confirmation, and determinism checks.

### `endpoint_config.yaml`

Create an endpoint-backed pack skeleton with:

```bash
python -m nemotron.steps.byob.scripts.scaffold_oracle_pack \
  --domain my_domain \
  --target /srv/bfcl/packs/my_domain \
  --transport endpoint \
  --language en \
  --version 0.1.0
```

Replace the placeholder HTTPS URL and the expected oracle id, version, and
`sha256:` content digest with metadata from the deployed immutable service. Store only
environment-variable names for credentials.

There is no standalone endpoint-config validator. Whole-pack preparation checks the
configuration, TLS and redirect policy, fixed BFCL Oracle HTTP v1 routes, tool catalog,
remote identity, isolated sessions, reset, calls, state, and session deletion. Assisted
`http_package` intake can reach review and freeze, but publication is currently
refused; check {doc}`../how-to/assisted-authoring` before choosing that route.

### `held_out.yaml`

Generate a shape with `scaffold_oracle_pack --include-held-out`, then replace every
example fixture id, template id, and policy value. Reference it as top-level
`manifest.held_out`; do not add it under `manifest.paths`.

Whole-pack validation checks that referenced ids exist, do not overlap deliberately
absent ids, and can be reserved without starving generation. No standalone held-out
validator exists.

## Manifest Fields You Usually Fill

The bundled English example is
`src/nemotron/steps/byob/data/tiny_oracle_pack/manifest.yaml`.

| Field | Required when | Meaning |
| --- | --- | --- |
| `pack_id` | Always | Stable non-empty identifier used in row provenance and cache identity. The scaffolder normalizes its `--domain` value to lowercase snake case. |
| `version` | Always | Pack revision included in provenance. Change it when publishing changed pack bytes. |
| `paths` | Optional | Pack-relative overrides for `tools`, `backend` or `endpoint`, `fixtures`, `templates`, `assertions`, and `validation_cases`. Defaults use the canonical names on this page. |
| `languages` | Recommended; required by most authored packs | Languages offered by model-facing surfaces. Every rendered block for a task must support the selected language. |
| `default_language` | When several languages need a default | Language selected when generation does not name one. |
| `clock` | Recommended pack metadata; required by assisted assembly | The pack's intended frozen time. Execution receives `oracle_runtime.clock` from the generation config, so keep the two values aligned; backend code must not read wall-clock time. |
| `primary_keys.<collection>` | When fixture key inference is ambiguous | Field that identifies one row in a fixture collection. |
| `absent_ids.<collection>` | When templates use an `absent:` slot | Identifiers guaranteed not to appear in that fixture collection. |
| `assistant_turn_templates.<type>.<lang>` | For every text milestone not overridden on its template | Shared wording for `ask_for_slot`, `ask_confirm`, `decline`, and `final_answer`. |
| `system_prompt` or `system_prompt_path` | Optional | Inline or pack-relative model-facing system prompt. Declare at most one. |
| `confirmation` | Optional | Pack vocabulary for confirmation parameter and pending status; defaults are `confirm`, `status`, and `awaiting_confirmation`. |
| `surface_guards.tool_names_exempt` | Only when a tool name is ordinary domain language | Names that may appear in user text without being treated as leaked implementation names. |
| `held_out` | When the pack has a held-out policy | Pack-relative path to `held_out.yaml`; it is not a member of `paths`. |

Advanced manifest behavior and endpoint identity fields are in the normative contract.

## The Public Tool Catalog

`tools.json` is an array of OpenAI-style function tool definitions. Each entry has:

- `type: "function"`;
- `function.name`, the exact public tool name;
- an optional model-facing `function.description`;
- `function.parameters`, a JSON Schema object;
- optional pack-only `x-mutates` and `x-requires-confirmation` booleans.

The two `x-*` keys inform validation and are removed from the catalog shown to a
candidate. A tool marked `x-requires-confirmation` must expose the pack's confirmation
parameter and must leave state unchanged when that parameter is false.

The catalog is the source of truth for the interface. It cannot state fixture values,
state transitions, business rejection conditions, conversation policy, or what a task
must assert.

## Why A Tool Name Appears In Several Files

One public name connects declarations that serve different purposes:

```text
tools.json
  declares get_book_status and its argument schema
        ↓
backend.py
  list_tools exposes the name; call_tool dispatches and executes it
        ↓
task_templates.yaml
  tools_present exposes it; a tool_call milestone expects it
        ↓
validation_cases.yaml
  probes known success and structured-error outcomes
        ↓
assertions.py
  decides whether the executed result or final state satisfies the task
```

Only the public name must match. A private helper such as `_get_book_status()` inside
`backend.py` is an implementation detail and is not part of the pack contract.

## Fixtures, Assertions, And Validation Cases

### `fixtures.json`

Fixtures are a JSON object whose values are collections of deterministic rows. A
template source such as `fixture:books.book_id` selects `book_id` from rows in the
`books` collection. The same document is passed to `reset()` as episode state.

The file is schema-optional, but it is practically required for packs whose backend
resets from domain records or whose templates use fixture slot sources.

### `assertions.py`

Every template names at least one success assertion. Each assertion accepts exactly:

```python
def assert_something(*, state, trace, task, ctx) -> None: ...
```

It returns `None` on success, raises `AssertionError` on failure, or returns a declared
`not_applicable` result. Export assertions through an `ASSERTIONS` mapping or by
`assert_*` name. `ASSERTION_CAPABILITIES` declares trace/executable compatibility and
the assertion category.

### `validation_cases.yaml`

Validation cases call the oracle directly before benchmark generation. Declare at
least one success and one negative case per tool. Negative cases prove structured
business errors or an awaiting-confirmation response; mutating tools also need cases
that demonstrate their state and confirmation behavior.

## Where To Go Next

- {doc}`python-backend` for the local oracle interface and invariants.
- {doc}`task-templates` for the fields that construct a conversation.
- {doc}`../how-to/start-from-domain-data` to choose manual or model-assisted authoring.
- {doc}`../how-to/author-a-pack` for the scaffold, validation, and smoke-run commands.
- {doc}`troubleshooting` to map a refusal to the source file that needs correction.
