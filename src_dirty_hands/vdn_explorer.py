
import os
import json
from vdn_graph_types import *
from block_names_groups import BLOCK_NAMES

BLOCK_NAMES_REDIRECT_TO_FLOW = [
    BLOCK_NAMES['exit_points']['to_flows'].block_type,
    BLOCK_NAMES['exit_points']['to_wait_flows'].block_type,
    BLOCK_NAMES['exit_points']['to_queues'].block_type,
]

BLOCK_TYPES_ENDS = [
    BLOCK_NAMES['exit_points']['to_flows'].block_type,
    BLOCK_NAMES['exit_points']['to_wait_flows'].block_type,
    BLOCK_NAMES['exit_points']['to_queues'].block_type,    
]
BLOCK_TYPES_ENDS.extend(map( \
        lambda b: b.block_type, \
        BLOCK_NAMES['exit_points']['ends']
    ))


def outputJsonFile(json_obj, name, subfolder, pre_processing=None):
    folder_file = f'./output/{subfolder}'
    os.makedirs(folder_file, exist_ok=True)

    filename = f'{folder_file}/{name}.json'
    with open(filename, 'w') as f:
        print("writing", name)
        if pre_processing is not None:
            json_obj = pre_processing(json_obj)
        s = ""
        if isinstance(json_obj, Jsonable):
            s = json_obj.to_json()
        else:
            s = json.dumps(json_obj)
        f.write(s)
        print(name, "written")
    return json_obj



#
# read and load graph

#
class FlowRead:
    name:str
    startBlockID:str
    output_folder:str|None
    blocks:dict|None
    def __init__(self, \
        name:str, \
        startBlockID:str, \
        output_folder:str|None, \
        blocks:dict|None \
    ) -> None:
        self.name = name
        self.startBlockID = startBlockID
        self.output_folder = output_folder
        self.blocks = blocks




def read_flows_from_files(file_list, pick_metadata: bool = False) -> map:
    '''
    flows_data = [None] * len(file_list)
    for index, file_name in enumerate(file_list):
        with open(file_name) as f:
            flows_data[index] = json.load(f)
    return filter(lambda d: d is not None, flows_data)
    '''
    
    def loader_flow(filename_flow_current):
        flow_details = {}
        with open(f'./resources/{filename_flow_current["res_folder"]}/{filename_flow_current["name"]}.json', 'r') as f:
            flow_details = json.load(f)

        result = {
            'name': filename_flow_current["name"],
            'output_folder': filename_flow_current['output_folder'],
            'startBlockID': flow_details['StartAction'],
            'blocks': flow_details['Actions']
        }
        if pick_metadata:
            result['metadata'] = flow_details['Metadata']
    return map(loader_flow, file_list)

