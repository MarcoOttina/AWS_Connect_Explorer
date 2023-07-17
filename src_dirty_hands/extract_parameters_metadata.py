import json
from typing import Callable
from collections.abc import Mapping

from files_lister import list_all_files
#from block_names_groups import BLOCK_NAMES
import block_names_groups

#global parameter_extracted_type_to_index
parameter_extracted_type_to_index:dict[str,int] = {
    'null': 0, 'None': 0, 'nil': 0, 'NULL': 0, \
    'list': 1, 'array': 1, \
    'dict': 2, 'dictionary': 2, 'map': 2, \
    'int': 3, 'integer': 3, \
    'double': 4, 'float': 4, 'number': 4, \
    'bool': 5, 'boolean': 5, \
    'string': 6, 'str': 6, 'char': 6, \
}
#global parameter_extracted_type_to_pythonic_type
parameter_extracted_type_to_pythonic_type:dict[str, str] = {
    'null': 'None', 'None': 'None', 'nil': 'None', 'NULL': 'None' \
    'string': 'str', 'str': 'str', 'char': 'str', \
    'list': 'list', 'array': 'list', \
    'dict': 'dict', 'dictionary': 'dict', 'map': 'dict', \
    'int': 'int', 'integer': 'int', \
    'double': 'double', 'float': 'double', 'number': 'double', \
    'bool': 'bool', 'boolean': 'bool'
}


def extract_type_name(val):
    if val is None:
        return 'None'
    t = type(val)
    s = str(t)
    module = str(t.__module__)
    if module == 'builtins':
        return s[8: -2] # "<class '...THE_CLASS...'>"
    else:
        return s[8: -2][len(module)+1 :]


def extract_filename(filename_and_extension):
    file_name = filename_and_extension
    i_dot = file_name.rfind('.')
    if i_dot > 0:
        file_name = file_name[ : i_dot]
    return file_name


