from core.message_handlers.base.message_base import MessageBase


class MessageConcepts(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "concepts"

    async def handle(self, client_request, client):
        concepts = client.db["concepts"].find({}, {"name": 1}).sort({"name": 1})
        return {"type": "concepts", "num": len(concepts), "results": concepts}