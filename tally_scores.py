import os
import csv


def append_dict_of_values_row_with_fields_list_to_csv(values_dict, fields_list, path):
    """
    Appends a row of fields to a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        fields (list): A list of fields to be appended as a row to the CSV file.

    Returns:
        None
    """
    with open(path, "a", newline="") as csvfile:
        fieldnames = fields_list
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(values_dict)



def score_tally(directory_path):
    solution_dir_path = os.path.abspath(directory_path)

    # Ensure the directory exists
    os.makedirs(solution_dir_path, exist_ok=True)

    report_filename = os.path.join(solution_dir_path, "score_report.csv")
    tally_header_string_list = ["percent", "model", "score", "time_stamp"]

    # # Check if the file exists and is empty to decide on writing the header
    if not os.path.exists(report_filename) or os.path.getsize(report_filename) == 0:
        #     with open(report_filename, 'w', newline='') as csvfile:
        #         csvfile.write(header_string)

        create_cvs_list_of_fields_to_csv_header(
            report_filename, tally_header_string_list
        )

    try:
        model_scores = {}
        total_scores = 0
        # Iterate over CSV files and tally scores
        for filename in os.listdir(directory_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(directory_path, filename)
                print(f"Processing file: {file_path}")
                with open(file_path, mode="r", newline="") as file:
                    # Read the file into a dictionary, trimming spaces from headers
                    reader = csv.DictReader(
                        (line.replace("\0", "") for line in file), skipinitialspace=True
                    )
                    # Adjust the fieldnames to strip leading and trailing spaces
                    reader.fieldnames = [name.strip() for name in reader.fieldnames]
                    for row in reader:
                        # Attempt to get the model name with a case-insensitive key searchhttps://docs.python.org/3/library/csv.html
                        for key in row.keys():
                            if key.lower() == "name_of_model".lower():
                                model_name = row[key]
                                print(
                                    f"name_of_model -> {model_name}"
                                )  # Confirming model name retrieval
                                score = int(row.get("score", 0))
                                model_scores.setdefault(
                                    model_name, {"total": 0, "count": 0}
                                )
                                model_scores[model_name]["total"] += score
                                model_scores[model_name]["count"] += 1
                                total_scores += 1

        # Prepare report lines excluding the header https://stackoverflow.com/questions/2363731/how-to-append-a-new-row-to-an-old-csv-file-in-python
        report_list = []
        for model_name, score_data in model_scores.items():
            percentage = (
                (score_data["total"] / total_scores) * 100 if total_scores > 0 else 0
            )
            score = f"{score_data["total"]} / {score_data["count"]}"
            report_line = [percentage, model_name, score]
            report_list.append(report_line)

        for report_line in report_list:
            print(report_line)

            date_time = datetime.now(UTC)
            readable_timestamp = date_time.strftime("%Y-%m-%d-%H:%M:%S%f")
            report_line.append(readable_timestamp)

            append_list_of_values_to_csv(report_filename, report_line)

        print(f"Report appended to {report_filename}")

    except Exception as e:
        print(f"Error processing score tally: {e}")



from datetime import datetime, UTC


def create_cvs_list_of_fields_to_csv_header(file_path, fields_list):
    """
    Appends a row of fields_list to a CSV file with the specified format.

    Args:
        file_path (str): The path to the CSV file.
        fields_list (list): A list of fields_list to be appended as a row to the CSV file.

    Returns:
        None
    """
    try:
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            # writer = csv.writer(file)
            writer.writerow(fields_list)
        print("Row appended successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def append_list_of_values_to_csv(file_path, fields_list):
    """
    Appends a row of fields_list to a CSV file with the specified format.

    Args:
        file_path (str): The path to the CSV file.
        fields_list (list): A list of fields_list to be appended as a row to the CSV file.

    Returns:
        None
    """
    try:
        print(f"fields_list {fields_list}")

        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            # writer = csv.writer(file)
            writer.writerow(fields_list)
        print("Row appended successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Example usage
score_tally("task_set_results_files")
