import re
from pathlib import Path

from docs_compiler.config import Config
from docs_compiler.resolver import resolve_doc

_REF_PATTERN = re.compile(r"\{REF:([^}]+)\}")


def resolve_references(
    content: str,
    name: str,
    config: Config,
    source_dir: Path,
    _seen: set[str] | None = None,
) -> str:
    if _seen is None:
        _seen = set()
    current_seen = _seen | {name}

    def replace_ref(match: re.Match) -> str:
        ref_name = match.group(1)
        if ref_name in current_seen:
            raise ValueError(
                f"Circular reference detected: '{ref_name}' is already in the resolution chain {current_seen}"
            )
        ref_path = resolve_doc(ref_name, config, source_dir)
        ref_content = ref_path.read_text()
        return resolve_references(ref_content, ref_name, config, source_dir, current_seen)

    return _REF_PATTERN.sub(replace_ref, content)
