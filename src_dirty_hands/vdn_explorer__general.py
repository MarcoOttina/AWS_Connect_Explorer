
import json

#
# CONFIGS, CONSTANTS, etc
#

'''
'''
NAMES_BLOCKS_TERNIMALS = [
    'DisconnectParticipant',
    'Loop',
    'TransferContactToQueue'
]
NAMES_BLOCKS_TRANSFERS= [
    'TransferToFlow'
]
NAME_END_FLOW = 'EndFlowExecution'


#
# cread
#

def read_flows_from_files(file_list):
    flows_data = [None] * len(file_list)
    for index, file_name in enumerate(file_list):
        with open(file_name) as f:
            flows_data[index] = json.load(f)
    return filter(lambda d: d is not None, flows_data)

def compose_flow_data_metadata(flows_raw_data:list, phone_numbers: list):
    '''
    Raw data is devided between "metadata", holding GUI-related data and reoursecs names/values taken as inputs,
    and "actions", which are the actual block composing the actual flow.
    The goal is to unify this scattered data into single structures while also collecting data for the whole
    network, like the "placeholders" (eg: "transfer_to_flow") requiring to be resolved
    '''


def resolve_flow_redirections(flows_data):
    pass

#
# main
#

def by_hand_list_filenames():
    pure_names = [
        "CustomerCareWaitFlowDutch",
        "CustomerCareWaitFlowFrench",
        "CustomerCareWorkFlow",
        "Dealer Workflow Test Tom",
        "LMSInboundFlow",
        "TransferToAgentWhisper"
    ]
    return [ff for ff in map(lambda fn: f'./resources/FCAB-BE/{fn}', pure_names)]

def main():
    print("start")
    filenames = by_hand_list_filenames()
    flows_data = read_flows_from_files(filenames)
    filenames = None
    
    

if __name__ == "__main__":
    main()