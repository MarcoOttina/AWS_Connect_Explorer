import json
import boto3
import os

# import block_names
from vdn_graph_types import *

__env = {
    "region": "eu-central-1",
    "aws_access_key_id": "ASIASA3T6Q2TEW5NQ27W",
    "aws_secret_access_key": "l7k+h5mG73oASI/VQSP8eqvzy1UxTzASs17ARL2o",
    "aws_session_token": "IQoJb3JpZ2luX2VjEE4aCXVzLWVhc3QtMSJHMEUCIF3aWZhHc29jwUOoGRyjActjViAcZ/PsxXfWLp2NulfxAiEAzmQfhEgvfQaYzqRMNLSzYxfqVwWb3PsYQ4CfBmI1QBIqvQMIp///////////ARACGgwxMzkyOTI3MzkyMzgiDFJdQz3hYh0mb8Iv9SqRA4zCkRLmn+rffAJjZP9Sqb/drg3WJZrIDLHdWf1ZRihargNf7WqX7onlWsNPBbkQbQu07eEem0ClzpTqymS6B06AoID255Xk7RnOVEFWpOmitvZ9iuJqy5rVG3Kpdixst96v524/KSnJn//yW80z0sqxV9kUL8sLwahUzz8y7rHJOpzX4LxRvydIwMUT8ajGjMYo889okgat/cqHY4dWp3AHrR7sZLyd0zolppmFNKwvfTGAcfMT9qWo670/SPvRAEDp+cpJgBzkRqVtyDPPudQGILFLqIulT3XS8hgEieLyflsGJVksr8xXNCB7PD0umwbep21zIPCwGUBWNuBAxXNtT11IQWVtJXIppjR7T21Ri6NlLXEg5sVQpALg5GLcF8hbrflcCoqD/iWP/6YCkSe/M+4rqBtjOv4muD/34tpXCHGIt1PRPGJdV6UXTXZW4VEpdtK8keNvSNf8d5t4i2vYM+pRveP44I0/xfUMY1Tm5Cs/COV0G0AhSoCX7itcGvaWHDYYXKvlVLJL6fdrgYMiMPndxqQGOqYBw9ixBeH6/jHN0/ogRjGXpo7RcEyGN/Ilvf1o/mczSw5NGEKQ00vm44vrbsIQxwYvKgZoO2b7VnF7EQ8S7JJvFEGmB8NfMjho00/TbcifmBEzmeod3R2nEDxM/UOQ6qkF13bs1Ml2z4e5b+7MPS+aFACaNlW8e8eYuWiwYH3k+mywxShf3uUN+WQRgtxRbkCbhSWQ71PIsij64FDrV7dK4X50KXip/w"
}

INSTANCE_DETAILS = {
    "market": "lsys",
    "language": "be",
    "arn": "arn:aws:connect:eu-central-1:139292739238:instance/93903ac6-b964-42d6-8383-3d90ab6799bd"
}


def instance_id_from_ARN(arn: str) -> str:
    return arn[1 + arn.rindex('/'):]


def outputJsonFile_OLD(json_obj, instanceIdFlow, what_is_it, pre_processing=None, market_lang_data=INSTANCE_DETAILS):
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
        print(what_is_it, "written")
    return json_obj


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
# START
#


def start_connection():
    service = 'connect'
    session = boto3.Session(
        aws_access_key_id=__env['aws_access_key_id'],
        aws_secret_access_key=__env['aws_secret_access_key'],
        aws_session_token=__env['aws_session_token']
    )
    client = session.client(
        service_name=service,
        region_name=__env['region']
    )
    return service, session, client


#
# READ FILE DATA ; BUILD A GRAPH
#

