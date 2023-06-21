import json
import boto3
import os
from typing import Callable, Self

__env = {"region": "eu-central-1", "aws_access_key_id": "ASIASA3T6Q2TEW5NQ27W", "aws_secret_access_key": "l7k+h5mG73oASI/VQSP8eqvzy1UxTzASs17ARL2o", "aws_session_token": "IQoJb3JpZ2luX2VjEE4aCXVzLWVhc3QtMSJHMEUCIF3aWZhHc29jwUOoGRyjActjViAcZ/PsxXfWLp2NulfxAiEAzmQfhEgvfQaYzqRMNLSzYxfqVwWb3PsYQ4CfBmI1QBIqvQMIp///////////ARACGgwxMzkyOTI3MzkyMzgiDFJdQz3hYh0mb8Iv9SqRA4zCkRLmn+rffAJjZP9Sqb/drg3WJZrIDLHdWf1ZRihargNf7WqX7onlWsNPBbkQbQu07eEem0ClzpTqymS6B06AoID255Xk7RnOVEFWpOmitvZ9iuJqy5rVG3Kpdixst96v524/KSnJn//yW80z0sqxV9kUL8sLwahUzz8y7rHJOpzX4LxRvydIwMUT8ajGjMYo889okgat/cqHY4dWp3AHrR7sZLyd0zolppmFNKwvfTGAcfMT9qWo670/SPvRAEDp+cpJgBzkRqVtyDPPudQGILFLqIulT3XS8hgEieLyflsGJVksr8xXNCB7PD0umwbep21zIPCwGUBWNuBAxXNtT11IQWVtJXIppjR7T21Ri6NlLXEg5sVQpALg5GLcF8hbrflcCoqD/iWP/6YCkSe/M+4rqBtjOv4muD/34tpXCHGIt1PRPGJdV6UXTXZW4VEpdtK8keNvSNf8d5t4i2vYM+pRveP44I0/xfUMY1Tm5Cs/COV0G0AhSoCX7itcGvaWHDYYXKvlVLJL6fdrgYMiMPndxqQGOqYBw9ixBeH6/jHN0/ogRjGXpo7RcEyGN/Ilvf1o/mczSw5NGEKQ00vm44vrbsIQxwYvKgZoO2b7VnF7EQ8S7JJvFEGmB8NfMjho00/TbcifmBEzmeod3R2nEDxM/UOQ6qkF13bs1Ml2z4e5b+7MPS+aFACaNlW8e8eYuWiwYH3k+mywxShf3uUN+WQRgtxRbkCbhSWQ71PIsij64FDrV7dK4X50KXip/w"}

INSTANCE_DETAILS = {
    "market": "lsys",
    "language": "be",
    "arn": "arn:aws:connect:eu-central-1:139292739238:instance/93903ac6-b964-42d6-8383-3d90ab6799bd"
}

#
class Jsonable:
    def to_json(self):
        return self
    

def instance_id_from_ARN(arn: str) -> str:
    return arn[1 + arn.rindex('/') :]


def outputJsonFile_OLD(json_obj, instanceIdFlow, what_is_it, pre_processing = None, market_lang_data = INSTANCE_DETAILS):
    folder_file = f'./output/{market_lang_data["market"]}/{market_lang_data["language"]}'
    os.makedirs(folder_file, exist_ok=True)
    
    filename = f'{folder_file}/{instanceIdFlow}__{what_is_it}.json'
    with open(filename, 'w') as f:
        print("writing", what_is_it)
        if pre_processing is not None:
            json_obj = pre_processing(json_obj)
        s = ""
        if isinstance(json_obj, Jsonable):
            s = json_obj.to_json()
        else:
             s = json.dumps(json_obj)
        f.write(s)
        print(what_is_it,"written")
    return json_obj


def outputJsonFile(json_obj, name, subfolder, pre_processing = None ):
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
        print(name,"written")
    return json_obj



#
# CLASSES
#


