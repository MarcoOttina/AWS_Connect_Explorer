import json
import boto3
import os
from typing import Callable

__env = {"region": "eu-central-1", "aws_access_key_id": "ASIASA3T6Q2TEW5NQ27W", "aws_secret_access_key": "l7k+h5mG73oASI/VQSP8eqvzy1UxTzASs17ARL2o", "aws_session_token": "IQoJb3JpZ2luX2VjEE4aCXVzLWVhc3QtMSJHMEUCIF3aWZhHc29jwUOoGRyjActjViAcZ/PsxXfWLp2NulfxAiEAzmQfhEgvfQaYzqRMNLSzYxfqVwWb3PsYQ4CfBmI1QBIqvQMIp///////////ARACGgwxMzkyOTI3MzkyMzgiDFJdQz3hYh0mb8Iv9SqRA4zCkRLmn+rffAJjZP9Sqb/drg3WJZrIDLHdWf1ZRihargNf7WqX7onlWsNPBbkQbQu07eEem0ClzpTqymS6B06AoID255Xk7RnOVEFWpOmitvZ9iuJqy5rVG3Kpdixst96v524/KSnJn//yW80z0sqxV9kUL8sLwahUzz8y7rHJOpzX4LxRvydIwMUT8ajGjMYo889okgat/cqHY4dWp3AHrR7sZLyd0zolppmFNKwvfTGAcfMT9qWo670/SPvRAEDp+cpJgBzkRqVtyDPPudQGILFLqIulT3XS8hgEieLyflsGJVksr8xXNCB7PD0umwbep21zIPCwGUBWNuBAxXNtT11IQWVtJXIppjR7T21Ri6NlLXEg5sVQpALg5GLcF8hbrflcCoqD/iWP/6YCkSe/M+4rqBtjOv4muD/34tpXCHGIt1PRPGJdV6UXTXZW4VEpdtK8keNvSNf8d5t4i2vYM+pRveP44I0/xfUMY1Tm5Cs/COV0G0AhSoCX7itcGvaWHDYYXKvlVLJL6fdrgYMiMPndxqQGOqYBw9ixBeH6/jHN0/ogRjGXpo7RcEyGN/Ilvf1o/mczSw5NGEKQ00vm44vrbsIQxwYvKgZoO2b7VnF7EQ8S7JJvFEGmB8NfMjho00/TbcifmBEzmeod3R2nEDxM/UOQ6qkF13bs1Ml2z4e5b+7MPS+aFACaNlW8e8eYuWiwYH3k+mywxShf3uUN+WQRgtxRbkCbhSWQ71PIsij64FDrV7dK4X50KXip/w"}

INSTANCE_DETAILS = {
    "market": "lsys",
    "language": "be",
    "arn": "arn:aws:connect:eu-central-1:139292739238:instance/93903ac6-b964-42d6-8383-3d90ab6799bd"
}


def instance_id_from_ARN(arn: str) -> str:
    return arn[1 + arn.rindex('/') :]


def outputJsonFile(json_obj, instanceIdFlow, what_is_it, pre_processing = None):
    folder_file = f'./output/{INSTANCE_DETAILS["market"]}/{INSTANCE_DETAILS["language"]}'
    os.makedirs(folder_file, exist_ok=True)
    
    filename = f'{folder_file}/{instanceIdFlow}__{what_is_it}.json'
    with open(filename, 'w') as f:
        print("writing", what_is_it)
        if pre_processing is not None:
            json_obj = pre_processing(json_obj)
        f.write(json.dumps(json_obj))
        print(what_is_it,"written")
    return json_obj



#
# CLASSES
#

class Jsonable:
    def to_json(self):
        return self