# structure: {"name":str, "res_folder":str, "output_folder":str}
def get_all_flows_list() -> list[dict[str, str]]:
    '''
    't_empty',
    't_mono',
    't_bi',
    't_small_pearl',
    'error',
    't_check',
    't_loop',
    't_small_cycle',
    't_chain_of_cycles',
    't_2_inner_cycles',
    '''
    tests = [
        't_loop_broken',
        't_cycle_multipl'
    ]
    tests = [{"name": t, 'res_folder': "tests", "output_folder": "graph"}
             for t in tests]

    # fcab_be = [ {"name": x, 'res_folder': "FCAB-BE" , "output_folder": "FCAB-BE"}  for x in ['CustomerCareWorkFlow','CustomerCareWaitFlowDutch']]
    fcab_be = []

    return tests + fcab_be


def readers_of_flows(pick_metadata: bool = False) -> map:
    all_flows_name = get_all_flows_list()

    def loader_flow(filename_flow_current):
        print("\n\nanalysing flow: ", filename_flow_current)
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

        return result
    return map(loader_flow, all_flows_name)


'''
def set_is_end_property(graph: GraphVDN, flow_details: dict):
    blocks_raw_data = flow_details['Actions']
    
    #block_types_to_group = block_names.get_block_types_to_group()
    
    loop_disconnect_node_filter = lambda n_start, n_end: \
        n_end is None or \
        not (n_end.block_type == 'Loop' or n_end.block_type == 'DisconnectParticipant')

    for id_node, node in graph.nodes_by_ID.items():
        block_data = blocks_raw_data[id_node]
        
        if node.block_type == 'Loop' or node.block_type == 'DisconnectParticipant': # block_data['Type']
            node.set_is_end(True)
        elif 'Transitions' in block_data:
            transitions = block_data['Transitions']
            
            if 'NextAction' in transitions:
                node.set_is_end(False)
            else:
                has_conditions = 'Conditions' in block_data['Transitions'] 
                has_errors = 'Errors' in block_data['Transitions']
                
                existing_nodes__conditions = [x for x in filter(lambda n: n['NextAction'] in graph.nodes_by_ID, transitions['Conditions']) ] if has_conditions else None
                existing_nodes__errors = [x for x in filter(lambda n: n['NextAction'] in graph.nodes_by_ID, transitions['Errors']) ] if has_errors else None

                if (existing_nodes__conditions is None or len(existing_nodes__conditions) == 0) and \
                   (existing_nodes__errors is None or len(existing_nodes__errors) == 0) :
                       node.set_is_end(True)
                else:
                    # if this node is able to reach itself through a non-Loop node, then it should considered as part of an end
                      
                    self_path_to_current_node = graph.shortest_path(\
                        id_node, \
                        id_node, \
                        check_trivial_start_self_link=False, \
                        node_filter= loop_disconnect_node_filter \
                    )
                    cycle_with_no_loop_blocks = self_path_to_current_node is not None and len(self_path_to_current_node) > 1
                    node.set_is_end(cycle_with_no_loop_blocks)
'''


