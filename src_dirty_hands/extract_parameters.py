import json

from files_lister import list_all_files

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


def extract_params():
    folder_files = "./resources/FCAB-BE"
    jsons = list_all_files(folder_files, allowed_extension='.json', import_os_required=True)

    parameters_by_file:dict[str,list[dict]] = {} # for each filename, stock the list of each blick (which hold its relative parameters, somewhere)
    for file in jsons:
        print(file)
        
        #list of all blocks info, holding all datas
        #all_blocks_params:list[dict] = []
        params_grouped_by_owning_block:dict[dict] = {}
            
        with open(f'{folder_files}/{file}') as f:
            data = json.load(f)
            
            #for each block (whose ID is the key of the dictionary below),
            # collect each parameter in a dictionary (the parameter's name is
            # this last dictionary's key)
            
            #metadata_parameters_by_id_block:dict[str, dict|object] = {}
            #metadata_parameters_by_id_block:dict[str, list[dict]] = {}
            metadata_parameters_by_id_block:dict[str, dict[str, dict[str, dict|object|str|bool|int|float|None]|object|str|bool|int|float|None ]] = {} # blockID -> (name -> param|something
            # blocks_by_id:dict[str, dict|object] = {}
            
            dynamic_params:dict[str,bool] = {}
            
            for id_block, metadata in data['Metadata']['ActionMetadata'].items():
                
                #print("....for block '", id_block, "', got metadata:", metadata)
                
                # read the "metadata" parameters, collecting all of them (except for the GUI-related 'position')
                
                if 'dynamicParams' in metadata:
                    for param_name in metadata['dynamicParams']:
                        dynamic_params[param_name] = True

                params_list:list[dict] = []
                # 'dynamicParams' is an array
                '''
                params_list:list[dict] = [ \
                        {'name': p, 'value': "", 'is_dynamic': True, 'is_explicitly_a_parameter': True, 'type_python':'null'} \
                        for p in metadata['dynamicParams'] \
                    ] if 'dynamicParams' in metadata else []
                '''
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
            
            #p = (data['']) ??????????????
            
        parameters_by_file[ file ] = {
            'filename': file,
            'blocks': params_grouped_by_owning_block
        }
    return parameters_by_file
        
if __name__ == "__main__":
    p = extract_params()
    print("extracted, now dump")
    with open('./parameters_compacted.json', 'w') as f:
        json.dump(p, f)
    print("dumped")