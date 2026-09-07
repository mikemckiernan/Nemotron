"""The authoring tools that read a source, on a source that is not the banking one.

Everything here is an observatory: telescopes, observing slots, proposals. The domain is
chosen for having nothing in common with the pack these tools were built against, because
each of these tests once passed on the banking source while failing on something the
banking source happens not to do. A tool offered to whoever brings their own backend has to
hold up on a source it has never seen, so the fixtures below are deliberately awkward in
ways a real source is awkward: rows that disagree about their fields, a collection short
enough that its every column looks small, helpers that build an error three different ways.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from nemotron.steps.byob.runtime.pack_authoring.probe_planning import (
    ProbeArgumentDraft,
    ProbeCaseDraft,
    ProbePlanDraft,
    ProbePlanDraftError,
    fixture_payload,
    materialize_plan,
    plan_findings,
)
from nemotron.steps.byob.runtime.source_adapters.local_python_reach import walk_source
from nemotron.steps.byob.runtime.source_adapters.probe_engine import AdapterProbePlan

_SCRIPTS = Path("src/nemotron/steps/byob/scripts")


def _tool(
    name: str,
    *,
    mutates: bool = False,
    requires_confirmation: bool = False,
    properties: dict | None = None,
) -> dict:
    return {
        "type": "function",
        "x-mutates": mutates,
        "x-requires-confirmation": requires_confirmation,
        "function": {
            "name": name,
            "description": f"{name} for one observing slot.",
            "parameters": {
                "type": "object",
                "properties": properties or {"slot_id": {"type": "string"}},
                "required": sorted(properties or {"slot_id": {}}),
                "additionalProperties": False,
            },
        },
    }


@dataclass(frozen=True)
class _Reviewed:
    """The three reviewed facts `plan_findings` reads, which is all the protocol asks for."""

    published_name: str
    mutates: bool
    requires_confirmation: bool


def _materialize(draft: ProbePlanDraft, tools: list[dict], fixtures: dict, **kwargs) -> dict:
    return materialize_plan(
        draft,
        tools=tools,
        fixtures=fixtures,
        clock="2031-04-02T00:00:00+00:00",
        seed=0,
        error_vocabulary=kwargs.pop("error_vocabulary", {}),
        **kwargs,
    )


def test_fixture_payload_withholds_a_column_no_two_rows_share() -> None:
    """A short collection is where a count threshold alone discloses the secrets.

    Three rows means every column holds at most three distinct values, so a rule that only
    counts admits the observer's API token along with the slot's status. What separates
    them is that no two rows share a token and two rows do share a status.
    """
    payload = json.loads(
        fixture_payload(
            {
                "observers": [
                    {"observer_id": "OBS-1", "api_token": "tok_a91", "tier": "guest"},
                    {"observer_id": "OBS-2", "api_token": "tok_b02", "tier": "guest"},
                    {"observer_id": "OBS-3", "api_token": "tok_c73", "tier": "staff"},
                ]
            }
        )
    )
    disclosed = payload["observers"]["selectable_values"]
    assert disclosed == {"tier": ["guest", "staff"]}
    assert payload["observers"]["fields"] == ["api_token", "observer_id", "tier"]


def test_fixture_payload_advertises_fields_the_first_row_lacks() -> None:
    """Rows of one collection need not agree, and a binding may name any field shown.

    A field a single row carries is still a field no two rows agree on, so it is counted
    against the rows that carry it rather than against the collection. Counted the other
    way, one row holding a key made the key look like a shared state.
    """
    payload = json.loads(
        fixture_payload(
            {
                "slots": [
                    {"slot_id": "S-1"},
                    {"slot_id": "S-2", "seeing": "poor", "override_key": "ok_71b"},
                    {"slot_id": "S-3", "seeing": "poor"},
                ]
            }
        )
    )
    assert payload["slots"]["fields"] == ["override_key", "seeing", "slot_id"]
    assert payload["slots"]["selectable_values"] == {"seeing": ["poor"]}


def test_fixture_payload_survives_nested_and_long_values() -> None:
    """A list value is not a state, and a paragraph is not one a restriction can name."""
    payload = json.loads(
        fixture_payload(
            {
                "proposals": [
                    {"targets": ["M31", "M42"], "abstract": "x" * 400, "band": "optical"},
                    {"targets": ["M13"], "abstract": "y" * 400, "band": "optical"},
                    {"targets": [], "abstract": "z" * 400, "band": "radio"},
                ]
            }
        )
    )
    assert payload["proposals"]["selectable_values"] == {"band": ["optical", "radio"]}


def test_restriction_reaches_a_field_only_later_rows_carry() -> None:
    """The field exists in the collection, so the binding stands, wherever it first appears."""
    tools = [_tool("read_slot")]
    fixtures = {
        "slots": [
            {"slot_id": "S-1"},
            {"slot_id": "S-2", "seeing": "excellent"},
            {"slot_id": "S-3", "seeing": "poor"},
        ]
    }
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="read_slot_success",
                tool="read_slot",
                intent="Read the slot with usable seeing.",
                arguments=[
                    ProbeArgumentDraft(
                        name="slot_id",
                        source="fixture",
                        collection="slots",
                        field="slot_id",
                        where_field="seeing",
                        where_value="excellent",
                    )
                ],
            )
        ]
    )
    document = _materialize(draft, tools, fixtures)
    assert document["cases"][0]["arguments"] == {"slot_id": "S-2"}


def test_mutating_tool_that_asks_nothing_still_expects_a_state_change() -> None:
    """A tool with nothing to confirm commits on every success, so the plan must say so.

    Reading the confirmation flag alone called such a call read-only, and the mutation
    probe then found no committing call for a tool that only ever commits.
    """
    tools = [_tool("log_weather", mutates=True, properties={"note": {"enum": ["clear"]}})]
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="log_weather_success",
                tool="log_weather",
                intent="Record the sky as clear.",
                arguments=[ProbeArgumentDraft(name="note", source="literal", literal="clear")],
            )
        ]
    )
    document = _materialize(draft, tools, {"slots": [{"slot_id": "S-1"}]})
    assert document["cases"][0]["expected_state_change"] is True


def test_confirming_tool_without_the_flag_expects_no_state_change() -> None:
    """The distinction the fix has to preserve: asking first means an unconfirmed call waits."""
    tools = [
        _tool(
            "cancel_slot",
            mutates=True,
            requires_confirmation=True,
            properties={"confirm": {"type": "boolean"}},
        )
    ]
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="cancel_slot_success",
                tool="cancel_slot",
                intent="Ask to cancel without confirming.",
                arguments=[ProbeArgumentDraft(name="confirm", source="literal", literal="false")],
            )
        ]
    )
    document = _materialize(draft, tools, {"slots": [{"slot_id": "S-1"}]})
    assert document["cases"][0]["expected_state_change"] is False


def test_numeric_literal_outside_its_enum_is_refused() -> None:
    """An enum of numbers pins the set, and a drafted literal arrives as text.

    Comparing the two unconverted let every number through, so a schema listing three
    priorities accepted a fourth and the call failed at run time instead of here.
    """
    tools = [_tool("rank_slot", properties={"priority": {"type": "integer", "enum": [1, 2, 3]}})]
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="rank_slot_success",
                tool="rank_slot",
                intent="Rank the slot.",
                arguments=[ProbeArgumentDraft(name="priority", source="literal", literal="9")],
            )
        ]
    )
    with pytest.raises(ProbePlanDraftError, match="outside the declared enum"):
        _materialize(draft, tools, {"slots": [{"slot_id": "S-1"}]})


def test_numeric_literal_inside_its_enum_is_coerced() -> None:
    tools = [_tool("rank_slot", properties={"priority": {"type": "integer", "enum": [1, 2, 3]}})]
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="rank_slot_success",
                tool="rank_slot",
                intent="Rank the slot.",
                arguments=[ProbeArgumentDraft(name="priority", source="literal", literal="2")],
            )
        ]
    )
    document = _materialize(draft, tools, {"slots": [{"slot_id": "S-1"}]})
    assert document["cases"][0]["arguments"] == {"priority": 2}


def test_plan_carries_the_error_path_it_was_derived_for() -> None:
    """A vocabulary read off one path and probed at another finds nothing there."""
    tools = [_tool("read_slot")]
    fixtures = {"slots": [{"slot_id": "S-1"}, {"slot_id": "S-2"}]}
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="read_slot_success",
                tool="read_slot",
                intent="Read a slot.",
                arguments=[ProbeArgumentDraft(name="slot_id", source="fixture", collection="slots", field="slot_id")],
            )
        ]
    )
    document = _materialize(draft, tools, fixtures, error_path=("failure", "detail", "code"))
    assert document["error_path"] == ["failure", "detail", "code"]
    assert _materialize(draft, tools, fixtures)["error_path"] == ["error", "code"]


def test_a_plan_without_a_timeout_case_is_a_finding_rather_than_a_refusal() -> None:
    """A source with no long operation has no honest timeout case, and may say so.

    The prompt used to demand one, which bought a fast call under a quarter-second deadline
    and a `timeout_cleanup` fail. A fail is never waivable; an absent case costs A2 and
    leaves A1 intact, so the tier is lower and the evidence is not false.
    """
    tools = [_tool("read_slot")]
    fixtures = {"slots": [{"slot_id": "S-1"}, {"slot_id": "S-2"}]}
    draft = ProbePlanDraft(
        success_cases=[
            ProbeCaseDraft(
                case_id="read_slot_success",
                tool="read_slot",
                intent="Read a slot.",
                arguments=[ProbeArgumentDraft(name="slot_id", source="fixture", collection="slots", field="slot_id")],
            )
        ],
        timeout_case=None,
    )
    plan = AdapterProbePlan.model_validate(_materialize(draft, tools, fixtures))
    reviewed = {"read_slot": _Reviewed("read_slot", mutates=False, requires_confirmation=False)}
    codes = {finding["code"]: finding["impact"] for finding in plan_findings(reviewed, plan)}
    assert codes["no_timeout_case"] == "blocks_a2"
    assert all(impact != "refuses_intake" for impact in codes.values())


def _observatory_source(root: Path) -> Path:
    """A source whose errors are built three ways, one of them from a module of its own."""
    (root / "rules").mkdir(parents=True)
    (root / "backend.py").write_text(
        """
