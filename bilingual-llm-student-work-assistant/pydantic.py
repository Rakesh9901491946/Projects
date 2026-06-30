from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, get_args, get_origin, get_type_hints


@dataclass
class _FieldSpec:
    default: Any = None
    default_factory: Any = None


def Field(default: Any = None, default_factory: Any = None, **_: Any) -> _FieldSpec:
    return _FieldSpec(default=default, default_factory=default_factory)


class BaseModel:
    @classmethod
    def _annotations(cls) -> dict[str, Any]:
        cached = getattr(cls, "__cached_type_hints__", None)
        if cached is None:
            cached = get_type_hints(cls)
            setattr(cls, "__cached_type_hints__", cached)
        return cached

    def __init__(self, **kwargs: Any) -> None:
        annotations = self.__class__._annotations()
        for name, annotation in annotations.items():
            if name in kwargs:
                value = kwargs[name]
            else:
                default = getattr(self.__class__, name, None)
                if isinstance(default, _FieldSpec):
                    if default.default_factory is not None:
                        value = default.default_factory()
                    else:
                        value = copy.deepcopy(default.default)
                else:
                    value = copy.deepcopy(default)
            setattr(self, name, self._coerce_value(annotation, value))

    @classmethod
    def model_validate(cls, payload: Any) -> "BaseModel":
        if isinstance(payload, cls):
            return payload
        if not isinstance(payload, dict):
            raise TypeError(f"Expected dict payload for {cls.__name__}, got {type(payload)!r}")
        return cls(**payload)

    def model_dump(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name in self.__class__._annotations():
            result[name] = self._dump_value(getattr(self, name))
        return result

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump(), ensure_ascii=False)

    def model_copy(self, update: dict[str, Any] | None = None) -> "BaseModel":
        payload = self.model_dump()
        if update:
            payload.update(update)
        return self.__class__.model_validate(payload)

    @classmethod
    def _coerce_value(cls, annotation: Any, value: Any) -> Any:
        if value is None:
            return None

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is list:
            inner = args[0] if args else Any
            return [cls._coerce_value(inner, item) for item in value]

        if origin is dict:
            key_type = args[0] if len(args) > 0 else Any
            value_type = args[1] if len(args) > 1 else Any
            return {
                cls._coerce_value(key_type, key): cls._coerce_value(value_type, item)
                for key, item in value.items()
            }

        if origin is tuple:
            return tuple(value)

        if origin is None and isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation.model_validate(value)

        if origin is not None:
            non_none_args = [arg for arg in args if arg is not type(None)]
            for arg in non_none_args:
                try:
                    return cls._coerce_value(arg, value)
                except Exception:
                    continue
            return value

        return value

    @classmethod
    def _dump_value(cls, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, list):
            return [cls._dump_value(item) for item in value]
        if isinstance(value, dict):
            return {key: cls._dump_value(item) for key, item in value.items()}
        return value
