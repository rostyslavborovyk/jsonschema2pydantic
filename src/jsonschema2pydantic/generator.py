from datetime import date, datetime
from typing import Annotated, Any, Union

from pydantic import BaseModel, ConfigDict, Field, create_model

__all__ = [
    "SchemaGenerator",
    "generate_schema",
]

_FIELD_ARG_MAPPING: dict[str, str] = {
    "description": "description",
    "minLength": "min_length",
    "maxLength": "max_length",
    "exclusiveMinimum": "gt",
    "exclusiveMaximum": "lt",
    "minimum": "ge",
    "maximum": "le",
}

_TYPE_MAPPING: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "date": date,
    "date-time": datetime,
    "null": None,
}


class SchemaGenerator:
    """SchemaGenerator is used to generate the pydantic models from json schema definition."""

    def __init__(self, definitions: dict[str, Any]) -> None:
        self._definitions_raw = definitions
        self._model_properties = {}
        self._definitions = {}

    def _get_type(self, name: str) -> type | None:
        if name not in _TYPE_MAPPING:
            raise ValueError(f"Not handled type {name}")
        return _TYPE_MAPPING[name]

    def _generate_definition(self, name: str) -> None:
        if name in self._definitions:
            return

        defs = self._definitions_raw["$defs"][name]

        self._definitions[name] = self._generate_schema(
            title=defs["title"],
            properties=defs["properties"],
            additional_properties=defs.get("additionalProperties"),
        )

    def _get_object_item_type(self, property_values: dict[str, Any]) -> type:
        _, source, object_name = property_values["$ref"].split("/")
        if source == "$defs":
            self._generate_definition(object_name)
            return self._definitions[object_name]
        else:
            raise ValueError(f"Source {source} is not supported!")

    def _generate_type_from_property_values(self, property_values: dict[str, Any]) -> type:
        if "$ref" in property_values:
            return self._get_object_item_type(property_values)
        elif "anyOf" in property_values:
            property_types = [
                self._generate_type_from_property_values(d) for d in property_values["anyOf"]
            ]
            return Union[*property_types]
        elif property_values.get("format") == "date":
            return self._get_type("date")
        elif property_values.get("format") == "date-time":
            return self._get_type("datetime")
        elif "type" not in property_values:
            return Any
        else:
            if property_values == {"type": "object"}:
                return Any

            property_type = property_values["type"]
            if property_type == "object":
                return dict[
                    str,
                    self._generate_type_from_property_values(
                        property_values["additionalProperties"]
                    ),
                ]
            elif property_type == "array":
                return list[self._generate_type_from_property_values(property_values["items"])]
            else:
                return self._get_type(property_type)

    def _generate_schema(
        self, title: str, properties: dict[str, Any], additional_properties: bool | None = None
    ) -> type[BaseModel]:
        model_properties = {}

        for property_, property_values in properties.items():
            field_kwargs = {}

            if "default" in property_values:
                field_kwargs["default"] = property_values["default"]
            else:
                field_kwargs["default"] = ...

            for json_schema_arg in _FIELD_ARG_MAPPING:
                if json_schema_arg in property_values:
                    field_kwargs[_FIELD_ARG_MAPPING[json_schema_arg]] = property_values[
                        json_schema_arg
                    ]

            model_properties[property_] = Annotated[
                self._generate_type_from_property_values(property_values), Field(**field_kwargs)
            ]

        config_kwargs = {}
        if additional_properties is not None:  # noqa: SIM102
            if not additional_properties:
                config_kwargs["extra"] = "forbid"

        return create_model(title, __config__=ConfigDict(**config_kwargs), **model_properties)

    def generate_schema(self) -> type[BaseModel]:
        """Generate pydantic schema from json schema definition."""
        return self._generate_schema(
            title=self._definitions_raw["title"],
            properties=self._definitions_raw["properties"],
            additional_properties=self._definitions_raw.get("additionalProperties"),
        )


def generate_schema(definitions: dict[str, Any]) -> type[BaseModel]:
    """Generate pydantic schema from json schema definition."""
    return SchemaGenerator(definitions).generate_schema()
