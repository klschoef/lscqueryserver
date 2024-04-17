from core.message_handlers.base.message_base import MessageBase


class MessageObjects(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "objects"

    def handle(self, client_request, client):
        objects = client.db["objects"].find({}, {"name": 1}).sort({"name": 1})
        return {"type": "objects", "num": len(objects), "results": objects}