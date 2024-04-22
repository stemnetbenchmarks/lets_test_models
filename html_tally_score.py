import csv
import html
import glob
import os
from datetime import datetime


def make_score_tally_html_report(target_csv_file_sources_dir, path_out):
    """
    works with
    html_for_all_score_tallies()
    """
    csv_files = glob.glob(os.path.join(target_csv_file_sources_dir, "*.csv"))

    # get files only that say 'score report'
    csv_files = [item for item in csv_files if "score_report" in item]

    print(f"For this many tallieses: {len(csv_files)}")


    try:
        html_content = """
        <html>
        <head>
            <title>Score Tally Summary</title>
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
            <h1>Score Tally Summary</h1>
            <table>
                <tr>
                    <th>Percent</th>
                    <th>Model</th>
                    <th>Task File</th>
                    <th>Score</th>
                    <th>Timestamp</th>
                </tr>
        """
        for csv_file in csv_files:
                        
            try:
                with open(csv_file, "r") as csvfile:
                    csvreader = csv.DictReader(csvfile)
                    for row in csvreader:

                        
                        # remove the redundancy in the set list
                        # Split the task_file string by comma and convert it to a set
                        task_files = set(row["task_file"].split(", "))
                        
                        # Join the unique task files back into a comma-separated string
                        row["task_file"] = ", ".join(task_files)

                        
                        html_content += """
                            <tr>
                                <td>{percent}</td>
                                <td>{model}</td>
                                <td>{task_file}</td>
                                <td>{score}</td>
                                <td>{time_stamp}</td>
                            </tr>
                        """.format(
                            percent=html.escape(row["percent"]),
                            model=html.escape(row["model"]),
                            task_file=html.escape(row["task_file"]),
                            score=html.escape(row["score"]),
                            time_stamp=html.escape(row["time_stamp"]),
                        )
            except Exception as e:
                print(f"make_score_tally_html_report(), No dice on {csv_file} -> {e}")
                print("")
        html_content += """
            </table>
        </body>
        </html>
        """
        with open(path_out, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print(f"Score Tally HTML summary generated successfully!")
    except Exception as e:
        print(f"No dice on generating Score Tally HTML summary -> {e}")
        print("")


def html_for_all_score_tallies():
    """
    works with
    make_score_tally_html_report(target_csv_file_sources_dir, path_out)
    """
    date_time = datetime.now()
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")
    target_csv_file_sources_dir = "task_set_results_files"
    report_destination = f"task_set_results_files/HTML_score_tally_summary_{clean_timestamp}.html"
    make_score_tally_html_report(target_csv_file_sources_dir, report_destination)


######
# Run
######
if __name__ == "__main__":
    html_for_all_score_tallies()
