from ..config import config as cfg
from ..connections import base

ALL_ARNs_CONNECT_INSTANCES= [
    "arn:aws:connect:eu-central-1:139292739238:instance/860727d5-3ac3-4f4c-8992-a59d9e64d79c",
    "arn:aws:connect:eu-central-1:274162447932:instance/bb90738e-d97d-4f84-996f-189d79988705"
]

client_connect = base.new_client('connect', cfg.new_clientConfig_from_config())

arn_instance = ALL_ARNs_CONNECT_INSTANCES[1]

instance_id_lsys_uk = base.instance_id_from_ARN(arn_instance)


resp = client_connect.describe_instance(
    InstanceId = instance_id_lsys_uk
    #InstanceId = ARN__CONNECT__LSYS_UK
)
instance = resp['Instance']
print(instance)
