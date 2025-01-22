import json
import os
import math
import pandas as pd

from core.stages.base_stage import BaseStage
import logging

from core.utils.evaluation_util import get_mean_recall_at_k_for_all_results
from core.utils.file_util import get_project_related_file_path


class SummaryStage(BaseStage):

    def run(self, config):
        summary = [["type", "name", "model/core", "weight", "topic", "r@k summary"]]
        k_values = [1, 3, 5, 10, 20, 50, 100]
        include_hints = [0, 1, 2, 3, 4, 5]
        r_at_k_latex_contents = []
        csv_r_at_k_matrices = []
        for step in config.steps:
            folder_name = f"results/single_results/{step.name}"
            for topic_name in [t.split("/")[-1] for t in config.topic_files]:
                single_results_path = get_project_related_file_path(config.project_folder, f"{folder_name}/{topic_name}")
                # find the json file in the folder
                json_file = None  # Initialize json_file variable
                for file in os.listdir(single_results_path):
                    if file.endswith(".json"):
                        json_file = os.path.join(single_results_path, file)
                        break  # Stop the search once the first json file is found

                if json_file:
                    # Code to process the JSON file
                    print(f"Processing {json_file}")
                    summary_entry = [step.type, step.name, step.faiss.model if step.faiss else step.solr.core, step.faiss.weights if step.faiss else step.solr.core, topic_name]

                    with open(json_file, 'r') as file:
                        data = json.load(file)
                        csv_output = get_r_at_k_csv_matrix(include_hints, k_values, data, add_descriptions=False)
                        csv_output_with_descriptions = get_r_at_k_csv_matrix(include_hints, k_values, data, add_descriptions=True, add_sum_field_at_end=True)

                        # store detail matrix as csv
                        csv_file_path = os.path.join(single_results_path, f"r_at_k.csv")
                        save_matrix_to_csv(csv_output_with_descriptions, csv_file_path)
                        csv_r_at_k_matrices.append(csv_output_with_descriptions)

                        # store detail matrix as latex table
                        latex_file_path = os.path.join(single_results_path, f"r_at_k.tex")
                        latex_content = get_r_at_k_latex_table(csv_output_with_descriptions, caption=f"R@K for {step.name} on {topic_name}", label=f"{step.name}_{topic_name}")
                        save_matrix_to_latex_table(latex_content, latex_file_path)
                        r_at_k_latex_contents.append(latex_content)

                        csv_summary = 0
                        hints_amount = len(csv_output)
                        multiplicator_matrix = []
                        for hint in range(hints_amount,0,-1):
                            multiplicator_matrix_entry = []
                            for i in range(0, len(k_values)):
                                multiplicator = hint
                                for j in range(i):
                                    if multiplicator < 1:
                                        multiplicator *= 0.5
                                    else:
                                        multiplicator -= 0.5
                                value = csv_output[hints_amount-hint][i]

                                if value > 0:
                                    # add 1 if there is a value
                                    multiplicator += 1
                                multiplicator_matrix_entry.append(multiplicator)
                                csv_summary += value * multiplicator
                            multiplicator_matrix.append(multiplicator_matrix_entry)

                        summary_entry.append(csv_summary)
                    summary.append(summary_entry)
                else:
                    print(f"No JSON file found in {single_results_path}")

        logging.info(f"calc summaries: {summary}")
        print("\n".join([",".join([str(x) for x in row]) for row in summary]))

        # store summary matrix as csv
        df = pd.DataFrame(summary[1:], columns=summary[0])
        csv_file_path = get_project_related_file_path(config.project_folder, f"results/summaries/overview.csv")
        df.to_csv(csv_file_path, index=False)
        with open(get_project_related_file_path(config.project_folder, f"results/summaries/r_at_k_values.tex"), 'w') as file:
            file.write("\n".join(r_at_k_latex_contents))

        # store descended sorted summary matrix as csv
        csv_file_path = get_project_related_file_path(config.project_folder, f"results/summaries/descended_sorted_overview.csv")
        df.sort_values(by=df.columns[-1], ascending=False).to_csv(csv_file_path, index=False)
        with open(get_project_related_file_path(config.project_folder, f"results/summaries/descended_r_at_k_values.tex"), 'w') as file:
            file.write("\n".join([r_at_k_latex_contents[i] for i in df.sort_values(by=df.columns[-1], ascending=False).index.tolist()]))





def save_matrix_to_csv(matrix, file_path):
    with open(file_path, 'w') as file:
        for row in matrix:
            file.write(",".join([str(x) for x in row]) + "\n")

def save_matrix_to_latex_table(content, file_path):
    with open(file_path, 'w') as file:
        file.write(content)

def get_r_at_k_latex_table(matrix, caption="", label="", formatting="{|p{2cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|p{1.5cm}|}"):
    output = ""
    output += "\\begin{table*}[htb!]\n"
    output += "    \\centering\n"
    output += "    \\begin{tabular}"
    output += formatting+"\n"
    output += "\\toprule\n"
    output += "\\textbf{Hints} & \\textbf{R@1} & \\textbf{R@3} & \\textbf{R@5} & \\textbf{R@10} & \\textbf{R@20} & \\textbf{R@50} & \\textbf{R@100}\\\\\n"
    output += "\\midrule\n"
    for row in matrix[1:]:
        output += " & ".join([x if isinstance(x, str) else format(x, ".2f") for x in row]) + "\\\\\n"
    output += "\\bottomrule\n"
    output += "    \\end{tabular}\n"
    output += "    \\caption{"+caption.replace("_", "\\_")+"}\n"
    output += "    \\label{tab:"+label.replace("_", "\\_")+"}\n"
    output += "\\end{table*}\n"
    return output

def get_r_at_k_csv_matrix(include_hints, k_values, data, add_descriptions=False, add_sum_field_at_end=False):
    csv_output = []

    if add_descriptions:
        csv_row = [""] + [f"R@{k}" for k in k_values]
        csv_output.append(csv_row)

    for hint_index in include_hints:
        csv_row = []
        if add_descriptions:
            csv_row.append(f"Hint-{hint_index+1}")
        for k in k_values:
            csv_row.append(get_mean_recall_at_k_for_all_results(data, hint_index, k))
        csv_output.append(csv_row)

    if add_sum_field_at_end:
        if add_descriptions:
            df = pd.DataFrame(csv_output[1:], columns=csv_output[0])
            means = ["All"] + df.iloc[:, 1:].mean().tolist()
        else:
            df = pd.DataFrame(csv_output)
            means = df.iloc[:, :].mean().tolist()

        csv_output.append(means)

    return csv_output

def generate_weights_matrix():
    weights = []
    for hint_id in range(6):
        # start with the highest number for the first hint
        hint_value = 6-hint_id
        weights_entry = []
        for k_pos in range(7):
            # start with the highest number for the first R@K value
            k_pos_value = 7-k_pos
            # the initial weight is the hint_value
            weight = hint_value
            # decrease the weight for each R@K value
            for j in range(k_pos):
                if weight >= 1:
                    # if the weight is greater or equal 1, subtract 0.5
                    weight -= 0.5
                else:
                    # if the weight is smaller then 1, multiply the value with 0.5, to prevent 0 or negative values
                    weight *= 0.5

            # at the end, add 1 to prevent 0 weights
            weight += 1

            # add to weight array
            weights_entry.append(weight)
        weights.append(weights_entry)
    return weights