import uuid

from shared import DataResource, OperatorCondition
from enums import OutBranchType

class DataManipulated:
    input: list[DataResource]
    set: list[DataResource]


class NodeLink:
    to: uuid
    type: OutBranchType
    isStandard: bool
    condition: None | OperatorCondition
    
    
class OutConnectionsPartition:
    standards: list[NodeLink]
    errors: list[NodeLink]


