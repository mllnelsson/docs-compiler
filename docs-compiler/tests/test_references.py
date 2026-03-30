import pytest

from docs_compiler.config import Config, ClaudeOutput
from docs_compiler.errors import DocNotFoundError
from docs_compiler.references import resolve_references


def _empty_config() -> Config:
    return Config(outputs=[ClaudeOutput(format="claude", include=[])])


def test_single_level_substitution(tmp_path):
    (tmp_path / "greeting.md").write_text("Hello World")

    result = resolve_references(
        "Start {REF:greeting} End", "main", _empty_config(), tmp_path
    )

    assert result == "Start Hello World End"


def test_nested_substitution(tmp_path):
    (tmp_path / "inner.md").write_text("inner content")
    (tmp_path / "middle.md").write_text("middle {REF:inner} end")

    result = resolve_references(
        "top {REF:middle} done", "top", _empty_config(), tmp_path
    )

    assert result == "top middle inner content end done"


def test_circular_reference_raises_value_error(tmp_path):
    (tmp_path / "a.md").write_text("{REF:b}")
    (tmp_path / "b.md").write_text("{REF:a}")

    with pytest.raises(ValueError, match="Circular reference"):
        resolve_references("{REF:a}", "root", _empty_config(), tmp_path)


def test_unknown_ref_raises_doc_not_found(tmp_path):
    with pytest.raises(DocNotFoundError):
        resolve_references("{REF:nonexistent}", "main", _empty_config(), tmp_path)
