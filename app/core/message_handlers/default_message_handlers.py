from core.message_handlers.handlers.message_concepts import MessageConcepts
from core.message_handlers.handlers.message_metadata import MessageMetadata
from core.message_handlers.handlers.message_objects import MessageObjects
from core.message_handlers.handlers.message_places import MessagePlaces
from core.message_handlers.handlers.message_query import MessageQuery
from core.message_handlers.handlers.message_texts import MessageTexts

default_message_handlers = [
    MessageMetadata(),
    MessageObjects(),
    MessageConcepts(),
    MessagePlaces(),
    MessageTexts(),
    MessageQuery()
]