# just added as documentation, since it's NOT serializable automatically; call "to_json()" for that purpose
class GraphVDNNode(Jsonable):
    id:str # it is a UUID
    original_data: dict
    is_end:bool
    links_out_ids_correct: list[str]
    links_out_ids_error: list[str]
    
    def __init__(self, id:str, is_end: bool):
        self.id = id
        self.is_end = is_end
        self.original_data = {}
        self.links_out_ids_correct = []
        self.links_out_ids_error = []
        
    def to_json(self):
        return {
            "id": self.id,
            "original_data": self.original_data,
            "is_end": self.is_end,
            "links_out_ids_correct": self.links_out_ids_correct,
            "links_out_ids_error": self.links_out_ids_error
        }
        
    def has_link_out(self, node_id):
        return node_id in self.links_out_ids_correct or node_id in self.links_out_ids_error 
        
    def add_node_id_to_link_out(self, node_id:str, is_correct_link:bool):
        if is_correct_link:
            if node_id in self.links_out_ids_correct:
                return False
            self.links_out_ids_correct.append(node_id)
        else:
            if node_id in self.links_out_ids_error:
                return False
            self.links_out_ids_error.append(node_id)
            
        return True
    
    '''
    TODO: aggiungere il parametro "metadata" che permetta di specificare il tipo di errore, se "is_correct_link" fosse falso, o che valore
    e' stato controllato ed e' stato determinante nel definire questa specifica diramazione.
    Quindi, riunire ambo i link sotto una unica collezione, che e' lista di una sovraclasse astratta, le cui due sottoclassi rappresentano
    i link "normali/corretti" ed i link di errore. Es: { 'id_next': str, 'is_correct': bool, 'metadata': dict|object }
    Modificare infine i for_each tali che effettuino dei filtri su quale link invocare la "azione".
    '''
    def add_node_to_link_out(self, node: object | dict, is_correct_link: bool):
        if not isinstance(node, GraphVDNNode):
            return False
        return self.add_node_id_to_link_out(node.id, is_correct_link)
    
    def for_each_link_out_correct(self, action: Callable[[str], None] ):
        for l_o in self.links_out_ids_correct:
            action(l_o)
    def for_each_link_out_error(self, action: Callable[[str], None] ):
        for l_o in self.links_out_ids_error:
            action(l_o)
    def for_each_link_out(self, action: Callable[[str], None] ):
        self.for_each_link_out_correct(action)
        self.for_each_link_out_error(action)
    

class GraphVDN(Jsonable):
    startID:str #UUID formatted
    nodes_by_ID: dict[str, GraphVDNNode]
    ends_IDs: list[str]
    
    def __init__(self, startID):
        self.startID = startID
        self.nodes_by_ID = {}
        self.ends_IDs = []
        
    def to_json(self):
        nodes = {}
        for n_id, n in self.nodes_by_ID.items():
            nodes[n_id] = n.to_json()
        return {
            "startID": self.startID,
            "nodes_by_ID": nodes,
            "ends": self.ends_IDs #[e_id for e_id, _ in nodes]
        }
        
    def add_block(self, original_data, id: str, is_end:bool = False):
        if id in self.nodes_by_ID:
            return
        gNode = GraphVDNNode(id, is_end)
        gNode.original_data = original_data
        self.nodes_by_ID[id] = gNode
        if is_end:
            #self.ends.append(gNode)
            self.ends_IDs.append(id)
            
    def has_node(self, id_node):
        return id_node in self.nodes_by_ID
    
    '''
    TODO: aggiungere il parametro "metadata" che permetta di specificare il tipo di errore, se "is_correct_link" fosse vero, o che valore
    e' stato controllato ed e' stato determinante nel definire questa specifica diramazione
    '''
    def add_link_id(self, id_node_source, id_node_destination, is_correct_link: bool):
        if id_node_source not in self.nodes_by_ID:
            return False
        if id_node_destination not in self.nodes_by_ID:
            return False
        return self.nodes_by_ID[id_node_source].add_node_id_to_link_out(id_node_destination, is_correct_link)

        
    def dfs(self, action:Callable[[GraphVDNNode,GraphVDNNode], None], visited_nodes: dict[str, bool], current_node: GraphVDNNode, father_node: GraphVDNNode):
        if current_node.id in visited_nodes:
            return
        visited_nodes[current_node.id] = True
        action(current_node, father_node)
        
        def dfs_iteration(id_out: str):
            if id_out in visited_nodes:
                return
            self.dfs(action, visited_nodes, self.nodes_by_ID[id_out], current_node)
        current_node.for_each_link_out(dfs_iteration)

    # Depth-First Search
    # scan the whole network, touching each nodes just once, performing an action on each node.
    # The action accepts two parameters: the current node and its father from the root
    # (the father of the root is None).
    def depth_first_search(self, action:Callable[[GraphVDNNode,GraphVDNNode], None]):
        starting_node = self.nodes_by_ID[self.startID]
        visited_nodes: dict[str, bool] = {}
        self.dfs(action, visited_nodes, starting_node, None)
        
    
    def get_all_ends(self):
        # TODO
        print("not implemented yet")
        self.depth_first_search(lambda current_node, father_node: print(('' if father_node is None else father_node.id), "->", current_node.id))
        
        return []
