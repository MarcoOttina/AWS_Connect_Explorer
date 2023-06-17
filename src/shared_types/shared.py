from enums import Operators, DataType
from typing import Any


class OperatorCondition:
    operator: Operators
    value: Any


class DataResource:
    type: DataType
    value: Any
    name: None | str


