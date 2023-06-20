import json
from typing import Any
import boto3
import os

__env = {"region": "eu-central-1", "aws_access_key_id": "ASIASA3T6Q2TEW5NQ27W", "aws_secret_access_key": "l7k+h5mG73oASI/VQSP8eqvzy1UxTzASs17ARL2o", "aws_session_token": "IQoJb3JpZ2luX2VjEE4aCXVzLWVhc3QtMSJHMEUCIF3aWZhHc29jwUOoGRyjActjViAcZ/PsxXfWLp2NulfxAiEAzmQfhEgvfQaYzqRMNLSzYxfqVwWb3PsYQ4CfBmI1QBIqvQMIp///////////ARACGgwxMzkyOTI3MzkyMzgiDFJdQz3hYh0mb8Iv9SqRA4zCkRLmn+rffAJjZP9Sqb/drg3WJZrIDLHdWf1ZRihargNf7WqX7onlWsNPBbkQbQu07eEem0ClzpTqymS6B06AoID255Xk7RnOVEFWpOmitvZ9iuJqy5rVG3Kpdixst96v524/KSnJn//yW80z0sqxV9kUL8sLwahUzz8y7rHJOpzX4LxRvydIwMUT8ajGjMYo889okgat/cqHY4dWp3AHrR7sZLyd0zolppmFNKwvfTGAcfMT9qWo670/SPvRAEDp+cpJgBzkRqVtyDPPudQGILFLqIulT3XS8hgEieLyflsGJVksr8xXNCB7PD0umwbep21zIPCwGUBWNuBAxXNtT11IQWVtJXIppjR7T21Ri6NlLXEg5sVQpALg5GLcF8hbrflcCoqD/iWP/6YCkSe/M+4rqBtjOv4muD/34tpXCHGIt1PRPGJdV6UXTXZW4VEpdtK8keNvSNf8d5t4i2vYM+pRveP44I0/xfUMY1Tm5Cs/COV0G0AhSoCX7itcGvaWHDYYXKvlVLJL6fdrgYMiMPndxqQGOqYBw9ixBeH6/jHN0/ogRjGXpo7RcEyGN/Ilvf1o/mczSw5NGEKQ00vm44vrbsIQxwYvKgZoO2b7VnF7EQ8S7JJvFEGmB8NfMjho00/TbcifmBEzmeod3R2nEDxM/UOQ6qkF13bs1Ml2z4e5b+7MPS+aFACaNlW8e8eYuWiwYH3k+mywxShf3uUN+WQRgtxRbkCbhSWQ71PIsij64FDrV7dK4X50KXip/w"}

INSTANCE_DETAILS = {
    "market": "lsys",
    "language": "be",
    "arn": "arn:aws:connect:eu-central-1:139292739238:instance/93903ac6-b964-42d6-8383-3d90ab6799bd"
}


def instance_id_from_ARN(arn: str) -> str:
    return arn[1 + arn.rindex('/') :]


def outputJsonFile(json_obj, instanceIdFlow, what_is_it, pre_processing = None, subdirectories = None):
    folder_file = f'./output/{INSTANCE_DETAILS["market"]}/{INSTANCE_DETAILS["language"]}'
    if subdirectories is not None and len(subdirectories) > 0:
        for sd in subdirectories:
            folder_file = f'{folder_file}/{sd}'

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

class Flow:
    __is_flow:bool
    data: dict
    def __init__(self, data:dict, is_flow:bool) -> None:
        self.data=data
        self.__is_flow=is_flow

    def is_flow(self):
        return self.__is_flow
    def is_module_flow(self):
        return not self.__is_flow
    
    def get_data(self):
        return self.data
    
    def __json__(self):
        return f'{"{"}\tis_flow: {self.__is_flow},\n\tdata: {"{"}\n\t\t{json.dumps(self.data)}{"}"}\n{"}"}'


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


def describeFlow(client_connect, instance_id: str):
    resp = client_connect.describe_instance(
        InstanceId = instance_id
        #InstanceId = ARN__CONNECT__LSYS_UK
    )
    return resp['Instance']

