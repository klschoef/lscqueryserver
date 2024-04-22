from core.message_handlers.base.message_base import MessageBase


class MessageMetadata(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "metadataquery"

    async def handle(self, client_request, client):
        result = {"type": "metadata", "num": 1, "totalresults": 1, "results": []}
        result['results'] = list(client.db['images'].find({"filepath": client_request.content.get('imagepath')}))
        return result