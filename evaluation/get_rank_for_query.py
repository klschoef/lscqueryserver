import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='Get Recall at K value of result json files')
    parser.add_argument('result_file', help='Result File')
    parser.add_argument('query_name', help='Name of the query like LSC23-KIS06')
    parser.add_argument('--latex_output', help='Output in Latex table format', type=bool, default=False)
    parser.add_argument('--show_header', help='Show header', type=bool, default=False)

    args = parser.parse_args()

    result_file = args.result_file
    data = None

    with open(result_file, 'r') as file:
        data = json.load(file)

    result_list = [item for item in data if item["query_name"] == args.query_name]

    if len(result_list) == 0:
        print("Query not found in the result file")
        return

    result = result_list[0]
    recall_per_hint = result.get("recall_per_hint")

    csv_output = []

    if args.show_header:
        csv_output.append([f"H{i+1}" for i in range(len(recall_per_hint))])

    csv_output.append([recall for recall in recall_per_hint]) # values

    seperator = "\t"
    if args.latex_output:
        seperator = " & "

    print("\n".join([seperator.join([str(x or "-") for x in row]) for row in csv_output]))


if __name__ == "__main__":
    main()
