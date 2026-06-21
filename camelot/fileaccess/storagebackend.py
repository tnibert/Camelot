from ..constants import env, DEPLOYMENT_AWS, DEPLOYMENT_LOCAL
from ..envvars import ENV_DEPLOYMENT
from .s3 import S3File
from .local import LocalFile

class InvalidStorageBackendException(Exception):
    pass

def storage_backend():
    """
    Select the destination (local vs S3) based on the environment
    :return: the class to instantiate for file access
    """
    env_deployment = env(ENV_DEPLOYMENT)
    if env_deployment == DEPLOYMENT_AWS:
        return S3File
    elif env_deployment == DEPLOYMENT_LOCAL:
        return LocalFile
    else:
        raise InvalidStorageBackendException("invalid photo destination specified")