import json

from rules import limits
from rules.envelope import refuse


class Registry:
    def _deny(self, code, because):
        answer = {"failure": {"detail": {"code": code, "because": because}}}
        return answer

    def read_slot(self, slot_id):
        if not slot_id.startswith("S-"):
            return self._deny("slot_id_malformed", "A slot identifier starts with S-.")
        return {"slot_id": slot_id}

    def book_slot(self, slot_id, proposal_id):
        if limits.exhausted(proposal_id):
            return refuse("proposal_quota_spent", "The proposal has no observing time left.")
        return {"failure": {"detail": {"code": "slot_already_booked", "because": "Another proposal holds it."}}}
""".lstrip(),
        encoding="utf-8",
    )
    (root / "rules" / "__init__.py").write_text("", encoding="utf-8")
    (root / "rules" / "envelope.py").write_text(
        """
def refuse(code, because):
    built = {"failure": {"detail": {"code": code, "because": because}}}
    return built
""".lstrip(),
        encoding="utf-8",
    )
    (root / "rules" / "limits.py").write_text(
        "def exhausted(proposal_id):\n    return proposal_id.endswith('-0')\n",
        encoding="utf-8",
    )
    # Never imported by the backend, so nothing here can be raised under probe.
    (root / "test_registry.py").write_text(
        'def test_thing():\n    assert {"failure": {"detail": {"code": "never_reachable"}}}\n',
        encoding="utf-8",
    )
    return root / "backend.py"


def _run(script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def test_walker_reaches_packages_and_submodules_the_backend_names(tmp_path: Path) -> None:
    """A closure missing a package's own `__init__` is a closure intake does not agree with."""
    backend = _observatory_source(tmp_path / "source")
    reach = walk_source(tmp_path / "source", backend)
    assert reach.modules == (
        "backend.py",
        "rules/__init__.py",
        "rules/envelope.py",
        "rules/limits.py",
    )
    assert reach.external == {}


