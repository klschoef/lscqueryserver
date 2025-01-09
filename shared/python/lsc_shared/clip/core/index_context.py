import logging

from lsc_shared.clip.core.exceptions.empty_index_exception import EmptyIndexException
from lsc_shared.clip.core.helpers.faiss_helper import load_clip_features, get_faiss_and_label_paths, save_faiss_index, append_labels_to_label_file

logging.basicConfig(level=logging.DEBUG)

class IndexContext:
    def __init__(self, faiss_folder):
        self.faiss_folder = faiss_folder
        self._index = None
        self._datalabels = None
        self._faiss_path, self._labels_path = get_faiss_and_label_paths(faiss_folder)

        # try to load clip features
        try:
            self.load_clip_features()
        except EmptyIndexException as e:
            logging.error(e)

    def get_index(self):
        if self._index is None:
            self.load_clip_features()
        return self._index

    def get_datalabels(self):
        if self._datalabels is None:
            self.load_clip_features()
        return self._datalabels

    def load_clip_features(self):
        try:
            self._index, self._datalabels = load_clip_features(folder_path=self.faiss_folder)
        except EmptyIndexException as e:
            logging.error(e)
            self._index = None
            self._datalabels = None

    def add_new_entry(self, features_array, label, store=True):
        if self._index is None:
            self.load_clip_features()
        self._index.add(features_array)
        self._datalabels.append(label)

        if store:
            save_faiss_index(self._index, self.faiss_folder)
            append_labels_to_label_file([label], self.faiss_folder)

    def store_index(self):
        save_faiss_index(self._index, self.faiss_folder)
        append_labels_to_label_file(self._datalabels, self.faiss_folder)
