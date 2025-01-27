class BasePipeline:
    def __init__(self):
        pass

    """
    Needs to return the image and image_document (image, image_document) after processing the image
    """
    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        raise NotImplementedError

    """
    valid_after_timestamp = datetime to check if an entry should be updated. If None, no timestamp check is performed
    """
    def should_update(self, image, image_document, mongo_collection, valid_after_timestamp=None, *args, **kwargs) -> bool:
        return True