__extractors:dict[str, Callable[[dict,dict], dict]] | None = None
def extract_connect_parameters(block_data, metadata) -> dict | None :
    global __extractors
    
    type_block = block_data['Type']
    
    if __extractors is None:
        
        def audio_extractor (bd, meta):
            params_block = bd['Parameters']
            audio_value = ""
            audio_arn = ""
            arn_value_set = False
            to_check_onto = params_block
            
            if 'Messages' in params_block:
                to_check_onto = params_block['Messages'][0]
                
            if ('PromptId' in to_check_onto):
                audio_arn = to_check_onto['PromptId']
                audio_value = audio_arn
                arn_value_set = True
            elif ('Text' in to_check_onto) or ('SSML' in to_check_onto):
                audio_value = to_check_onto['Text' if 'Text' in to_check_onto else 'SSML']
                arn_value_set = True
           
            if ("".__eq__(audio_arn)) and ( 'audio' in meta and len(meta['audio']) > 0):
                meta_audio = meta['audio'][0]
                if "".__eq__(audio_value):
                    audio_value = meta_audio['text'].strip() if 'text' in meta_audio else ""
                if audio_value.startswith('arn'):
                    audio_arn = audio_value
                    arn_value_set = True
                elif 'id' in meta_audio:
                    audio_arn = meta_audio['id']
                    arn_value_set = True
                if "".__eq__(audio_value):
                    audio_value = audio_arn
                    arn_value_set = True
            
            if ('parameters' in meta) and ('PromptId' in meta['parameters']) :
                audio_value = meta['parameters']['PromptId']
                arn_value_set = True
            elif 'promptName' in meta:
                audio_value = meta['promptName']
                arn_value_set = True
            
            print("audio_value 0 -> ", audio_value)
            if  (isinstance(audio_value, Mapping) or (type(audio_value) is dict)) \
                and ('promptName' in audio_value):
                audio_value = audio_value['promptName']
                print("\taudio_value 1 -> ", audio_value)
                
            if not arn_value_set:
                print("\n\nERROR: nothing set in block with type ", bd['Type'], "; and ID: ", bd['Identifier'])
       
            return { \
                'name': "Text", \
                'type': "prompt", \
                'display_name': audio_value, \
                'arn': audio_arn, \
                'value': audio_value, \
                'value_type': 'str'
            }
            
        def null_return(bd,meta):
            return None
        
        __extractors = {
            'MessageParticipantIteratively' : audio_extractor,
            'MessageParticipant': audio_extractor,
            'GetParticipantInput': audio_extractor,
            'Compare': lambda bd, meta: {
                'name': "CompareValues", \
                'type': "check", \
                'display_name': 'Check', \
                'arn': '', \
                'value': { \
                    'comparisonValue': bd['Parameters']['ComparisonValue'], \
                    'values': [v for v in map( \
                        lambda condition: condition['Condition']['Operands'][0], \
                        bd['Transitions']['Conditions'])]
                },
                'value_type': 'list'
            },
            'UpdateContactTargetQueue': lambda bd, meta: { \
                'name': "QueueID", \
                'type': "set", \
                'display_name': meta['queue']['text'], \
                'arn': bd['Parameters']['QueueId'], \
                'value': bd['Parameters']['QueueId'], \
                'value_type': 'string'
            },
            'UpdateContactAttributes': lambda bd, meta: {
                'name': "Attributes", \
                'type': "set", \
                'display_name': 'Set Contact Attribute', \
                'arn': '', \
                # [(k,v) for k, v in bd['Parameters']['Attributes'].items()]
                'value': bd['Parameters']['Attributes'], \
                'value_type': 'dict'
            },
            'Loop': lambda bd, meta: {
                'name': "Loop", \
                'type': "loop", \
                'display_name': 'Loop', \
                'arn': '', \
                'value': bd['Parameters']['LoopCount'] if 'LoopCount' in bd['Parameters'] else 0, \
                'value_type': 'int'
            },
            'UpdateContactEventHooks': lambda bd, meta:{
                'name': [k for k,v in bd['Parameters']['EventHooks'].items()][0], \
                'type': "set", \
                'display_name': [v['displayName'] for k,v in meta['parameters']['EventHooks'].items()][0], \
                'arn': [v for k,v in bd['Parameters']['EventHooks'].items()][0], \
                'value': [v for k,v in bd['Parameters']['EventHooks'].items()][0], \
                'value_type': 'str'
            },
            'CheckHoursOfOperation':lambda bd, meta: {
                'name': "CheckWO", \
                'type': "check", \
                'display_name': meta['parameters']['HoursOfOperationId']['displayName'], \
                'arn': bd['Parameters']['HoursOfOperationId'], \
                'value': bd['Parameters']['HoursOfOperationId'], \
                'value_type': 'str'
            },
            'InvokeLambdaFunction': lambda bd, meta: {
                'name': "InvokeLambdaFunction", \
                'type': "lambda", \
                'display_name': 'Lambda', \
                'arn': bd['Parameters']['LambdaFunctionARN'], \
                    #[(k,v) for k, v in bd['Parameters'].items()]
                'value': bd['Parameters'], \
                'value_type': 'dict'
            },
            # TODO: finish implementing types
            'DisconnectParticipant': null_return,
            'TransferToFlow': null_return,
            'TransferContactToQueue': null_return,
            'EndFlowExecution': null_return,
            'CheckMetricData': null_return,
            'UpdateContactRecordingBehavior': null_return,
            'UpdateContactTextToSpeechVoice': null_return
        }
    
    if type_block not in __extractors:
        print("\n\n----------------------\nERROR: unrecognized type block:", type_block)
        print("block: ", block_data)
        print("meta: ", metadata)
        return None
    
    p =__extractors[type_block](block_data, metadata)
    if p is not None:
        s = p["value_type"]
        s = parameter_extracted_type_to_pythonic_type[s]
        p["value_type"] = s
        p["value_type_index"] = parameter_extracted_type_to_index(s)
    return p


