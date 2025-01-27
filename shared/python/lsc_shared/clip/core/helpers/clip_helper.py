import os

import open_clip
import pandas as pd
import logging
import faiss
import math

logging.basicConfig(level=logging.DEBUG)

def search_in_index(features, index, amount_of_results):
    distances, ids = index.search(features, amount_of_results)
    return distances, ids


def filter_and_label_results(ids, distances, labels, resultsPerPage, selectedPage):
    results = []
    result_ids = []
    result_distances = []
    page_start = (selectedPage - 1) * resultsPerPage
    page_end = selectedPage * resultsPerPage

    for i in range(page_start, page_end):
        current_id = ids[0][i]
        distance = distances[0][i]
        if current_id == -1:
            break
        results.append(str(labels[current_id]))
        result_ids.append(int(current_id))
        result_distances.append(str(distance))
    return results, result_ids, result_distances


def get_clip_features_from_text(text, clip_context):
    inp = clip_context.tokenizer(text).to(clip_context.device)
    return clip_context.model.encode_text(inp).cpu()

def clip_text_search(text, index_context, clip_context, max_results, results_per_page=None, selected_page=1):
    if results_per_page is None:
        results_per_page = max_results
    text_features = get_clip_features_from_text(text, clip_context)
    distances, ids = search_in_index(text_features, index_context.get_index(), max_results)
    return filter_and_label_results(ids, distances, index_context.get_datalabels(), results_per_page, selected_page)

def clip_similarity_search(index_context, idx, max_results):
    distances, ids = index_context.get_index().search(index_context.get_index().reconstruct(idx), max_results)
    return distances, ids

def calculate_l2_distance(list1, list2):
    """Calculate the L2 distance between two lists of floats."""
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length.")

    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(list1, list2)))
    return distance