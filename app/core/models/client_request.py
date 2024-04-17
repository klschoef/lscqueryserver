import json


class ClientRequest:
    def __init__(self, message_string):
        self.message_string = message_string
        self.message = json.loads(message_string)
        self.message = self.message or {}
        self.content = self.message.get('content', {})
        self.type = self.content.get('type')
        self.source = self.message.get('source')
        self.version = self.content.get("version", 1)
