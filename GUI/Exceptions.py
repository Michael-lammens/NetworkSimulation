class ParseLogNoTypeSpecified(Exception):
    def __init__(self, message="Exception raised when attempting to index leading type field. C files should have a log type for every write to STDOUT"):
        super().__init__(message)
class StartUninitializedFlow(Exception):
    def __init__(self, message="Exception raised when attempting to start a flow instance before initialization. HINT: Call instance.set_args() first"):
        super().__init__(message)
class RedefineInstanceArgs(Exception):
    def __init__(self, message="Exception raised when attempting to redefine parameters of an already initialized flow. This would result in undefined behavior. HINT: Create a new flow instead."):
        super().__init__(message)
