from __future__ import annotations

import re
from pathlib import Path

import yaml

from nemotron.steps.byob.runtime.benchmark_families.bfcl.pack_loader import (
    TURN_POLICIES,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
REFERENCE = REPO_ROOT / "docs" / "build-benchmarks" / "function-calling" / "reference"


def _read(name: str) -> str:
    return (REFERENCE / name).read_text(encoding="utf-8")


def test_task_template_reference_tracks_runtime_turn_policies() -> None:
    text = _read("task-templates.md")

    for policy in TURN_POLICIES:
        assert f"`{policy}`" in text


def test_task_template_yaml_examples_parse() -> None:
    blocks = re.findall(r"```yaml\n(.*?)\n```", _read("task-templates.md"), re.DOTALL)

    assert blocks
    for block in blocks:
        assert yaml.safe_load(block) is not None


def test_python_backend_reference_names_the_complete_interface() -> None:
    text = _read("python-backend.md")

    for signature in (
        "def list_tools() -> list[str]",
        "def reset(*, ctx, fixtures=None)",
        "def call_tool(name: str, arguments: dict, *, ctx)",
        "def get_state() -> dict",
    ):
        assert signature in text


def test_oracle_pack_input_reference_links_the_field_guides() -> None:
    text = _read("oracle-pack-inputs.md")

    assert "{doc}`python-backend`" in text
    assert "{doc}`task-templates`" in text
    for required in (
        "manifest.yaml",
        "tools.json",
        "task_templates.yaml",
        "assertions.py",
        "validation_cases.yaml",
    ):
        assert required in text
