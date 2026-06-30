from __future__ import annotations

from typing import Any

from bilingual_productivity_llm.common.config import load_json_config
from bilingual_productivity_llm.common.schemas import BaseModel, Field


class ModelConfig(BaseModel):
    architecture: str
    parameter_budget: str
    context_length: int
    norm: str
    position_encoding: str


class PretrainDataConfig(BaseModel):
    language_mix: dict[str, float] = Field(default_factory=dict)


class TrainingLoopConfig(BaseModel):
    objective: str
    precision: str
    save_every_steps: int
    eval_every_steps: int


class PretrainConfig(BaseModel):
    version: int
    model: ModelConfig
    data: PretrainDataConfig
    training: TrainingLoopConfig


class TaskTuneDefaults(BaseModel):
    citation_style: str
    strict_schema_validation: bool = True


class TaskTuneDataConfig(BaseModel):
    include_synthetic: bool = True
    include_curated_gold: bool = True


class TaskTuneConfig(BaseModel):
    version: int
    tasks: list[str] = Field(default_factory=list)
    defaults: TaskTuneDefaults
    data: TaskTuneDataConfig


class EvalConfig(BaseModel):
    version: int
    metrics: list[str] = Field(default_factory=list)
    thresholds: dict[str, float] = Field(default_factory=dict)


def load_pretrain_config(path: str) -> PretrainConfig:
    return PretrainConfig.model_validate(load_json_config(path))


def load_task_tune_config(path: str) -> TaskTuneConfig:
    return TaskTuneConfig.model_validate(load_json_config(path))


def load_eval_config(path: str) -> EvalConfig:
    return EvalConfig.model_validate(load_json_config(path))


def summarize_training_stack(pretrain: PretrainConfig, task_tune: TaskTuneConfig) -> dict[str, Any]:
    return {
        "architecture": pretrain.model.architecture,
        "parameter_budget": pretrain.model.parameter_budget,
        "context_length": pretrain.model.context_length,
        "languages": pretrain.data.language_mix,
        "tasks": task_tune.tasks,
        "citation_style": task_tune.defaults.citation_style,
        "strict_schema_validation": task_tune.defaults.strict_schema_validation,
    }
