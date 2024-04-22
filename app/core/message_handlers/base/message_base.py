from abc import ABC, abstractmethod


class MessageBase(ABC):

    """
    return True if this handler should handle the given client_request, otherwise False
    input: client_request: ClientRequest
    """
    @abstractmethod
    def should_handle(self, client_request):
        pass

    """
    return result dict, which should send to the client
    input: client_request: ClientRequest, client: Client
    """
    @abstractmethod
    async def handle(self, client_request, client):
        pass