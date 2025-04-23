from core.message_handlers.base.message_base import MessageBase


class MessageRemoveImage(MessageBase):

    def should_handle(self, client_request):
        return client_request.type == "remove_image"

    async def handle(self, client_request, client):
        clip_connection = client.clip_connection
        filepath = client_request.content.get("filepath", None)
        clip_response = await clip_connection.query_raw({
            "type": "remove_image",
            "filepath": filepath
        })

        if clip_response.get("success", True):
            client.db["images"].delete_one({'filepath': filepath})

        return {"type": "remove_image", "success": True, "response": clip_response}