def extract_params_from_file(filename, folder_files):
    print(filename)
    
    #list of all blocks info, holding all datas
    #all_blocks_params:list[dict] = []
    params_grouped_by_owning_block:dict[dict] = {}
    
    entry_point = {
        'id': "",
        'block_type': "",
    }
    
    file_name = extract_filename(filename)

    with open(f'{folder_files}/{filename}') as f:
        data = json.load(f)
        
        id_starting_point = data['StartAction']
        entry_point['id'] = id_starting_point
        
        #for each block (whose ID is the key of the dictionary below),
        # collect each parameter in a dictionary (the parameter's name is
        # this last dictionary's key)

        metadata_parameters_by_id_block:dict[str, dict[str, dict[str, dict|object|str|bool|int|float|None]|object|str|bool|int|float|None]] = {} # blockID -> (name -> param|something 
        dynamic_params:dict[str,bool] = {}
        
        for id_block, metadata in data['Metadata']['ActionMetadata'].items():
            
            # read the "metadata" parameters, collecting all of them (except for the GUI-related 'position') 
            if 'dynamicParams' in metadata:
                for param_name in metadata['dynamicParams']:
                    dynamic_params[param_name] = True

            params_list:list[dict] = []
            
            # 'parameters' is a dictionary
            if 'parameters' in metadata:
                params_list:list[dict] = [ \
                        {'name': name, 'value': value, 'is_dynamic': False, 'is_explicitly_a_parameter': True, 'type_python':extract_type_name(value)} \
                        for (name, value) in metadata['parameters'].items() \
                    ]
            # other non-'position' parameters are unknown in general
            for metadata_name, metadata_value in metadata.items():
                if metadata_name != 'dynamicParams' and metadata_name != 'position':
                    '''
                    Deprecated: DO NOT UNPACK lists or dictionaries
                    
                    param_iteration = None
                    if type(metadata_value) == dict:
                        param_iteration = metadata_value.items()
                    elif type(metadata_value) == list:
                        param_iteration = map(lambda x: (metadata_name, x), metadata_value)
                    else:
                        param_iteration = map(lambda x: (metadata_name, x), [metadata_value])
                        
                    params_list.extend([ \
                        {\
                            'name': name, \
                            'value': value, \
                            'is_dynamic': (value if type(value) == bool else ( str(value).strip().lower() == 'true')), \
                            'is_explicitly_a_parameter': False, \
                            'type_python':extract_type_name(value) \
                        } \
                        for (name, value) in param_iteration \
                    ])
                    '''
                    params_list.append( { \
                            'name': metadata_name, \
                            'value': metadata_value, \
                            'is_dynamic': True if metadata_name in dynamic_params else \
                                # string-formatted conversion into bool
                                (metadata_value if type(metadata_value) == bool else ( str(metadata_value).strip().lower() == 'true')), \
                            'is_explicitly_a_parameter': False, \
                            'type_python':extract_type_name(metadata_value) \
                        })
            
            params_metadata_by_params_name:dict = {}
            for param_metadata in params_list:
                #print("NAMEH ->", param_metadata['name'])
                params_metadata_by_params_name[param_metadata['name']] = param_metadata
            metadata_parameters_by_id_block[id_block] = params_metadata_by_params_name
        

        for block in data['Actions']:
            id_block = block['Identifier']
            block_params:dict[str, str|dict|int|float|bool|None]|None = block['Parameters'] if 'Parameters' in block else None # "name" -> "value"
            
            all_parameters_current_block:dict[str, int|bool|str|dict|None|float] = {}
            
            metadata_each_params: dict[str, dict|int|bool|str|None|float] = metadata_parameters_by_id_block[id_block] # data read from the "Metadata" section
            
            has_block_params = block_params is not None and len(block_params) > 0
            if has_block_params:
                #has_metadata_corrispondance = metadata_each_params is not None ## DEPRECATED / NOT USED
                
                for param_name, param_block_data in block_params.items():
                    #try to merge parameters
                    
                    metadata_of_current_param:dict | None = metadata_each_params[param_name] if param_name in metadata_each_params else None
                    has_current_param_metadata = metadata_of_current_param is not None

                    full_parameter_data = {
                        'id_owner_block': id_block, #its owning block
                        "param_name": param_name,
                        # not merged, but ... "collected", at least ...
                        "value":{
                            "from_metadata": metadata_of_current_param['value'] if has_current_param_metadata else None,
                            "from_block": param_block_data
                        },
                        "is_dynamic": param_name in dynamic_params,
                        'is_explicitly_a_parameter': True,
                        'type_python': metadata_of_current_param['type_python'] if has_current_param_metadata else extract_type_name(param_block_data),
                    }
                    all_parameters_current_block[param_name] = full_parameter_data
                    
                    # OLD-TODO: verificare se il nome da "metadata" e quello da "block.Parameters" fossero uguali, se si unirli in un unicum
                    
            # add remaining non-block params data
            for param_name, param_data in metadata_each_params.items():
                if (not has_block_params) or param_name not in block_params:
                    #print("IN METADATA, param_name:", param_name, "->", param_data)
                    
                    full_parameter_data = {
                        'id_owner_block': id_block, #its owning block
                        "param_name": param_name,
                        # not merged, but ... "collected", at least ...
                        "value":{
                            "from_metadata": param_data['value'],
                            "from_block": None
                        },
                        "is_dynamic": param_data['is_dynamic'],
                        'is_explicitly_a_parameter': param_data['is_explicitly_a_parameter'],
                        'type_python': param_data['type_python'],
                    }
                    all_parameters_current_block[param_name] = full_parameter_data
            
            transitions:list[dict] = []
            transitions_data:dict = block['Transitions']
            if 'NextAction' in transitions_data:
                transitions.append({
                    'next_node_ID':transitions_data['NextAction'],
                    'is_correct': True,
                    'additional_data': 'default_link'
                    })
            if 'Conditions' in transitions_data:
                transitions.extend( \
                    [ \
                        cc for cc in map(
                            lambda c: { \
                                'next_node_ID':c['NextAction'], \
                                'is_correct': True, \
                                'additional_data': c['Condition'] \
                            },
                            transitions_data['Conditions']
                        ) \
                    ]
                )
            if 'Errors' in transitions_data:
                transitions.extend( \
                    [ \
                        cc for cc in map(
                            lambda c: { \
                                'next_node_ID':c['NextAction'], \
                                'is_correct': False, \
                                'additional_data': c['ErrorType'] \
                            },
                            transitions_data['Errors']
                        ) \
                    ]
                )
            
            #metadata_current_block = data['Metadata']
            metadata_ = data['Metadata']['ActionMetadata']
            if id_block not in metadata_:
                print("what is this block not having a ActionMetadata object associated with? \n\tID:", id_block, ", type:", block['Type'])
            
            params_grouped_by_owning_block[id_block] = {
                'block_id' : id_block,
                'parameters': all_parameters_current_block,
                'block_type': block['Type'],
                'transitions': transitions,
                'parameters_extracted_by_hand': extract_connect_parameters(block, metadata_[id_block]) if id_block in metadata_ else None
            }
            
            #print("\n\nall_parameters_current_block, for block with ID: ", id_block, ", and type: ",  block['Type'], " holds:")
            #print(all_parameters_current_block)
        
        entry_point['block_type'] = params_grouped_by_owning_block[id_starting_point]['block_type']
        
        #
        # now collect all "exit-points" (redirections to numbers, to queue and to wait flows)
        #exit_points
        
        #p = (data['']) ??????????????
        
    return {
        'filename': file_name,
        'blocks': params_grouped_by_owning_block,
        'entry_point': entry_point,
    }

