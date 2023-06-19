import boto3
from config import config as cfg


class NewClientConfig:
    region: str = cfg.DEFAULT_REGION
    __aws_access_key_id: (str | None) = None
    __aws_secret_access_key: (str | None) = None
    __aws_session_token: (str | None) = None
    
    #TODO altro? credenziali?
    def __init__(self, region: (str | None) = None, aws_access_key_id: (str | None) = None,
        aws_secret_access_key: (str | None) = None,
        aws_session_token: (str | None) = None):
        if region is not None:
            self.region = region
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__aws_session_token = aws_session_token
        

def new_client( service: (str | None) = 'connect', client_config: (NewClientConfig | None) = None):
    '''
    returns a boto3 Client instance
    '''
    if service is None:
        return None
    
    if client_config is None:
        client_config = NewClientConfig()
        
    if client_config.__aws_access_key_id is None or client_config.__aws_secret_access_key is None or client_config.__aws_session_token is None or \
        client_config.__aws_access_key_id.strip() == "" or client_config.__aws_secret_access_key.strip() == "" or client_config.__aws_session_token.strip() == "":
        return boto3.client(service, region = client_config.region)
    
    session = boto3.Session(
        aws_access_key_id = client_config.__aws_access_key_id,
        aws_secret_access_key = client_config.__aws_secret_access_key,
        aws_session_token = client_config.__aws_session_token
    )
    return session.resource(service)


def instance_id_from_ARN(arn: str) -> str:
    return arn[1 + arn.rindex('/') :]
