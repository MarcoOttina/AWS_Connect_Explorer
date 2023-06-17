from enum import Enum



class OutBranchType(Enum):
    Direct = 1
    EventTriggered = 2
    Check = 3
    Prompt = 4
    
    
class BlockType(Enum):
    PlayPrompt = 1
    Check = 2
    SetCustomAttributes = 3
    Termination = 4
    LambdaCall = 5
    # TODO : add other types

def block_type_from_str(block_type):
    if not block_type:
        return None
    
    if block_type == "PlayPrompt":
        return BlockType.PlayPrompt
    elif block_type == "Check":
        return BlockType.Check
    elif block_type == "SetCustomAttributes":
        return BlockType.SetCustomAttributes
    elif block_type == "Termination":
        return BlockType.Termination
    elif block_type == "LambdaCall":
        return BlockType.LambdaCall
    
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