def adjustCreatedTimeObj(instance_description):
    #instance_description['CreatedTime'] = instance_description['CreatedTime'].strftime("%d/%m/%y")
    instance_description['CreatedTime'] = instance_description['CreatedTime'].isoformat()
    return instance_description

def adjustFlowDetail_Content(flow_detail):
    flow_detail['Content'] = json.loads(flow_detail['Content'])
    return flow_detail #TODO: just return the 'Content', as Daniele wants?


def download__instance_flows_numbers(instance_id_flow):
    #
    print("\ngetting", "instance")
    instance_description = \
        outputJsonFile(
            describeFlow(client, instance_id=instance_id_flow), 
            instance_id_flow,
            "instance_flow",
            adjustCreatedTimeObj
        )
    print("got")

    #
    print("\ngetting", "phones")
    phones = client.list_phone_numbers(
        InstanceId=instance_id_flow,
        PhoneNumberTypes=[
            'TOLL_FREE', 'DID',
        ]
    )['PhoneNumberSummaryList']
    print("got")
    outputJsonFile(phones, instance_id_flow, "phones")
    
    #
    print("\ngetting", "flows")
    flows_resp = client.list_contact_flows(
        InstanceId= instance_id_flow
        )['ContactFlowSummaryList']
    #flows = [f for f in map( lambda f: Flow(f, True) ,flows_resp)]
    flows = flows_resp #[f for f in map( lambda ff: {"data":ff, "is_flow": True} ,flows_resp)]
    flows_resp = None
    print("got", len(flows), "flows")
    outputJsonFile(flows, instance_id_flow, "all_main_flows_summaries")
    
    #
    print("\ngetting", "flow modules")
    flow_modules = client.list_contact_flow_modules(
        InstanceId=instance_id_flow,
        ContactFlowModuleState='Active'
    )['ContactFlowModulesSummaryList']
    print("got")
    outputJsonFile(flow_modules, instance_id_flow, "flow_modules_summaries")

    # mixing flows
    all_flows = [
        f for f in map(lambda ff: {
            'Id': ff['Id'],
            'Arn': ff['Arn'],
            'Name': ff['Name'],
            'Type': ff['ContactFlowType'],
            'State': ff['ContactFlowState'],
            'is_not_module': True
            }
            , flows)
    ]
    flows = None
    all_flows.extend(
        [f for f in map(
            lambda ff: {
            'Id': ff['Id'],
            'Arn': ff['Arn'],
            'Name': ff['Name'],
            'State': ff['State'],
            'Type': 'module',
            'is_not_module': False                
            }
            ,flow_modules
        )]
    )
    flow_modules = None
    print("got", len(all_flows), "combined flows, saving")
    outputJsonFile(all_flows, instance_id_flow, "flows_summaries")
    print("got")
    
    print("getting all flows details")
    all_flows_details =[f for f in map(
            lambda ff: \
                client.describe_contact_flow(
                    InstanceId=instance_id_flow,
                    ContactFlowId=ff['Id'])['ContactFlow']
                if ff['is_not_module'] else \
                client.describe_contact_flow_module(
                    InstanceId=instance_id_flow,
                    ContactFlowId=ff['Id'])['ContactFlowModule'] \
            , all_flows)
    ]
    #all_flows = None
    for f in all_flows_details:
        outputJsonFile(
            f,
            instance_id_flow,
            f'{f["Id"]}_flow_detail',
            pre_processing= adjustFlowDetail_Content,
            subdirectories=['flows_details']
        )
    print("got")
    
    return {
        'instance_description': instance_description,
        'phones': phones,
        'flows': all_flows,
        'flows_details': all_flows_details
    }
    
    
    
    
    


if __name__ == "__main__":
    __instance_id__flow = instance_id_from_ARN(INSTANCE_DETAILS['arn'])
    print("instance ID:", __instance_id__flow)

    download__instance_flows_numbers(__instance_id__flow)

