# import csv
# import html


# def make_html_report(path_in, path_out):
    
    
#     # Open the CSV file
#     with open('your_file.csv', 'r') as csvfile:
#         csvreader = csv.DictReader(csvfile)

#         # Generate HTML content
#         html_content = """
#         <html>
#         <head>
#             <title>CSV Summary</title>
#             <style>
#                 table, th, td {
#                     border: 1px solid black;
#                     border-collapse: collapse;
#                     padding: 5px;
#                 }
#             </style>
#         </head>
#         <body>
#             <h1>CSV Summary</h1>
#             <table>
#                 <tr>
#                     <th>Score</th>
#                     <th>Selected Option</th>
#                     <th>Correct Option</th>
#                     <th>Task Failure Comment</th>
#                     <th>Name of Model</th>
#                     <th>Task from Instructions</th>
#                     <th>Error Log</th>
#                     <th>Duration of Single Task</th>
#                     <th>Readable Timestamp</th>
#                 </tr>
#         """

#         # Iterate over the rows in the CSV file
#         for row in csvreader:
#             html_content += """
#                 <tr>
#                     <td>{score}</td>
#                     <td>{selected_option}</td>
#                     <td>{correct_option}</td>
#                     <td>{task_failure_comment}</td>
#                     <td>{name_of_model}</td>
#                     <td>{task_from_instructions}</td>
#                     <td>{error_log}</td>
#                     <td>{duration_of_single_task}</td>
#                     <td>{readable_timestamp}</td>
#                 </tr>
#             """.format(
#                 score=html.escape(row['score']),
#                 selected_option=html.escape(row['selected_option']),
#                 correct_option=html.escape(row['correct_option']),
#                 task_failure_comment=html.escape(row['task_failure_comment']),
#                 name_of_model=html.escape(row['name_of_model']),
#                 task_from_instructions=html.escape(row['task_from_instructions']),
#                 error_log=html.escape(row['error_log']),
#                 duration_of_single_task=html.escape(row['duration_of_single_task']),
#                 readable_timestamp=html.escape(row['readable_timestamp'])
#             )

#         html_content += """
#             </table>
#         </body>
#         </html>
#         """

#         # Save the HTML content to a file
#         with open('csv_summary.html', 'w', encoding='utf-8') as html_file:
#             html_file.write(html_content)

#     print("HTML summary generated successfully!")
    
    
# target_csv_file_sources_dir = "task_set_results_mistral-7b-instruct_20240320111343547741_my_test1_jsonl.csv"
# report_destination = ""

# glob get list of csv files:
# for csv in glob_list:
    

#     def make_html_report(target_csv_file_sources_dir, report_destination):


import csv
import html
import glob
import os

def make_html_report(path_in, path_out):
    
    try:
        # Open the CSV file
        with open(path_in, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            # Generate HTML content
            html_content = """
            <html>
            <head>
                <title>CSV Summary</title>
                <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                        padding: 5px;
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
                        <th>Task from Instructions</th>
                        <th>Error Log</th>
                        <th>Duration of Single Task</th>
                        <th>Readable Timestamp</th>
                    </tr>
            """

            # Iterate over the rows in the CSV file
            for row in csvreader:
                html_content += """
                    <tr>
                        <td>{score}</td>
                        <td>{selected_option}</td>
                        <td>{correct_option}</td>
                        <td>{task_failure_comment}</td>
                        <td>{name_of_model}</td>
                        <td>{task_from_instructions}</td>
                        <td>{error_log}</td>
                        <td>{duration_of_single_task}</td>
                        <td>{readable_timestamp}</td>
                    </tr>
                """.format(
                    score=html.escape(row['score']),
                    

                        
                    selected_option=html.escape(row['selected_option']),
                    correct_option=html.escape(row['correct_option']),
                    # task_failure_comment=html.escape(row['task_failure_comment']),
                    task_failure_comment = "",
                    name_of_model=html.escape(row['name_of_model']),
                    task_from_instructions=html.escape(row['task_from_instructions']),
                    error_log=html.escape(row['error_log']),
                    duration_of_single_task=html.escape(row['duration_of_single_task']),
                    readable_timestamp=html.escape(row['readable_timestamp'])
                    

                )
            html_content += """
                </table>
            </body>
            </html>
            """
            
        
            
            # Save the HTML content to a file
            with open(path_out, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
        print(f"HTML summary generated successfully for {path_in}!")

    except Exception as e:
        print( f"No dice on {path_in} -> {e}" )   
        print( "" )   
        
target_csv_file_sources_dir = "task_set_results_files"
report_destination = "task_set_results_files"


# Get a list of CSV files in the target directory
csv_files = glob.glob(os.path.join(target_csv_file_sources_dir, "*.csv"))


# Process each CSV file
for csv_file in csv_files:
    
    try:    
        # Generate the output file path
        output_file = os.path.join(report_destination, f"{os.path.splitext(os.path.basename(csv_file))[0]}.html")

    except Exception as e:
        print( f"No dice on {csv_file} -> {e}" )   
        print( "" )   
    
    # Call the make_html_report function for each CSV file
    make_html_report(csv_file, output_file)