class ClientRequest:
    def __init__(self, message):
        self.message = message or {}
        self.content = message.get('content', {})
        self.type = self.content.get('type')
        self.source = message.get('source')
        self.version = self.content.get("version", 1)