def out_links_from_raw_data(raw_block_data:dict) -> dict[str, list[dict]]:
    transitions_data:dict = raw_block_data['Transitions']

    transitions: dict[str, list[dict]] = {
        'correct': [],
        'errors': []
    }

    if 'NextAction' in transitions_data:
        transitions['correct'].append({
            'next_node_ID':transitions_data['NextAction'],
            'is_correct': True,
            'additional_data': 'default_link'
            })
    if 'Conditions' in transitions_data:
        transitions['correct'].extend( \
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
        transitions['errors'].extend( \
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
    return transitions


def load_flow_blocks_into_graph(
    graph: GraphVDN, \
    flow_details: dict, \
    ):
    raw_block_data = flow_details['blocks']
    
    def original_data_setter(node: GraphVDNNode, node_data: object | dict):
        node.block_type = node_data['Type']
        # TODO: is there any more data to be extracted? like "Parameters" from the super "metadata" field (i.e., the "flow_details" variable)

    # graph nodes creation
    for rod in raw_block_data:
        is_end = False
        graph.add_node_block(
            rod, rod['Identifier'], is_end, original_data_setter)
        
    # out link (i.e., edges) creation
    for rod in raw_block_data:
        id_node = rod['Identifier']
        node = graph.node_by_id(id_node)
        transitions = out_links_from_raw_data(rod)
        corrects = transitions['correct']
        for c_l in corrects:
            node.add_node_id_to_link_out() # TODOOOOOOOOOOOOOOOO AGGIUNGERE LINK
    
    graph.recalculate_ends(
        block_types_of_ends= BLOCK_TYPES_ENDS, \
        is_selfLoop_marking_end=True, \
        # node_end_check=
    )
    # TODO: usare anche  redirection_checker: (Callable[[GraphVDNNode,dict], bool]|None)
    # and redirection_data_extractor: (Callable[ [GraphVDNNode,dict], dict['name':str,'arn':str]]|None)
    # raccogliere questi dati

def gather_redirection_metadata(graph: GraphVDN, raw_graph_data: dict):
    pass
    # TODO: ottenere tutte le "ends", percorrerle e raccogliere tutte le redirezioni
    # nota: alcune di esse (TransferContactToQueue) impostano il flow PRIMA di 
    # invocare tale coda, oppure ereditano in qualche variabile il riferimento al
    # waitflow: collezionare tale dato per impostare bene la redirezione

def graph_from_flow_raw_data( \
        raw_data:dict \
        #, redirection_checker: (Callable[[GraphVDNNode,dict], bool]|None) = None , \
        #, redirection_data_extractor: (Callable[ [GraphVDNNode,dict], dict['name':str,'arn':str]]|None) = None \
    ) -> GraphVDN:
    gsMetadata: GraphStructuralMetadata = GraphStructuralMetadata(
        # redirection_checker = redirection_checker, \
        # redirection_data_extractor = redirection_data_extractor \
    )
    graph = GraphVDN( \
        startID = raw_data['startBlockID'], \
        name = raw_data['name'], \
        graphStructuralMetadata = gsMetadata
    )
    gsMetadata.set_graph(graph)
    load_flow_blocks_into_graph(graph, raw_data)
    
    ends = graph.get_all_ends()
    #
    # TODO : c'e' altro da fare qui???
    # tipo ... compose_flow_data_metadata
    #
    return graph
    

def compose_flow_data_metadata(flows_raw_data:list, phone_numbers: list):
    '''
    Raw data is devided between "metadata", holding GUI-related data and reoursecs names/values taken as inputs,
    and "actions", which are the actual block composing the actual flow.
    The goal is to unify this scattered data into single structures while also collecting data for the whole
    network, like the "placeholders" (eg: "transfer_to_flow") requiring to be resolved
    ''' 
    pass


def resolve_flow_redirections(graphs:dict[str, GraphVDN]) -> list[GraphVDN]:
    pass

#
# main
#

def by_hand_list_filenames(folder_files):
    from files_lister import list_all_files
    '''
    pure_names = [
        "CustomerCareWaitFlowDutch",
        "CustomerCareWaitFlowFrench",
        "CustomerCareWorkFlow",
        "Dealer Workflow Test Tom",
        "LMSInboundFlow",
        "TransferToAgentWhisper"
    ]
    '''
    pure_names = list_all_files(folder_files, 'json', True)
    return [ff for ff in map(lambda fn: f'{folder_files}{fn}', pure_names)]

def check_node_is_redirection(node:GraphVDNNode, raw_data: dict) -> bool:
    return node.block_type in BLOCK_NAMES_REDIRECT_TO_FLOW

def extract_redirection_data(node: GraphVDNNode, raw_data: dict) -> dict['name':str,'arn':str]:
    return {
        'name': node.block_type,
        'arn': None #todo
    }



#
#
#

def main():
    print("start")
    filenames = by_hand_list_filenames('./resources/FCAB-BE/')
    flows_data = read_flows_from_files(filenames)
    filenames = None
    
    graphs_by_filename: dict[str, GraphVDN] = {}
    for flow in flows_data:
        graph = graph_from_flow_raw_data( \
            flow, \
            redirection_checker = check_node_is_redirection, \
            redirection_data_extractor =    
        )
        graphs_by_filename[graph.name] = graph
        
    solved_graphs:list[GraphVDN] = resolve_flow_redirections(graphs_by_filename)
    
    for e in map( lambda g: (g.get_all_ends(), g), solved_graphs):
        outputJsonFile(e[0], e[1].name, 'paths/', pre_processing=None )

if __name__ == "__main__":
    main()