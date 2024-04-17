"""
Exception class to send an error to the client.
Just raise this error in any process of message handling.
"""
class ResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)