from ..constants import env, DEPLOYMENT_AWS, DEPLOYMENT_LOCAL, DEPLOYMENT_TEST
from ..envvars import ENV_DEPLOYMENT
from .s3 import S3File
from .local import LocalFile
from .memory import InMemoryFile

class InvalidStorageBackendException(Exception):
    pass

def storage_backend():
    """
    Select the storage backend based on the environment
    :return: the class to instantiate for file access
    """
    env_deployment = env(ENV_DEPLOYMENT)
    if env_deployment == DEPLOYMENT_AWS:
        return S3File
    elif env_deployment == DEPLOYMENT_LOCAL:
        return LocalFile
    elif env_deployment == DEPLOYMENT_TEST:
        return InMemoryFile
    else:
        raise InvalidStorageBackendException("invalid photo destination specified")