def load_flow_blocks_into_graph(graph: GraphVDN, flow_details: dict):
    blocks_original_data = flow_details['blocks']

    blocks_by_ids: dict[str, dict] = {}
    for b in blocks_original_data:
        blocks_by_ids[b['Identifier']] = b

    # nodes creation

    def original_data_setter(node: GraphVDNNode, node_data: object | dict):
        node.block_type = node_data['Type']
        # TODO: is there any more data to be extracted? like "Parameters" from the super "metadata" field (i.e., the "flow_details" variable)

    for bod in blocks_original_data:
        # integrity check
        if 'Transitions' in bod:
            transitions = bod['Transitions']
            empty_branches = ('NextAction' not in transitions) and (
                ('Conditions' in transitions and 'Errors' in transitions)
                and
                (len(transitions['Conditions']) ==
                 0 and len(transitions['Errors']) == 0)
            )
            if empty_branches:
                print("ERROR: ", bod['Identifier'],
                      " in \"Transition\" has no NextAction field and both Errors and Conditions arrays are empty")
        is_end = False  # is_end_node(bod['Identifier'], bod)
        graph.add_node_block(
            bod, bod['Identifier'], is_end, original_data_setter)

    for id_start_node, node in graph.nodes_by_ID.items():
        out_nodes_data = node.original_data['Transitions']

        default_out_link: str = None
        if 'NextAction' in out_nodes_data:
            default_out_link = out_nodes_data['NextAction']
            if default_out_link != id_start_node:
                added = graph.add_link_id(
                    id_start_node, default_out_link, True)
                if not added:
                    print(".....link default \t not added between:",
                          id_start_node, "->", default_out_link)
            else:
                print("#1 node", id_start_node, "is adding itself as link")

        if 'Conditions' in out_nodes_data:
            # the correct flow, the usual one
            for out_link in out_nodes_data['Conditions']:
                out_link_id = out_link['NextAction']
                if out_link_id != default_out_link:
                    if out_link_id != id_start_node:
                        # metadata= { 'value': out_link['ErrorType']['Operands'][0], 'condition': '==' if out_link['Condition']['Operator'] == "Equals" else "OPERATOR_NOT_FOUND" }
                        added = graph.add_link_id(
                            id_start_node, out_link_id, True)
                        if not added:
                            print(".....link correct \t not added between:",
                                  id_start_node, "->", out_link_id)
                    else:
                        print("#2 node", id_start_node,
                              "is adding itself as link")
        if 'Errors' in out_nodes_data:
            for out_link in out_nodes_data['Errors']:
                out_link_id = out_link['NextAction']
                if out_link_id != default_out_link:
                    if out_link_id != id_start_node:
                        # metadata= { 'value': out_link['ErrorType'] }
                        added = graph.add_link_id(
                            id_start_node, out_link_id, False)
                        if not added:
                            print(",,,,,link error \t not added between:",
                                  id_start_node, "->", out_link_id)
                    else:
                        print("#3 node", id_start_node,
                              "is adding itself as link")

    '''
    # checks NOW the "end-ness" of nodes
    print("creating the link for these nodes:")
    for id_start_node, node in graph.nodes_by_ID.items():
        print("\t", id_start_node, "-->", node.short_description())
        
        node.original_data = {}
    '''
    graph.recalculate_ends(
        is_selfLoop_marking_end=True,
        block_types_of_ends=['Loop', 'DisconnectParticipant', 'TransferToFlow']
    )


def merge_graphs(graphs_by_filename: dict[str, GraphVDN]) -> dict[str, GraphVDN]:
    merged_graphs: dict[str, GraphVDN] = {}

    return merged_graphs

#
#
#
#
#
#
#
#


def __main():
    __instance_id__flow = instance_id_from_ARN(INSTANCE_DETAILS['arn'])
    print("instance ID:", __instance_id__flow)

    # TODO: allow there to pick metadata file
    readers = readers_of_flows(False)
    graphs_by_filename: dict[str, GraphVDN] = {}

    for flow in readers:
        print("\nreading", flow["name"], "flow")
        graph = GraphVDN(flow['startBlockID'])
        graphs_by_filename[flow['name']] = graph

        load_flow_blocks_into_graph(graph, flow)
        # set_is_end_property(graph, flow)
        #
        print("now, to json")
        outputJsonFile(graph.to_json(), flow["name"], flow['output_folder'])

        paths = graph.get_all_ends()
        print("\n all", len(paths), "paths")
        i = 0
        for p in paths:
            outputJsonFile(p.to_json(), f'path_{i}', f'paths/{flow["name"]}')
            i += 1

    print("\n\n now merge the graphs")
    gg = merge_graphs(graphs_by_filename)
    d = {}
    for flow_name, graph in gg.items():
        d[flow_name] = graph.to_json()
    outputJsonFile(d, 'merged_graphs', "merged_graphs")


if __name__ == "__main__":
    __main()
