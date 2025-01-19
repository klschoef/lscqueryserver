import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='Get Recall at K value of result json files')
    parser.add_argument('result_file', help='Result File')
    parser.add_argument('--k_values', help='K values to calculate Recall at K', nargs='+', type=int, default=[1, 3, 5, 10, 20, 50, 100])
    parser.add_argument('--include_hints', help='hint indices (0-5)', nargs='+', type=int, default=[0, 1, 2, 3, 4, 5])
    parser.add_argument('--include_overall_mean', help='Include overall mean', type=bool, default=True)
    parser.add_argument('--latex_output', help='Output in Latex table format', type=bool, default=False)

    args = parser.parse_args()

    result_file = args.result_file
    data = None

    with open(result_file, 'r') as file:
        data = json.load(file)

    csv_output = []



    # add header labels
    csv_output.append(["Hint"]+[f"R@{k}" for k in args.k_values])

    for hint_index in args.include_hints:
        csv_row = []
        csv_row.append(f"Hint-{hint_index+1}")
        for k in args.k_values:
            csv_row.append(get_mean_recall_at_k_for_all_results(data, hint_index, k))
        csv_output.append(csv_row)

    if args.include_overall_mean:
        csv_row = ["All"]
        num_columns = len(csv_output[0]) - 1
        for col_index in range(1, len(csv_output[0])):
            column_total = 0
            num_values = 0
            for row in csv_output[1:]:
                value = row[col_index]
                column_total += value
                num_values += 1
            column_mean = column_total / num_values
            csv_row.append(column_mean)
        csv_output.append(csv_row)

    # normalize all numbers to 4 decimal places
    csv_output = [[round(x, 4) if isinstance(x, float) else x for x in row] for row in csv_output]

    seperator = "\t"
    if args.latex_output:
        seperator = " & "

    print("\n".join([seperator.join([str(x) for x in row]) for row in csv_output]))


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


if __name__ == "__main__":
    main()
