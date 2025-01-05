import logging

from core.exceptions.empty_index_exception import EmptyIndexException
from core.helpers.clip_helper import loadClipFeatures

logging.basicConfig(level=logging.DEBUG)

class IndexContext:
    def __init__(self, csvfilename):
        self.csvfilename = csvfilename
        self._index = None
        self._data = None
        self._datalabels = None

        # try to load clip features
        try:
            loadClipFeatures(csvfilename=self.csvfilename)
        except EmptyIndexException as e:
            logging.error(e)

    def get_index(self):
        if self._index is None:
            self.load_clip_features()
        return self._index

    def get_data(self):
        if self._data is None:
            self.load_clip_features()
        return self._data

    def get_datalabels(self):
        if self._datalabels is None:
            self.load_clip_features()
        return self._datalabels

    def load_clip_features(self):
        try:
            self._index, self._data, self._datalabels = loadClipFeatures(csvfilename=self.csvfilename)
        except EmptyIndexException as e:
            logging.error(e)
            self._index = None
            self._data = None
            self._datalabels = None
