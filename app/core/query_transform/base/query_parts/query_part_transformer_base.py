from abc import ABC, abstractmethod


class QueryPartTransformerBase(ABC):
    """
    Define if this transformer should be used for the given query_dict.
    :param query_dict: The query dict
    :return: True if this transformer should be used, otherwise False
    """

    @abstractmethod
    def should_use(self, query_dict):
        pass

    """
    Transform the result_object with the given query_dict.
    :param result_object: The result object
    :param query_dict: The query dict
    :return: None - transform the result_object in place
    """

    @abstractmethod
    def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        pass

    """
    Return a list of needed kwargs for this transformer.
    :return: List of needed kwargs
    """

    def needed_kwargs(self):
        return []
