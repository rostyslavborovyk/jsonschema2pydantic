# jsonschema2pydantic

Convert jsonschema to pydantic model

## Installation

```bash
pip install jsonschema2pydantic
```

## Examples

```python
from pydantic import BaseModel
from jsonschema2pydantic import generate_schema

class Model(BaseModel):
    field_1: str
    field_2: int
    field_3: bool

DynamicModel = generate_schema({
  "properties": {
    "field_1": {
      "title": "Field 1",
      "type": "string"
    },
    "field_2": {
      "title": "Field 2",
      "type": "integer"
    },
    "field_3": {
      "title": "Field 3",
      "type": "boolean"
    }
  },
  "required": [
    "field_1",
    "field_2",
    "field_3"
  ],
  "title": "Model",
  "type": "object"
})

assert Model.model_json_schema() == DynamicModel.model_json_schema()
```