#
#
#

def extract_params_all_files():
    folder_files = "./resources/FCAB-BE"
    jsons = list_all_files(folder_files, allowed_extension='json', import_os_required=True)

    parameters_by_file:dict[str,list[dict]] = {} # for each filename, stock the list of each blick (which hold its relative parameters, somewhere)
    for file in jsons:
        params_grouped_by_owning_block = extract_params_from_file(file, folder_files)
        parameters_by_file[ extract_filename(file) ] = params_grouped_by_owning_block
    return parameters_by_file

#
#
#

def extract_graph_structure_data(flows_dict):
    flows_with_gS = {}
    
    map_BlockType_group = block_names_groups.flatten_block_names( block_names_groups.BLOCK_NAMES )
    
    for flow_name, flow in flows_dict.items():
        blocks:dict = flow['blocks']
        
        block_groups = {
            'to_flows': {},
            'to_queues': {},
            'to_wait_flows': {},
            'resume_flows':{},
            'unclassified': {}
        }
        
        flow_structure =  {
            'filename': flow['filename'],
            'blocks': flow['blocks'],
            'entry_point': flow['entry_point'],
            'block_groups': block_groups
        }
        
        for block_id, block_data in blocks.items(): # "_" == "block_id"
            grouped_blocks_mapped_by_id = None
            block_group_data = None
            
            block_type = block_data['block_type'] # e.g., "TransferToFlow", "Loop", "MessageParticipant", "CheckHoursOfOperation", ..
            if block_type in map_BlockType_group:
                block_group_data = map_BlockType_group[block_type]
                block_group = block_names_groups.extract_group_from_complete_group(block_group_data['group'])
                # for instances: 'flow_set', 'to_queues', 'to_wait_flows', 'ends', 'resume_flows', ...
            else:
                block_group = 'unclassified'
                block_group_data = block_names_groups.new_block_name_metadata(block_type, block_type)
    
            if block_group in block_groups:
                grouped_blocks_mapped_by_id = block_groups[block_group] 
            else:
                grouped_blocks_mapped_by_id = {}
                block_groups[block_group] = grouped_blocks_mapped_by_id
                
            grouped_blocks_mapped_by_id[block_id] = block_group_data

        
        flows_with_gS[flow_name] = flow_structure

    return flows_with_gS

#
#
#

def merge_flow_graphs(flows_data):
    '''
    NOTA 1:
    per effettare il merge, bisogna:
    -) raggruppare tutte le direzioni per destinazione (così che se ci fossero
        2+ RedirectToXYZ allora la stessa sostituzione dovrà essere fatta per tutti)
    -) cercare tutti i link in uscita (di altri nodi) che puntano a ciascuna di queste
        redirezioni in questi gruppi (insomma, si forma una fetta di ipergrafo in cui i vertici
        di ogni arco sono insieme di "nodi con link uscenti)
    '''
    pass

#
#
#
#
#
        
if __name__ == "__main__":
    p = extract_params_all_files()
    print("extracted, now dump")
    with open('./output/parameters_compacted.json', 'w') as f:
        json.dump(p, f)
    print("dumped")
    
    g_s = extract_graph_structure_data(p)
    print("extracted graph structure, now dump")
    with open('./output/graph_structure.json', 'w') as f:
        json.dump(g_s, f)