def test_error_vocabulary_reads_three_idioms_and_skips_unreachable_code(tmp_path: Path) -> None:
    """Every code the backend can reach, at a path three segments deep, and nothing else.

    The three shapes are a method on a class that assigns then returns, a helper imported
    from a sibling package, and an envelope written inline at the call site. The test module
    beside them contributes nothing, because the backend never imports it.

    The description sits under `because`, which is on no list of names this script carries,
    so finding it is the shape rule working: every value written there is a sentence and no
    other entry is.
    """
    _observatory_source(tmp_path / "source")
    result = _run(
        "extract_error_vocabulary.py",
        "--source",
        str(tmp_path / "source"),
        "--error-path",
        "failure.detail.code",
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["message_key"] == "because"
    assert set(report["vocabulary"]) == {
        "slot_id_malformed",
        "proposal_quota_spent",
        "slot_already_booked",
    }
    assert report["vocabulary"]["slot_id_malformed"] == "A slot identifier starts with S-."
    assert report["vocabulary"]["proposal_quota_spent"] == "The proposal has no observing time left."
    assert report["undescribed_codes"] == []


def test_error_vocabulary_prefers_the_entry_a_helper_grafts_on(tmp_path: Path) -> None:
    """The entry filled at every call is the least likely one to be the description.

    A helper of this shape puts the collection name into `entity` unconditionally and the
    sentence into `message` only when it has one. Reading the envelope's literal keys found
    `entity` and nothing else, so every code was explained as the word "telescopes".
    """
    source = tmp_path / "source"
    source.mkdir()
    (source / "backend.py").write_text(
        """
def _fail(code, *, entity=None, field=None, message=None):
    envelope = {"code": code, "entity": entity, "field": field}
    if message is not None:
        envelope["message"] = message
    return {"error": envelope}


def park_telescope(telescope_id):
    if not telescope_id:
        return _fail("invalid_argument", entity="telescopes", field="telescope_id",
                     message="telescope_id must be a non-empty string")
    return _fail("telescope_missing", entity="telescopes", field="telescope_id")
""".lstrip(),
        encoding="utf-8",
    )
    result = _run("extract_error_vocabulary.py", "--source", str(source))
    assert result.returncode == 2, result.stdout
    report = json.loads(result.stdout)
    assert report["message_key"] == "message"
    assert report["vocabulary"]["invalid_argument"] == "telescope_id must be a non-empty string"
    # No sentence was ever written for it, and saying so beats offering "telescopes".
    assert report["undescribed_codes"] == ["telescope_missing"]


def test_error_vocabulary_refuses_a_path_nothing_reaches(tmp_path: Path) -> None:
    _observatory_source(tmp_path / "source")
    result = _run(
        "extract_error_vocabulary.py",
        "--source",
        str(tmp_path / "source"),
        "--error-path",
        "error.code",
    )
    assert result.returncode == 1
    assert "no literal error code reaches" in json.loads(result.stderr)["reason"]


def test_dependency_lock_is_blocked_when_it_would_name_a_dependency(tmp_path: Path) -> None:
    """A correct lock that loses every probe is not a pass, and an exit code has to say so."""
    source = tmp_path / "source"
    _observatory_source(source)
    (source / "rules" / "limits.py").write_text(
        "import pytest\n\n\ndef exhausted(proposal_id):\n    return bool(pytest)\n",
        encoding="utf-8",
    )
    (source / "tools.json").write_text(json.dumps([_tool("read_slot")]), encoding="utf-8")
    result = _run("derive_dependency_lock.py", "--source", str(source), "--check")
    assert result.returncode == 2, result.stdout
    report = json.loads(result.stdout)
    assert report["status"] == "blocked"
    assert [item["import_name"] for item in report["dependencies"]] == ["pytest"]
    assert report["findings"][0]["impact"] == "blocks_all_probes"


def test_dependency_lock_passes_only_when_it_is_empty(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _observatory_source(source)
    (source / "tools.json").write_text(json.dumps([_tool("read_slot")]), encoding="utf-8")
    (source / "fixtures.json").write_text(json.dumps({"slots": [{"slot_id": "S-1"}]}), encoding="utf-8")
    result = _run("derive_dependency_lock.py", "--source", str(source))
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "pass"
    assert report["dependencies"] == []
    assert report["verified_against_intake"] is True


def test_dependency_lock_verification_keeps_a_symlink_intake_would_refuse(tmp_path: Path) -> None:
    """Copying a link's target in place tests a source the runtime will never see."""
    source = tmp_path / "source"
    _observatory_source(source)
    (source / "tools.json").write_text(json.dumps([_tool("read_slot")]), encoding="utf-8")
    outside = tmp_path / "outside.py"
    outside.write_text("VALUE = 1\n", encoding="utf-8")
    (source / "rules" / "limits.py").unlink()
    (source / "rules" / "limits.py").symlink_to(outside)
    result = _run("derive_dependency_lock.py", "--source", str(source))
    assert result.returncode == 1
    # Following the link instead put a real file in the replica, and the report then
    # vouched for a source the runtime refuses to load.
    assert "symlink" in json.loads(result.stderr)["reason"].lower()
