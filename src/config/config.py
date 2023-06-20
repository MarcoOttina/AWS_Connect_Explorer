import json

#from connections import base
#from ..connections import base
#from . import connections.base

import connections


DEFAULT_REGION = "eu-central-1"

def new_clientConfig_from_config(env_file_path: (str|None) = None):
    if env_file_path is None:
        env_file_path = "../../resources/.env"
        
    with open(env_file_path) as f:
        configs = json.load(f)
        return connections.base.NewClientConfig(
            configs['region'] if 'region' in configs else None,
            configs['aws_access_key_id'] if 'aws_access_key_id' in configs else None,
            configs['aws_secret_access_key'] if 'aws_secret_access_key' in configs else None,
            configs['aws_session_token'] if 'aws_session_token' in configs else None,
        )
        
    return None
