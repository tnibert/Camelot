import shutil
from io import BytesIO
from os import makedirs

from camelot.constants import MIN_FREE_THRES, DATA_PARTITION_PATH
from camelot.controllers.utilities import DiskExceededException

CHUNK_SIZE = 430 # bytes

class LocalFile:
    def __init__(self, path: str):
        self.path = path

    def write(self, fi: BytesIO):
        # ensure that there is sufficient space on the filesystem, compare threshold to free space
        if MIN_FREE_THRES > shutil.disk_usage(DATA_PARTITION_PATH)[2]:
            raise DiskExceededException("Don't have enough space to store new photos")

        makedirs("/".join(self.path.split("/")[:-1]), exist_ok=True)    # todo: don't split on string

        fi.seek(0)
        with open(self.path, 'wb+') as destination:
            chunk = fi.read(CHUNK_SIZE)
            while chunk:  # loop until the chunk is empty (the file is exhausted)
                destination.write(chunk)
                chunk = fi.read(CHUNK_SIZE)  # read the next chunk

    def read(self) -> BytesIO:
        pass
