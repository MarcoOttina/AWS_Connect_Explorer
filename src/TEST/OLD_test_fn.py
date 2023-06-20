import boto3
import json

AWS_DEFAULT_REGION = "eu-central-1"
ALL_ARNs_CONNECT_INSTANCES= [
    "arn:aws:connect:eu-central-1:139292739238:instance/b7ce6533-17d8-4c72-acc1-78c08c8b3554"
]
ARN__CONNECT__LSYS_UK = ALL_ARNs_CONNECT_INSTANCES[len(ALL_ARNs_CONNECT_INSTANCES)-1]




def instance_id_from_arn(arn):
    return arn[arn.rindex('/')+1:]


def list_all_buckets():
    s3 = boto3.resource('s3')
    # Print out bucket names
    all_buckets = s3.buckets.all()
    for bucket in all_buckets:
        print(bucket.name)
    return all_buckets



def main():
    
    print("start connecting")

    instance_id_lsys_uk = instance_id_from_arn(ARN__CONNECT__LSYS_UK)
    print(instance_id_lsys_uk)


    client = boto3.client('connect', region_name=AWS_DEFAULT_REGION)
    #print(client)

    '''
    resp = client.list_instances()

    print("resp", resp)
    all_instances = resp['InstanceSummaryList']

    print("\n\n START READING INSTANCES\n\n")
    attributes_to_print = ['Id', 'ServiceRole', 'InstanceAlias']
    for inst in all_instances:
        for a in attributes_to_print:
            print(a, "->", inst[a], end=' , ')
        print("")
    '''
    print("\n\n now describe this specific instance", instance_id_lsys_uk)

    resp = client.describe_instance(
        InstanceId = instance_id_lsys_uk
        #InstanceId = ARN__CONNECT__LSYS_UK
    )
    instance = resp['Instance']
    print(instance)
    #print(dir(client), "\n\n")
    #print(vars(client))

    #c_a = client.get_contact_attributes()
    '''response = client.list_contact_flows(
        InstanceId='string',
        ContactFlowTypes=['CONTACT_FLOW']
    )'''
    phones = client.list_phone_numbers(
        InstanceId=instance_id_lsys_uk,
        PhoneNumberTypes=[
            'TOLL_FREE', 'DID',
        ]
    )['PhoneNumberSummaryList']
    print("\n\nphones:")
    print(phones)
    phones = None

    lambda_arns =  client.list_lambda_functions(
        InstanceId=instance_id_lsys_uk
    )['LambdaFunctions']
    print("\n\nlambda ARNs:")
    print(lambda_arns)
    lambda_arns = None


    print("\n\n\n FINISH")


if __name__ == "__main__":
    main()
