from datetime import date

import pytest
from pydantic import BaseModel, Field, ValidationError

from jsonschema2pydantic.generator import SchemaGenerator, generate_schema


def test_simple_schema_1():
    schema_raw = {
        "$defs": {
            "Child": {
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "age": {"title": "Age", "type": "integer"},
                },
                "required": ["title", "age"],
                "title": "Child",
                "type": "object",
            }
        },
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "price": {"title": "Price", "type": "integer"},
            "child": {"$ref": "#/$defs/Child"},
        },
        "required": ["name", "price", "child"],
        "title": "ParentSimple",
        "type": "object",
    }

    model_class = generate_schema(schema_raw)

    data = {"name": "Victor Gugo", "price": 40, "child": {"title": "asd", "age": 512}}

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_list_of_strings_2():
    class Parent(BaseModel):
        title: str
        age: int
        children: list[str]

    model_class = generate_schema(Parent.model_json_schema())

    data = {"title": "Victor Gugo", "age": 40, "children": ["1", "2"]}

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_list_of_objects_3():
    class Child(BaseModel):
        title: str
        age: int

    class Parent(BaseModel):
        title: str
        age: int
        children: list[Child]

    model_class = generate_schema(Parent.model_json_schema())

    data = {"title": "Victor Gugo", "age": 40, "children": [{"title": "asdf", "age": 120}]}

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_sum_types_4():
    class Parent(BaseModel):
        field_1: int | float

    model_class = generate_schema(Parent.model_json_schema())

    data = {
        "field_1": 3,
    }

    assert isinstance(model_class.model_validate(data), BaseModel)

    data_2 = {
        "field_1": 40.3,
    }

    assert isinstance(model_class.model_validate(data_2), BaseModel)


def test_schema_with_list_sum_types_5():
    class Parent(BaseModel):
        field_1: list[int | float]

    model_class = generate_schema(Parent.model_json_schema())

    data = {
        "field_1": [3, 2],
    }

    assert isinstance(model_class.model_validate(data), BaseModel)

    data_2 = {
        "field_1": [40.3, 0],
    }

    assert isinstance(model_class.model_validate(data_2), BaseModel)


def test_schema_with_datetime_types_6():
    class Parent(BaseModel):
        field_1: date

    model_class = generate_schema(Parent.model_json_schema())

    data = {
        "field_1": "2024-01-01",
    }

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_none_type_7():
    class Parent(BaseModel):
        field_1: str | None

    model_class = generate_schema(Parent.model_json_schema())

    data = {
        "field_1": "asdf",
    }

    assert isinstance(model_class.model_validate(data), BaseModel)

    data = {
        "field_1": None,
    }

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_default_type_8():
    class Parent(BaseModel):
        field_1: str | None = Field(default="None")

    model_class = generate_schema(Parent.model_json_schema())

    data = {
        "field_1": "asdf",
    }

    assert isinstance(model_class.model_validate(data), BaseModel)

    data = {}

    assert isinstance(model_class.model_validate(data), BaseModel)