#
# START
#


service = 'connect'
session = boto3.Session(
        aws_access_key_id = __env['aws_access_key_id'],
        aws_secret_access_key = __env['aws_secret_access_key'],
        aws_session_token = __env['aws_session_token']
    )
client = session.client(
        service_name= service,
        region_name= __env['region']
    )


#
#
#

def read_all_flows():
    filename_CustomerCareWorkFlow = 'CustomerCareWorkFlow'
    flow_details = {}
    with open(f'./resources/FCAB-BE/{filename_CustomerCareWorkFlow}.json', 'r') as f:
        flow_details = json.load(f)
    
    return {
        'startBlockID': flow_details['StartAction'],
        'blocks': flow_details['Actions']
    }
    
def load_flow_blocks_into_graph(graph: GraphVDN, flow_details: dict):
    #i = 0
    blocks_original_data = flow_details['blocks']
    #blocks_amount = len(blocks_original_data)
    
    '''
    # use a map ID->node_data to make everything easier
    blocks_original_data_by_id = {}
    for bod in blocks_original_data:
        blocks_original_data_by_id[bod['Identifier']] = bod
        
        #current_node = blocks_original_data_by_id[flow_details['startBlockID']] # WHY?
    '''
    
    def is_end_node(node_data):
        return 'NextAction' not in node_data['Transitions'] #TODO: is a more complicated analysis required?
    
    for bod in blocks_original_data:
        graph.add_block(bod, bod['Identifier'], is_end_node(bod))
    
    #creates the links
    
    for id_start_node, node in graph.nodes_by_ID.items():
        out_nodes_data = node.original_data['Transitions']
        
        if 'Conditions' in out_nodes_data:
            for out_link in out_nodes_data['Conditions']: # the correct flow, the usual one
                graph.add_link_id(id_start_node, out_link['NextAction'], False) #metadata= { 'value': out_link['Condition']['Operands'][0], 'condition': '==' if out_link['Condition']['Operator'] == "Equals" else "OPERATOR_NOT_FOUND" }
    
        if 'Errors' in out_nodes_data:
            for out_link in out_nodes_data['Errors']:
                graph.add_link_id(id_start_node, out_link['NextAction'], True)
        
        node.original_data = {}
           

#
#
#
#
#
#
#
#

if __name__ == "__main__":
    __instance_id__flow = instance_id_from_ARN(INSTANCE_DETAILS['arn'])
    print("instance ID:", __instance_id__flow)

    flow = read_all_flows()
    
    graph = GraphVDN(flow['startBlockID'])
    
    load_flow_blocks_into_graph(graph, flow)
    
    graph.get_all_ends()
    print("now, to json")
    print(graph.to_json())

