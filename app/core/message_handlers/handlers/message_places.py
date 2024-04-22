from core.message_handlers.base.message_base import MessageBase


class MessagePlaces(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "places"

    async def handle(self, client_request, client):
        places = client.db["places"].find({}, {"name": 1}).sort({"name": 1})
        return {"type": "places", "num": len(places), "results": places}