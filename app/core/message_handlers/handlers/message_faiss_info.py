from core.message_handlers.base.message_base import MessageBase


class MessageFaissInfo(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "faiss_info"

    async def handle(self, client_request, client):
        clip_connection = client.clip_connection
        clip_response = await clip_connection.query_raw({
            "type": "faiss_info"
        })

        return {"type": "faiss_info", "faiss_info": clip_response}