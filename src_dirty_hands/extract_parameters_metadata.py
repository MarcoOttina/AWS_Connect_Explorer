import json

from files_lister import list_all_files
#from block_names import BLOCK_NAMES
import block_names


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
                    #print("IN BLOCK, param_name:", param_name, "->", param_block_data)
                    
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
            
            params_grouped_by_owning_block[id_block] = {
                'block_id' : id_block,
                'parameters': all_parameters_current_block,
                'block_type': block['Type'],
                'transitions': transitions
            }
        
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
    
    map_BlockType_group = block_names.flatten_block_names( block_names.BLOCK_NAMES )
    
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
                block_group = block_names.extract_group_from_complete_group(block_group_data['group'])
                # for instances: 'flow_set', 'to_queues', 'to_wait_flows', 'ends', 'resume_flows', ...
            else:
                block_group = 'unclassified'
                block_group_data = block_names.new_block_name_metadata(block_type, block_type)
    
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