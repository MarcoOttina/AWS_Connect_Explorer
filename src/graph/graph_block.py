import uuid

from ..shared_types.enums import BlockType, OutBranchType
from ..shared_types.connect_types import DataManipulated


class GraphBlock:
    ID: uuid
    type: BlockType
    isBranchingPoint: bool
    outConnections: OutBranchType
    totalDataManipulated: DataManipulated
    
