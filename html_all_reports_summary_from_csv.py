import csv
import html
import glob
import os
from datetime import datetime


def make_html_report(target_csv_file_sources_dir, path_out):

    csv_files = glob.glob(os.path.join(target_csv_file_sources_dir, "*.csv"))

    try:
        html_content = """
        <html>
        <head>
            <title>CSV Summary</title>
            <style>
                table, th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    padding: 5px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h1>CSV Summary</h1>
            <table>
                <tr>
                    <th>Score</th>
                    <th>Selected Option</th>
                    <th>Correct Option</th>
                    <th>Task Failure Comment</th>
                    <th>Name of Model</th>
                    <th>Task File</th>
                    <th>Task from Instructions</th>
                    <th>Retries</th>
                    <th>Error Log</th>
                    <th>Duration of Single Task</th>
                    <th>Readable Timestamp</th>
                </tr>
        """

        for csv_file in csv_files:
            try:
                with open(csv_file, "r") as csvfile:
                    csvreader = csv.DictReader(csvfile)
                    for row in csvreader:
                        html_content += """
                            <tr>
                                <td>{score}</td>
                                <td>{selected_option}</td>
                                <td>{correct_option}</td>
                                <td>{task_failure_comment}</td>
                                <td>{name_of_model}</td>
                                <td>{task_file}</td>
                                <td>{task_from_instructions}</td>
                                <td>{retry_counter}</td>
                                <td>{error_log}</td>
                                <td>{duration_of_single_task}</td>
                                <td>{readable_timestamp}</td>
                            </tr>
                        """.format(
                            score=html.escape(
                                row["score"]),
                            selected_option=html.escape(
                                row["selected_option"]),
                            correct_option=html.escape(
                                row["correct_option"]),
                            task_failure_comment=html.escape(
                                row["task_failure_comment"]),
                            name_of_model=html.escape(
                                row["name_of_model"]),
                            task_file=html.escape(
                                row["task_file"]),                            
                            task_from_instructions=html.escape(
                                row["task_from_instructions"]),
                            retry_counter=html.escape(
                                row["retry_counter"]),
                            error_log=html.escape(
                                row["error_log"]),
                            duration_of_single_task=html.escape(
                                row["duration_of_single_task"]),
                            readable_timestamp=html.escape(row["readable_timestamp"]),
                        )
            except Exception as e:
                print(f"No dice on {csv_file} -> {e}")
                print("")

        html_content += """
            </table>
        </body>
        </html>
        """

        with open(path_out, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"HTML summary generated successfully!")
    except Exception as e:
        print(f"No dice on generating HTML summary -> {e}")
        print("")



def html_for_all_reports():

    date_time = datetime.now()
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")

    target_csv_file_sources_dir = "task_set_results_files"
    report_destination = f"task_set_results_files/HTML_summary_{clean_timestamp}.html"

    make_html_report(target_csv_file_sources_dir, report_destination)


######
# Run
######
if __name__ == "__main__":

    html_for_all_reports()
