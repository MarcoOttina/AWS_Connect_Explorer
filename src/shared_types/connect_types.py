import uuid

from shared import DataResource, OperatorCondition
from enums import OutBranchType

class DataManipulated:
    input: list[DataResource]
    set: list[DataResource]


class BlockLink:
    to: uuid
    type: OutBranchType
    isStandard: bool
    condition: None | OperatorCondition
    
    
class OutConnectionsPartition:
    standards: list[BlockLink]
    errors: list[BlockLink]


