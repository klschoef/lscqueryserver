class BasePipeline:
    def __init__(self):
        pass

    """
    Needs to return the image and image_document (image, image_document) after processing the image
    """
    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        raise NotImplementedError
