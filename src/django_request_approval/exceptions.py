

class RequestExistsException(Exception):
    message = "Transfer request exists"

    def __str__(self) -> str:
        return self.message
    

class PermissionDeniedException(Exception):
    message = "Permission denied"

    def __str__(self) -> str:
        return self.message