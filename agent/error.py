class LLMError(Exception):
    pass


class TransientError(LLMError):
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class PermanentError(LLMError):
    pass


class ResourceLimitError(LLMError):
    pass


class ModelMisbehaviorError(LLMError):
    pass


class ToolFatalError(Exception):
    pass