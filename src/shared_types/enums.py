from enum import Enum



class OutBranchType(Enum):
    Direct = 1
    EventTriggered = 2
    Check = 3
    Prompt = 4
    
    
class NodeType(Enum):
    PlayPrompt = 1
    Check = 2
    SetCustomAttributes = 3
    Termination = 4
    LambdaCall = 5
    # TODO : add other types

def Node_type_from_str(Node_type):
    if not Node_type:
        return None
    
    if Node_type == "PlayPrompt":
        return NodeType.PlayPrompt
    elif Node_type == "Check":
        return NodeType.Check
    elif Node_type == "SetCustomAttributes":
        return NodeType.SetCustomAttributes
    elif Node_type == "Termination":
        return NodeType.Termination
    elif Node_type == "LambdaCall":
        return NodeType.LambdaCall
    
    return None



class Operators(Enum):
    Equal = '=='
    NotEqual = '!='
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    
    
class DataType(Enum):
    int = 'int'
    float = 'float'
    bool = 'bool'
    String = 'String'
    ARN = 'ARN'
    AudioFile = 'AudioFile'
    PhoneNumber = 'PhoneNumber'
    # TODO : are there any others?
    
    


# VDN Path related end type
class VDNPathEndType(Enum):
    Standard = 1
    Loop = 2
    # TODO : others?