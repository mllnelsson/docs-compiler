from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

from docs_compiler.errors import ConfigError


class DocEntry(BaseModel):
    git: str | None = None
    path: str | None = None


class ClaudeOutput(BaseModel):
    format: Literal["claude"]
    include: list[str]


class PluginOutput(BaseModel):
    format: Literal["plugin"]
    name: str
    skills: list[str] = []
    agents: list[str] = []


class TocOutput(BaseModel):
    format: Literal["toc"]


Output = Annotated[
    ClaudeOutput | PluginOutput | TocOutput,
    Field(discriminator="format"),
]


class Config(BaseModel):
    docs: dict[str, DocEntry] = {}
    outputs: list[Output]


def _read_yaml(path: Path) -> dict:
    try:
        raw = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")

    if not isinstance(raw, dict):
        raise ConfigError("Config must be a YAML mapping")

    return raw


def _parse_config(raw: dict) -> Config:
    if "outputs" not in raw:
        raise ConfigError("Config must contain 'outputs'")

    try:
        return Config.model_validate(raw)
    except ValidationError as e:
        raise ConfigError(f"Invalid config: {e}") from e


def load_config(path: Path) -> Config:
    return _parse_config(_read_yaml(path))
