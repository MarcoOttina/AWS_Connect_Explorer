def new_block_name_metadata(block_type, name, parameters: dict|None = None):
    return {
        "block_type": block_type,
        "display_name": name,
        "parameters": parameters
    }


def __t(block_type, name, parameters: dict|None = None):
    return new_block_name_metadata(block_type, name, parameters)

def new_parameters_block_name_metadata(from_block, from_metadata):
    return {
        "from_action": from_block,
        "from_metadata": from_metadata
    }

def __p(from_block, from_metadata):
    return new_parameters_block_name_metadata(from_block, from_metadata)

BLOCK_NAMES = {
    "exit_points": {
        "to_flows": [
            __t("TransferToFlow", "Transfer to flow")
        ],
        "to_queues": [
            __t("TransferContactToQueue", "Transfer to queue")
        ],
        "to_wait_flows": [
            __t("TransferContactToQueue", "Transfer to wait flow")
        ],
        "resume_flows": [
            __t("EndFlowExecution", "End flow / Resume")
        ],
        "ends": [ 
            __t("DisconnectParticipant", "Disconnect"),
            __t("Loop", "Loop")
        ]
        # , "test": { "t1": [t("t1", "t1"),t("t1.5", "t1.5")], "t2": __t("t2", "t2"), }
    },
    "flow_set": [
        __t("UpdateContactEventHooks", "Set customer queue flow")
    ],
    "prompts": [
        __t("MessageParticipant", "Play prompt"),
        __t("MessageParticipantIteratively", "Loop prompts", __p(["Attributes", "TragetContact"], [ "parameters->Attributes", "dynamicParams"]) )
    ],
    "vars_set": [
        __t("UpdateContactAttributes", "Set contact attributes", __p(["Attributes", "TragetContact"], [ "parameters->Attributes", "dynamicParams"]))
    ],
    "branching": [
        __t("CheckHoursOfOperation", "Check Working hours", __p(["HoursOfOperationId"], ["HoursOfOperationId", "Hours"])),
        __t("Compare", "Check / switch", __p(["ComparisonValue"], ["conditions", "conditionsMetadata"])),
        __t("CheckMetricData", "CheckMetricData", __p(["MetricType"], ["conditionMetadata", "useDynamic"]))
    ],
    "external_services": [
        __t("InvokeLambdaFunction", "Invoke Lambda function", __p(["LambdaFunctionARN", "InvocationTimeLimitSeconds", "ResponseValidation"], ["dynamicMetadata"]))
    ]
}

__group_key_name = 'group'

def __flat_dict(d, r, base_group:str = None):
    for gn, g in d.items():
        group_name = gn.strip()
        if group_name != __group_key_name and (not group_name.startswith(f'{__group_key_name}.')):
            
            if type(g) == dict and ( \
                    ("block_type" not in g) and\
                    ("display_name" not in g) \
                ):
                __flat_dict(g, r, group_name if base_group is None else f'{base_group}.{group_name}')

            elif type(g) == list:
                    
                for elem in g:
                    elem[__group_key_name] = \
                        group_name if base_group is None else \
                        f'{base_group}.{group_name}'

                    r[elem['block_type']] = elem
            else:
                g[__group_key_name] = \
                    group_name if base_group is None else \
                    f'{base_group}.{group_name}'
                if 'block_type' in g:
                    r[g['block_type']] = g


def flatten_block_names(bl):
    r = {}
    __flat_dict(bl, r)
    return r

__block_types_to_group = None
def get_block_types_to_group():
    global __block_types_to_group
    if __block_types_to_group is None:
        __block_types_to_group = flatten_block_names(BLOCK_NAMES)
    return __block_types_to_group


def extract_group_from_complete_group(complete_group_name):
    dot_index = complete_group_name.rfind('.')
    if dot_index < 0:
        return complete_group_name
    return complete_group_name[dot_index+1 :]


if __name__ == "__main__":
    import json
    print("->")
    fbn = get_block_types_to_group()
    
    print(fbn)
    with open('./output/bn.json', 'w') as f:
        json.dump(fbn, f)
    
    example_complete_group = "exit_points.test.t2"
    
    print("\n\n", example_complete_group, " -> extraction... -> ", extract_group_from_complete_group(example_complete_group))
    print(extract_group_from_complete_group("hello world"))
        