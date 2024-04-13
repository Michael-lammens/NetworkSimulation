class ParseLogNoTypeSpecified(Exception):
    def __init__(self, message="Exception raised when attempting to index leading type field. C files should have a log type for every write to STDOUT"):
        super().__init__(message)