def test_schema_with_more_types_9():
    class Child(BaseModel):
        field_1: str
        field_2: int
        field_3: float
        field_4: bool
        field_5: list[str]
        field_6: list[int]
        field_7: list[float]
        field_8: list[bool]
        field_11: str | None
        field_12: int | None
        field_13: float | None
        field_14: bool | None
        field_15: list[str | None]
        field_16: list[int | None]
        field_17: list[float | None]
        field_18: list[bool | None]

    class Parent(BaseModel):
        field_1: str
        field_2: int
        field_3: float
        field_4: bool
        field_5: list[str]
        field_6: list[int]
        field_7: list[float]
        field_8: list[bool]
        field_9: Child
        field_10: list[Child]
        field_11: str | None
        field_12: int | None
        field_13: float | None
        field_14: bool | None
        field_15: list[str | None]
        field_16: list[int | None]
        field_17: list[float | None]
        field_18: list[bool | None]
        field_19: Child
        field_20: list[Child | None]
        field_21: str | None = None
        field_22: int | None = None
        field_23: float | None = None
        field_24: bool | None = None

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    child_data = {
        "field_1": "asdf",
        "field_2": 12,
        "field_3": 0.1,
        "field_4": False,
        "field_5": ["asdf"],
        "field_6": [12],
        "field_7": [0.1],
        "field_8": [False],
        "field_11": "asdf",
        "field_12": 12,
        "field_13": 0.1,
        "field_14": False,
        "field_15": ["asdf"],
        "field_16": [12],
        "field_17": [0.1],
        "field_18": [False],
    }

    data = {
        "field_1": "asdf",
        "field_2": 12,
        "field_3": 0.1,
        "field_4": False,
        "field_5": ["asdf"],
        "field_6": [12],
        "field_7": [0.1],
        "field_8": [False],
        "field_9": child_data,
        "field_10": [child_data],
        "field_11": "asdf",
        "field_12": 12,
        "field_13": 0.1,
        "field_14": False,
        "field_15": ["asdf"],
        "field_16": [12],
        "field_17": [0.1],
        "field_18": [False],
        "field_19": child_data,
        "field_20": [child_data],
    }

    assert isinstance(model_class.model_validate(data), BaseModel)

    assert model_class.model_json_schema() == Parent.model_json_schema()


def test_schema_with_min_length_10():
    class Parent(BaseModel):
        field_1: str = Field(..., min_length=3)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": "asdf"}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": "af"}), BaseModel)


def test_schema_with_max_length_11():
    class Parent(BaseModel):
        field_1: str = Field(..., max_length=3)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": "af"}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": "asdf"}), BaseModel)


def test_schema_with_gt_12():
    class Parent(BaseModel):
        field_1: int = Field(..., gt=0)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": 1}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": 0}), BaseModel)


def test_schema_with_lt_13():
    class Parent(BaseModel):
        field_1: int = Field(..., lt=0)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": -1}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": 0}), BaseModel)


def test_schema_with_ge_13():
    class Parent(BaseModel):
        field_1: int = Field(..., ge=0)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": 0}), BaseModel)
    assert isinstance(model_class.model_validate({"field_1": 1}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": -1}), BaseModel)


def test_schema_with_le_13():
    class Parent(BaseModel):
        field_1: int = Field(..., le=0)

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": -1}), BaseModel)
    assert isinstance(model_class.model_validate({"field_1": 0}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": 1}), BaseModel)


def test_big_schema_with_dict14():
    class Parent(BaseModel):
        field_1: dict[str, float]

    model_class = SchemaGenerator(Parent.model_json_schema()).generate_schema()

    assert model_class.model_json_schema() == Parent.model_json_schema()

    assert isinstance(model_class.model_validate({"field_1": {"1": 1}}), BaseModel)
    assert isinstance(model_class.model_validate({"field_1": {"2": "2"}}), BaseModel)

    with pytest.raises(ValidationError):
        assert isinstance(model_class.model_validate({"field_1": {"2": "a"}}), BaseModel)


def test_simple_schema_15():
    schema_raw = {
        "title": "Parent",
        "type": "object",
        "properties": {
            "field_1": {
                "type": "integer"
            },
            "field_2": {
                "type": "string"
            },
            "field_3": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/Child"
                }
            }
        },
        "required": [
            "field_1",
            "field_2",
            "field_3"
        ],
        "$defs": {
            "Child": {
                "type": "object",
                "properties": {
                    "field_5": {
                        "type": "integer"
                    },
                    "field_6": {
                        "type": "string"
                    },
                },
                "required": [
                    "field_5",
                    "field_6",

                ],
                "additionalProperties": False
            },
        },
        "additionalProperties": False
    }

    model_class = generate_schema(schema_raw)

    data = {"field_1": 50, "field_2": "value 2", "field_3": [{"field_5": 1, "field_6": "abc"}]}

    assert isinstance(model_class.model_validate(data), BaseModel)
