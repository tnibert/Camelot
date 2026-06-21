from io import BytesIO

IN_MEMORY_FILES = {}

class InMemoryFile:
    """
    InMemoryFile provides interface to persist a file, but is backed by memory.  Used for testing.
    """
    def __init__(self, path: str):
        self.path = path

    def write(self, fi: BytesIO):
        fi.seek(0)
        IN_MEMORY_FILES[self.path] = fi.read()

    def read(self) -> bytes:
        return IN_MEMORY_FILES[self.path]

    def delete(self):
        del IN_MEMORY_FILES[self.path]