# just added as documentation, since it's NOT serializable automatically; call "to_json()" for that purpose
class GraphVDNNode(Jsonable):
    is_end:bool
    id:str # it is a UUID
    block_type: str
    original_data: dict
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
            "is_end": self.is_end,
            "block_type": self.block_type,
            "links_out_ids_correct": self.links_out_ids_correct,
            "links_out_ids_error": self.links_out_ids_error,
            "original_data": self.original_data
        }
    def short_description(self):
        return {
            "type": self.block_type,
            "is_end": self.is_end,
            "id": self.id,
            "links_out": {
                "correct": len(self.links_out_ids_correct),
                "errors": len(self.links_out_ids_error)
            }
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


class forwardLink:
    never_cloned:bool
    path_length:int
    source_node:GraphVDNNode|None # works as "current node" as well
    dest_node:GraphVDNNode|None
    source_link: Self|None
    dest_link: Self|None
    def __init__(self, source_node:GraphVDNNode|None, dest_node:GraphVDNNode|None = None, prev_link:(Self|None)=None) -> None:
        self.path_length = 1
        self.never_cloned = True
        self.source_node = source_node
        self.dest_node = dest_node
        self.dest_link = None
        if prev_link is None:
            self.source_link = None
        else:
            prev_link.dest_link = self
            self.source_link = prev_link
            self.path_length = prev_link.path_length + 1
    def is_end(self):
        return self.dest_node == None #self.dest_link == None
    def is_start(self):
        return self.source_node == None #self.source_link == None
    def is_middle(self):
        return not( self.is_end() or self.is_start() )
    def is_source_end(self):
        return False if self.source_node is None else self.source_node.is_end
    def clone_after_first(self):
        if self.never_cloned:
            self.never_cloned = False
            return self
        c = forwardLink(self.source_node, self.dest_node)
        c.source_link = self.source_link
        c.path_length = self.path_length
        return c

class VDNPath(Jsonable):
    id_start:str|None
    id_end:str|None
    steps_ids:list[str]
    end_type:str|None
    def __init__(self):
        self.id_start = None
        self.id_end = None
        self.steps_ids = None
        self.end_type = "unknown"
    def to_json(self):
        return {
            "start_id": self.id_start,
            "end_id": self.id_end,
            "end_type": self.end_type,
            "length_path": len(self.steps_ids),
            "steps_ids": self.steps_ids
        }

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

    def add_node_block(self, original_data, id: str, is_end:bool = False, \
        field_from_original_data_setter: Callable[[GraphVDNNode, object|dict],None] = None):
        if id in self.nodes_by_ID:
            print("-------- ID gia' presente:", id)
            return
        gNode = GraphVDNNode(id, is_end)
        gNode.original_data = original_data
        field_from_original_data_setter(gNode, original_data)
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
            print("___#1 add link id: ID source not found:", id_node_source)
            return False
        if id_node_destination not in self.nodes_by_ID:
            print("___#1 add link id: ID dest not found:", False)
            return False
        return self.nodes_by_ID[id_node_source].add_node_id_to_link_out(id_node_destination, is_correct_link)

        
    def __dfs(self, action:Callable[[GraphVDNNode,GraphVDNNode], None], visited_nodes: dict[str, bool], current_node: GraphVDNNode, father_node: GraphVDNNode):
        if current_node.id in visited_nodes:
            return
        visited_nodes[current_node.id] = True
        action(current_node, father_node)
        
        def dfs_iteration(id_out: str):
            if id_out in visited_nodes:
                return
            self.__dfs(action, visited_nodes, self.nodes_by_ID[id_out], current_node)
        current_node.for_each_link_out(dfs_iteration)

    # Depth-First Search
    # scan the whole network, touching each nodes just once, performing an action on each node.
    # The action accepts two parameters: the current node and its father from the root
    # (the father of the root is None).
    def depth_first_search(self, action:Callable[[GraphVDNNode,GraphVDNNode], None]):
        starting_node = self.nodes_by_ID[self.startID]
        visited_nodes: dict[str, bool] = {}
        self.__dfs(action, visited_nodes, starting_node, None)
        
    # the path collector is a function accepting the list of already collected paths, the current "end node" and its relative incoming link
    def __gae(self, paths_to_vdns: list[VDNPath], path_collector: Callable[[list[VDNPath], GraphVDNNode, forwardLink], VDNPath] , current_node: GraphVDNNode, incoming_link: forwardLink) -> None:
        if current_node.is_end:
            path_collector(paths_to_vdns, current_node, incoming_link)
            return
        
        # avoid infinite recursion by detecting a cycle
        already_explored_nodes: dict[str, bool] = {}
        already_explored_nodes[current_node.id] = True
        backward_iter_link = incoming_link.source_link
        no_cycle = True
        while (backward_iter_link is not None) \
            and (backward_iter_link.source_node is not None) \
            and no_cycle:
                no_cycle = (backward_iter_link.source_node.id not in already_explored_nodes) # is the previous node alreadi seen
                if no_cycle:
                    already_explored_nodes[backward_iter_link.source_node.id] = True
                    backward_iter_link = backward_iter_link.source_link
        already_explored_nodes.clear()
        already_explored_nodes = None
        if not no_cycle:
            return
        
        #recursion
        def gae_on_out_links(id_out_node):
            out_node = self.nodes_by_ID[id_out_node]
            next_link = forwardLink(current_node, out_node, incoming_link.clone_after_first())
            self.__gae(paths_to_vdns, path_collector, out_node,next_link)
            
        current_node.for_each_link_out(gae_on_out_links)
    
    def get_all_ends(self) -> list[VDNPath]:
        self.depth_first_search(lambda current_node, father_node: print(('ENTRY POINT' if father_node is None else father_node.id), "->", current_node.id))
        
        starting_node = self.nodes_by_ID[self.startID]
        
        #forward_links : dict[str, str] = {} # keep track of
        super_root: forwardLink = forwardLink(None, dest_node=starting_node)
        
        paths_to_vdns: list[VDNPath] = []
        
        def path_collector(already_collected_paths: list[VDNPath], end_node:GraphVDNNode, incoming_link:forwardLink):
            new_VDN_path:VDNPath = VDNPath()
            new_VDN_path.id_end = end_node.id
            new_VDN_path.end_type = end_node.block_type
            new_VDN_path.steps_ids = [ "" ] * incoming_link.path_length
            new_VDN_path.steps_ids[incoming_link.path_length-1] = end_node.id
            
            # collect all IDs, in a backward manner
            i = incoming_link.path_length - 1
            backward_link_iter = incoming_link
            while i >= 0 and (backward_link_iter is not None): # and (backward_link_iter.dest_node is not None):
                # the last node, the "end", is already collected (hence, the "-1" below): already jump backward
                backward_link_iter = backward_link_iter.source_link
                i -= 1
                if (backward_link_iter is not None and backward_link_iter.dest_node is not None): # a jump is done, the current "link" might be the "super_node"
                    new_VDN_path.steps_ids[i] = backward_link_iter.dest_node.id
            new_VDN_path.id_start = new_VDN_path.steps_ids[0]
            
            already_collected_paths.append(new_VDN_path)
            return new_VDN_path
            
        self.__gae(paths_to_vdns, path_collector, starting_node, super_root)
        return paths_to_vdns





#
# START
#


def start_connection():
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
    return service, session, client


#
# READ FILE DATA ; BUILD A GRAPH
#

# structure: {"name":str, "res_folder":str, "output_folder":str}
def get_all_flows_list() -> list[dict[str,str]]:
    tests = [
        't_empty',
        't_mono',
        't_bi',
        't_small_pearl',
        'error',
        't_check',
        't_loop',
        't_loop_broken',
        't_small_cycle',
        't_chain_of_cycles',
        't_2_inner_cycles'
    ]
    tests = [ {"name": t, 'res_folder': "tests", "output_folder": "graph"} for t in tests]
    
    #fcab_be = [ {"name": x, 'res_folder': "FCAB-BE" , "output_folder": "FCAB-BE"}  for x in ['CustomerCareWorkFlow','CustomerCareWaitFlowDutch']]
    fcab_be = []
    
    return tests + fcab_be


def readers_of_flows() -> map:
    all_flows_name = get_all_flows_list()
    def loader_flow(filename_flow_current):
        print("analysing flow: ", filename_flow_current)
        flow_details = {}
        with open(f'./resources/{filename_flow_current["res_folder"]}/{filename_flow_current["name"]}.json', 'r') as f:
            flow_details = json.load(f)
    
        return {
            'name': filename_flow_current["name"],
            'output_folder':filename_flow_current['output_folder'],
            'startBlockID': flow_details['StartAction'],
            'blocks': flow_details['Actions']
        }
    return map(loader_flow, all_flows_name)
    
    
def load_flow_blocks_into_graph(graph: GraphVDN, flow_details: dict):
    blocks_original_data = flow_details['blocks']
    
    # nodes creation
    
    def is_end_node(node_data):
        #TODO: is a more complicated analysis required?
        return 'NextAction' not in node_data['Transitions'] \
            or node_data['Type'] == 'Loop' # a loop is an end node since no cycle is allowed
    
    def original_data_setter (node: GraphVDNNode, node_data: object|dict):
        node.block_type = node_data['Type']
        
    for bod in blocks_original_data:
        graph.add_node_block(bod, bod['Identifier'], is_end_node(bod), original_data_setter)
    
    #creates the links
    
    for id_start_node, node in graph.nodes_by_ID.items():
        out_nodes_data = node.original_data['Transitions']
        
        default_out_link:str = None
        if 'NextAction' in out_nodes_data:
            default_out_link = out_nodes_data['NextAction']
            added = graph.add_link_id(id_start_node, default_out_link, True)
            if not added:
                print(".....link default \t not added between:", id_start_node, "->", default_out_link)
    
        if 'Conditions' in out_nodes_data:
            for out_link in out_nodes_data['Conditions']: # the correct flow, the usual one
                out_link_id = out_link['NextAction']
                if out_link_id != default_out_link:
                    added = graph.add_link_id(id_start_node, out_link_id, True) # metadata= { 'value': out_link['ErrorType']['Operands'][0], 'condition': '==' if out_link['Condition']['Operator'] == "Equals" else "OPERATOR_NOT_FOUND" }
                    if not added:
                        print(".....link correct \t not added between:", id_start_node, "->", out_link_id)
    
        if 'Errors' in out_nodes_data:
            for out_link in out_nodes_data['Errors']:
                out_link_id = out_link['NextAction']
                if out_link_id != default_out_link:
                    added = graph.add_link_id(id_start_node, out_link_id, False) # metadata= { 'value': out_link['ErrorType'] }
                    if not added:
                        print(",,,,,link error \t not added between:", id_start_node, "->", out_link_id)
        
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

    readers = readers_of_flows()
    
    for flow in readers:
        print("\n\nreading", flow["name"], "flow")
        graph = GraphVDN(flow['startBlockID'])
        
        load_flow_blocks_into_graph(graph, flow)
        print("now, to json")
        outputJsonFile(graph.to_json(), flow["name"], flow['output_folder'])
        
        paths = graph.get_all_ends()
        print("\n\n all", len(paths), "paths")
        i = 0
        for p in paths:
            outputJsonFile(p.to_json(), f'path_{i}', f'paths/{flow["name"]}')
            i += 1

