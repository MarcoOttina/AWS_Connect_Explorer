import uuid

from shared_types.enums import NodeType, OutBranchType
from shared_types.connect_types import DataManipulated


class GraphNode:
    ID: uuid
    type: NodeType
    isBranchingPoint: bool
    outConnections: OutBranchType
    totalDataManipulated: DataManipulated
    
