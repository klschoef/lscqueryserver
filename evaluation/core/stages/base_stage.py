import abc


class BaseStage(abc.ABC):

    @abc.abstractmethod
    def run(self, config):
        pass
