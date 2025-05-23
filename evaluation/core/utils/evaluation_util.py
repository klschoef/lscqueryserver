def get_mean_recall_at_k_for_all_results(dict_array, hint_index, k):
    total = 0
    for query in dict_array:
        total += get_recall_at_k_for_quest_results(query, hint_index, k)

    return total / len(dict_array)


"""
get the recall at k value for one single query with a given hint index. Returns 1 (found) or 0 (not found in the recall@k)
    {
        "query_name": "LSC23-KIS07",
        "recall_per_hint": [
            63,
            null,
            40,
            5,
            1,
            2
        ]
    },
    
"""


def get_recall_at_k_for_quest_results(query, hint_index, k):
    found_index = query.get('recall_per_hint')[hint_index]

    if found_index is None:
        return 0

    return 1 if found_index <= k else 0

def recall_at_k(ranks, num_of_relevant_items, k):
    top_k = retrieved_items[:k]
    relevant_in_top_k = [item for item in top_k if item in relevant_items]
    if len(relevant_items) == 0:
        return 0.0
    return len(relevant_in_top_k) / len(relevant_items)