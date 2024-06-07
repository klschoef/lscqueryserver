import uuid
import json

from core.clip.clip_connection import ClipConnection
from core.exceptions.response_error import ResponseError
from core.message_handlers.default_message_handlers import default_message_handlers
from core.models.client_request import ClientRequest
from core.serializers.object_serializer import ObjectSerializer
from core.utils.log_util import LogUtil


class Client:
    def __init__(self, db_connection, websocket, path, connection_id=None):
        self.db = db_connection
        self.websocket = websocket
        self.path = path
        self.connection_id = connection_id
        if not self.connection_id:
            self.connection_id = str(uuid.uuid4())
        self.clip_connection = ClipConnection(self)
        self.cached_results = {}

    async def handle(self):
        while True:
            message = await self.websocket.recv()
            await self.handle_message(message)

    async def handle_message(self, message):
        print(f"Received message {message} for client {self.connection_id} on path {self.path}")
        LogUtil.write_to_queries_log(message)
        client_request = ClientRequest(message)
        message = client_request.message
        message["clientId"] = self.connection_id
        await self.send_progress_step(f"Parsing message {client_request.content.get('type')} ...")

        if client_request.source == "appcomponent":
            handler_found = False

            # iterate through each message handler
            try:
                for handler in default_message_handlers:
                    if handler.should_handle(client_request):
                        handler_found = True
                        results = await handler.handle(client_request, self)
                        # make all fields serializable
                        results = ObjectSerializer.objects_to_serialized_json(results)
                        # send results back to the client
                        print(f"send results {results}")
                        await self.websocket.send(json.dumps(results))
                if not handler_found:
                    print(f"Unknown content type {client_request.content.get('type')}")
                    await self.send_error(f"Unknown content type {client_request.content.get('type')}")
            except ResponseError as e:
                await self.send_error(e.message)
            except Exception as e:
                await self.send_error(f"An unknown error occurred: {e}")
        else:
            print(f"Unknown source type {message.get('source')}")
            await self.send_error(f"Unknown source type {message.get('source')}")

    """
    Send an error message to the client
    """

    async def send_error(self, error):
        if self.websocket:
            await self.websocket.send(json.dumps({"type": "error", "error": error}))

    """
    Send a process step like 'loading data' etc. to the client
    """

    async def send_progress_step(self, message):
        if self.websocket:
            await self.websocket.send(json.dumps({"type": "progress", "message": message}))
