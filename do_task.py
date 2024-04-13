# -*- coding: utf-8 -*-
import os

"""
Uncomment for cloud mode
"""
# import requests
# import anthropic
# from dotenv import load_dotenv
# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")
# mistral_api_key = os.getenv("mistral_api_key")
# anthropic_api_key = os.getenv("anthropic_api_key")


"""
Offline and Vanilla OK!
"""
import traceback
import string
import random
import time
import sys
from datetime import datetime, UTC
import json  # Added missing import
import re
import subprocess
import csv
import html
import glob

#
from call_llamacpp import gguf_api, mini_gguf_api


"""
.env: get your environment variables:
  Using the Google Secretes (like.env) system
  built into colab on the left menu: the 'key' icon.
"""
# from google.colab import userdata

# mistral_api_key = userdata.get("mistral_api_key")
# # mistral_api_key = 'xxx'
# openai_api_key = userdata.get("open_ai_key")


"""# make a list of json files"""
# import openai
# from google.colab import userdata

# Load environment variables from .env file


def make_answers_directory_and_csv_path_header_string(
    this_original_task_file, model_name
):
    """
    Returns a list of .json files in the current working directory.
    """
    solution_dir_path = "task_set_results_files"
    date_time = datetime.now(UTC)
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")

    # make path absolute
    solution_dir_path = os.path.abspath(solution_dir_path)

    # Check if the directory exists
    if not os.path.exists(solution_dir_path):

        # If it does not exist, create it
        # Ensure the directory exists
        try:
            os.makedirs(
                solution_dir_path, exist_ok=True
            )  # Ensure the directory is created if it does not exist
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating directory {solution_dir_path}: {e}")
            return  # Exit the function if directory creation fails

    # make path absolute, belts and suspenders
    solution_dir_path = os.path.abspath(solution_dir_path)

    # Extract just the last part of {model_name} and {this_original_task_file}
    model_name_last_part = os.path.basename(model_name).replace(
        ".", "_"
    )  # Replacing dots to avoid file extension confusion
    original_task_file_last_part = os.path.basename(this_original_task_file).replace(
        ".", "_"
    )

    task_set_results_path = f"task_set_results_{model_name_last_part}_{clean_timestamp}_{original_task_file_last_part}.csv"

    # Determine the path to the file that should be saved
    task_set_results_path = os.path.join(solution_dir_path, task_set_results_path)

    # TODO:
    # 1. extract just the last part of {model_name}
    # 2. extract just the last part of {this_original_task_file}
    # 3. make path, create directories and empty file

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(task_set_results_path), exist_ok=True)

    # header_string = '"score","this_row_or_line_number","selected_option","correct_option","task_failure_comment","name_of_model","task_file","task_from_instructions","question_task_prompt","list_of_ranked_choice_options","draft_task_attempt_log","error_log","duration_of_single_task","readable_timestamp"\n'

    # # Create an empty file (or just close it if it already exists)
    # with open(task_set_results_path, "a", newline="") as csvfile:
    #     csvfile.write(header_string)

    header_string_list = [
        "score",
        "this_row_or_line_number",
        "selected_option",
        "correct_option",
        "task_failure_comment",
        "name_of_model",
        "task_file",
        "task_from_instructions",
        "question_task_prompt",
        "list_of_ranked_choice_options",
        "draft_task_attempt_log",
        "formatting_notes",
        "retry_counter",
        "error_log",
        "duration_of_single_task",
        "readable_timestamp",
    ]

    # Create an empty file (or just close it if it already exists)
    with open(task_set_results_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_string_list)

    return task_set_results_path


def merge_answer_csv_files():
    # TODO
    pass


# Helper Function
def list_files_in_aitaskfiles_dir(file_type_list=None):
    """
    Returns a list of task files in the current working directory.
    """
    file_path = "ai_task_files"
    output_list = None

    # make path absolute
    file_path = os.path.abspath(file_path)

    # Check if the directory exists
    if not os.path.exists(file_path):

        # If it does not exist, create it
        # Ensure the directory exists
        try:
            os.makedirs(
                file_path, exist_ok=True
            )  # Ensure the directory is created if it does not exist
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating directory {file_path}: {e}")
            return  # Exit the function if directory creation fails

    # make path absolute, belts and suspenders
    file_path = os.path.abspath(file_path)

    try:
        if file_type_list is None:
            # default to:
            file_type_list = [".json", ".csv"]
            print("No files types specified, defaulting to: .json and .csv")

        output_list = []

        # if not a list already, then make it a list
        if isinstance(file_type_list, str):
            file_type_list = [file_type_list]

        for this_file_type in file_type_list:
            # Define the directory path
            directory_path = "ai_task_files"

            # List all files in the specified directory
            files_in_cwd = os.listdir(directory_path)

            # Filter the list to include only files of the requested type
            task_files = [
                os.path.abspath(os.path.join(directory_path, file))
                for file in files_in_cwd
                if file.endswith(this_file_type)
            ]

            output_list.append(task_files)

        # remove empty lists
        output_list = [item for item in output_list if item]

        # flattened_list
        output_list = [item for sublist in output_list for item in sublist]

        # print(output_list)
        if not output_list:
            message = f"\n\nExit Dungeon: Your file list in /{file_path}/ is empty, add a file and try!\n\n"
            sys.exit(message)

        # remove duplicates
        output_list_set = set(output_list)
        output_list = list(output_list_set)

        return output_list

    except Exception as e:
        traceback.print_exc()
        raise e


"""# Process Json
- make a model/skeleton template
"""


# Helper Function
def load_json_file(file_path):
    """
    Loads and reads a JSON file, returning its content as a Python dictionary.

    :param file_path: Path to the .json file to be read.
    :return: A dictionary containing the data from the JSON file.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# Helper Function
def list_create_deep_empty_structure(data):
    """
    Recursively creates a deep copy of the provided data structure,
    replacing all terminal values with empty lists, and maintaining the same structure.

    :param data: The original data structure, potentially containing nested dictionaries.
    :return: A new data structure with the same keys but with empty lists as terminal values.
    """
    if isinstance(data, dict):  # Checks if the current data item is a dictionary
        return {
            key: list_create_deep_empty_structure(value) for key, value in data.items()
        }
    else:
        return []  # Replaces non-dictionary values with an empty list


# Helper Function
def string_create_deep_empty_structure(data):
    """
    Recursively creates a deep copy of the provided data structure,
    replacing all terminal values with empty lists, and maintaining the same structure.

    :param data: The original data structure, potentially containing nested dictionaries.
    :return: A new data structure with the same keys but with empty lists as terminal values.
    """
    if isinstance(data, dict):  # Checks if the current data item is a dictionary
        return {
            key: string_create_deep_empty_structure(value)
            for key, value in data.items()
        }
    else:
        return ""  # Replaces non-dictionary values with an empty list


# Helper Function
def create_empty_json_file(original_data, new_file_path):
    """
    Creates a new JSON file replicating the structure of the original data,
    but with empty lists for all terminal values.

    :param original_data: Dictionary containing the original data.
    :param new_file_path: Path for the new .json file to be created.
    """
    # Create a new structure with the same keys but with empty lists as terminal values
    empty_data = list_create_deep_empty_structure(original_data)

    # Write this new structure to a new JSON file
    with open(new_file_path, "w") as file:
        json.dump(empty_data, file, indent=4)

    return empty_data


# Helper Function
def create_empty_selectbest_frame(original_data, new_file_path):
    """
    Creates a new JSON file replicating the structure of the original data,
    but with empty lists for all terminal values.

    :param original_data: Dictionary containing the original data.
    :param new_file_path: Path for the new .json file to be created.
    """
    # Create a new structure with the same keys but with empty lists as terminal values
    empty_data = string_create_deep_empty_structure(original_data)

    # Write this new structure to a new JSON file
    with open(new_file_path, "w") as file:
        json.dump(empty_data, file, indent=4)

    return empty_data


"""# put translation into list_skeleton_json"""


def extract_code_from_markdown(markdown_text, function_name):
    """
    requires re
    Extract the longest code block from the given Markdown text.

    Args:
        markdown_text (str): The Markdown text containing code blocks.

    Returns:
        str: The longest code block found in the text, or an empty string if no code block is found.

    variation cases:

    variations include
    ```
    ```

    ```markdown
    ```

    ```python
    ```

    ```code
    ```


    """
    # Regular expression pattern to match code blocks
    code_block_pattern = r"```(python|rust|markdown|code)?\n([\s\S]*?)\n```"
    # Find all code blocks in the text
    code_blocks = re.findall(code_block_pattern, markdown_text, re.MULTILINE)
    
    print(f"extract_code_from_markdown code_blocks -> {code_blocks}")


    # """
    # TODO
    # Find def {function_name} or fn {function_name}
    # """
    # code here
    
    
    # # if still more than one, Find the longest code block
    # longest_code_block = max(code_blocks, key=lambda x: len(x[1]), default=("", ""))

    # print(f"extract_code_from_markdown longest_code_block -> {longest_code_block}")

    
    # return longest_code_block[1]

    # Find the code blocks containing the function definition
    function_pattern = rf"(def|fn)\s+{function_name}\s*\("
    matching_code_blocks = []
    for lang, code in code_blocks:
        if re.search(function_pattern, code, re.MULTILINE):
            matching_code_blocks.append((lang, code))

    # default
    match = None

    # If there are multiple matching code blocks, find the longest one
    if len(matching_code_blocks) > 1:
        print('found more than one match containing function definition')
        longest_matching_code_block = max(matching_code_blocks, key=lambda x: len(x[1]))
        # print(f"extract_code_from_markdown longest_matching_code_block -> {longest_matching_code_block}")
        
        match = longest_matching_code_block[1]
        
    elif len(matching_code_blocks) == 1:
        # print(f"extract_code_from_markdown matching_code_blocks[0][1] -> {matching_code_blocks[0][1]}")
        match = matching_code_blocks[0][1]
        
    if match: 
        print(f"\n found this code: {match} \n")
        return match

    return None

####################################
# helper functions for coding layer
####################################
import ast


def check_equivalent_string(expected, actual):
    """
    Checked if forced-type as
    'string'
    make these equivilant
    """
    try:
        return str(expected) == str(actual)
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def check_equivalent_integer(expected, actual):
    """
    Checked if forced-type as
    'int'
    make these equivilant
    """
    try:
        return int(expected) == int(actual)
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def check_equivalent_float(expected, actual, tolerance=1e-6):
    """
    Checked if forced-type as
    'float'
    make these equivilant
    """
    try:
        expected_float = float(expected)
        actual_float = float(actual)
        return abs(expected_float - actual_float) < tolerance and (
            expected_float < 0
        ) == (actual_float < 0)
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def check_equivalent_boolean(expected, actual):
    """
    Checked if forced-type as
    'bool'
    make these equivilantequivalent
    """
    try:
        # print('bool')
        if isinstance(expected, bool) and isinstance(actual, bool):
            return expected == actual

    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def check_equivalent_none(expected, actual):
    """
    Checked if forced-type as
    'None'
    make these equivilantequivalent
    """
    try:
        return expected is None and actual is None
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


# helper wrapper 1: check all
def simple_types_check_equivalent(expected, actual):
    """
    Check if expected and actual are equivalent using various type-specific comparison functions.
    Returns True if any of the type-specific comparisons are True, otherwise returns False.
    """
    checks = [
        check_equivalent_string,
        check_equivalent_integer,
        check_equivalent_float,
        check_equivalent_boolean,
        check_equivalent_none,
    ]

    try:

        for check_func in checks:
            if check_func(expected, actual):
                return True

        return False
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def check_equivalent_list(expected_list, actual_list_str):
    """
    Check if two lists are equivalent by comparing each element using the check_equivalent function.
    The actual_list_str is expected to be a string representation of a list.
    Returns True if the lists are equivalent, otherwise returns False.
    """
    try:
        # Convert the actual_list_str to a list using ast.literal_eval
        actual_list = ast.literal_eval(actual_list_str)

        if len(expected_list) != len(actual_list):
            # print('wrong length false')
            return False

        for expected_item, actual_item in zip(expected_list, actual_list):
            if not simple_types_check_equivalent(expected_item, actual_item):
                return False

        return True

    except (SyntaxError, ValueError):
        # If the actual_list_str is not a valid list representation, return False
        # print('exception')
        return False


def check_equivalent_dict(expected_dict, actual_dict):
    """
    Check if two dictionaries are equivalent by comparing each key-value pair using the check_equivalent function.
    Returns True if the dictionaries are equivalent, otherwise returns False.
    """
    try:
        if len(expected_dict) != len(actual_dict):
            return False

        for key in expected_dict:
            if key not in actual_dict:
                return False

            expected_value = expected_dict[key]
            actual_value = actual_dict[key]

            if isinstance(expected_value, dict):
                if not check_equivalent_dict(expected_value, actual_value):
                    return False
            elif isinstance(expected_value, list):
                if not check_equivalent_list(expected_value, actual_value):
                    return False
            else:
                if not simple_types_check_equivalent(expected_value, actual_value):
                    return False
        return True
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


# helper wrapper 2: check all
def check_equivalent_all(expected, actual):
    """
    Check if expected and actual are equivalent using various type-specific comparison functions.
    Returns True if any of the type-specific comparisons are True, otherwise returns False.
    """
    checks = [
        check_equivalent_string,
        check_equivalent_integer,
        check_equivalent_float,
        check_equivalent_boolean,
        check_equivalent_none,
        check_equivalent_list,
    ]

    try:

        for check_func in checks:
            if check_func(expected, actual):
                return True

        return False
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


import os
import shutil
import subprocess

import os
import shutil
import subprocess

# def run_rust_code(run_this_code, test_case, dependencies=None):
#     """
#     1. create repo called coding_challenge
#         $ cargo new coding_challenge
#     2. overwrite src/main.rs with code
#     3. add dependencies to Cargo.toml (if provided)
#     4. run unit tests
#         $ cargo test
#     5. check if the test passed or failed based on the expected output
#     6. remove coding_challenge dir
#     """
#     # Test Case Data
#     input_values = test_case["input"]
#     expected_output = test_case["expected_output"]

#     project_dir = "coding_challenge"

#     # 1. Create the project directory
#     os.makedirs(project_dir, exist_ok=True)

#     # 2. Initialize a new Cargo project
#     subprocess.run(["cargo", "new", "--bin", project_dir], check=True)

#     # 3. Overwrite src/main.rs with the provided code
#     main_rs_path = os.path.join(project_dir, "src", "main.rs")
#     with open(main_rs_path, "w") as f:
#         f.write(run_this_code)

#     # 4. Add dependencies to Cargo.toml (if provided)
#     if dependencies:
#         cargo_toml_path = os.path.join(project_dir, "Cargo.toml")
#         with open(cargo_toml_path, "a") as f:
#             f.write("\n[dependencies]\n")
#             for dep_name, dep_version in dependencies.items():
#                 f.write(f"{dep_name} = \"{dep_version}\"\n")

#     # 5. Run unit tests
#     os.chdir(project_dir)
#     test_result = subprocess.run(["cargo", "test"], capture_output=True, text=True)
#     stdout = test_result.stdout

#     # 6. Check if the test passed or failed based on the expected output
#     test_passed = str(expected_output) in stdout

#     # 7. Remove the project directory
#     os.chdir("..")
#     shutil.rmtree(project_dir)

#     return test_passed

import os
import shutil
import subprocess

def run_rust_code(extracted_code, testcases_list, function_name, dependencies=None):
    """
    1. create repo called coding_challenge
        $ cargo new coding_challenge
    2. create a code test script based on the test case data
        input & expected output
     
    3. make script with BOTH function AND code-test
    4. write BOTH function AND code-test to src/main.rs
    5. add dependencies to Cargo.toml (if provided)
    6. run cargo test
        $ cargo test
        test the expected output inside the rust test
        output pass/fail (or equivilant)
    7. get test result (passed or failed), stdout, stderr
    8. remove coding_challenge dir
    9. Return 'pass' or 'fail' with stdout, stderr
    """
    stdout = ''
    stderr = ''

    print("\n Starting run_rust_code(extracted_code, testcases_list, function_name, dependencies=None")

    print('extracted_code', extracted_code)
    print('testcases_list', testcases_list)
    print('function_name', function_name)
    print('dependencies', dependencies)

    try:
        project_dir = "coding_challenge"

        # if directory exists, remove it. 
        if os.path.isdir(project_dir):
            shutil.rmtree(project_dir)


        # 1. Initialize a new Cargo project (this creates directory)
        # why --bin?
        subprocess.run(["cargo", "new", "--bin", project_dir], check=True)

        # 2. Make test script
        """
        e.g.
        #[cfg(test)]
        mod tests {
            use super::*;

            #[test]
            fn test_add() {
                assert_eq!(add(2, 3), 5);
                assert_eq!(add(5, -3), 2);
                assert_eq!(add(-4, -6), -10)    }
        }    
        """
        
        """
        Construct code test
        """
        test_script = "#[cfg(test)]\n"
        test_script += "mod tests {\n"
        test_script += "    use super::*;\n"
        test_script += "\n"
        test_script += "    #[test]\n"
        test_script += "    fn test_add() {\n"
        
        for this_testcase in testcases_list:
            # extract Test Case Data
            input_values = this_testcase["input"]
            expected_output = this_testcase["expected_output"]
            
            """
            Construct code test values string
            """
            input_values_string = ', '.join(map(str, input_values))
            # input_values_string = ''
            # for this_value in input_values:
            #     input_values_string += str(this_value)
            #     input_values_string += ','
            
            test_script += f"        assert_eq!({function_name}({input_values_string}), {expected_output});\n"
        
        test_script += "}\n" 
        test_script += "}\n" 
        
        # 3: make overall script
        run_this_code = extracted_code + "\n" + test_script
        
        print('run_this_code', run_this_code)
        
        # 4. Overwrite src/main.rs with the provided code
        main_rs_path = os.path.join(project_dir, "src", "main.rs")
        with open(main_rs_path, "w") as f:
            f.write(run_this_code)

        # 5. Add dependencies to Cargo.toml (if provided)
        if dependencies:
            cargo_toml_path = os.path.join(project_dir, "Cargo.toml")
            with open(cargo_toml_path, "a") as f:
                f.write("\n[dependencies]\n")
                for dep_name, dep_version in dependencies.items():
                    f.write(f"{dep_name} = \"{dep_version}\"\n")

        # 6. Run unit tests
        os.chdir(project_dir)
        test_result = subprocess.run(["cargo", "test"], capture_output=True, text=True)

        # 7. results
        stdout = test_result.stdout
        stderr = test_result.stderr
        all_output = stdout + stderr
        # maybe extract a pass/fail? what is cargos output format?

        print(f"""rust output 

            rust stdout -> {stdout} 


            rust stderr ->  {stderr}

            """)

        # Regular expression pattern to match the test result
        pattern = r"test result: (\w+)\. (\d+) passed; (\d+) failed;"

        # default
        match = None
        # Search for the pattern in the output
        match = re.search(pattern, stdout)
        print(f"regex match -> {match}")

        pass_fail_result = 'fail'

        if match:
            result = match.group(1)
            passed = int(match.group(2))
            failed = int(match.group(3))
            print(f"Tests Passed or failed. Passed: {passed}, Failed: {failed}")
            
            if result == "ok" and failed == 0:
                print("All tests passed!")
                pass_fail_result = 'pass'
                stdout = 'pass'
                stderr = ''
            else:
                print(f"Tests failed. Passed: {passed}, Failed: {failed}")
                pass_fail_result = 'fail'
        else:
            print("No success match found")
            pass_fail_result = 'fail'
            
        # 8. The myth of the eternal return
        if pass_fail_result == 'fail':

            pattern = r"^error\[([A-Z0-9]+)\]: (.*)$"
            errors = re.findall(pattern, all_output, re.MULTILINE)
            error_set = set(f"Error Number: {error_num}, Description: {error_desc.strip()}" for error_num, error_desc in errors)
            error_set_string = ', '.join(str(item) for item in error_set)
            
            print("error_set", error_set_string)
            stderr = error_set_string

        print(f"returning")
        print(f"pass_fail_result -> {pass_fail_result}")
        print(f"stdout -> {stdout}")
        print(f"stderr -> {stderr}")
        return pass_fail_result, stdout, stderr
        # return stdout, stderr

    except Exception as e:
        traceback.print_exc()
        print("Issue:", str(e))
        return 'fail', None, 'fail'

    finally:
        # 9. Remove the project directory
        os.chdir("..")
        shutil.rmtree(project_dir)

def run_code_in_subprocess(
    extracted_code, 
    test_cases, 
    function_name, 
    this_testcase, 
    programming_language,
    dependencies=None):
    """
    for javascript/typescript, 
    other packages need to be installed
    
    input_values list is for the code test case
    """
    try:
        print("\n Starting run_code_in_subprocess()")
        print(f"extracted_code -> {extracted_code}")
        print(f"test_cases -> {test_cases}")
        print(f"function_name -> {function_name}")
        print(f"this_testcase -> {this_testcase}")
        print(f"programming_language -> {programming_language}")
        print(f"dependencies -> {dependencies}")
        
        if this_testcase:
            input_values = this_testcase["input"]
            expected_output = this_testcase["expected_output"]
        ######################################
        # Pathways for programmming languages
        ######################################
        if programming_language == 'python':


            # run only function the requested in the script
            run_this_code = f"{extracted_code}\n\nif __name__ == '__main__': print({function_name}(*{input_values}))"

            print('selected python')
            process = subprocess.run(
                [sys.executable, "-c", run_this_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            print(f"python output -> {process}")

            stdout = getattr(process, "stdout", "").strip()
            stderr = getattr(process, "stderr", "").strip()

            process_proxy_return_dict = {
                'stdout':stdout,
                'stderr':stderr
            }
            return process_proxy_return_dict

        elif programming_language == 'rust':
            print("language, rust in run_code_in_subprocess()")
        
            score, stdout, stderr = run_rust_code(
                extracted_code, 
                test_cases, 
                function_name, 
                dependencies=None)
            
            print(f"""
                the rust 
                score -> {score}
                stdout -> {stdout}
                stderr -> {stderr}""")
            
            if score == 'pass':
                process_proxy_return_dict = {
                    'stdout': score,
                    'stderr': stdout + stderr
                }
                return process_proxy_return_dict

            else:
                process_proxy_return_dict = {
                    'stdout': 'fail',
                    'stderr': stdout + stderr
                }
                return process_proxy_return_dict
        
        elif programming_language == 'javascript':
            print('selected javascript')
            # Execute JavaScript code using Node.js
            process = subprocess.run(
                ["node", "-e", run_this_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            # Execute JavaScript code using Node.js
            if isinstance(js_process, subprocess.CompletedProcess):
                stdout, stderr = js_process.stdout, js_process.stderr

                process_proxy_return_dict = {
                    'stdout':stdout,
                    'stderr':stderr
                }
                return process_proxy_return_dict

        elif programming_language == 'typescript':
            print('selected typescript')
            # Execute TypeScript code using Node.js with ts-node
            process = subprocess.run(
                ["ts-node", "-e", run_this_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if isinstance(ts_process, subprocess.CompletedProcess):
                stdout, stderr = ts_process.stdout, ts_process.stderr

                process_proxy_return_dict = {
                    'stdout':stdout,
                    'stderr':stderr
                }
                return process_proxy_return_dict
        
        else:  # if no matching language 
            print('no output, defaulting to fail')
            process_proxy_return_dict = {
                'stdout': None,
                'stderr': f'no known language ? -> {programming_language}'
            }
            return process_proxy_return_dict

        # default if no other return
        process_proxy_return_dict = {
            'stdout': None,
            'stderr': 'unable to run'
        }
        return process_proxy_return_dict
    
    except Exception as e:
        traceback.print_exc()
        print(f"run_code_in_subprocess() failed error = {str(e)}")
        process_proxy_return_dict = {
            'stdout':'',
            'stderr':str(e)
        }

        return process_proxy_return_dict

###################################
# helper function for coding layer
# TODO: how is this returning the words stdout stderr?
def pass_fail_unit_test_function__stdout_stderr(
    code_markdown,
    test_cases,
    function_name,
    retry_or_error_event_counter_list,
    error_log,
    programming_language,
    dependencies=None
):
    """
    standard issues:
    - input() is not allowed
    -
    ```
    def calculate_area(x,y):\n
        return x*y
    ```
    """

    # Extract the code from the Markdown
    extracted_code = extract_code_from_markdown(code_markdown, function_name)
    
    if not extracted_code:
        print('warning, no code extracted')
        return False, f"This is not code correctly formated in markdown: {code_markdown}"

    if programming_language == 'rust':
        print('rust selected in pass_fail_unit_test_function__stdout_stderr()')
        
        this_testcase = ''
        rust_result = run_code_in_subprocess(
            extracted_code, 
            test_cases, 
            function_name, 
            this_testcase, 
            programming_language,
            dependencies=None)
        
        print(f"rust_result -> {rust_result}")
        # set two outputs
        stdout = rust_result['stdout']
        stderr = rust_result['stderr']

        # log error if fail
        if rust_result['stdout'] == 'fail':
            print("rust: No stdout found. Fail as error.")
            stdout = False
            error_log.append(rust_result['stderr'])

        # return no stdout if error or fail
        return stdout, stderr
    
    for this_testcase in test_cases:

        try:
            input_values = this_testcase["input"]
            expected_output = this_testcase["expected_output"]

            """
            Construct the full script with the test case applied
            This script defines the function from the markdown, 
            then calls it with the current test case's inputs
            """
            extracted_code = extracted_code.replace("print(", "# print(")
            # extracted_code = extracted_code.replace("\nprint(", "# print(")
            extracted_code = extracted_code.replace(
                "input()", "'error_no_input_allowed'"
            )

            # # run only function the requested in the script
            # run_this_code = f"{extracted_code}\n\nif __name__ == '__main__': print({function_name}(*{input_values}))"
            
            # # Python version: Run the 'run_this_code' script using subprocess
            # process = subprocess.run(
            #     [sys.executable, "-c", run_this_code],
            #     stdout=subprocess.PIPE,
            #     stderr=subprocess.PIPE,
            #     universal_newlines=True,
            # )
            
            # multi-languaeg-version
            process = run_code_in_subprocess(extracted_code, test_cases, function_name, this_testcase, programming_language)

            # read stdout and std err
            stdout = process['stdout']
            stderr = process['stderr']
            
            stderr_plus = (
                "Feedback: This code "
                + extracted_code
                + " lead to this error: "
                + stderr
                + ", stdout: "
                + stdout
                + "Try again: "
            )


            print(f"\n after run_code_in_subprocess:")
            print(f"expected_output -> {expected_output} {type(expected_output)}")
            print(f"stdout -> {stdout} {type(stdout)}")
            print(f"stderr -> {stderr} {type(stderr)}")

            if not stdout:
                print("No stdout found. Fail as error.")
                error_log.append(stderr)
                return False, stderr_plus

            actual_output = stdout

        except Exception as e:
            traceback.print_exc()
            error_message = str(e)
            return False, error_message

        # Compare the actual_output output with the expected output
        try:
            print('Valid-ish stdout:')
            print(f"expected_output -> {expected_output} {type(expected_output)}")
            print(f"actual_output -> {actual_output}")

            boolean_check = check_equivalent_all(expected_output, actual_output)

            if boolean_check is True:
                print(
                    f"Test Case Passed: Input = {input_values}, Expected Output = {expected_output}"
                )
                return "pass", ""

            else:
                print(
                    f"Test Case Failed: Input = {input_values}, Expected Output = {expected_output}, Actual Output = {stdout}"
                )
                # error_log.append(f"test cases: {str(test_cases)}")
                error_log.append(stdout)
                error_log.append(stderr)
                retry_or_error_event_counter_list.append(True)
                return False, stderr_plus

        except Exception as e:
            traceback.print_exc()
            # error_log.append(f"test cases: {str(test_cases)}")
            error_log.append(stdout)
            error_message = str(e) + process.stderr.strip()
            error_log.append(error_message)
            retry_or_error_event_counter_list.append(True)
            return False, error_message


# Helper Function
def populate_skeleton_json_with_data(skeleton_json, source_data):
    """
    Recursively fills the skeleton_json structure with data from the source_data.
    For lists, it merges items instead of replacing them, ensuring unique values.

    :param skeleton_json: The skeleton_json structure with potentially empty lists as terminal values.
    :param source_data: The source data structure from which values are to be copied.
    :return: The skeleton_json structure filled with values from source_data, with care for unique list items.
    """
    if isinstance(skeleton_json, dict) and isinstance(source_data, dict):
        for key in skeleton_json:
            if key in source_data:
                # Recurse into nested dictionaries or replace/merge list and terminal values
                skeleton_json[key] = populate_skeleton_json_with_data(
                    skeleton_json[key], source_data[key]
                )
    elif isinstance(skeleton_json, list):
        # Ensure unique items are added from source_data to skeleton_json list, preserving existing items.
        skeleton_json.extend(
            [item for item in source_data if item not in skeleton_json]
        )
        return skeleton_json
    elif isinstance(skeleton_json, list) and not skeleton_json:
        # For an empty list in skeleton_json, directly copy the source_data list to it
        return source_data.copy()
    # For terminal values, or if the structures don't match (dict/list), return source_data to replace or fill in.
    else:
        return source_data
    return skeleton_json


"""## save json utility"""


# Helper Function
def save_json_to_file(input_text, file_name, target_language, optional_tag=""):
    """
    Saves a JSON object to a file.

    :param data: The JSON object to save.
    :param file_path: The path to the JSON file where the object should be saved.
    """
    # with open(file_path, 'w') as file:
    #     json.dump(data, file, indent=4)

    # make readable time
    date_time = datetime.now(UTC)
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")

    new_title = f"{target_language}_{clean_timestamp}_{file_name}"

    new_title = optional_tag + new_title

    # Determine the path to the directory that should contain the file
    directory_path = "translations"

    # Check if the directory exists
    if not os.path.exists(directory_path):

        # If it does not exist, create it
        # Ensure the directory exists
        try:
            os.makedirs(
                directory_path, exist_ok=True
            )  # Ensure the directory is created if it does not exist
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating directory {directory_path}: {e}")
            return  # Exit the function if directory creation fails

    # Determine the path to the file that should be saved
    file_path = os.path.join(directory_path, new_title)

    # Save the JSON data to the file with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(input_text, outfile, indent=4, ensure_ascii=False)


# Helper Function
def set_save_json_to_file(input_text, file_name, target_language, optional_tag=""):
    """
    Saves a JSON object to a file.

    :param data: The JSON object to save.
    :param file_path: The path to the JSON file where the object should be saved.
    """
    # with open(file_path, 'w') as file:
    #     json.dump(data, file, indent=4)

    # make readable time
    date_time = datetime.now(UTC)
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")

    new_title = f"{target_language}_{clean_timestamp}_{file_name}"

    new_title = optional_tag + new_title

    # Determine the path to the directory that should contain the file
    directory_path = "translations/sets"

    # Check if the directory exists
    if not os.path.exists(directory_path):

        # If it does not exist, create it
        # Ensure the directory exists
        try:
            os.makedirs(
                directory_path, exist_ok=True
            )  # Ensure the directory is created if it does not exist
        except Exception as e:
            traceback.print_exc()
            print(f"Error creating directory {directory_path}: {e}")
            return  # Exit the function if directory creation fails

    # Determine the path to the file that should be saved
    file_path = os.path.join(directory_path, new_title)

    # Save the JSON data to the file with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(input_text, outfile, indent=4, ensure_ascii=False)


"""# Swap-Out, Swap-Back (Wax-on, Wax-off)"""


# def get_swap_in(input_string):
#     """
#     returns the value of something not in the string
#     """
#     placeholder_list = [
#         ")))***",
#         "^|.|.|",
#         "###$$$",
#         "%&%&%&",
#         "'''(((",
#         "+++,,,",
#         "---...",
#         "///000",
#         "111222",
#         "333444",
#         "555666",
#         "777888",
#         "999:::",
#         ";;;<<<",
#         "===>>>",
#         "???@@@",
#         "AAABBB",
#         "CCCDDD",
#         "EEEFFF",
#         "GGGHHH",
#         "IIIJJJ",
#         "KKKLLL",
#         "MMMNNN",
#         "OOOPPP",
#         "QQQRRR",
#         "SSSTTT",
#         "UUUVVV",
#         "WWWXXX",
#         "YYYZZZ",
#         "[[[sss",
#         "]]]^^^",
#         "___```",
#         "aaabbb",
#         "cccddd",
#         "eeefff",
#         "ggghhh",
#         "iiijjj",
#         "kkklll",
#         "mmmnnn",
#         "oooppp",
#         "qqqrrr",
#         "sssttt",
#         "uuuvvv",
#         "wwwxxx",
#         "yyyzzz",
#         "{|{{|||",
#         "}~}~}~~~",
#         "!",
#         '"',
#         "#",
#         "$",
#         "%",
#         "&",
#         "'",
#         "(",
#         ")",
#         "*",
#         "+",
#         ",",
#         "-",
#         ".",
#         "/",
#         "0",
#         "1",
#         "2",
#         "3",
#         "4",
#         "5",
#         "6",
#         "7",
#         "8",
#         "9",
#         ":",
#         ";",
#         "<",
#         "=",
#         ">",
#         "?",
#         "@",
#         "A",
#         "B",
#         "C",
#         "D",
#         "E",
#         "F",
#         "G",
#         "H",
#         "I",
#         "J",
#         "K",
#         "L",
#         "M",
#         "N",
#         "O",
#         "P",
#         "Q",
#         "R",
#         "S",
#         "T",
#         "U",
#         "V",
#         "W",
#         "X",
#         "Y",
#         "Z",
#         "[",
#         "]",
#         "^",
#         "_",
#         "`",
#         "a",
#         "b",
#         "c",
#         "d",
#         "e",
#         "f",
#         "g",
#         "h",
#         "i",
#         "j",
#         "k",
#         "l",
#         "m",
#         "n",
#         "o",
#         "p",
#         "q",
#         "r",
#         "s",
#         "t",
#         "u",
#         "v",
#         "w",
#         "x",
#         "y",
#         "z",
#         "{",
#         "|",
#         "}",
#         "~",
#     ]

#     for this_placeholder in placeholder_list:
#         if this_placeholder not in input_string:
#             print(f"item found -> {this_placeholder}")
#             return this_placeholder

#     return "Unable to find item not in the input_string"


# # helper_function
# def swap_two(input_string, item_1, item_2):
#     """
#     Swap two items in a string. Tada!

#     or change only the first item, the 2nd item is optional.

#     protection from swap-collisions is included
#     """

#     original_string = input_string

#     # validity sanity check (item_2 is optional, only item 1 is needed)
#     if item_1 not in input_string:
#         print(
#             f"NOTHING DONE: item to match not in string -> {item_1} vs. {input_string}"
#         )
#         return input_string

#     use_this_placeholder = ";;;<<<"

#     """all possible ascii placeholders, and more:
#     while there is a risk of item 1 or two coliding with the placeholder
#     there is also a risk of the placeholder coliding with part of the string
#     the longer the string, the more likely it contains any given single
#     ascii character
#     """
#     placeholder_list = [
#         ")))***",
#         "^|.|.|",
#         "###$$$",
#         "%&%&%&",
#         ";;;<<<",
#         "+++,,,",
#         "---...",
#         "///000",
#         "111222",
#         "333444",
#         "555666",
#         "777888",
#         "999:::",
#         ";;;<<<",
#         "===>>>",
#         "???@@@",
#         "AAABBB",
#         "CCCDDD",
#         "EEEFFF",
#         "GGGHHH",
#         "IIIJJJ",
#         "KKKLLL",
#         "MMMNNN",
#         "OOOPPP",
#         "QQQRRR",
#         "SSSTTT",
#         "UUUVVV",
#         "WWWXXX",
#         "YYYZZZ",
#         "[[[sss",
#         "]]]^^^",
#         "___```",
#         "aaabbb",
#         "cccddd",
#         "eeefff",
#         "ggghhh",
#         "iiijjj",
#         "kkklll",
#         "mmmnnn",
#         "oooppp",
#         "qqqrrr",
#         "sssttt",
#         "uuuvvv",
#         "wwwxxx",
#         "yyyzzz",
#         "'''(((",
#         "{|{{|||",
#         "}~}~}~~~",
#         "!",
#         '"',
#         "#",
#         "$",
#         "%",
#         "&",
#         "'",
#         "(",
#         ")",
#         "*",
#         "+",
#         ",",
#         "-",
#         ".",
#         "/",
#         "0",
#         "1",
#         "2",
#         "3",
#         "4",
#         "5",
#         "6",
#         "7",
#         "8",
#         "9",
#         ":",
#         ";",
#         "<",
#         "=",
#         ">",
#         "?",
#         "@",
#         "A",
#         "B",
#         "C",
#         "D",
#         "E",
#         "F",
#         "G",
#         "H",
#         "I",
#         "J",
#         "K",
#         "L",
#         "M",
#         "N",
#         "O",
#         "P",
#         "Q",
#         "R",
#         "S",
#         "T",
#         "U",
#         "V",
#         "W",
#         "X",
#         "Y",
#         "Z",
#         "[",
#         "]",
#         "^",
#         "_",
#         "`",
#         "a",
#         "b",
#         "c",
#         "d",
#         "e",
#         "f",
#         "g",
#         "h",
#         "i",
#         "j",
#         "k",
#         "l",
#         "m",
#         "n",
#         "o",
#         "p",
#         "q",
#         "r",
#         "s",
#         "t",
#         "u",
#         "v",
#         "w",
#         "x",
#         "y",
#         "z",
#         "{",
#         "|",
#         "}",
#         "~",
#     ]

#     """
#     check that:
#     item_2 is not in placeholder
#     that placeholder does not collide with something in string
#     """
#     placeholder_ok = False
#     for this_placeholder in placeholder_list:
#         print(f"trying -> '{this_placeholder}'")
#         if (
#             (item_1 not in this_placeholder)
#             and (item_2 not in this_placeholder)
#             and (this_placeholder not in input_string)
#         ):
#             use_this_placeholder = this_placeholder
#             placeholder_ok = True
#             print(f"use_this_placeholder -> {use_this_placeholder}")
#             break
#         else:
#             print("collision detected, try next placeholder...")

#     if not placeholder_ok:
#         # print error message and exit program
#         message = """FAILED: collision error,
#         for swap_two(),
#         a new placeholder needed.
#         action item: add novel option to placeholder_list
#         """
#         print(message)
#         sys.exit()

#     # Replace item_1 with a temporary placeholder
#     output_swapped_string = input_string.replace(item_1, use_this_placeholder)
#     print(output_swapped_string)

#     # Replace item_2 with item_1
#     output_swapped_string = output_swapped_string.replace(item_2, item_1)
#     print(output_swapped_string)

#     # Replace that temporary placeholder with item_2 (done and done)
#     output_swapped_string = output_swapped_string.replace(use_this_placeholder, item_2)

#     message = f"""
#     Final comarison:
#     old -> {original_string}
#     new -> {output_swapped_string}
#     """
#     print(message)

#     return output_swapped_string


# input_string = ""
# target = "'"
# swapper = get_swap_in(input_string)

# # Run before
# swap_two(input_string, target, swapper)

# # Run After
# swap_two(input_string, target, swapper)

"""# Functions to call Mistral"""

"""
related tools:

api throttle_protection
api async

"""


"""
# mode: [{"role": "user", "content": "say yes"}]

    # Define the request body
    request_body = {
      "model": "mistral-small",
      "messages": [{"role": "user", "content": user_input}]
    }

    # Send the request
    response = requests.post(endpoint_url, headers=headers, json=request_body)
"""


def pretty_print_option_list(lst):
    if not lst:
        return False

    max_index_width = len(str(len(lst)))
    pretty_string = ""

    for index, item in enumerate(lst, start=1):
        pretty_string += f" Option {index:>{max_index_width}}. {item}; "

    return pretty_string.rstrip()


def pretty_print_list(lst):
    if not lst:
        return False

    max_index_width = len(str(len(lst)))
    pretty_string = ""

    for index, item in enumerate(lst, start=1):
        pretty_string += f"{index:>{max_index_width}}. {item}; "

    return pretty_string.rstrip()


# Helper Function
def segment_for_adding_to_context_history(role, comment):

    if role == "user":
        segment = {"role": "user", "content": comment}

    elif role == "assistant":
        segment = {"role": "assistant", "content": comment}

    elif role == "system":
        segment = {"role": "system", "content": comment}

    else:
        print("error segment_for_adding_to_context_history(role, comment)")
        print(role, comment)
        print("error")

    return segment


# Helper Function
def add_to_and_return_context_history(user_input, context_history, role):

    if role == "user":
        segment = {"role": "user", "content": user_input}

    elif role == "assistant":
        segment = {"role": "assistant", "content": user_input}

    elif role == "system":
        segment = {"role": "system", "content": user_input}

    else:
        print("error add_to_context_history() error")
        print(role, user_input)
        print("role error?")

    context_history.append(segment)

    return context_history


def find_matching_file_paths(file_paths, target_file_name):
    """
    Finds and returns all paths from a list of file paths that match the target file name.

    Parameters:
    - file_paths (list of str): The list of file paths to search through.
    - target_file_name (str): The file name to match.

    Returns:
    - list of str: A list of full paths matching the target file name.
    """
    matching_paths = []

    for path in file_paths:
        # Extract the name of the file from the path
        file_name = path.split("/")[-1]
        if file_name == target_file_name:
            matching_paths.append(path)

    # return one path
    return matching_paths[0]


# Helper Function
def one_response_to_user(user_input, context_history, use_this_model):
    """
    Input: context_history
    Ouput Tuple: assistant_says, context_history
    """

    counter(3)

    # prompt user
    context_history = prompt_user(user_input, context_history)

    # prompt assistant
    response = ask_mistral_model(context_history, use_this_model)

    return response


def extract_dictionaries_from_string_no_pips(input_string):

    input_string = input_string.replace("\n", "")

    pattern = r"{.*?}"
    matches = re.findall(pattern, input_string)
    dictionaries = []

    for match in matches:
        try:
            dictionary = eval(match)
            if isinstance(dictionary, dict):
                dictionaries.append(dictionary)
        except (SyntaxError, NameError, TypeError):
            pass

    return dictionaries


# Helper Function
def counter(timeout=10):
    count = 0
    start_time = time.time()
    while time.time() - start_time < timeout:
        count += 1
        time.sleep(1)
    return count


def replace_special_characters_with_text_swap(input_item):

    if not isinstance(input_item, str):

        input_item = str(input_item)

    # Remove duplicate spaces
    input_item = re.sub(r"\s+", " ", input_item.strip())

    replacements = {
        ",": "(comma)",
        '"': "(double quote or inverted commas)",
        "'": "(single quote or apostrophe)",
        "[": "(left square bracket)",
        "]": "(right square bracket)",
        "{": "(left curly bracket)",
        "}": "(right curly bracket)",
        ":": "(colon)",
        "\\n": "(newline)",
        "\n": "(newline)",
    }

    for char, replacement in replacements.items():
        input_item = input_item.replace(char, replacement)

    return input_item


from html import escape


def make_html_report(target_csv_file_sources_dir, path_out):
    """
    Return error and instruction data to normal text.

    Todo
    Maybe use set for error to remove duplicates...
    """

    csv_files = glob.glob(os.path.join(target_csv_file_sources_dir, "*.csv"))

    # remove "score_report.csv" from list
    csv_files.remove("task_set_results_files/score_report.csv")
    # print(csv_files)

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

            print(f"in make_html_report(), This csv_file -> {csv_file}")

            try:
                with open(csv_file, "r") as csvfile:
                    csvreader = csv.DictReader(csvfile)
                    for row in csvreader:

                        # selected option

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
                            score=escape(row["score"]),
                            selected_option=escape(row["selected_option"]),
                            correct_option=escape(row["correct_option"]),
                            task_failure_comment=escape(row["task_failure_comment"]),
                            name_of_model=escape(row["name_of_model"]),
                            task_file=escape(row["task_file"]),
                            task_from_instructions=escape(
                                replace_text_with_special_characters_swapback(
                                    row["task_from_instructions"]
                                )
                            ),
                            retry_counter=escape(row["retry_counter"]),
                            error_log=escape(
                                replace_text_with_special_characters_swapback(
                                    row["error_log"]
                                )
                            ),
                            duration_of_single_task=escape(
                                row["duration_of_single_task"]
                            ),
                            readable_timestamp=escape(row["readable_timestamp"]),
                        )
            except Exception as e:
                traceback.print_exc()
                print(f"No dice on file -> {csv_file}, error -> {e}")
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
        traceback.print_exc()
        print(f"No dice on generating HTML summary -> {e}")
        print("")


def html_for_all_reports():

    date_time = datetime.now()
    clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")

    target_csv_file_sources_dir = "task_set_results_files"
    report_destination = f"task_set_results_files/HTML_summary_{clean_timestamp}.html"

    make_html_report(target_csv_file_sources_dir, report_destination)



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
                traceback.print_exc()
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
        traceback.print_exc()
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


def replace_text_with_special_characters_swapback(input_item):

    if not isinstance(input_item, str):

        input_item = str(input_item)

    # Remove duplicate spaces
    # input_item = re.sub(r"\s+", " ", input_item.strip())

    # # original
    # replacements = {
    #     ",": "(comma)",
    #     '"': "(double quote or inverted commas)",
    #     "'": "(single quote or apostrophe)",
    #     "[": "(left square bracket)",
    #     "]": "(right square bracket)",
    #     "{": "(left curly bracket)",
    #     "}": "(right curly bracket)",
    #     ":": "(colon)",
    #     "\\n": "(newline)",
    #     "\n": "(newline)",
    # }

    reverse_replacements = {
        "(comma)": ",",
        "(double quote or inverted commas)": '"',
        "(single quote or apostrophe)": "'",
        "(left square bracket)": "[",
        "(right square bracket)": "]",
        "(left curly bracket)": "{",
        "(right curly bracket)": "}",
        "(colon)": ":",
        "(newline)": "\n",
    }

    for char, replacement in reverse_replacements.items():
        input_item = input_item.replace(char, replacement)

    return input_item


"""
anthropic
"""


def simple_ask_anthropic_py(input_string, this_model):
    """
    import anthropic
    """

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=anthropic_api_key,
    )
    message = client.messages.create(
        model=this_model,
        max_tokens=1024,
        messages=[{"role": "user", "content": input_string}],
    )

    # print(message.content)

    answer = message.content[0].text

    # print(answer)

    return answer


def simple_ask_anthropic(input_string, this_model):
    """
    "claude-2.1"
    "claude-3-opus-20240229",

    """

    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": this_model,
        "max_tokens_to_sample": 1024,
        "prompt": f"\n\nHuman: {input_string}\n\nAssistant:",
    }

    response = requests.post(
        "https://api.anthropic.com/v1/complete", headers=headers, json=data
    )

    if response.status_code == 200:
        result = response.json()
        answer = result["completion"]
    else:
        print(f"Request failed with status code {response.status_code}")

        answer = response.text

    # print(answer)

    return answer


"""
Mistral
"""


def print_rec_ai(response, context_history):

    # Get the response data
    response_data = response.json()

    # Print the Mistral response

    ##
    ##
    # Turn this print on to see full return data
    ##
    ##
    """
    e.g.
    {
      "id": "635cb8d445ujhe5546bb64e5e7",
      "object": "chat.completion",
      "created": 170hrjfjf7084,
      "model": "mistral-tiny",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Enjoy your cup of tea!"
          },
          "finish_reason": "stop",
          "logprobs": null
        }
      ],
      "usage": {
        "prompt_tokens": 575,
        "total_tokens": 629,
        "completion_tokens": 54
      }
    }
    """
    # print(json.dumps(response_data, indent=2))
    # print(type(response_data))

    output = response_data
    # print(type(output))
    # print(type(output["choices"][0]))

    # extract just the 'what they said' part out
    assistant_says = output["choices"][0]["message"]["content"]

    # print(assistant_says)

    new_comment = {"role": "assistant", "content": assistant_says}

    # add what assistant said to context history
    context_history.append(new_comment)

    return assistant_says, context_history


def add_to_context_history(role, comment):

    if role == "user":
        segment = {"role": "user", "content": comment}

    elif role == "assistant":
        segment = {"role": "assistant", "content": comment}

    elif role == "system":
        segment = {"role": "system", "content": comment}

    else:
        print("add_to_context_history(role, comment)")
        print(role, comment)
        print("error")

    return segment


def prompt_user(user_input, context_history):

    context_history.append(add_to_context_history("user", user_input))

    return context_history


def go_user(user_input, context_history, use_this_model):
    """
    Input: context_history
    Ouput Tuple: assistant_says, context_history
    """

    # prompt user
    context_history = prompt_user(user_input, context_history)

    # prompt assistant
    response = ask_mistral_api(context_history, use_this_model)

    # ETL: Extract, Transform, & Load
    assistant_says, context_history = print_rec_ai(response, context_history)

    return assistant_says, context_history


def ask_mistral_api(context_history, use_this_model):

    # Define the endpoint URL
    endpoint_url = "https://api.mistral.ai/v1/chat/completions"

    # Set the headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {mistral_api_key}",
    }

    # Define the request body
    request_body = {"model": use_this_model, "messages": context_history}

    #################
    #################
    # Hit the ai api
    #################
    #################
    # Send the request
    response = requests.post(endpoint_url, headers=headers, json=request_body)

    # Check the response status code
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} {response.text}")

    return response


def simple_ask_mistral_cloud(input_string, use_this_model):
    """
    you have: a string
    you need: a response

    1. make minimal history contexxt
    2. make a generic system instruction, for show
    3. make system-user context: string input
    4. ask mistral for that model
    5. extract just the response string
    6. return only reply (no 'history')
    """

    # 1. make minimal history contexxt
    context_history = []

    # 2. make a generic system instruction
    generic_system_instruction = "You are helpful and answer accurately."
    context_history.append(add_to_context_history("system", generic_system_instruction))

    # 3. make system-user context: string input
    context_history.append(add_to_context_history("user", input_string))

    # 4. ask mistral for that model
    response = ask_mistral_api(context_history, use_this_model)

    # Get the response data
    response_data = response.json()

    # 5. extract just the response string

    ##
    ##
    # Turn this print on to see full return data
    ##
    ##
    """
    e.g.
    {
      "id": "635cb8d445ujhe5546bb64e5e7",
      "object": "chat.completion",
      "created": 170hrjfjf7084,
      "model": "mistral-tiny",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Enjoy your cup of tea!"
          },
          "finish_reason": "stop",
          "logprobs": null
        }
      ],
      "usage": {
        "prompt_tokens": 575,
        "total_tokens": 629,
        "completion_tokens": 54
      }
    }
    """
    # print(json.dumps(response_data, indent=2))
    # print(type(response_data))

    output = response_data
    # print(type(output))
    # print(type(output["choices"][0]))

    # extract just the 'what they said' part out
    assistant_says = output["choices"][0]["message"]["content"]

    # 6. return only reply (no 'history')
    return assistant_says


def strip_non_alpha(text):
    # regex to leave only a-z characters
    pattern = re.compile("[^a-z]")
    return pattern.sub("", text).lower()


def keep_talking(context_history, use_this_model):
    """
    A very minimal chat with memory.

    Uses:
      query(input_string)
      strip_non_alpha(text)
    """
    still_talking = True
    dialogue_history = ""

    while still_talking:

        user_input = input("Say...")

        exit_phrase_list = [
            "exit",
            "quit",
            "quite",
            "!q",
            "q",
            "done",
            "finish",
            "end",
            "bye",
            "good bye",
        ]

        # check if user is exiting convesation
        if strip_non_alpha(user_input) in exit_phrase_list:
            print("\nAll Done!")
            break

        else:
            assistant_says, context_history = go_user(
                user_input, context_history, use_this_model
            )

            print(assistant_says)

            # save dialogue so far
            dialogue_history = context_history

    # when out of loop, return history
    return dialogue_history


# save history
def record_history_save_files(dialogue_history):

    date_time = datetime.now()
    timestamp = date_time.strftime("%Y/%m/%d  %H:%M:%S:%f")
    clean_timestamp = date_time.strftime("%Y%m%d%H%M")

    # To save the data directly as a JSON file:

    # Convert the Python dictionary list to a JSON string
    json_data = json.dumps(dialogue_history)

    # Open a file for writing in JSON format
    with open(f"json_dialog_{clean_timestamp}.json", "w") as json_file:
        # Write the JSON string to the file
        json_file.write(json_data)

    # To save the data as a file readable as a script:

    # Create a new file for writing
    with open(f"script_dialog_{clean_timestamp}.txt", "w") as script_file:

        # add timestamp
        text = timestamp + "\n\n"
        script_file.write(text)

        # Iterate over the dictionary list
        for item in dialogue_history:
            # Write the role and content of each item to the file, separated by a newline
            script_file.write(f"{item['role']}: {item['content']}\n\n")


# # Helper Function
# def ask_mistral_model(context_history, use_this_model):

#     # Define the endpoint URL
#     endpoint_url = "https://api.mistral.ai/v1/chat/completions"

#     # Set the headers
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "Authorization": f"Bearer {mistral_api_key}",
#     }


#     # Define the request body
#     request_body = {"model": use_this_model, "messages": context_history}

#     # pause if error occurs
#     counter(2)

#     #################
#     #################
#     # Hit the ai api
#     #################
#     #################
#     # Send the request
#     response = requests.post(endpoint_url, headers=headers, json=request_body)

#     # Check the response status code
#     if response.status_code != 200:
#         print(f"Error: {response.status_code} {response.text}")
#         return None

#         # pause if error occurs
#         counter(10)

#     # Get the response data
#     response_data = response.json()

#     # Print the Mistral response

#     ##
#     ##
#     # Turn this print on to see full return data
#     ##
#     ##
#     """
#     e.g.
#     {
#       "id": "635cb8d445ujhe5546bb64e5e7",
#       "object": "chat.completion",
#       "created": 170hrjfjf7084,
#       "model": "mistral-tiny",
#       "choices": [
#         {
#           "index": 0,
#           "message": {
#             "role": "assistant",
#             "content": "Enjoy your cup of tea!"
#           },
#           "finish_reason": "stop",
#           "logprobs": null
#         }
#       ],
#       "usage": {
#         "prompt_tokens": 575,
#         "total_tokens": 629,
#         "completion_tokens": 54
#       }
#     }
#     """
#     # print(json.dumps(response_data, indent=2))
#     # print(type(response_data))

#     output = response_data
#     # print(type(output))
#     # print(type(output["choices"][0]))

#     # extract just the 'what they said' part out
#     assistant_says = output["choices"][0]["message"]["content"]

#     return assistant_says


# """
# # functions to call openAI api

# There are a number of functions and versions of functions
# that can be used to call openAI's api, with many factors
# including rety, timeout, async, etc.

# To avoid requiring libary-package installs that are not needed
# if you are not using openAI's web-api, these are commented out.


"""

# !pip install -q openai

# # functions to call openAI 2024 api


# # import openai
# # import time
# # from openai import AsyncOpenAI

# # # openai_api_key = ""

# # from google.colab import userdata
# # openai_api_key = userdata.get('open_ai_key')

# # python dotenv

# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# from openai import OpenAI

# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key = openai_api_key,
# )

# """
# api module parts
# """

# import string
# import asyncio
# from openai import AsyncOpenAI
# import threading

# ############
# # Not Async
# ############
# """
# openai_call_context_timeout() with x-retries and time-limit freeze protection
# """


# def container_api_call(client, model, temp, context, result_container):
#     try:
#         completion = client.chat.completions.create(
#             model=model,
#             temperature=temp,
#             messages=context
#         )
#         result_container['completion'] = completion
#     except Exception as e:
traceback.print_exc()
#         result_container['error'] = e


# def run_api_call_with_timeout(client, model, temp, context, timeout):
#     """
#     flags the thread and moves to background after time-out
#     but does not attempt to 'kill' the thread.
#     If thread finishes, output ~should stay in background
#     un-unused by anything.
#     """
#     try:
#         result_container = {}
#         api_thread = threading.Thread(target=container_api_call, args=(client, model, temp, context, result_container))
#         api_thread.start()
#         api_thread.join(timeout)

#         if api_thread.is_alive():
#             # If the API call is still running after the timeout
#             print("The API call timed out.")
#             return None  # Or handle the timeout situation as needed

#         if 'error' in result_container:
#             # If there was an error during the API call
#             print("An error occurred:", result_container['error'])
#             return None

#         return result_container.get('completion')

#     except Exception as e:
traceback.print_exc()
#         raise( e, f"ERROR in function: run_api_call_with_timeout(input_string)" )


# # helper function ()
# def openai_call_context_timeout(client, context, model="gpt-4", max_retries=10, temp=0.9, timeout_min=8):
#     """
#     requires: container_api_call(), run_api_call_with_timeout()
#     """
#     # load_dotenv()
#     # openai.api_key = os.getenv("OPENAI_API_KEY")

#     # convert timeout into seconds (int)
#     timeout_sec = int(timeout_min * 60)

#     # makes sure number is not zero
#     if timeout_sec <= 0:
#         timeout_sec = 1

#     """
#     Time parameters for retry to double in duration until the max seconds limit
#     """
#     base_delay_sec = 2
#     max_delay_sec = 16

#     retries = 0
#     while retries <= max_retries:
#         try:
#             # call API within a time-out filter
#             completion = run_api_call_with_timeout(
#                 client,
#                 model=model,
#                 temp=temp,
#                 context=context,
#                 timeout=timeout_sec
#             )

#             text = completion.choices[0].message.content

#             print(f"openai_call_context_timeout() -> {text}")

#             return text

#         except Exception as e:
traceback.print_exc()
#             print(f"an error occurred: {e}")
#             retries += 1
#             if retries > max_retries:
#                 print("max retries reached. exiting.")
#                 raise

#             # using min() to ensure that delay <= max
#             real_delay_sec = min(max_delay_sec, (2 ** retries) * base_delay_sec)
#             print(f"retrying in {real_delay_sec} seconds...")
#             # pause before retrying
#             time.sleep(real_delay_sec)
#             """
#             Note: time delay is not a crash-exception, it is a re-try
#             """

# # test
# context = []

# # "system"
# system_prompt = f"""You are a talking bird."""

# context.append({
#     "role": "system", "content": system_prompt
# })

# prompt = "Squawk, I am a bird."
# context.append({
#     "role": "assistant", "content": prompt
# })

# prompt = "what is a bird?"
# context.append({
#     "role": "user", "content": prompt
# })

# print(context)

# # result = openai_call_context(context, model="gpt-4", max_retries=2)

# # result = await openai_call_context_timeout_async(client, context, model="gpt-3.5-turbo", max_retries=2, temp=0.9, timeout_min=2)

# # print(f"result -> {result}")

# # test
# context = []

# # "system"
# system_prompt = f"""You are a talking bird."""

# context.append({"role": "system", "content": system_prompt})

# prompt = "Squawk, I am a bird."
# context.append({"role": "assistant", "content": prompt})

# prompt = "what is a bird?"
# context.append({"role": "user", "content": prompt})

# print(context)


# result = openai_call_context(context, model="gpt-4", max_retries=2)

# result = await openai_call_context_timeout_async(client, context, model="gpt-3.5-turbo", max_retries=2, temp=0.9, timeout_min=2)

# print(f"result -> {result}")

# data = [
#     {"role": "system", "content": "You are a talking bird."},
#     {"role": "assistant", "content": "Squawk, I am a bird."},
#     {"role": "user", "content": "what is a bird?"},
# ]

# with open("instruct.txt", "w") as f:
#     for item in data:
#         if item["role"] == "system":
#             f.write(item["content"] + "\n")

# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key = my_api_key,
# )


# pause_time_seconds = .5

# # Helper Function
# def pause_ok():
#     time.sleep(pause_time_seconds)
#     return "Pause OK!"

# # Helper Function: Call API Function
# def call_openai_chat_api(this_input, select_model=3):
#     """
#     Requires:
#       import time
#       pip install openai
#       import openai
#       api key from openai, included in subscription:
#       https://platform.openai.com/account/api-keys

#       # Helper Function
#       def pause_ok():
#           time.sleep(pause_time_seconds)
#           return "OK!"


#     Chat type query to openAI:
#     pecify Model, default is "gpt-3.5-turbo"
#     user input-2 selects which model to use: 3, 4

#     Sample use:

#     this_input = "Hello."
#     select_model = 3

#     call_openai_chat_api(this_input, select_model=3)
#     """

#     try:
#         if select_model == 4:
#             this_model = "gpt-4"

#         elif select_model == "gpt-4":
#             this_model = "gpt-4"

#         elif select_model == "gpt-3.5-turbo":
#             this_model = "gpt-3.5-turbo"

#         elif select_model == 3:
#             this_model = "gpt-3.5-turbo"

#         # Pause to avoid throttling
#         print(f"Pausing {pause_time_seconds} seconds...")
#         print(pause_ok())
#         # time.sleep(pause_time_seconds)
#         # print(f"Pausing {pause_time_seconds} seconds...OK!")


#         ## Hit API
#         completion = client.chat.completions.create(model=this_model, messages=[{"role": "user", "content": this_input}])

#         # Terminal Inspection for Examination (optional)
#         # print(completion)

#         ## Results (slicing into the json object output)
#         results = completion.choices[0].message.content

#     except Exception as e:
traceback.print_exc()
#         print("API call function call_openai_chat_api(this_input, select_model=3) failed, error = ", e)
#         return e

#     return results

# call_openai_chat_api("testing")

"""## Add System instructions for rules"""


# Helper Function
def task_extract_markdown_json_to_dict(dict_str, error_log):
    """
    TODO or final_answer


    This function CAN fail and should fail
    if the AI needs to retry at a task.
    Do not stop server when this this triggers an exception.

    edge case: before there is a populated output_log

    if passing, this function will return a valid json object
    """

    """
    Extracts JSON string enclosed between ```json and ``` markers.

    Parameters:
    - text (str): The input text containing the JSON block.

    Returns:
    - str: The extracted JSON string, or an empty string if no JSON block is found.
    """
    print(
        f"\n\n Starting check_function_description_keys, dict_str -> {repr(dict_str)} {type(dict_str)}"
    )

    ########################
    # Check Json Formatting
    ########################

    # pre-check
    # load
    try:
        if "'" not in dict_str:

            # Load the string into a Python dictionary
            dict_data = json.loads(dict_str)

            dict_str = dict_data["translation"]

            if dict_leaf_detection_boolean_true_means_defective(dict_str):
                return dict_str

            else:
                print(f"Failed dict_str precheck")

    except Exception as e:
        traceback.print_exc()
        print(f"Failed dict_str precheck {str(e)}")

    # extraction 1
    try:
        if """```json""" in dict_str:

            pattern = r"```json\n([\s\S]*?)\n```"
            match = re.search(pattern, dict_str)
            dict_str = match.group(1) if match else ""

    except Exception as e:
        traceback.print_exc()
        print(
            f"\nTRY AGAIN: check_function_description_keys() extraction from markdown failed: {e}"
        )
        print(f"Failed dict_str -> {repr(dict_str)}")
        return False

    print(
        f"\n  extraction-1 from markdown dict_str -> {repr(dict_str)} {type(dict_str)}"
    )

    try:

        if """{\'final_answer\':""" in dict_str:
            dict_str = dict_str.replace(
                """{\'final_answer\':""", """{"final_answer":"""
            )

        if """{'final_answer':""" in dict_str:
            dict_str = dict_str.replace("""{'final_answer':""", """{"final_answer":""")

        if """{\\'final_answer\\':""" in dict_str:
            dict_str = dict_str.replace(
                """{\\'final_answer\\':""", """{"final_answer":"""
            )

    except Exception as e:
        traceback.print_exc()
        print(f"Failed dict_str -> {repr(dict_str)} {str(e)}")
        return False

    print(f" dict_str -> {repr(dict_str)} {type(dict_str)}")

    dict_str = clean_and_convert_to_json(dict_str)
    print(f" clean_and_convert_to_json dict_str -> {repr(dict_str)} {type(dict_str)}")

    try:

        if """{\'final_answer\':""" in dict_str:
            dict_str = dict_str.replace(
                """{\'final_answer\':""", """{"final_answer":"""
            )

        if """{'final_answer':""" in dict_str:
            dict_str = dict_str.replace("""{'final_answer':""", """{"final_answer":""")

        if """{\\'final_answer\\':""" in dict_str:
            dict_str = dict_str.replace(
                """{\\'final_answer\\':""", """{"final_answer":"""
            )

    except Exception as e:
        traceback.print_exc()
        print(f"Failed dict_str -> {repr(dict_str)} {str(e)}")
        return False

    # clean
    try:
        """
        Swap in and swap out escaped single commas
        to avoid them being removed during reformatting
        or the reformatting otherwise breaking the json
        """

        # try safety cleaning
        dict_str = dict_str.replace("True", "true")
        dict_str = dict_str.replace("False", "false")
        dict_str = dict_str.replace("None", "null")

        # remove trailing delimiter comma
        print(f"{dict_str[:-6]}")
        dict_str = dict_str.replace('",\n}', '"\n}')

    except Exception as e:
        traceback.print_exc()
        print(f"\nTRY AGAIN:try safety cleaning: {e}")
        print(f"Failed repr(dict_str) -> {repr(dict_str)}")
        return False

    # load
    try:
        # try converting
        print(f"dict_str -> {repr(dict_str)} {type(dict_str)}")

        # Load the string into a Python dictionary
        dict_data = json.loads(dict_str)

    except Exception as e:
        traceback.print_exc()
        print(f"\nTRY AGAIN: trying json.loads(dict_str) Dictionary load failed: {e}")
        print(f"Failed repr(dict_str) -> {repr(dict_str)}")
        return False

    # extraction 2
    try:
        # Extract the value associated with the key 'translation'
        dict_str = dict_data["translation"]

    except Exception as e:
        traceback.print_exc()
        print(
            f"\nTRY AGAIN: check_function_description_keys() extraction 2 from translation = dict_data['translation'] failed: {e}"
        )
        print(f"Failed repr(dict_str) -> {repr(dict_str)}")
        return False

    print(f"\n  final extracted from markdown, dict, etc. ->{repr(dict_str)}")

    # if ok...
    return dict_str


def duration_min_sec(start_time, end_time):

    duration = end_time - start_time

    duration_seconds = duration.total_seconds()

    minutes = int(duration_seconds // 60)
    seconds = duration_seconds % 60
    time_message = f"{minutes}_min__{seconds:.1f}_sec"

    return time_message


def check_answer_in_dict(answer_number, data_dict):
    print(
        f"""def check_answer_in_dict(answer_number, data_dict):

        Scoring:
        answer_number       -> {answer_number}
        type(answer_number) -> {type(answer_number)}

        data_dict        -> {data_dict}
        type(data_dict)  -> {type(data_dict)}

        """
    )
    try:

        # make sure int type
        answer_number = int(answer_number)
        data_dict = {int(key): value for key, value in data_dict.items()}

        # check for string or int form in dict of errors
        if answer_number in data_dict:
            error_reason = data_dict[answer_number]
            return error_reason

        else:
            return None

    except Exception as e:
        traceback.print_exc()
        print(f"check_answer_in_dict() issue: {str(e)}")
        return None


# Helper Function
def set_translator__system_prompt(context_history, target_language):

    ################
    # System Prompt
    ################

    # set translation language and structure of output in system
    text_input = f"""
    You are an expert helpful {target_language} language translator bot that produces high
    quality professional translations. You translate writen UTF-8 language, not emojis or syntax not
    readable by a person.

    You always deliver your translation in the same simple standard format
    between a demiter of three pips like markdown text
    between two sets of ```


    You do not put anything else in ``` ever, only your translation.
    This is how your translation is identified.

    Tour translation format is like this, with no other commentary needed:

    You only translate into {target_language}, and only produce a translation no other commentary.
    Your translations are clear, accurate, helpful, honrable, brief, polite, and professional.
    Your do you best to tranlsate every leaf value field leaving nothing blank.
    Every final leaf values MUST be translated.

    Do not say anything else, just your translation between two sets of ```

    You always double check your work and make sure the translation is
    excellent in the context of the whole body of translation.
    """

    # Remove duplicate spaces
    text_input = re.sub(r"\s+", " ", text_input.strip())

    role = "system"

    context_history.append(segment_for_adding_to_context_history(role, text_input))

    # # inspection
    # print("set_translator__system_prompt -> ", context_history)

    return context_history


# Helper Function
def set_translate__user_prompt(context_history, target_language, original_data):

    ###########################
    # User Translation Request
    ###########################

    # set translation language and structure of output in system
    text_input = f"""translate {original_data}' into {target_language} with the translation in pipes |||YOUR_TRANSLATION||| no other commentary needed, just a translation please"""

    # # Remove duplicate spaces
    # text_input = re.sub(r'\s+', ' ', text_input.strip())

    role = "user"

    context_history.append(segment_for_adding_to_context_history(role, text_input))

    # # inspection
    # print("set_translate__user_prompt", context_history)

    return context_history


# Helper Function
def dict_leaf_detection_boolean_true_means_defective(input_dict):
    """
    Recursively checks if any terminal leaf node in a nested structure is an empty string,
    an empty list, or a single character.

    :param input_dict: The nested input_dict structure to check.
    :return: True if any leaf node is an empty string, an empty list, or a single character; False otherwise.
    """
    if isinstance(input_dict, dict):  # If the current item is a dictionary
        return any(
            dict_leaf_detection_boolean_true_means_defective(value)
            for value in input_dict.values()
        )
    elif isinstance(input_dict, list):  # If the current item is a list
        return any(
            dict_leaf_detection_boolean_true_means_defective(item)
            for item in input_dict
        )
    else:  # If the current item is a leaf node
        return (
            input_dict == ""
            or (isinstance(input_dict, list) and len(input_dict) == 0)
            or (isinstance(input_dict, str) and len(input_dict) == 1)
        )


def print_find_all_models(path="jan/models/"):

    base_path = add_segment_to_absolute_base_path("jan/models/")

    folders_and_files_with_gguf = find_folders_and_files_with_gguf(base_path)

    print("\nAvailable Models:")
    for this_model_path in folders_and_files_with_gguf:
        print("     ", this_model_path)

    print("\n\n")


def find_folders_and_files_with_gguf(base_path):
    folders_and_files_with_gguf = []
    # Iterate through all items in base path
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Check each file in the directory
            for file in os.listdir(item_path):
                # Check if the file ends with '.gguf'
                if file.endswith(".gguf"):
                    # Construct the desired string format: basefolder/filename
                    result = f"{item}/{file}"
                    folders_and_files_with_gguf.append(result)
                    break  # Found a matching file, no need to check the rest
    return folders_and_files_with_gguf


def clean_and_convert_to_json(input_str):
    # Step 1: Automatically handle the known structure without using regex
    # This involves replacing the problematic starting and ending quotes if they exist.
    cleaned_str = input_str.replace("'{", "{").replace("}'", "}")

    # Step 2: Use regex to replace improperly escaped single quotes with double quotes,
    # while ensuring not to change single quotes within words.
    # This regex targets single quotes that are either at the start of the string or
    # followed by a colon or a space, which we assume are not part of the actual text.
    cleaned_str = re.sub(r"(?<=\{|\,)\s*'([^']+)'(?=\:)", r'"\1"', cleaned_str)

    # Additional handling to replace the escaped single quotes inside the value
    cleaned_str = cleaned_str.replace("\\'", "'")

    # Step 3: Convert the cleaned string to a JSON object
    # try:
    #     json_obj = json.loads(cleaned_str)
    # except json.JSONDecodeError as e:
    #     print(f"Error decoding JSON: {e}")
    #     return None

    return cleaned_str


def remove_specific_strings(original_list, strings_to_remove):
    """
    Remove specific strings from a list of strings.

    Parameters:
    - original_list: List of strings from which to remove.
    - strings_to_remove: List of strings to be removed.

    Returns:
    - A new list with specific strings removed.
    """
    # Using list comprehension to filter out the strings to remove
    return [item for item in original_list if item not in strings_to_remove]


def strip_newlines_and_spaces(text):
    # Remove newlines
    text = text.replace("\n", " ")

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_underscores_from_strings_in_list(list_of_strings):
    """
    Removes single underscores and escaped underscores from each string in a list.

    Parameters:
    - list_of_strings (list of str): A list where each element is a string that may contain
      single underscores, single escaped underscores, or double escaped underscores.

    Returns:
    - list of str: A new list of list_of_strings with all such underscores removed.
    """
    pattern = r"(\\{0,20})_"
    cleaned_list_of_strings = [
        re.sub(pattern, " ", string) for string in list_of_strings
    ]

    return cleaned_list_of_strings


def str_to_int_or_none(string_input):
    try:
        return int(string_input)
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return None


def adjust_capitalization(strings):
    """
    Modifies each string in the given list by ensuring that words
    originally in all caps are changed so that only their first letter
    is capitalized.

    Args:
    - strings (list of str): The list of strings to process.

    Returns:
    None; the modification is done in-place.
    """
    for i, s in enumerate(strings):
        new_words = []
        for word in s.split():
            # Check if the word is in all caps (ignoring digits and punctuation)
            if word.isupper():
                # Change the word so only the first letter is capitalized
                new_word = word.capitalize()
                new_words.append(new_word)
            else:
                new_words.append(word)
        # Join the processed words back into a string
        strings[i] = " ".join(new_words)


# Helper Function
def check_structure_of_response(dict_str):
    """ """
    # print(f"\n\n Starting check_structure_of_response, dict_str -> {repr(dict_str)} {type(dict_str)}")
    print(f"\n\n Starting check_structure_of_response, dict_str ")

    try:
        # Define the regex pattern to match text between triple pipes
        pattern = r"\|\|\|(.+?)\|\|\|"

        # Use re.findall to find all occurrences that match the pattern
        matches_list = re.findall(pattern, dict_str)

        # matches_list is a list of all captured groups in the text
        # If you expect only one match and want to return just that, you can adjust the code accordingly

        strings_to_remove = [
            "YOUR_TRANSLATION",
            "YOUR TRANSLATION",
            "YOUR_TRANSCRIPTION",
            "your_translation",
            "Your_Translation",
            "your_Translation",
            "your translation",
            "best_selection",
            "best selection",
            "TRANSLATION",
            "selection",
            "#",
        ]

        matches_list = remove_specific_strings(matches_list, strings_to_remove)

        cleaned_matches_list = remove_underscores_from_strings_in_list(matches_list)

        translation = cleaned_matches_list

        # Remove duplicates
        translation_set = set(translation)
        translation_list = list(translation_set)

        # adjust all-capitalized words to only starting with a capital letter
        adjust_capitalization(translation_list)

        # inspection
        print(f"check_structure_of_response()  translation_list -> {translation_list}")

        if len(translation_list):
            return translation_list

        else:
            print(f"check_structure_of_response error parsing ai translation_list")
            return False

    except Exception as e:
        traceback.print_exc()
        print(
            f"check_structure_of_response error parsing ai translation_list -> {str(e)}"
        )
        return False


# Helper Function
def task_check_structure_of_response(
    structured_output_format,
    dict_str,
    task_mode_answer_option_choices_provided_boolean,
    these_original_task_options,
    retry_or_error_event_counter_list,
    error_log,
):
    """
    checking the structure of the response...depends on what the desired structure is.
    """
    print(f"structured_output_format -> {structured_output_format}")
    print(f"dict_str -> {dict_str}")

    try:
        # print(f"\n\n Starting check_structure_of_response, dict_str -> {repr(dict_str)} {type(dict_str)}")
        print(f"\n\n Starting task_check_structure_of_response, dict_str ")

        # if the model is structuring the output in ||| ||| pipes, then look for pipes
        if structured_output_format == "pipes":

            # Define the regex pattern to match text between triple pipes
            pattern = r"\|\|\|(.+?)\|\|\|"

            # Use re.findall to find all occurrences that match the pattern
            matches_list = re.findall(pattern, dict_str)

            # inspection
            print(f"matches_list -> {matches_list}")

            # matches_list is a list of all captured groups in the text
            # If you expect only one match and want to return just that, you can adjust the code accordingly

            strings_to_remove = [
                "final answer option number",
                "number",
                "final answer",
                "FINAL ANSWER",
                "final_answer",
                "NUMBER",
            ]

            matches_list = remove_specific_strings(matches_list, strings_to_remove)

            if task_mode_answer_option_choices_provided_boolean:
                print(f"matches_list before filer ->  {matches_list}")

                matches_list = remove_non_integers_from_list(matches_list)

                print(
                    f"remove_non_integers_from_list(matches_list) matches_list ->  {matches_list}"
                )

                """
                Use a list of strings of option-number-integers:
                """
                # remove any 'option' this is not a real option
                option_number_list = []
                for this_int in range(1, len(these_original_task_options) + 1):
                    option_number_list.append(str(this_int))
                print(f"option_number_list ->  {option_number_list}")
                matches_list = [
                    item for item in matches_list if item in option_number_list
                ]

            if matches_list:
                print(
                    f"matches_list after option-number-string-only cleaned ->  {matches_list}"
                )
                response_to_task = matches_list[-1]
            else:
                response_to_task = ""

            # cleaned_matches_list = remove_underscores_from_strings_in_list(matches_list)

            # translation = cleaned_matches_list

            # # Remove duplicates
            # translation_set = set(translation)
            # response_to_task = list(translation_set)

            # # adjust all-capitalized words to only starting with a capital letter
            # adjust_capitalization(response_to_task)

            # inspection
            print(
                f"task_check_structure_of_response()  response_to_task -> {response_to_task}"
            )

            if len(response_to_task):
                return response_to_task

            else:
                print(
                    f"no response, task_check_structure_of_response error parsing ai response_to_task"
                )
                return False

        elif structured_output_format == "markdown_json":

            print(
                f"use context, structured_output_format -> {structured_output_format}"
            )
            response_to_task = task_extract_markdown_json_to_dict(dict_str, error_log)

            # inspection
            print(
                f"task_check_structure_of_response()  response_to_task -> {response_to_task}"
            )

            if len(response_to_task):
                return response_to_task

            else:
                print(
                    f"answer length = 0 (zero), elif structured_output_format == markdown_json, in task_check_structure_of_response error parsing ai response_to_task"
                )
                return False

        else:
            raise "No output structure mode selected: task_check_structure_of_response()"

    except Exception as e:
        traceback.print_exc()
        print(
            f"Exception task_check_structure_of_response() error parsing ai response_to_task -> {str(e)}"
        )
        return False


"""# Call api within: Check json structure against original"""


def remove_non_integers_from_list(input_list):
    try:
        return [
            item
            for item in input_list
            if isinstance(item, int) or (isinstance(item, str) and item.isdigit())
        ]
    except Exception as e:
        traceback.print_exc()
        raise e


def extract_values_from_dict(dict_str):
    """
    take dict, list, or string-dict-json
    returns the values from a dictionary as a list
    """

    try:
        # inspection
        print("\n extract_values_from_dict()")
        print(f"dict_str -> {dict_str}")
        print(f"type(dict_str) -> {type(dict_str)}")

        # if a list, take last item from list
        if isinstance(dict_str, list):
            dict_str = dict_str[-1]

        print(f"dict_str -> {dict_str}")
        print(f"type(dict_str) -> {type(dict_str)}")

        # if a list, take last item from list
        if isinstance(dict_str, str):
            print("string input")
            dict_str = dict_str.replace("'", '"')
            # Parse the string into a Python dictionary
            dict_str = json.loads(dict_str)

        # Extract the values and convert to a list
        values_list = list(dict_str.values())
        print(f"values_list -> {values_list}")
        print(f"type(values_list) -> {type(values_list)}")

        return values_list

    except Exception as e:
        traceback.print_exc()
        print(f"extract_values_from_dict failed to get values, maybe bad input {str(e)}")
        return False


def return_list_of_jsons_from_string(dict_str):

    try:

        if "`" in str(dict_str):
            dict_str = dict_str.replace("\n", " ")

            # Define the pattern to match JSON blocks enclosed in triple backticks
            pattern = r"```json(.*?)```"
            matches = re.finditer(pattern, dict_str)

            # Initialize an empty list to store extracted JSON strings
            json_blocks = []

            for match in matches:
                # Extract the JSON string from the match and append it to the list
                json_blocks.append(match.group(1))

            # Return the list of JSON strings
            return json_blocks[-1]

        else:
            # try without pips
            print("try extract_dictionaries_from_string_no_pips(dict_str) ")
            return extract_dictionaries_from_string_no_pips(dict_str)

    except Exception as e:
        traceback.print_exc()
        print(
            f"failed, no json return_list_of_jsons_from_string(dict_str) dict_str-> {dict_str} {str(e)}"
        )
        return False


# Helper Function
def json_number_check_structure_of_response_to_list(dict_str) -> list:
    """
    This function CAN fail and should fail
    if the AI needs to retry at a task.
    Do not stop server when this this triggers an exception.

    edge case: before there is a populated output_log

    if passing, this function will return a valid json object
    """

    """
    1. Extracts JSON string enclosed between ```json and ``` markers.

    2. extracts values from the dict

    Parameters:
    - text (str): The input text containing the JSON block.

    Returns:
    - str: The extracted JSON string, or an empty string if no JSON block is found.
    """
    print(
        f"\n\n json_number_check_structure_of_response_to_list -> {repr(dict_str)} \nType -> {type(dict_str)}"
    )

    if "'" in str(dict_str):
        extracted_dict = return_list_of_jsons_from_string(dict_str)
        if isinstance(extracted_dict, list):
            extracted_dict = extracted_dict[-1]

        print(f"extracted_dict -> {extracted_dict}")
        print(f"type(extracted_dict) {type(extracted_dict)}")

    else:
        result = extract_dictionaries_from_string_no_pips(dict_str)
        # get last item
        extracted_dict = result[-1]

    if not extracted_dict:
        return False

    number_list = extract_values_from_dict(extracted_dict)

    print(
        f"\n  final extracted from markdown, dict, etc. number_list ->{repr(number_list)}"
    )

    # if ok...
    return number_list


def make_score_tally(directory_path):
    """
    Sorry, this is an attrocity that I will replace
    with real code
    as soon as I have time (so...maybe never)
    """
    solution_dir_path = os.path.abspath(directory_path)

    # Ensure the directory exists
    os.makedirs(solution_dir_path, exist_ok=True)

    report_filename = os.path.join(solution_dir_path, "score_report.csv")
    tally_header_string_list = ["percent", "model", "task_file", "score", "time_stamp"]

    # # Check if the file exists and is empty to decide on writing the header
    if not os.path.exists(report_filename) or os.path.getsize(report_filename) == 0:
        #     with open(report_filename, 'w', newline='') as csvfile:
        #         csvfile.write(header_string)

        create_cvs_list_of_fields_to_csv_header(
            report_filename, tally_header_string_list
        )

    try:
        report_data_dict = {}
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
                                task_file = row.get(
                                    "task_file", ""
                                )  # Get the task_file field
                                report_data_dict.setdefault(
                                    # model_name, {"total": 0, "count": 0}
                                    model_name,
                                    {"total": 0, "count": 0, "task_files": []},
                                )
                                report_data_dict[model_name]["total"] += score
                                report_data_dict[model_name]["count"] += 1
                                report_data_dict[model_name]["task_files"].append(
                                    task_file
                                )  # Append task_file to the list

                                total_scores += 1

        # Prepare report lines excluding the header https://stackoverflow.com/questions/2363731/how-to-append-a-new-row-to-an-old-csv-file-in-python
        report_list = []
        for model_name, score_data in report_data_dict.items():
            # for stone-age python:
            score_total_item = score_data["total"]
            score_count_item = score_data["count"]

            percentage = (
                (score_total_item / score_count_item) * 100 if total_scores > 0 else 0
            )
            # where total is correct number and count is...the total

            score = f"{score_total_item} / {score_count_item}"
            task_files = ", ".join(
                score_data["task_files"]
            )  # Join task_files into a comma-separated string
            report_line = [percentage, model_name, task_files, score]
            report_list.append(report_line)

        for report_line in report_list:
            print(report_line)

            date_time = datetime.now(UTC)
            readable_timestamp = date_time.strftime("%Y-%m-%d-%H:%M:%S%f")
            report_line.append(readable_timestamp)

            append_list_of_values_to_csv(report_filename, report_line)

        print(f"Report appended to {report_filename}")

    except Exception as e:
        traceback.print_exc()
        print(f"Error processing score tally: {e}")


def get_absolute_base_path():
    # Get the absolute path to the current user's home directory (Starts from root, ends at home directory)
    home_directory = os.path.expanduser("~")  # e.g., "/home/john"

    absolute_path = os.path.abspath(home_directory)

    return absolute_path


def add_segment_to_absolute_base_path(additional_segment):
    # Get the absolute path to the current user's home directory
    home_directory = os.path.expanduser("~")
    # print(f"Home Directory: {home_directory}")  # Debugging print

    # Create an absolute path by joining the home directory with the additional segment
    absolute_path = os.path.join(home_directory, additional_segment)
    # print(f"Joined Path Before abspath: {absolute_path}")  # Debugging print

    # Ensure the path is absolute (this should not change the path if already absolute)
    absolute_path = os.path.abspath(absolute_path)
    # print(f"Final Absolute Path: {absolute_path}")  # Debugging print

    return absolute_path


"""
For extraction of 'line' of jsonl for task data in json, goes with json_to_values_list(json_obj):
"""


def extract_object_by_line_number(jsonl_file_path, line_number):
    """
    Retrieves a JSON object from a specified line number in a JSON Lines file.

    Parameters:
    - jsonl_file_path: str. The path to the JSON Lines file.
    - line_number: int. The line number of the object to retrieve, starting from 0.

    Returns:
    - dict: The JSON object at the specified line number. None if the line number is out of bounds.
    """
    with open(jsonl_file_path, "r") as file:
        for current_line_number, line in enumerate(file):
            if current_line_number == line_number:
                return json.loads(line)
    return None


"""
For extraction of 'line' of jsonl for task data in json, goes with extract_object_by_line_number(jsonl_file_path, line_number):
"""


def json_to_values_list(json_obj):
    """
    Converts a JSON object into a list of its values.

    Parameters:
    - json_obj: dict. The JSON object to convert.

    Returns:
    - list: A list of values from the JSON object.
    """
    return list(json_obj.values())


"""
# Example usage:

# To extract an object from the 2nd line (line_number = 1 since it's zero-indexed):
selected_object = extract_object_by_line_number('task2.jsonl', 0)

# Then convert the selected object to a list of its values:
values_list = json_to_values_list(selected_object)

# Note: 'data.jsonl' should be replaced with the actual path to your JSON Lines file.
values_list
"""


def is_substring_boolean(if_this_string, in_this_string):
    if not if_this_string:
        return False

    # Define math symbols to keep
    math_symbols = "+-*/^="

    # Remove punctuation from both strings, excluding math symbols
    if_this_string = if_this_string.translate(
        str.maketrans("", "", "".join(set(string.punctuation) - set(math_symbols)))
    )
    in_this_string = in_this_string.translate(
        str.maketrans("", "", "".join(set(string.punctuation) - set(math_symbols)))
    )

    # Strip whitespace and convert to lowercase
    if_this_string = if_this_string.strip().lower()
    in_this_string = in_this_string.strip().lower()

    # Check if if_this_string is a substring of in_this_string
    return if_this_string in in_this_string


def extract_specific_fields(json_obj, fields):
    """
    Extracts specified fields from a JSON object.

    Parameters:
    - json_obj: dict. The JSON object to extract data from.
    - fields: list. A list of strings representing the keys of the fields to extract.

    Returns:
    - dict: A dictionary containing only the specified fields from the original JSON object.
    """
    return {field: json_obj[field] for field in fields if field in json_obj}


def count_jsonl_lines(file_path):
    """
    Counts the number of lines (objects) in a JSONL file.

    Args:
        file_path (str): The path to the JSONL file.

    Returns:
        int: The number of lines (objects) in the file.
    """
    count = 0
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                json.loads(line)
                count += 1
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line}")
    return count


def get_csv_len_in_rows(path):
    try:
        with open(path, "r") as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader)
        return row_count

    except Exception as e:
        traceback.print_exc()
        raise e


def get_file_extension(file_path):
    """
    Returns the file extension (suffix) from a given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file extension (suffix) without the leading dot.
    """
    # Get the base name of the file (the part after the last directory separator)
    base_name = os.path.basename(file_path)

    # Split the base name into the file name and extension
    name, ext = os.path.splitext(base_name)

    # Return the extension without the leading dot

    output = "." + ext[1:].lower()

    return output


def filter_jsonl_by_condition(jsonl_file_path, condition_function):
    """
    Filters objects in a JSON Lines file based on a specified condition function.

    Parameters:
    - jsonl_file_path: str. The path to the JSON Lines file.
    - condition_function: function. A function that takes a JSON object as input and returns True if the object meets the condition, False otherwise.

    Returns:
    - list: A list of JSON objects that meet the condition.
    """
    matching_objects = []
    with open(jsonl_file_path, "r") as file:
        for line in file:
            json_obj = json.loads(line)
            if condition_function(json_obj):
                matching_objects.append(json_obj)
    return matching_objects


# Example condition function:
def example_condition(json_obj):
    return json_obj["field"] == "specific_value"


"""
# Define the path to your JSON Lines file
jsonl_file_path = 'task2.jsonl'

# Specify the line number from which to extract the JSON object (e.g., line 2)
line_number = 1  # Remember, it's zero-indexed

# Specify the fields you're interested in extracting from the JSON object
fields_of_interest = ['ctx_b', 'endings']

# Step 1: Extract the JSON object from the specified line
json_object = extract_object_by_line_number(jsonl_file_path, line_number)

# Check if the json_object is not None to avoid errors in the next step
if json_object is not None:
    # Step 2: Extract only the specified fields from the JSON object
    specific_fields = extract_specific_fields(json_object, fields_of_interest)
    print("Extracted Fields:", specific_fields)
else:
    print("No JSON object found at the specified line.")


"""


# helper function
def call_api_within_structure_check(
    context_history,
    use_this_model,
    parameter_dict,
    ai_local_or_cloud_mode,
    skeleton_json,
):
    retry_counter = 0
    json_ok_flag = False

    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]

    anthropic_model_list = [
        "claude-2.1",
        "claude-3-opus-20240229",
    ]

    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # gguf_model_list = [
    #     "jais",
    #     "tiny_llama",
    #     "mistral7b",
    # ]

    while not json_ok_flag:

        ####################
        # get a translation
        ####################

        try:
            # check json structure

            ########################
            # Select Model and Mode
            ########################

            # for off-line local mode
            if ai_local_or_cloud_mode == "gguf":
                print("Started gguf")

                # get model path name-end

                # inspection
                print(f"use_this_model -> {use_this_model}")

                configies_dict = {
                    "model_path_base": add_segment_to_absolute_base_path("jan/models/"),
                    "model_nickname": use_this_model,
                    "cpp_path": add_segment_to_absolute_base_path(
                        "code/llama_cpp/llama.cpp"
                    ),
                    "pipeline_mode": mini_gguf_api,
                }

                # inspection
                # print(f"configies_dict -> {configies_dict}")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](
                    context_history, parameter_dict, configies_dict
                )
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################

            # mistral
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

            # anthropic
            elif use_this_model in anthropic_model_list:
                print(f"Anthropic api selected...{use_this_model}")
                dict_str = simple_ask_anthropic_py(context_history, use_this_model)

            elif use_this_model in open_ai_model_list:
                print(f"openAI api selected...{use_this_model}")
                dict_str = openai_call_context_timeout(
                    client,
                    context_history,
                    model=use_this_model,
                    max_retries=10,
                    temp=0.9,
                    timeout_min=8,
                )

            else:
                print(f"no known api selected...{use_this_model}")
                raise f"No known model option chosen...use_this_model -> {use_this_model}"

        except Exception as e:
            traceback.print_exc()
            jsonchecked_translation = None
            print(f"Failed: {str(e)}")

        jsonchecked_translation = check_structure_of_response(dict_str)

        if jsonchecked_translation:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(
                f"\n\ncall api with structure check while not json_ok_flag: retry_counter -> {retry_counter}\n"
            )

    print(
        f"all api with structure check out-while not json_ok_flag: retry_counter -> {retry_counter}"
    )

    return jsonchecked_translation


# helper function
def general_task_call_api_within_structure_check(
    context_history,
    use_this_model,
    parameter_dict,
    ai_local_or_cloud_mode,
    task_mode_answer_option_choices_provided_boolean,
    task_mode_output_structure_mode,
    draft_task_attempt_log,
    retry_x_times,
    these_original_task_options,
    this_task_config_dict,
    retry_or_error_event_counter_list,
    error_log,
    test_cases=None,
    function_name=None,
    programming_language=None,
):
    """
    task_mode_output_structure_mode is passed to the output structure checker
    """

    if "function_writing" in this_task_config_dict:
        function_writing = this_task_config_dict["function_writing"]
    else:
        function_writing = False

    # default
    dict_str = ""

    retry_counter = 0
    json_ok_flag = False

    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]

    anthropic_model_list = [
        "claude-2.1",
        "claude-3-opus-20240229",
    ]
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # gguf_model_list = [
    #     "jais",
    #     "tiny_llama",
    #     "mistral7b",
    # ]

    error_message_list_grab_last = []

    while (not json_ok_flag) and (retry_counter < retry_x_times):

        ####################
        # get a translation
        ####################

        """
        Add the last error to the input as feedback,
        if making a function
        and if there was an error.

        Note: pathways other than writing code might use this too.
        """
        if error_message_list_grab_last and function_writing:
            context_history = error_message_list_grab_last[0] + context_history

        try:
            # check json structure

            ########################
            # Select Model and Mode
            ########################

            # for off-line local mode
            if ai_local_or_cloud_mode == "gguf":
                print("Started gguf")

                # get model path name-end

                # inspection
                print(f"use_this_model -> {use_this_model}")

                configies_dict = {
                    "model_path_base": add_segment_to_absolute_base_path("jan/models/"),
                    "model_nickname": use_this_model,
                    "cpp_path": add_segment_to_absolute_base_path(
                        "code/llama_cpp/llama.cpp"
                    ),
                    "pipeline_mode": mini_gguf_api,
                }

                # # inspection
                # print(f"configies_dict -> {configies_dict}")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](
                    context_history, parameter_dict, configies_dict
                )
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

                draft_task_attempt_log.append(response)

            ################
            # for cloud api
            ################
            # mistral
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

            # anthropic
            elif use_this_model in anthropic_model_list:
                print(f"Anthropic api selected...{use_this_model}")
                dict_str = simple_ask_anthropic_py(context_history, use_this_model)

            elif use_this_model in open_ai_model_list:
                print(f"openAI api selected...{use_this_model}")
                dict_str = openai_call_context_timeout(
                    client,
                    context_history,
                    model=use_this_model,
                    max_retries=10,
                    temp=0.9,
                    timeout_min=8,
                )

            else:
                print(f"no known api selected...{use_this_model}")
                raise f"No known model option chosen...use_this_model -> {use_this_model}"

        except Exception as e:
            traceback.print_exc()
            task_response_string = None
            print(
                f"\n\nMaybe incorrect model choice, use_this_model -> {use_this_model}: general_task_call_api_within_structure_check Failed: {str(e)}"
            )

        if not dict_str:
            print(
                f"general_task_call_api_within_structure_check, not returned string,  dict_str -> {dict_str}, type -> {type(dict_str)}"
            )
            return False

        if function_writing:

            # print(f"""
            #     Input inspection: general_task_call_api_within_structure_check()

            #     code_markdown:
            #     dict_str -> {dict_str} {type(dict_str)}

            #     test_cases -> {test_cases} {type(test_cases)}

            #     function_name -> {function_name} {type(function_name)}

            #     retry_or_error_event_counter_list -> {retry_or_error_event_counter_list} {type(retry_or_error_event_counter_list)}

            #     error_log -> {error_log} {type(error_log)}

            #     """)

            task_response_string, error_message = (
                pass_fail_unit_test_function__stdout_stderr(
                    code_markdown=dict_str,
                    test_cases=test_cases,
                    function_name=function_name,
                    retry_or_error_event_counter_list=retry_or_error_event_counter_list,
                    error_log=error_log,
                    programming_language=programming_language,
                    dependencies=None,
                )
            )
            print(f"""
                general_task_call_api_within_structure_check pass_fail_unit_test_function__stdout_stderr 
                task_response_string -> {task_response_string}
                """)
            print(f"error_message -> {error_message}")

            if task_response_string == "pass":
                return task_response_string

            else:
                error_message_list_grab_last.append(error_message)
                # retry_counter += 1
                task_response_string = None

        else:
            task_response_string = task_check_structure_of_response(
                task_mode_output_structure_mode,
                dict_str,
                task_mode_answer_option_choices_provided_boolean,
                these_original_task_options,
                retry_or_error_event_counter_list,
                error_log,
            )

        if task_response_string:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(
                f"\n\ngeneral_task_call_api_within_structure_check in while retry_counter -> {retry_counter}\n"
            )

            if retry_counter > retry_x_times:
                return False

    print(
        f"general_task_call_api_within_structure_check finalretry_counter -> {retry_counter}"
    )

    return task_response_string


""" call_api_within_number_check"""


# helper function
def number_call_api_within_structure_check(
    context_history, use_this_model, parameter_dict, ai_local_or_cloud_mode
):
    retry_counter = 0
    json_ok_flag = False

    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]

    anthropic_model_list = [
        "claude-2.1",
        "claude-3-opus-20240229",
    ]

    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # gguf_model_list = [
    #     "jais",
    #     "tiny_llama",
    #     "mistral7b",
    # ]

    while not json_ok_flag:

        ####################
        # get a translation
        ####################

        try:
            # check json structure

            ########################
            # Select Model and Mode
            ########################

            # for off-line local mode
            if ai_local_or_cloud_mode == "gguf":
                print("Started gguf")

                # get model path name-end

                # inspection
                print(f"use_this_model -> {use_this_model}")

                configies_dict = {
                    "model_path_base": add_segment_to_absolute_base_path("jan/models/"),
                    "model_nickname": use_this_model,
                    "cpp_path": add_segment_to_absolute_base_path(
                        "code/llama_cpp/llama.cpp"
                    ),
                    "pipeline_mode": mini_gguf_api,
                }

                print(f"configies_dict -> {configies_dict}")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](
                    context_history, parameter_dict, configies_dict
                )
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################
            # mistral
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

            # anthropic
            elif use_this_model in anthropic_model_list:
                print(f"Anthropic api selected...{use_this_model}")
                dict_str = simple_ask_anthropic_py(context_history, use_this_model)

            elif use_this_model in open_ai_model_list:
                print(f"openAI api selected...{use_this_model}")
                dict_str = openai_call_context_timeout(
                    client,
                    context_history,
                    model=use_this_model,
                    max_retries=10,
                    temp=0.9,
                    timeout_min=8,
                )

            else:
                print(f"no known api selected...{use_this_model}")
                raise f"No known model option chosen...use_this_model -> {use_this_model}"

        except Exception as e:
            traceback.print_exc()
            json_checked_value_list = None
            print(f"Failed: {str(e)}")

        json_checked_value_list = json_number_check_structure_of_response_to_list(
            dict_str
        )

        if json_checked_value_list:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(
                f"\n\nnumber_call_api_within_structure_check in retry_counter -> {retry_counter}\n"
            )

    print(
        f"number_call_api_within_structure_check out retry_counter -> {retry_counter}"
    )

    return json_checked_value_list


# helper function
def task_number_call_api_within_structure_check(
    context_history,
    use_this_model,
    parameter_dict,
    ai_local_or_cloud_mode,
    retry_x_times,
    models_dir_path,
):
    retry_counter = 0
    json_ok_flag = False

    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]

    anthropic_model_list = [
        "claude-2.1",
        "claude-3-opus-20240229",
    ]
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # gguf_model_list = [
    #     "jais",
    #     "tiny_llama",
    #     "mistral7b",
    # ]

    while not json_ok_flag:

        ####################
        # get a translation
        ####################

        try:
            # check json structure

            ########################
            # Select Model and Mode
            ########################

            # for off-line local mode
            if ai_local_or_cloud_mode == "gguf":
                print("Started gguf")

                # get model path name-end

                # inspection
                print(f"use_this_model -> {use_this_model}")

                configies_dict = {
                    "model_path_base": add_segment_to_absolute_base_path(
                        models_dir_path
                    ),
                    "model_nickname": use_this_model,
                    "cpp_path": add_segment_to_absolute_base_path(
                        "code/llama_cpp/llama.cpp"
                    ),
                    "pipeline_mode": mini_gguf_api,
                }

                print(f"configies_dict -> {configies_dict}")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](
                    context_history, parameter_dict, configies_dict
                )
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################
            # mistral
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

            # anthropic
            elif use_this_model in anthropic_model_list:
                print(f"Anthropic api selected...{use_this_model}")
                dict_str = simple_ask_anthropic_py(context_history, use_this_model)

            elif use_this_model in open_ai_model_list:
                print(f"openAI api selected...{use_this_model}")
                dict_str = openai_call_context_timeout(
                    client,
                    context_history,
                    model=use_this_model,
                    max_retries=10,
                    temp=0.9,
                    timeout_min=8,
                )

            else:
                print(f"no known api selected...{use_this_model}")
                raise f"No known model option chosen...use_this_model -> {use_this_model}"

        except Exception as e:
            traceback.print_exc()
            json_checked_value_list = None
            print(f"Failed: {str(e)}")

        json_checked_value_list = json_number_check_structure_of_response_to_list(
            dict_str
        )

        if json_checked_value_list:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(
                f"\n\nnumber_call_api_within_structure_check in retry_counter -> {retry_counter}\n"
            )

            # exit after x retries
            if retry_counter > retry_x_times:
                return False

    print(
        f"number_call_api_within_structure_check out retry_counter -> {retry_counter}"
    )

    return json_checked_value_list


"""# Crawler model call"""


# helper function
def crawler_call_api_within_json_structure_check(
    context_history, use_this_model, ai_local_or_cloud_mode, skeleton_json
):
    retry_counter = 0
    json_ok_flag = False

    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]

    anthropic_model_list = [
        "claude-2.1",
        "claude-3-opus-20240229",
    ]

    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # TODO
    # gguf_model_list = ["jais", "tiny_llama", "mistral7b", "mistral"]

    while not json_ok_flag:

        ####################
        # get a translation
        ####################

        try:
            # check json structure

            ########################
            # Select Model and Mode
            ########################

            # for off-line local mode
            if ai_local_or_cloud_mode == "gguf":
                print("Started gguf")

                # get model path name-end

                #######################
                # Tune Your Paramaters
                #######################
                parameter_dict = {
                    "--temp": 0.8,  # (default value is 0.8)
                    "--top-k": 40,  # (selection among N most probable. default: 40)
                    "--top-p": 0.9,  # (probability above threshold P. default: 0.9)
                    "--min-p": 0.05,  # (minimum probability threshold. default: 0.05)
                    "--seed": -1,  # seed, =1 is random seed
                    "--tfs": 1,  # (tail free sampling with parameter z. default: 1.0) 1.0 = disabled
                    "--threads": 8,  # (~ set to number of physical CPU cores)
                    "--typical": 1,  # (locally typical sampling with parameter p  typical (also like ~Temperature) (default: 1.0, 1.0 = disabled).
                    "--mirostat": 2,  # (default: 0,  0= disabled, 1= Mirostat, 2= Mirostat 2.0)
                    "--mirostat-lr": 0.05,  # (Mirostat learning rate, eta.  default: 0.1)
                    "--mirostat-ent": 3.0,  # (Mirostat target entropy, tau.  default: 5.0)
                    "--ctx-size": 500,  # Sets the size of the prompt context
                }

                configies_dict = {
                    "model_path_base": add_segment_to_absolute_base_path("jan/models/"),
                    "model_nickname": use_this_model,
                    "cpp_path": add_segment_to_absolute_base_path(
                        "code/llama_cpp/llama.cpp"
                    ),
                }

                ######################
                # local api with gguf
                ######################
                response = gguf_api(context_history, parameter_dict, configies_dict)
                print(f" response[0] -> {response[0]}")
                print(f" response[1] -> {response[1]}")
                print(f" response[2] -> {response[2]}")
                dict_str = response[2]

                if len(dict_str) == 0:
                    raise "error"

            ################
            # for cloud api
            ################
            # mistral
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

            # anthropic
            elif use_this_model in anthropic_model_list:
                print(f"Anthropic api selected...{use_this_model}")
                dict_str = simple_ask_anthropic_py(context_history, use_this_model)

            elif use_this_model in open_ai_model_list:
                print(f"openAI api selected...{use_this_model}")
                dict_str = openai_call_context_timeout(
                    client,
                    context_history,
                    model=use_this_model,
                    max_retries=10,
                    temp=0.9,
                    timeout_min=8,
                )

            else:
                print(f"no known api selected...{use_this_model}")
                raise f"No known model option chosen...use_this_model -> {use_this_model}"

        except Exception as e:
            traceback.print_exc()
            jsonchecked_translation = None
            print(f"Failed: {str(e)}")

        jsonchecked_translation = check_structure_of_response(dict_str, skeleton_json)

        if jsonchecked_translation:
            json_ok_flag = True

        else:
            retry_counter += 1

    print(
        f"crawler_call_api_within_json_structure_check retry_counter -> {retry_counter}"
    )

    return jsonchecked_translation


"""# Put Flesh on the Skeleton
- add translations to the lists
"""


# helper function
def set_select_best__system_prompt(context_history, target_language):

    ########################################
    # System Prompt to pick best traslation
    ########################################

    # set translation language and structure of output in system
    text_input = f"""
    You are a helpful expert translator bot that selects high
    quality professional translations from a list, choosing
    the one best translation.

    You always present your selection in the same precise format
    between two sets of ``` like markdown.

    You always only use  wo sets of ``` triple pips to surround the translation.

    Your final translation selections are clear, accurate, helpful, honrable, brief, polite, and professional.
    Always select one best translation, only one.

    You always do your best to produce top quality results.

    Do not say anything else, just your translation between two sets of ```
    """

    # Remove duplicate spaces
    text_input = re.sub(r"\s+", " ", text_input.strip())

    role = "system"

    context_history.append(segment_for_adding_to_context_history(role, text_input))

    return context_history


# helper function
def set_select_best__user_prompt(
    context_history, target_language, populated_skeleton, original_data
):

    ###########################
    # User Translation Request to select best translation
    ###########################

    # set translation language and structure of output in system
    text_input = f"""
    Carefully select the best {target_language} language translation
    of {original_data} from this list of translations: {populated_skeleton}.

    Double check your work and make sure the translation is
    accurate, brief, and polite.

    Aways only use triple pips to surround the translation.
     between two sets of ```

    Do not say anything else, just your translation  between two sets of ```

    Do your best!
    """

    # Remove duplicate spaces
    text_input = re.sub(r"\s+", " ", text_input.strip())

    role = "user"

    context_history.append(segment_for_adding_to_context_history(role, text_input))

    # print("\n\n\n\nset_select_best__user_prompt() context_history", context_history)

    return context_history


"""# Crawler functions
1. make list of paths
2. extrac path value
3. write path value
"""

"""
####################
# Crawler functions
####################

1. make list of paths   generate_paths(json_object)
2. extrac path value    extract_values_by_paths(json_object, paths_list)
3. write path value     insert_values_by_paths(skeleton_json, paths_list, translated_values)

"""


def generate_paths(json_object, current_path=None):
    if current_path is None:
        current_path = []
    paths_list = []
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            paths_list += generate_paths(value, current_path + [key])
    elif isinstance(json_object, list):
        for idx, item in enumerate(json_object):
            paths_list += generate_paths(item, current_path + [str(idx)])
    else:  # Terminal leaf found
        paths_list.append(current_path)
    return paths_list


def extract_value_by_path(target_dict, this_path):
    """
    Extracts a single value from a JSON object based on a single this_path.

    :param target_dict: The JSON object from which to extract the value.
    :param this_path: The this_path to the value as a list of keys/indexes.
    :return: The value at the specified this_path.
    """
    target_dict_copy = target_dict.copy()
    print("start: extract_value_by_path()")
    print(f"target_dict -> {target_dict}")
    print(f"this_path -> {this_path}")

    for step in this_path:
        if isinstance(step, str) and step.isdigit():
            step = int(step)  # Convert to integer if it's a list index
        target_dict_copy = target_dict_copy[step]
    return target_dict_copy


def remove_duplicates_from_terminal_list(target_dictionary, this_path):
    """
    Removes duplicates from a terminal-leaf list in a JSON object based on a specified path.

    :param target_dictionary: The JSON object to modify.
    :param this_path: The path to the terminal list as a list of keys/indexes.
    :return: None. The function modifies the JSON object in place.
    """
    # Navigate to the terminal-leaf list's parent
    parent = target_dictionary
    for step in this_path[
        :-1
    ]:  # Exclude the last step to get to the parent of the terminal-leaf list
        if isinstance(step, str) and step.isdigit():
            step = int(step)  # Convert string digits to integer if necessary
        parent = parent[step]

    # Extract the last step, which is the key/index of the terminal-leaf list
    last_step = this_path[-1]
    if isinstance(last_step, str) and last_step.isdigit():
        last_step = int(last_step)  # Convert string digits to integer if necessary

    # Remove duplicates by converting the list to a set and back to a list
    terminal_list = parent[last_step]
    if isinstance(terminal_list, list):  # Ensure the terminal-leaf is indeed a list
        parent[last_step] = list(
            dict.fromkeys(terminal_list)
        )  # Remove duplicates, preserving order

    print("Duplicates removed from terminal-leaf list.")


def read_jsonl_file(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            obj = json.loads(line)
            question = obj["question"]
            options = obj["options"]
            data.append((question, options))
    return data


def extract_row_from_jsonl(this_row_or_line_number, this_path):
    """
    Extracts a specific row from a CSV file, ensuring that commas within quotes are correctly parsed as part of the same field.

    Parameters:
        this_row_or_line_number (int): The index of the row to extract from the CSV.
        this_path (str): The path to the CSV file.

    Returns:
        list: The extracted row as a list of strings, respecting quoted fields. Returns an empty list if the row
              does not exist, the file cannot be opened, or parsing fails.
    """
    try:
        with open(this_path, mode="r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == this_row_or_line_number:
                    return row
    except FileNotFoundError:
        print(f"File not found: {this_path}")
    except csv.Error as e:
        print(f"CSV parsing error in file {this_path}: {e}")
    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")

    # Return empty list if the row was not found, an error occurred, or file cannot be parsed
    print("WARNING: No row found or error in parsing in extract_row_from_csv()")
    return []


# Ensure your CSV is correctly formatted, particularly for complex fields encapsulated by quotes.


def extract_string_value_by_path(json_object, this_path):
    """
    Extracts a single value from a JSON object based on a single this_path.

    :param json_object: The JSON object from which to extract the value.
    :param this_path: The this_path to the value as a list of keys/indexes.
    :return: The value at the specified this_path.
    """

    json_object_copy = json_object.copy()

    print("start: extract_string_value_by_path()")
    print(f"json_object -> {json_object}")
    print(f"this_path -> {this_path}")

    for step in this_path:
        json_object_copy = json_object_copy[step]

    return json_object_copy


def randomize_list(original_list):
    """
    index from one, produces
    randomized_list,
    original_to_randomized,
    randomized_to_original

    # Example usage
    original_list = [1, 2, 3, 4, 5]
    randomized_list, original_to_randomized, randomized_to_original = randomize_list(original_list)

    print("Original List:", original_list)
    print("Randomized List:", randomized_list)
    print("Original to Randomized Lookup Table:", original_to_randomized)
    print("Randomized to Original Lookup Table:", randomized_to_original)
    """
    # Create a copy of the original list
    randomized_list = original_list[:]

    # Shuffle the list in-place
    random.shuffle(randomized_list)

    # Create lookup tables
    original_to_randomized = {}
    randomized_to_original = {}

    for i, item in enumerate(original_list, start=1):
        original_to_randomized[i] = randomized_list.index(item) + 1
        randomized_to_original[randomized_list.index(item) + 1] = i

    return randomized_list, original_to_randomized, randomized_to_original


def lower_clean_string(input_string):
    """
    Cleans the input string by converting it to lowercase, removing spaces,
    and stripping all punctuation.

    Parameters:
    - input_string (str): The string to be cleaned.

    Returns:
    - str: The cleaned string.

    elif isinstance(new_value_or_list, list):
        for this_new_value in new_value_or_list:
    """

    # Convert to lowercase
    lowercased = input_string.lower()
    # Remove punctuation
    no_punctuation = lowercased.translate(str.maketrans("", "", string.punctuation))
    # Remove spaces
    cleaned_string = no_punctuation.replace(" ", "")

    return cleaned_string


def lower_clean_string_or_list(input_string_or_list):
    """
    Cleans the input string by converting it to lowercase, removing spaces,
    and stripping all punctuation.

    Parameters:
    - input_string_or_list (str): The string to be cleaned.

    Returns:
    - str: The cleaned string.

    elif isinstance(new_value_or_list, list):
        for this_new_value in new_value_or_list:
    """
    print(
        f"Starting lower_clean_string_or_list(input_string_or_list), input_string_or_list -> {input_string_or_list}"
    )

    if isinstance(input_string_or_list, str):
        cleaned_string_or_list = lower_clean_string(input_string_or_list)
        return cleaned_string_or_list

    elif isinstance(input_string_or_list, list):
        cleaned_string_or_list = []

        # iterate and append
        for this_here_string in input_string_or_list:

            # clean
            cleaned_string = lower_clean_string(this_here_string)

            cleaned_string_or_list.append(cleaned_string)
        return cleaned_string_or_list

    else:
        print(
            f"Warning: lower_clean_string_or_list() input not string or list input_string_or_list -> {type(input_string_or_list)}{input_string_or_list}"
        )

        return input_string_or_list


def clean_extract_string_value_by_path(json_object, this_path):
    """
    Extracts a single value from a JSON object based on a single this_path.

    :param json_object: The JSON object from which to extract the value.
    :param this_path: The this_path to the value as a list of keys/indexes.
    :return: The value at the specified this_path.
    """
    json_object_copy = json_object.copy()

    print("start: clean_extract_string_value_by_path()")
    print(f"json_object -> {json_object}")
    print(f"this_path -> {this_path}")

    for step in this_path:
        json_object_copy = json_object_copy[step]
        json_object_copy = lower_clean_string_or_list(json_object_copy)
    return json_object_copy


def insert_int_value_by_path(target_dictionary, this_path, translated_value):
    """
    Alters dictionary in place

    I really don't like this code.
    """
    target = target_dictionary
    for step in this_path[:-1]:  # Navigate through the path except for the last step
        step = int(step) if step.isdigit() else step
        target = target[step]
    final_step = this_path[-1]
    final_step = int(final_step) if final_step.isdigit() else final_step
    target[final_step] = translated_value


def core_insert_string_value_by_path(json_structure, path, new_value):
    """
    Attempts to append a value to a list at the specified path within the json_structure.
    Provides more detailed error messages if the path is not found.

    :param json_structure: The JSON structure to update.
    :param path: The path to the target list as a list of keys.
    :param new_value: The value to append.
    """
    target = json_structure
    for i, step in enumerate(path):
        try:
            if isinstance(target, dict) and step in target:
                if i == len(path) - 1:  # If it's the final step, append new_value
                    if isinstance(target[step], list):
                        target[step].append(new_value)
                    else:
                        raise ValueError(
                            f"Target at path {'/'.join(path)} is not a list."
                        )
                else:  # Not the final step, move deeper into the structure
                    target = target[step]
            else:
                print(f"Path error: {'/'.join(path[:i + 1])} not found.")
        except TypeError as e:
            print(f"TypeError accessing {'/'.join(path[:i])}: {str(e)}")

            # If for some reason the loop completes without appending (shouldn't happen if errors are caught)
            print(
                f"\n\n\nwarning: core_insert_string_value_by_path() no intput? new_value -> {new_value}  \n\n\n"
            )


def insert_string_value_by_path(dict_tree_structure, path, new_value_or_list):
    """
    wrapper for core_insert_string_value_by_path()

    accepts list of items
    or single string items

    checks to see if they are already in the dict (not working)

    if not,

    it add them.
    check if matches pre-translated

    todo:
    make sure the value does not already exist in destination list
    """

    print(
        f"start: insert_string_value_by_path() new_value_or_list -> {new_value_or_list}"
    )

    cleaned_newvalue_or_list = lower_clean_string_or_list(new_value_or_list)
    existing_item_list = clean_extract_string_value_by_path(dict_tree_structure, path)

    print(f"insert_string_value_by_path() existing_item_list -> {existing_item_list}, ")
    print(f"cleaned_newvalue_or_list->{cleaned_newvalue_or_list}")

    # Check if the value is a string

    if isinstance(new_value_or_list, str):
        new_value_or_list = [new_value_or_list]

    # Check if the value is a list
    if isinstance(new_value_or_list, list):
        for this_new_value in new_value_or_list:
            if lower_clean_string_or_list(this_new_value) not in existing_item_list:
                core_insert_string_value_by_path(
                    dict_tree_structure, path, this_new_value
                )
            else:
                print(
                    f"item overlap: {lower_clean_string_or_list(this_new_value)}{existing_item_list}"
                )

    else:
        print(f"warning: insert_string_value_by_path() no intput? {new_value_or_list}")


def replace_leaf_by_path(json_structure, path, new_value):
    """
    Replaces the value at the specified path within the json_structure with new_value.

    :param json_structure: The JSON structure (dictionary) to update.
    :param path: A list representing the path to the target leaf. Each element in the path
                 is a dictionary key or a list index.
    :param new_value: The new value to replace at the target leaf.
    """
    target = json_structure
    # Iterate through the path to find the target container (dict or list) for the new value
    for step in path[:-1]:  # Navigate through the path except for the last step
        if step.isdigit():  # Convert to int if the step is an index in a list
            step = int(step)
        target = target[step]

    final_step = path[-1]
    if final_step.isdigit():  # Convert the last step if it's an index
        final_step = int(final_step)

    # Replace the old value with the new value at the final step
    target[final_step] = new_value


"""# Main Function"""


def add_ranks_votes_to_candidate(vote_list, candidate_dictionary):
    """
    Adds each item from vote_list to the list in candidate_dictionary corresponding to the item's sequence position,
    where the sequence position is mapped to alphabetical keys ('a', 'b', 'c', etc.).

    :param vote_list: List of numbers to be added.
    :param candidate_dictionary: Dictionary with alphabetical keys representing sequence positions and values as lists.
    """
    # Create a list of keys from the dictionary to map index to keys
    keys = list(candidate_dictionary.keys())

    for index, value in enumerate(vote_list):
        # Ensure the index is within the this_range_inclusive of available keys
        if index < len(keys):
            # Append the item to the list for the corresponding key based on sequence position
            candidate_dictionary[keys[index]].append(value)
        else:
            # Optionally handle or log if the index exceeds the available keys
            print(f"No key available for index {index} in candidate_dictionary.")
            raise Exception("Index exceeds the number of keys in candidate_dictionary.")

    return candidate_dictionary


def extract_top_rank(list_dict_of_options):
    # # Assuming 'ranked_votes' is your dictionary where each key is an item and each value is a list of ranks
    # ranked_votes = {
    #     'item1': [1, 2, 3],
    #     'item2': [2, 1, 3],
    #     'item3': [3, 3, 1]
    # }
    print(f"extract_top_rank(), list_dict_of_options -> {list_dict_of_options}")

    # Calculate the sum of ranks for each item
    sum_of_ranks = {item: sum(ranks) for item, ranks in list_dict_of_options.items()}

    # Determine the item with the highest sum of ranks
    highest_ranked_item = max(sum_of_ranks, key=sum_of_ranks.get)

    return highest_ranked_item


def filter_list_convert_to_int(input_list):
    """
    Note: this needs to be able to fail without crashing and pass that on
    so a new translation can be retried.

    This also needs to be able to take in a list already as int
    and say, ok, pass those 'int's back out as ok.

    Takes a list of strings, removes any items that contain non-digit characters,
    and converts the remaining items to integers.

    :param input_list: List of strings to process.
    :return: A list of integers after filtering out non-digit strings and converting.
    """
    try:

        # Filter out non-digit strings and convert the rest to integers
        # result = [int(item) for item in input_list if item.isdigit()]
        result = [
            item if isinstance(item, int) else int(item)
            for item in input_list
            if isinstance(item, int) or item.isdigit()
        ]

        return result

    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return False


def mini_translate_json(
    list_of_targeted_languages,
    use_this_model,
    ai_local_or_cloud_mode,
    number_of_preliminary_translations,
    number_of_ranked_votes,
    parameter_dict=None,
):

    # set parameters to defaults if none are given
    if not parameter_dict:
        #######################
        # Tune Your Paramaters
        #######################
        parameter_dict = {
            "--temp": 0.8,  # (default value is 0.8)
            "--top-k": 40,  # (selection among N most probable. default: 40)
            "--top-p": 0.9,  # (probability above threshold P. default: 0.9)
            "--min-p": 0.05,  # (minimum probability threshold. default: 0.05)
            "--seed": -1,  # seed, =1 is random seed
            "--tfs": 1,  # (tail free sampling with parameter z. default: 1.0) 1.0 = disabled
            "--threads": 8,  # (~ set to number of physical CPU cores)
            "--typical": 1,  # (locally typical sampling with parameter p  typical (also like ~Temperature) (default: 1.0, 1.0 = disabled).
            "--mirostat": 2,  # (default: 0,  0= disabled, 1= Mirostat, 2= Mirostat 2.0)
            "--mirostat-lr": 0.05,  # (Mirostat learning rate, eta.  default: 0.1)
            "--mirostat-ent": 3.0,  # (Mirostat target entropy, tau.  default: 5.0)
            "--ctx-size": 500,  # Sets the size of the prompt context
        }

    ######################
    # Translation Factory
    ######################

    # json .... because focusing on json?
    json_files_list = list_files_in_aitaskfiles_dir(".json")

    if not json_files_list:
        print("Error: You missed a step, No Json files were provided.")
        raise "No Json files were provided."

    # inspection
    print("JSON files in the CWD:", json_files_list)

    for this_original_json_file in json_files_list:

        # Load the original JSON file
        original_data = load_json_file(this_original_json_file)

        # Create a new JSON file with the deep empty structure
        name_of_skeleton_saved_file = "empty_lists_" + "_" + this_original_json_file

        skeleton_json = create_empty_json_file(
            original_data, name_of_skeleton_saved_file
        )

        name_of_EMPTY_dict_of_selected_best_saved_file = (
            "empty_string_best_" + "_" + this_original_json_file
        )
        dict_of_selected_best = create_empty_selectbest_frame(
            original_data, name_of_EMPTY_dict_of_selected_best_saved_file
        )

        #########################################
        # Crawler: Make preliminary Translations
        #########################################

        paths_list = generate_paths(original_data)
        check_paths_list = generate_paths(skeleton_json)
        dict_of_selected_best_paths_list = generate_paths(dict_of_selected_best)

        print(
            f"""
        mini_translate_json()
        Starting this file: 
        this_original_json_file      -> {this_original_json_file}
        paths_list                   -> {paths_list}
        check_paths_list             -> {check_paths_list}
        dict_of_selected_best_paths_list -> {dict_of_selected_best_paths_list}
        """
        )

        # Sanity check
        if paths_list != dict_of_selected_best_paths_list:
            error_message = "Error: Path lists between the original JSON and its skeleton do not match."
            print(error_message)
            raise ValueError(error_message)

        # for this language
        for target_language in list_of_targeted_languages:

            # make a blank frame of lists for the translations
            # make a copy!
            populated_skeleton = skeleton_json.copy()
            print(f"\n\n\nInitial populated_skeleton -> {populated_skeleton}\n\n\n")

            # for this leaf
            for this_path in paths_list:

                leaf_ok_flag = False
                leaf_fail_counter = 0

                while not leaf_ok_flag:

                    if leaf_fail_counter > 10:
                        raise f"leaf_fail_counter > 10 -> {leaf_fail_counter}"

                    untranslated_leaf = extract_string_value_by_path(
                        original_data, this_path
                    )

                    # make empty conversation
                    # reset context history for new 'conversation' about translation
                    # context_history = f"translate '{untranslated_leaf}'' into {target_language} with the translation in pipes |||YOUR_TRANSLATION||| no other commentary needed, just a translation please"
                    # context_history = f"""
                    # translate only '{untranslated_leaf}'' into {target_language} with the translation formatted
                    # inside tripple pipes |||YOUR_TRANSLATION||| just that. no other commentary, no underscores _, not all caps.
                    # translate and earn a treat"""

                    context_history = f"""
                    translate only '{untranslated_leaf}' into {target_language} formatted 
                    inside tripple pipes |||your_translation||| just that. no other commentary,
                    translate and earn a treat: best translation is |||"""

                    # making N translation-versions
                    for i in range(number_of_preliminary_translations):
                        """
                        using both the populated skeleton and the original file:
                        - tree-search through both (original and blank-list-skeleton) in the same way
                        - check and guarantee that the dict-address (often nested)
                        is the same for the original and where the answers are recorded
                        - part 1: extract just the next terminal leaf, return this.
                        separate step next ->
                        - part 2: put a new (language translated value) in the corresponding
                        place in blank-skeleton list.
                        """
                        """
                        ####################
                        # Crawler functions
                        ####################

                        1. make list of paths   generate_paths(json_object)
                        2. extrac path value    extract_value_by_path(original_data, this_path)
                        (translate)
                        3. add to list          insert_string_value_by_path(json_structure, path, new_value)
                        4. write final value    insert_int_value_by_path(skeleton_json, paths_list, translated_values)

                        """

                        ############
                        # Translate
                        ############
                        translated_value = call_api_within_structure_check(
                            context_history,
                            use_this_model,
                            parameter_dict,
                            ai_local_or_cloud_mode,
                            skeleton_json,
                        )

                        # remove overt duplicates
                        # Convert list to set to remove duplicates
                        unique_set = set(translated_value)
                        # Convert set back to list
                        translated_value = list(unique_set)

                        # add-insert value to json
                        print(
                            f"populated_skeleton Before appending: {populated_skeleton}"
                        )
                        print(f"skeleton_json -> {skeleton_json}")
                        print(f"this_path -> {this_path}")
                        print(f"untranslated_leaf -> {untranslated_leaf}")
                        print("\n\nTRANSLATION:")
                        print(f"translated_value -> {translated_value}")

                        # adds to dict IF not already there:
                        insert_string_value_by_path(
                            populated_skeleton,
                            this_path,
                            translated_value,
                        )

                        print(
                            f"populated_skeleton After appending: {populated_skeleton}"
                        )

                    #####################################################
                    # Select Top Top Goodest Translation Star-Good-Prime
                    #####################################################
                    set_save_json_to_file(
                        populated_skeleton,
                        this_original_json_file,
                        target_language,
                        "set_of_translations_",
                    )

                    # reset context history for new 'conversation' about selection
                    context_history = []

                    print("\n\n\nSelect Top Top Goodest Translation Star-Good-Prime")

                    remove_duplicates_from_terminal_list(populated_skeleton, this_path)

                    # set prompts to select best translation
                    list_of_ranked_choice_options = extract_value_by_path(
                        populated_skeleton, this_path
                    )

                    # # Combine into one list of strings using list comprehension
                    # list_of_ranked_choice_options = [item for sublist in list_of_ranked_choice_options_nested for item in sublist]
                    # list_of_ranked_choice_options = list_of_ranked_choice_options_nested

                    # turn list of options int dict
                    dict_of_options = {
                        option: "score_here" for option in list_of_ranked_choice_options
                    }

                    # turn list of options int dict
                    list_dict_of_options = {
                        option: [] for option in list_of_ranked_choice_options
                    }

                    print(
                        f"""
                    mini_translate_json() Select Top Top
                    list_of_ranked_choice_options        -> {list_of_ranked_choice_options}
                    dict_of_options        -> {dict_of_options}
                    list_dict_of_options   -> {list_dict_of_options}
                    """
                    )

                    #######################
                    #######################
                    # System Instructions
                    #######################
                    #######################

                    # context_history = set_select_best__system_prompt(
                    #     context_history, target_language
                    # )
                    # # User Prompt
                    # context_history = set_select_best__user_prompt(
                    #     context_history, target_language, list_of_ranked_choice_options, untranslated_leaf
                    # )

                    # context_history = f"""
                    # Select the most accurate {target_language} translation for '{untranslated_leaf}' from these options: {list_of_ranked_choice_options}.
                    # Place your choice, spelled exactly the same, between triple pipes, like this: |||best_selection|||.
                    # No additional comments. A tasty reward awaits your accurate selection."""

                    # """
                    # Select the most accurate {target_language} translation for '{untranslated_leaf}' from these options: {list_of_ranked_choice_options}.
                    # Indicate your choice by placing it between triple pipes, like this: |||best_selection|||.
                    # No additional comments. The reward of a job well done awaits your accurate selection!"""

                    # context_history = f"""
                    # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {list_of_ranked_choice_options}.
                    # Place your evaluations in order as Pipe-Separated Values. like this four options |#|#|#|#| or just one item like this |#|
                    # No additional comments. A tasty reward awaits your accurate selection """

                    answer_form = {
                        "t-1": "score_here",
                        "t-2": "score_here",
                        "t-3": "score_here",
                    }

                    answer_form = {
                        "translation-1": "score_here",
                        "translation-2": "score_here",
                        "translation-3": "score_here",
                    }

                    # context_history = f"""
                    # Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {dict_of_options}.
                    # Place your evaluations as a value to the key in Json format. Return your markdown json object
                    # listing each translation only as t-number as:
                    # ```json
                    # {answer_form}
                    # ```
                    # No additional comments. A tasty reward awaits your accurate selection."""

                    # context_history = f"""
                    # Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {dict_of_options}.
                    # Place your evaluations as a value to the key in Json format. Return your markdown json object
                    # listing each translation only as t-number
                    # as:
                    # ```json
                    # {answer_form}
                    # ```
                    # One key-value pair per translation (one key, one value -> "translation-1": "score_here", not nested). No additional comments. A tasty reward awaits your accurate selection.
                    # """

                    context_history = f"""
                    Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {dict_of_options}. 
                    Place your evaluations as the value to a key in Json format. Return your markdown json object 
                    listing each translation only as t-number 
                    as: 
                    ```json 
                    {answer_form} 
                    ```
                    Just fill in the score, that's all. One key-value pair per translation (one generic key, one value which is your score -> "translation-1": "score_here", not nested). No additional comments. A tasty reward awaits your accurate selection.
                    """

                    context_history = f"""
                    Evaluate each {target_language} translation for '{untranslated_leaf}' from these options: {dict_of_options}. 
                    If the translation is not even in {target_language}, it should get a zero. 
                    Place your evaluations  (0-10, 0 is bad, 10 is good) as the value to a key in Json format. Return your markdown json object 
                    listing each translation only as "translation-number" 
                    as: 
                    ```json 
                    {answer_form} 
                    ```
                    Just fill in the score, that's all. One key-value pair per translation (one generic key, one value which is your score -> "translation-1": "score_here", not nested). 
                    No additional comments. A tasty reward awaits your accurate selection. 
                    """

                    # context_history = f"""
                    # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {dict_of_options}.
                    # Place your evaluations as value to the key in Json format. Return your properly formatted dict as:
                    # '''json

                    # '''

                    ###################
                    ###################
                    # Select Bestest
                    # By ranked choice
                    ###################
                    ###################

                    # turn list of options int dict
                    dict_of_options = {
                        option: None for option in list_of_ranked_choice_options
                    }
                    # get highest ranked item:
                    selected_option = None

                    while_counter = 0

                    for i in range(number_of_ranked_votes):

                        print(f"while_counter -> {while_counter}")

                        vote_check_ok = False

                        while not vote_check_ok:
                            """
                            TODO if a different function rank_vote_call_api_within_structure_check()
                            you should be able to filter everything except numbers out of the answer

                            also...
                            1. any complete duplicates can be filtered out...
                            2. any non-numbers filtered out
                            """
                            print(f"while_counter -> {while_counter}")
                            print("number_call_api_within_structure_check")

                            # get a list of votes and make sure it matches the list of candidates
                            list_of_votes = number_call_api_within_structure_check(
                                context_history,
                                use_this_model,
                                parameter_dict,
                                ai_local_or_cloud_mode,
                            )

                            print(f"\n\nlist_of_votes -> {list_of_votes}")
                            print(f"type list_of_votes -> {type(list_of_votes)}")

                            # filter out words and make type int
                            list_of_votes = filter_list_convert_to_int(list_of_votes)

                            print(f"list_of_votes -> {list_of_votes}")
                            print(
                                f"list_of_ranked_choice_options -> {list_of_ranked_choice_options}"
                            )
                            print(f"type list_of_votes -> {type(list_of_votes)}\n\n")

                            print(f"list_dict_of_options -> {list_dict_of_options}")

                            if list_of_votes:

                                # if there is one vote per candidate, list each candidates votes
                                if len(list_of_votes) == len(
                                    list_of_ranked_choice_options
                                ):
                                    add_ranks_votes_to_candidate(
                                        list_of_votes, list_dict_of_options
                                    )

                                    print(
                                        f"new list_dict_of_options -> {list_dict_of_options}"
                                    )

                                    # exit loop
                                    vote_check_ok = True

                                else:  # if len of list is wrong
                                    while_counter += 1
                                    print("len of list is wrong")

                            else:  # if no list at all!
                                while_counter += 1
                                print("no list at all!")

                    # tally the ranked votes and pick the winner
                    selected_option = extract_top_rank(list_dict_of_options)

                    print(f"selected_option -> {selected_option}")

                    # add value to json
                    insert_int_value_by_path(
                        dict_of_selected_best, this_path, selected_option
                    )

                    print(f"dict_of_selected_best -> {dict_of_selected_best}")

                    # Exit While
                    print("\nHats in the air, we can all leave. Buubye!!\n\n\n")
                    leaf_ok_flag = True

            ##########################
            # per language: save file
            ##########################
            print("trying to save file...")

            # try:
            #     # if test fails
            #     if dict_leaf_detection_boolean_true_means_defective(dict_of_selected_best):
            #         return False

            # except Exception as e:
            traceback.print_exc()
            #     print(f"\nTRY AGAIN: dict_leaf_detection_boolean_true_means_defective() empty or stub leaf found: {e}")
            #     print(f"Failed dict_str -> {dict_of_selected_best}")
            #     return False

            # add value to json
            save_json_to_file(
                dict_of_selected_best,
                this_original_json_file,
                target_language,
                "selected_",
            )


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
        traceback.print_exc()
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
        traceback.print_exc()
        print(f"An error occurred: {str(e)}")


def do_task_please(
    list_of_models,
    ai_local_or_cloud_mode,
    number_of_preliminary_drafts,
    retry_x_times,
    number_of_ranked_votes,
    task_mode_configies,
    task_file_config_dic_list,
    parameter_dict=None,
    models_dir_path="jan/models",
):
    """
    Output format notes:

    "solution":
        {
            "solution_plan_outline":
            "draft_revisions_and_comments":
            "final_answer":
        }



    mode options 1:
    open, single, choice

    mode options 2:
    context, instruction, simple

    task_mode_configies = {
        "answer_option_choices_provided" = True,
        "validate_the_answer" = True,
        "use_history_context_dict_list" = False,
        "system_instructions" = False,
        # "LMQL": False,
    }

    """
    print_find_all_models(models_dir_path)

    # task mode items:
    task_mode_answer_option_choices_provided_boolean = task_mode_configies[
        "answer_option_choices_provided"
    ]
    task_mode_validate_the_answer = task_mode_configies["validate_the_answer"]
    task_mode_use_history_context_dict_list = task_mode_configies[
        "use_history_context_dict_list"
    ]
    task_mode_system_instructions = task_mode_configies["system_instructions"]
    task_mode_input_state_context_mode = task_mode_configies["input_state_context_mode"]
    task_mode_output_structure_mode = task_mode_configies["output_structure_mode"]
    task_mode_ranked_choice_output_structure_mode = task_mode_configies[
        "ranked_choice_output_structure_mode"
    ]

    # set parameters to defaults if none are given
    if not parameter_dict:
        #######################
        # Tune Your Paramaters
        #######################
        parameter_dict = {
            "--temp": 0.8,  # (default value is 0.8)
            "--top-k": 40,  # (selection among N most probable. default: 40)
            "--top-p": 0.9,  # (probability above threshold P. default: 0.9)
            "--min-p": 0.05,  # (minimum probability threshold. default: 0.05)
            "--seed": -1,  # seed, =1 is random seed
            "--tfs": 1,  # (tail free sampling with parameter z. default: 1.0) 1.0 = disabled
            "--threads": 8,  # (~ set to number of physical CPU cores)
            "--typical": 1,  # (locally typical sampling with parameter p  typical (also like ~Temperature) (default: 1.0, 1.0 = disabled).
            "--mirostat": 2,  # (default: 0,  0= disabled, 1= Mirostat, 2= Mirostat 2.0)
            "--mirostat-lr": 0.05,  # (Mirostat learning rate, eta.  default: 0.1)
            "--mirostat-ent": 3.0,  # (Mirostat target entropy, tau.  default: 5.0)
            "--ctx-size": 500,  # Sets the size of the prompt context
        }

    ##################################
    # do_task_please Factory
    ##################################
    """
    Maybe modified to only look at each question one at a time.
    e.g. no overall multi-item dictionary

    but still a dict or list of possible answers
    to rank later.

    how to manage...writing answer each time to file....

    maybe keep a list of optional answers 
    then for each question write answer to
    the answer_(original_name)_model_name_timestamp)_file 
    """

    file_type_list = [".jsonl", ".csv"]

    # Example usage
    task_files_list = list_files_in_aitaskfiles_dir(file_type_list)

    if not task_files_list:
        print("Error: You missed a step, No task files were provided.")
        raise "No task files were provided."

    # inspection
    print(f"\nTask set files in folder -> {task_files_list}")

    #############################
    # iterate task-set by config
    #############################
    for this_task_config_dict in task_file_config_dic_list:

        # unpack task_file_config_dic_list
        file_name = this_task_config_dict["file_name"]
        # file_type = this_task_config_dict["file_type"]
        # file_structure = this_task_config_dict["file_structure"]
        task_field_name = this_task_config_dict["task_field_name"]
        # index_of_task = this_task_config_dict["index_of_task"]
        # index_of_options = this_task_config_dict["index_of_options"]
        options_field_name = this_task_config_dict["options_field_name"]
        scoring_field_name = this_task_config_dict["scoring_field_name"]

        if "function_name__field_name" in this_task_config_dict:
            function_name__field_name = this_task_config_dict[
                "function_name__field_name"
            ]
            print(f"function_name__field_name -> {function_name__field_name}")
        else:
            function_name__field_name = None

        if "function_test_cases__field_name" in this_task_config_dict:
            function_test_cases__field_name = this_task_config_dict[
                "function_test_cases__field_name"
            ]
            print(
                f"function_test_cases__field_name -> {function_test_cases__field_name}"
            )
        else:
            function_test_cases__field_name = None

        if "error_comment_data_lookup_table_field_name" in this_task_config_dict:
            error_comment_data_lookup_table_field_name = this_task_config_dict[
                "error_comment_data_lookup_table_field_name"
            ]
        else:
            error_comment_data_lookup_table_field_name = None

        if "randomize_option_choices" in this_task_config_dict:
            randomize_option_choices = this_task_config_dict["randomize_option_choices"]
        else:
            randomize_option_choices = False

        if "function_writing" in this_task_config_dict:
            function_writing = this_task_config_dict["function_writing"]
        else:
            function_writing = False

        this_offset = this_task_config_dict["this_offset"]
        this_range_inclusive = this_task_config_dict["this_range_inclusive"]
        use_offset_and_range = this_task_config_dict["use_offset_and_range"]

        """
        Over-ride!
        If the file config file has extra instructions, overide the defaults.
        """
        if "output_structure_mode" in this_task_config_dict:
            task_mode_output_structure_mode = this_task_config_dict[
                "output_structure_mode"
            ]

        if "input_state_context_mode" in this_task_config_dict:
            task_mode_input_state_context_mode = this_task_config_dict[
                "input_state_context_mode"
            ]

        if "ranked_choice_output_structure_mode" in this_task_config_dict:
            task_mode_ranked_choice_output_structure_mode = this_task_config_dict[
                "ranked_choice_output_structure_mode"
            ]

        if "answer_option_choices_provided" in this_task_config_dict:
            task_mode_answer_option_choices_provided_boolean = this_task_config_dict[
                "answer_option_choices_provided"
            ]

        if "validate_the_answer" in this_task_config_dict:
            task_mode_validate_the_answer = this_task_config_dict["validate_the_answer"]

        if "use_history_context_dict_list" in this_task_config_dict:
            task_mode_use_history_context_dict_list = this_task_config_dict[
                "use_history_context_dict_list"
            ]

        if "system_instructions" in this_task_config_dict:
            task_mode_system_instructions = this_task_config_dict["system_instructions"]

        this_original_task_file = find_matching_file_paths(task_files_list, file_name)

        print(
            f"\n\n\n Now starting this_original_task_file -> {this_original_task_file}"
        )

        ############
        # For Model
        ############
        for use_this_model in list_of_models:
            ###
            # Make answers file pathway.
            ###
            task_set_results_path = make_answers_directory_and_csv_path_header_string(
                this_original_task_file, use_this_model
            )

            print(f"task_set_results_path -> {task_set_results_path}")

            ########################
            # Iterate through tasks
            ########################

            print(
                f"""
                do_task_please()
                Starting this file: 
                this_original_task_file      -> {this_original_task_file}
                """
            )

            """
            To stay lite:
            - get the number of rows in the csv
            - for each row, access that row only
            (note...a csv might be a little mega huge)
            https://colab.research.google.com/drive/1lVtU6RErVic3-LrL085eFNgkRirzfnUk#scrollTo=KXWL8qptpfRJ 
            """

            # if csv
            if ".csv" == get_file_extension(this_original_task_file):
                this_original_task_file_length = get_csv_len_in_rows(
                    this_original_task_file
                )

            # if jsonl
            if ".jsonl" == get_file_extension(this_original_task_file):
                this_original_task_file_length = count_jsonl_lines(
                    this_original_task_file
                )

            # TODO
            # if directory of json files
            print(f"this_original_task_file_length -> {this_original_task_file_length}")

            # offset and range (note: dont' redefine "range" as a saved-word)
            if use_offset_and_range:

                if isinstance(this_offset, int) and isinstance(
                    this_range_inclusive, int
                ):
                    print("this_offset and this_range_inclusive found")
                    start = this_offset
                    stop = min(
                        this_offset + this_range_inclusive,
                        this_original_task_file_length,
                    )

            else:
                print("NO this_offset and this_range_inclusive found")
                start = 0

                # set -1 because len is from 1, but index is from 0
                stop = this_original_task_file_length - 1

            ############################
            ############################
            # For this task in task-set
            #  within this_offset and this_range_inclusive
            ############################
            ############################
            print(f"start -> {this_offset} {type(this_offset)}")
            print(f"start -> {this_range_inclusive} {type(this_range_inclusive)}")
            print(
                f"this_original_task_file_length -> {this_original_task_file_length} {type(this_original_task_file_length)}"
            )
            print(f"start -> {start} {type(start)}")
            print(f"stop -> {stop} {type(stop)}")

            for this_row_or_line_number in range(start, stop + 1):

                # set start time
                start_time_whole_single_task = datetime.now(UTC)

                # start/reset error log
                error_log = []

                # the length of this list is the goal
                retry_or_error_event_counter_list = []

                draft_task_attempt_log = []

                print(f"this_row_or_line_number -> {this_row_or_line_number}")

                """
                get task from file
                """
                task_ok_flag = False
                task_fail_counter = 0

                dotask_try_counter = 0

                while (not task_ok_flag) and (dotask_try_counter <= retry_x_times):

                    if task_fail_counter > 10:
                        print(
                            f"break while: task_fail_counter > 10 -> {task_fail_counter}"
                        )
                        break

                    """
                    TODO
                    Handling headers...
                    (setting?)

                    process csv assuming
                    this row = index

                    question is first item
                    string of options is second

                    "What is 2+2?", [4, 2^2, 2**2, 2*2, all of the above]
                    """
                    # row_as_list = extract_row_from_csv(this_row_or_line_number, this_original_task_file)
                    """
                    jsonl mode

                    task_field_name
                    options_field_name

                    """

                    # Specify the line number from which to extract the JSON object (e.g., line 2)
                    # this_row_or_line_number  # Remember, it's zero-indexed

                    # Specify the fields you're interested in extracting from the JSON object
                    fields_of_interest = [
                        task_field_name,
                        options_field_name,
                        scoring_field_name,
                        error_comment_data_lookup_table_field_name,
                        function_test_cases__field_name,
                        function_name__field_name,
                        "programming_language",
                    ]

                    # Step 1: Extract the JSON object from the specified line
                    json_object = extract_object_by_line_number(
                        this_original_task_file, this_row_or_line_number
                    )

                    # Check if the json_object is not None to avoid errors in the next step
                    if json_object is not None:
                        # Step 2: Extract only the specified fields from the JSON object
                        specific_fields = extract_specific_fields(
                            json_object, fields_of_interest
                        )
                        print(
                            "\nspecific_fields[] -> Extracted Fields:", specific_fields
                        )
                    else:
                        print(
                            "\nExit here, stop waiting for Godot. No JSON object found at the specified line."
                        )
                        task_ok_flag = True
                        break

                    #################
                    # Task et Option
                    #################
                    """
                    """
                    this_task = specific_fields[task_field_name]

                    if error_comment_data_lookup_table_field_name:
                        error_comment_data_lookup_table = specific_fields[
                            error_comment_data_lookup_table_field_name
                        ]
                    else:
                        error_comment_data_lookup_table = None

                    if "options" in specific_fields:
                        these_original_task_options = specific_fields[
                            options_field_name
                        ]
                    else:
                        these_original_task_options = None

                    # correct option and scoring

                    if scoring_field_name in specific_fields:
                        correct_option = specific_fields[scoring_field_name]
                        print(f"correct_option -> {correct_option}")
                    elif function_writing:
                        correct_option = "pass"
                    else:
                        correct_option = None

                    if these_original_task_options:
                        task_summary = f"Task: {this_task}, Options: {pretty_print_list(these_original_task_options)}"
                    else:
                        task_summary = f"Task: {this_task}"

                    print(f"this_task -> {this_task}")
                    print(
                        f"these_original_task_options -> {these_original_task_options}"
                    )
                    print(f"task_summary -> {task_summary}")

                    # code
                    if function_test_cases__field_name in specific_fields:
                        test_cases = specific_fields[function_test_cases__field_name]
                        print(f"test_cases -> {test_cases}{type(test_cases)}")
                    else:
                        test_cases = None

                    if function_name__field_name:
                        function_name = specific_fields[function_name__field_name]
                        print(f"function_name -> {function_name}{type(function_name)}")
                    else:
                        function_name = None

                    
                    # programming_language for code test
                    if 'programming_language' in specific_fields:
                        programming_language = specific_fields['programming_language']
                        print(f"test_cases -> {test_cases}{type(test_cases)}")
                    else:
                        programming_language = None


                    ##############################
                    ##############################
                    # option choice randomization
                    ##############################
                    ##############################

                    # setting default values
                    displayed_option_choices = []
                    randomized_option_list = []
                    original_to_randomized_lookup = {}
                    randomized_to_original_lookup = {}

                    # if there are options and you want to randomize them
                    if (
                        randomize_option_choices is True
                    ) and these_original_task_options:
                        print("\nRandomizing Task Option Choices")

                        (
                            randomized_option_list,
                            original_to_randomized_lookup,
                            randomized_to_original_lookup,
                        ) = randomize_list(these_original_task_options)

                        displayed_option_choices = randomized_option_list

                        print(
                            f"""

                            these_original_task_options   -> {these_original_task_options}
                            randomized_option_list        -> {randomized_option_list}

                            original_to_randomized_lookup -> {original_to_randomized_lookup}
                            randomized_to_original_lookup -> {randomized_to_original_lookup}

                            """
                        )

                    else:
                        displayed_option_choices = these_original_task_options

                    # make empty conversation
                    # reset context history for new 'conversation' about translation
                    # context_history = f"translate '{untranslated_task}'' into {target_language} with the translation in pipes |||YOUR_TRANSLATION||| no other commentary needed, just a translation please"
                    # context_history = f"""
                    # translate only '{untranslated_task}'' into {target_language} with the translation formatted
                    # inside tripple pipes |||YOUR_TRANSLATION||| just that. no other commentary, no underscores _, not all caps.
                    # translate and earn a treat"""

                    # context_history = f"""
                    # translate only '{untranslated_task}' into {target_language} formatted
                    # inside tripple pipes |||your_translation||| just that. no other commentary,
                    # translate and earn a treat: best translation is """

                    """
                    Option: 

                    dict_multiple_choice_solution_body_context 
                    pipes_multiple_choice_solution_body_context 

                    dict_multiple_choice_solution_body_nocontext 
                    pipes_multiple_choice_solution_body_nocontext 

                    dict_open_solution_body_context 
                    pipes_open_solution_body_context 

                    dict_open_solution_body_nocontext 
                    pipes_open_solution_body_nocontext 

                    output_structure_mode: "dict" or "pipe" 
                    input_state_context_mode: "context_dict_list" or "one_string" 
                    """

                    # alt_dict_multiple_choice_solution_body_nocontext = {
                    #     "solution":
                    #     {
                    #         "solution_plan_outline": "",
                    #         "draft_revisions_and_comments": "",
                    #         "final_answer_option_number": int,
                    #     }
                    # }

                    pipes_open_solution_body_nocontext = """
                    Plan, draft, revisions, and comments, 
                    then in triple pipes: 
                    |||final answer||| 
                    """

                    dict_open_solution_body_nocontext = {
                        "solution": {
                            "solution_plan_outline": "",
                            "draft_revisions_and_comments": "",
                            "final_answer": "",
                        }
                    }

                    pipes_multiple_choice_solution_body_nocontext = """
                    solution_plan_outline: ...(YOUR PLAN), 
                    draft_revisions_and_comments: ...(YOUR COMMENTS), 
                    Then in triple pipes, the final answer option number: |||number|||
                    """

                    dict_multiple_choice_solution_body_nocontext = {
                        "solution_plan_outline": "",
                        "draft_revisions_and_comments": "",
                        "final_answer_option_number": int,
                    }

                    # inspection
                    print(
                        f"""
                    task mode items:
                    task_mode_answer_option_choices_provided_boolean -> {task_mode_answer_option_choices_provided_boolean}
                    task_mode_validate_the_answer -> {task_mode_validate_the_answer}
                    task_mode_use_history_context_dict_list -> {task_mode_use_history_context_dict_list}
                    task_mode_system_instructions -> {task_mode_system_instructions}
                    task_mode_output_structure_mode -> {task_mode_output_structure_mode}
                    task_mode_input_state_context_mode -> {task_mode_input_state_context_mode}
                    task_mode_ranked_choice_output_structure_mode -> {task_mode_ranked_choice_output_structure_mode}

                    """
                    )

                    ######################
                    ######################
                    # not multiple-choice
                    ######################
                    ######################
                    # if the question is not multiple-choice
                    if not task_mode_answer_option_choices_provided_boolean:
                        """
                        2^3 == 8

                        context:
                            dict:
                                dict_open_solution_body_context

                            pipes:
                                pipes_open_solution_body_context

                        no-context:
                            dict_open_solution_body_nocontext
                            pipes_open_solution_body_nocontext
                        """

                        if function_writing:
                            ############
                            # Pipes |||
                            ############
                            if task_mode_output_structure_mode == "markdown":
                                ############
                                # Open Task: use context dict list
                                ############
                                context_history = f"""

                                    {this_task}

                                    Put your {programming_language} code in markdown format (three pips)
                                    without hard-coding any answers into the function.

                                    Write any other comments or plans before you write the function 
                                    and outside of the {programming_language} markdown.
                                    """

                            else:
                                print(
                                    f"""not multiple-choice exit: prompt selection 1: option problem task_mode_output_structure_mode {task_mode_output_structure_mode}"""
                                )
                                sys.exit()

                        #############
                        # if context
                        #############
                        elif task_mode_use_history_context_dict_list:
                            # TODO: make context dict list maker

                            ############
                            # Pipes |||
                            ############
                            if task_mode_output_structure_mode == "pipes":
                                ############
                                # Open Task: use context dict list
                                ############
                                context_history = f"""

                                What is the best response for this task? 
                                {this_task}

                                Give your answer in this format:
                                {pipes_open_solution_body_nocontext}

                                """

                            ##############
                            # {dict: ...}
                            ##############
                            elif task_mode_output_structure_mode == "dict":
                                ############
                                # Open Task: use context dict list
                                ############
                                context_history = f"""

                                What is the best response for this task? 
                                {this_task}

                                Give your answer in this format:
                                {dict_open_solution_body_nocontext}

                                """
                            else:
                                print(
                                    f"""not function not multiple-choice exit: prompt selection 1: option problem task_mode_output_structure_mode {task_mode_output_structure_mode}"""
                                )
                                sys.exit()

                        ################
                        # if NO context
                        ################
                        elif not task_mode_use_history_context_dict_list:

                            ############
                            # Pipes |||
                            ############
                            if task_mode_output_structure_mode == "pipes":
                                ############
                                # Open Task: use context dict list
                                ############
                                context_history = f"""

                                What is the best response for this task? 
                                {this_task}

                                Give your answer in this format:
                                {pipes_open_solution_body_nocontext}

                                """

                            ##############
                            # {dict: ...}
                            ##############
                            elif task_mode_output_structure_mode == "dict":
                                ############
                                # Open Task: use context dict list
                                ############
                                context_history = f"""

                                What is the best response for this task? 
                                {this_task}

                                Give your answer in this format:
                                {dict_open_solution_body_nocontext}

                                """
                            else:
                                print(
                                    f""" exit: prompt selection 1: option problem task_mode_output_structure_mode {task_mode_output_structure_mode}"""
                                )
                                sys.exit()

                    ##################
                    ##################
                    # multiple choice
                    ##################
                    ##################
                    # elif "multiple_choice":
                    if task_mode_answer_option_choices_provided_boolean is True:
                        """
                        dict_multiple_choice_solution_body_context
                        pipes_multiple_choice_solution_body_context

                        dict_multiple_choice_solution_body_nocontext
                        pipes_multiple_choice_solution_body_nocontext
                        """

                        """
                        Your answer must be the number of the option in the order given. "1" is the first option. 

                        """

                        #############
                        # if context
                        #############
                        if task_mode_use_history_context_dict_list:
                            # TODO: make context dict list maker

                            ############
                            # Pipes |||
                            ############
                            if task_mode_output_structure_mode == "pipes":

                                context_history = f"""
                                Which is the best option?

                                For this task: 
                                {this_task} 

                                From this list of options: 
                                {pretty_print_list(displayed_option_choices)} 

                                Your answer must be the number of the option in the order given. "1" is the first option. 

                                Give your answer in this format: 
                                {pipes_multiple_choice_solution_body_nocontext}
                                    """

                            ##############
                            # {dict: ...}
                            ##############
                            elif task_mode_output_structure_mode == "dict":

                                ##################
                                # Multiple Choice one string prompt (no context dict list)
                                ##################
                                context_history = f"""

                                Which is the best option?

                                For this task: 
                                {this_task} 

                                From this list of options: 
                                {pretty_print_list(displayed_option_choices)} 

                                Your answer must be the number of the option in the order given. "1" is the first option. 

                                Give your answer in this format: 
                                {dict_multiple_choice_solution_body_nocontext}
                                """

                            else:
                                print(
                                    f""" multiple choice if context exit: prompt selection 1: option problem task_mode_output_structure_mode {task_mode_output_structure_mode}"""
                                )
                                sys.exit()

                        ################
                        # if NO context
                        ################
                        if not task_mode_use_history_context_dict_list:

                            ############
                            # Pipes |||
                            ############
                            if task_mode_output_structure_mode == "pipes":
                                ##################
                                # Multiple Choice: use context dict list
                                ##################
                                context_history = f"""
                                Which is the best option?

                                For this task: 
                                {this_task} 

                                From this list of options: 
                                {pretty_print_list(displayed_option_choices)} 

                                Your answer must be the number of the option in the order given. "1" is the first option. 

                                Give your answer in this format: 
                                {pipes_multiple_choice_solution_body_nocontext}
                                """

                            ##############
                            # {dict: ...}
                            ##############
                            elif task_mode_output_structure_mode == "dict":

                                ##################
                                # Multiple Choice one string prompt (no context dict list)
                                ##################
                                context_history = f"""

                                Which is the best option?

                                For this task: 
                                {this_task} 

                                From this list of options: 
                                {pretty_print_list(displayed_option_choices)} 

                                Your answer must be the number of the option in the order given. "1" is the first option. 

                                Give your answer in this format: 
                                {dict_multiple_choice_solution_body_nocontext}
                                """

                            else:
                                print(
                                    f""" multiple choice if NO context, exit: prompt selection 1: option problem task_mode_output_structure_mode {task_mode_output_structure_mode}"""
                                )
                                sys.exit()

                    print(f"context_history -> {context_history}")

                    old_history = context_history

                    list_of_ranked_choice_options = []

                    # making N translation-versions
                    for i in range(number_of_preliminary_drafts):
                        """
                        using both the populated skeleton and the original file:
                        - tree-search through both (original and blank-list-skeleton) in the same way
                        - check and guarantee that the dict-address (often nested)
                        is the same for the original and where the answers are recorded
                        - part 1: extract just the next terminal task, return this.
                        separate step next ->
                        - part 2: put a new (language translated value) in the corresponding
                        place in blank-skeleton list.
                        """
                        """
                        ####################
                        # Crawler functions
                        ####################

                        1. make list of paths   generate_paths(json_object)
                        2. extrac path value    extract_value_by_path(original_data, this_path)
                        (translate)
                        3. add to list          insert_string_value_by_path(json_structure, path, new_value)
                        4. write final value    insert_int_value_by_path(skeleton_json, paths_list, translated_values)

                        """

                        ##########
                        # Do Task
                        ##########
                        """
                        Set the structured_output_format:
                        """

                        task_response_string = (
                            general_task_call_api_within_structure_check(
                                context_history,
                                use_this_model,
                                parameter_dict,
                                ai_local_or_cloud_mode,
                                task_mode_answer_option_choices_provided_boolean,
                                task_mode_output_structure_mode,
                                draft_task_attempt_log,
                                retry_x_times,
                                these_original_task_options,
                                this_task_config_dict,
                                retry_or_error_event_counter_list,
                                error_log,
                                test_cases,
                                function_name,
                                programming_language,
                            )
                        )

                        # # remove overt duplicates
                        # # Convert list to set to remove duplicates
                        # unique_set = set(task_response_string)
                        # # Convert set back to list
                        # task_response_string = list(unique_set)

                        print(f"task_response_string -> {task_response_string}")
                        print(
                            f"type task_response_string -> {type(task_response_string)}"
                        )

                        # if NOT using a list of numbered options, string ok!
                        if task_mode_answer_option_choices_provided_boolean:
                            task_response_string = str_to_int_or_none(
                                task_response_string
                            )
                            print("str_to_int_or_none(task_response_string)")
                            print(f"new task_response_string -> {task_response_string}")

                        if task_response_string:

                            if task_mode_answer_option_choices_provided_boolean:
                                list_of_ranked_choice_options.append(
                                    int(task_response_string)
                                )
                                print("appended int")

                            else:
                                list_of_ranked_choice_options.append(
                                    str(task_response_string)
                                )
                                print("appended string")

                        print(
                            f"list_of_ranked_choice_options -> {list_of_ranked_choice_options}"
                        )

                        if function_writing and (task_response_string == "pass"):
                            print("Pass: Made function, ok to move on.")
                            break

                    #####################################################
                    ########################################################
                    ###########################################################
                    # Select Top Top Goodest Rankified Chooose Star-Good-Prime
                    ###########################################################
                    ########################################################
                    #####################################################

                    # reset context history for new 'conversation' about selection
                    context_history = []
                    question_task_prompt = old_history
                    date_time = datetime.now(UTC)
                    readable_timestamp = date_time.strftime("ymd_%Y-%m-%d")

                    print("\n\n\nSelect Top Top Goodest Star-Good-Prime")

                    if list_of_ranked_choice_options:

                        print(
                            f"list_of_ranked_choice_options -> {list_of_ranked_choice_options}"
                        )
                        print(
                            f"len(list_of_ranked_choice_options) -> {len(list_of_ranked_choice_options)}"
                        )

                        set_ist_of_options = set(list_of_ranked_choice_options)
                        list_of_ranked_choice_options = list(set_ist_of_options)

                        print("After removing duplicates:")
                        print(
                            f"list_of_ranked_choice_options -> {list_of_ranked_choice_options}"
                        )
                        print(
                            f"len(list_of_ranked_choice_options) -> {len(list_of_ranked_choice_options)}"
                        )

                        if len(list_of_ranked_choice_options) > 1:

                            # Combine into one list of strings using list comprehension
                            set_list_of_ranked_choice_options = set(
                                list_of_ranked_choice_options
                            )
                            list_of_ranked_choice_options = list(
                                set_list_of_ranked_choice_options
                            )

                            # turn list of options int dict
                            dict_of_options = {
                                option: "score_here"
                                for option in list_of_ranked_choice_options
                            }

                            # turn list of options int dict
                            list_dict_of_options = {
                                option: [] for option in list_of_ranked_choice_options
                            }

                            print(
                                f"""
                            do_task_please() Select Top Top
                            list_of_ranked_choice_options        -> {list_of_ranked_choice_options}
                            dict_of_options        -> {dict_of_options}
                            list_dict_of_options   -> {list_dict_of_options}
                            """
                            )

                            #######################
                            #######################
                            # System Instructions
                            #######################
                            #######################

                            """
                            read task_from_instructions

                            """

                            # context_history = set_select_best__system_prompt(
                            #     context_history, target_language
                            # )
                            # # User Prompt
                            # context_history = set_select_best__user_prompt(
                            #     context_history, target_language, list_of_ranked_choice_options, untranslated_task
                            # )

                            # context_history = f"""
                            # Select the most accurate {target_language} translation for '{untranslated_task}' from these options: {list_of_ranked_choice_options}.
                            # Place your choice, spelled exactly the same, between triple pipes, like this: |||best_selection|||.
                            # No additional comments. A tasty reward awaits your accurate selection."""

                            # """
                            # Select the most accurate {target_language} translation for '{untranslated_task}' from these options: {list_of_ranked_choice_options}.
                            # Indicate your choice by placing it between triple pipes, like this: |||best_selection|||.
                            # No additional comments. The reward of a job well done awaits your accurate selection!"""

                            # context_history = f"""
                            # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {list_of_ranked_choice_options}.
                            # Place your evaluations in order as Pipe-Separated Values. like this four options |#|#|#|#| or just one item like this |#|
                            # No additional comments. A tasty reward awaits your accurate selection """

                            # context_history = f"""
                            # Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {dict_of_options}.
                            # Place your evaluations as a value to the key in Json format. Return your markdown json object
                            # listing each translation only as t-number as:
                            # ```json
                            # {answer_form}
                            # ```
                            # No additional comments. A tasty reward awaits your accurate selection."""

                            # context_history = f"""
                            # Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {dict_of_options}.
                            # Place your evaluations as a value to the key in Json format. Return your markdown json object
                            # listing each translation only as t-number
                            # as:
                            # ```json
                            # {answer_form}
                            # ```
                            # One key-value pair per translation (one key, one value -> "translation-1": "score_here", not nested). No additional comments. A tasty reward awaits your accurate selection.
                            # """

                            # context_history = f"""
                            # Evaluate (0-10, 0 is terrible, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {dict_of_options}.
                            # Place your evaluations as the value to a key in Json format. Return your markdown json object
                            # listing each translation only as t-number
                            # as:
                            # ```json
                            # {answer_form}
                            # ```
                            # Just fill in the score, that's all. One key-value pair per translation (one generic key, one value which is your score -> "translation-1": "score_here", not nested). No additional comments. A tasty reward awaits your accurate selection.
                            # """

                            # context_history = f"""
                            # Evaluate each solution for this task'{task_summary}' from these options: {pretty_print_list(dict_of_options)}.
                            # Place your evaluations  (0-10, 0 is bad, 10 is good) as the value to a key in Json format. Return your markdown json object
                            # listing each option only as "option-number"
                            # as:
                            # ```json
                            # {answer_form}
                            # ```
                            # Just fill in the score, that's all. One key-value pair per option, not nested.
                            # No additional comments. A tasty reward awaits your accurate markdown json selection. ``json
                            # """

                            # context_history = f"""
                            # Evaluate each solution option for the task '{task_summary}'. Evaluate these options: {pretty_print_list(dict_of_options)}.
                            # Place your evaluations  (0-10, 0 is bad, 10 is good) as the value to a key in markdown ```json format.
                            # as:
                            # ```json
                            # {answer_form}
                            # ```
                            # Just fill in the score, that's all. One key-value pair per option (one key, one value. not nested; -> "option-1": "your_score_here", ).
                            # No additional comments. A tasty reward awaits your accurate markdown``` selection. ``json
                            # """

                            # context_history = f"""
                            # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {dict_of_options}.
                            # Place your evaluations as value to the key in Json format. Return your properly formatted dict as:
                            # '''json

                            # '''
                            # No additional comments. A tasty reward awaits your accurate selection."""

                            answer_form = {
                                "option-1": "score_here",
                                "option-2": "score_here",
                                "option-3": "score_here",
                            }

                            sample_2 = '{"option-1": '

                            context_history = f"""
                            For this original task: '{task_summary}'. Evaluate only these {len(list_of_ranked_choice_options)} 
                            options: {pretty_print_option_list(dict_of_options)}. 
                            (0-10; 0 is bad, 10 is good) Place your evaluation of each as the value to a key in markdown ```json format. 
                            as: 
                            ```json 
                            {answer_form} 
                            ```
                            Just fill in the score, that's all. One key-value pair for each of the {len(list_of_ranked_choice_options)} 
                            evaluated options (one key, one value. not nested; not everything in the original question. -> "option-1": "your_score_here", ). 
                            No additional comments. A tasty reward awaits your accurate markdown selection. 
                            Let's stare: {sample_2}
                            """

                            answer_form = {
                                "option-1": "score_here",
                                "option-2": "score_here",
                                "option-3": "score_here",
                            }

                            context_history = f"""
                            For this original task: '{task_summary}'. Evaluate only these {len(list_of_ranked_choice_options)} 
                            options: {pretty_print_option_list(dict_of_options)}. 
                            (0-10; 0 is bad, 10 is good) Place your evaluation of each as the value to a key in dict or json format. 
                            as: 
                            {answer_form} 
                            Just fill in the score, that's all. One key-value pair for each of the {len(list_of_ranked_choice_options)} 
                            evaluated options (one key, one value. not nested; not everything in the original question. -> "option-1": "your_score_here", ). 
                            No additional comments. A tasty reward awaits your accurate markdown selection. 
                            """

                            ###################
                            ###################
                            # Select Bestest
                            # By ranked choice
                            ###################
                            ###################
                            # TODO limit max while counter

                            # turn list of options int dict
                            dict_of_options = {
                                option: None for option in list_of_ranked_choice_options
                            }
                            # get highest ranked item:
                            selected_option = None

                            while_counter = 0

                            for i in range(number_of_ranked_votes):

                                print(f"while_counter -> {while_counter}")

                                vote_check_ok = False

                                while not vote_check_ok:

                                    # exit while loop if too many fails
                                    if task_fail_counter > retry_x_times:
                                        selected_option = None
                                        error_log.append(
                                            "task_fail_counter more than retry_x_times"
                                        )
                                        break

                                    """
                                    TODO if a different function rank_vote_call_api_within_structure_check()
                                    you should be able to filter everything except numbers out of the answer

                                    also...
                                    1. any complete duplicates can be filtered out...
                                    2. any non-numbers filtered out
                                    """
                                    print(f"while_counter -> {while_counter}")
                                    print("number_call_api_within_structure_check")

                                    # get a list of votes and make sure it matches the list of candidates
                                    list_of_votes = (
                                        task_number_call_api_within_structure_check(
                                            context_history,
                                            use_this_model,
                                            parameter_dict,
                                            ai_local_or_cloud_mode,
                                            retry_x_times,
                                            models_dir_path,
                                        )
                                    )

                                    print(f"\n\nlist_of_votes -> {list_of_votes}")
                                    print(
                                        f"type list_of_votes -> {type(list_of_votes)}"
                                    )

                                    # filter out words and make type int
                                    list_of_votes = filter_list_convert_to_int(
                                        list_of_votes
                                    )

                                    print(f"list_of_votes -> {list_of_votes}")
                                    print(
                                        f"list_of_ranked_choice_options -> {list_of_ranked_choice_options}"
                                    )
                                    print(
                                        f"type list_of_votes -> {type(list_of_votes)}\n\n"
                                    )

                                    print(
                                        f"list_dict_of_options -> {list_dict_of_options}"
                                    )

                                    if list_of_votes:

                                        # if there is one vote per candidate, list each candidates votes
                                        if len(list_of_votes) == len(
                                            list_of_ranked_choice_options
                                        ):
                                            add_ranks_votes_to_candidate(
                                                list_of_votes, list_dict_of_options
                                            )

                                            print(
                                                f"new list_dict_of_options -> {list_dict_of_options}"
                                            )

                                            # exit loop
                                            vote_check_ok = True

                                        else:  # if len of list is wrong
                                            while_counter += 1
                                            task_fail_counter += 1
                                            retry_or_error_event_counter_list.append(
                                                True
                                            )
                                            error_log.append("length of list is wrong.")
                                            print("len of list is wrong")
                                            print(
                                                f"while_counter:{while_counter}, task_fail_counter:{task_fail_counter}"
                                            )

                                    else:  # if no list at all!
                                        while_counter += 1
                                        task_fail_counter += 1
                                        retry_or_error_event_counter_list.append(True)
                                        error_log.append("No select_best list.")
                                        print("no list at all!")
                                        print(
                                            f"while_counter:{while_counter}, task_fail_counter:{task_fail_counter}"
                                        )

                            # tally the ranked votes and pick the winner
                            selected_option = extract_top_rank(list_dict_of_options)

                            print(f"selected_option -> {selected_option}")

                        else:
                            # make the best choice...the only option
                            selected_option = list_of_ranked_choice_options[0]

                    else:
                        selected_option = None

                    ##########
                    ##########
                    # Scoring
                    ##########
                    ##########
                    """
                    Scoring depends whether the option list has been randomized.
                    If the list has been randomized, adjust the AI's choice
                    to be as if it had not been.
                    """

                    # if there are options and you want to randomize them
                    if (
                        randomize_option_choices is True
                    ) and these_original_task_options:
                        print(
                            f""" Inspection

                        these_original_task_options   -> {these_original_task_options}
                        randomized_option_list        -> {randomized_option_list}

                        original_to_randomized_lookup -> {original_to_randomized_lookup}
                        randomized_to_original_lookup -> {randomized_to_original_lookup}

                        Original selected_option      -> {selected_option}
                        """
                        )

                        if selected_option is not None:
                            selected_option = randomized_to_original_lookup[
                                selected_option
                            ]

                            print(
                                f""" 
                            selected_option               -> {selected_option}
                            """
                            )

                    if error_comment_data_lookup_table:
                        # get task failure comment
                        task_failure_comment = check_answer_in_dict(
                            selected_option, error_comment_data_lookup_table
                        )

                        print(
                            f"""
                            Scoring:
                            selected_option       -> {selected_option}
                            type(selected_option) -> {type(selected_option)}

                            correct_option        -> {correct_option}
                            type(correct_option)  -> {type(correct_option)}

                            """
                        )

                    else:
                        task_failure_comment = ""

                    # default
                    score = 0

                    # make str
                    selected_option = str(selected_option)
                    correct_option = str(correct_option)

                    # for write function
                    if function_writing and (selected_option == "pass"):
                        score = 1

                    # if multiple choice and should check answer:
                    elif (
                        task_mode_validate_the_answer
                        and task_mode_answer_option_choices_provided_boolean
                    ):
                        print(
                            f"selected_option -> {selected_option} type -> {type(selected_option)}"
                        )
                        print(
                            f"correct_option -> {correct_option} type -> {type(correct_option)}"
                        )

                        if selected_option == correct_option:
                            print("Score!")
                            score = 1
                        else:
                            print(
                                f"Oops: selected_option -> {selected_option} vs. correct_option -> {correct_option}"
                            )
                            score = 0

                        # making csv row
                        print("with score: making csv row...")

                    """
                    Formatting Notes Section
                    Add question order randomization to formatting notes.
                    """
                    formatting_notes = ""

                    if randomize_option_choices is True:
                        formatting_notes += str(randomize_option_choices)

                    formatting_notes = replace_special_characters_with_text_swap(
                        formatting_notes
                    )

                    # if open-answer and should check answer:
                    """
                    If open answer contains
                    - without capitalization
                    - without puncutation
                    - without spaces 
                    """
                    if task_mode_validate_the_answer and (
                        not task_mode_answer_option_choices_provided_boolean
                    ):
                        print("checking substring")
                        print(
                            f"selected_option -> {selected_option} type -> {type(selected_option)}"
                        )
                        print(
                            f"correct_option -> {correct_option} type -> {type(correct_option)}"
                        )

                        if is_substring_boolean(selected_option, correct_option):
                            print("Score!")
                            score = 1
                        else:
                            print("Oops")
                            score = 0

                        # making csv row
                        print("with score: making csv row...")

                    safe_task_attempt_log = replace_special_characters_with_text_swap(
                        draft_task_attempt_log
                    )

                    safe_question_task_prompt = (
                        replace_special_characters_with_text_swap(question_task_prompt)
                    )

                    safe_task_from_instructions = (
                        replace_special_characters_with_text_swap(this_task)
                    )

                    if error_log:
                        error_log_safe_string = (
                            replace_special_characters_with_text_swap(error_log)
                        )

                    else:  # if error log is empty
                        error_log = ""
                        error_log_safe_string = ""

                    just_model_file_name = os.path.basename(use_this_model)
                    just_this_original_task_file_name = os.path.basename(
                        this_original_task_file
                    )

                    # set rnf time
                    end_time_whole_single_task = datetime.now(UTC)

                    duration_of_single_task = duration_min_sec(
                        start_time_whole_single_task, end_time_whole_single_task
                    )

                    retry_counter = len(retry_or_error_event_counter_list)

                    # turn into min, sec

                    list_of_items_to_write_to_csv = [
                        score,
                        this_row_or_line_number,
                        selected_option,
                        correct_option,
                        task_failure_comment,
                        just_model_file_name,
                        just_this_original_task_file_name,
                        safe_task_from_instructions,
                        safe_question_task_prompt,
                        list_of_ranked_choice_options,
                        safe_task_attempt_log,
                        formatting_notes,
                        retry_counter,
                        error_log_safe_string,
                        duration_of_single_task,
                        readable_timestamp,
                    ]

                    # answer_row = f'"{score}", "{this_row_or_line_number}", "{selected_option}", "{correct_option}", "{use_this_model}", "{this_original_task_file}", "{task_from_instructions}", "{question_task_prompt}", "{list_of_ranked_choice_options}", "{replace_special_characters_with_text_swap(draft_task_attempt_log)}", "{readable_timestamp}"\n'
                    # print(f"answer_row -> {answer_row}")

                    # answer_row = strip_newlines_and_spaces(answer_row)
                    # # print(f"\n\nanswer_row -> {answer_row}")
                    # answer_row = answer_row + "\n"
                    # print(f"\n\nanswer_row -> {answer_row}")

                    # append to task_set_results_path

                    # # Check if the file exists to determine if the header needs to be written
                    # file_exists = os.path.exists(task_set_results_path)

                    # with open(task_set_results_path, 'a', newline='') as csvfile:
                    #     # Write the data row
                    #     csvfile.write(answer_row)

                    append_list_of_values_to_csv(
                        task_set_results_path, list_of_items_to_write_to_csv
                    )

                    # Exit While
                    print("\nHats in the air, we can all leave. Buubye!!\n\n\n")
                    task_ok_flag = True

                    # # Check if the file exists
                    # if not os.path.exists(task_set_results_path):
                    #     # If the file doesn't exist, create it with the header
                    #     with open(task_set_results_path, 'w', newline='') as csvfile:  # Use 'w' mode to write the header
                    #         csvwriter = csv.writer(csvfile, delimiter=',')
                    #         header = ["this_row_or_line_number", "selected_option", "use_this_model", "this_original_task_file", "task_from_instructions", "question_task_prompt", "list_of_ranked_choice_options", "draft_task_attempt_log", "readable_timestamp"]
                    #         csvwriter.writerow(header)

                    # Assume `answer_row` is a list of values you want to write to the CSV
                    # For example, constructing `answer_row` might look like this:
                    # answer_row = ["fail", this_row_or_line_number, "fail", use_this_model, this_original_task_file, task_from_instructions, question_task_prompt, list_of_ranked_choice_options, draft_task_attempt_log, readable_timestamp]
                    # Make sure `answer_row` is a list here, not a string.

                    # # Strip newlines and spaces from each element if needed
                    # answer_row = [strip_newlines_and_spaces(str(item)) for item in answer_row]

                    # # Now, append this row to the CSV file
                    # with open(task_set_results_path, 'a', newline='') as csvfile:
                    #     csvwriter = csv.writer(csvfile, delimiter=',')
                    #     csvwriter.writerow(answer_row)

                if not task_ok_flag:

                    # making csv row
                    print("if not task_ok_flag: making csv row...")
                    # answer_row = f'"fail", "{this_row_or_line_number}", "fail", "{use_this_model}", "{this_original_task_file}", "{task_from_instructions}", "{question_task_prompt}", "{list_of_ranked_choice_options}", "{replace_special_characters_with_text_swap(draft_task_attempt_log)}", "{readable_timestamp}"\n'
                    # # print(f"answer_row -> {answer_row}")
                    # answer_row = strip_newlines_and_spaces(answer_row)
                    # answer_row = answer_row + "\n"

                    # print(f"\n\nanswer_row -> {answer_row}")

                    # # Strip newlines and spaces from each element if needed
                    # answer_row = [strip_newlines_and_spaces(str(item)) for item in answer_row]

                    # # # Now, append this row to the CSV file
                    # # with open(task_set_results_path, 'a', newline='') as csvfile:
                    # #     csvwriter = csv.writer(csvfile, delimiter=',')
                    # #     csvwriter.writerow(answer_row)

                    # with open(task_set_results_path, 'a', newline='') as csvfile:
                    #     csvfile.write(answer_row)

                    # nicely format some fields
                    safe_task_attempt_log = replace_special_characters_with_text_swap(
                        draft_task_attempt_log
                    )

                    safe_question_task_prompt = (
                        replace_special_characters_with_text_swap(question_task_prompt)
                    )

                    safe_task_from_instructions = (
                        replace_special_characters_with_text_swap(this_task)
                    )

                    just_model_file_name = os.path.basename(use_this_model)
                    just_this_original_task_file_name = os.path.basename(
                        this_original_task_file
                    )

                    print(f"just_model_file_name -> {just_model_file_name}")

                    task_failure_comment = "no answer given"

                    retry_counter = len(retry_or_error_event_counter_list)

                    # replace some fields with 'fail'
                    list_of_items_to_write_to_csv = [
                        "fail",
                        this_row_or_line_number,
                        "fail",
                        correct_option,
                        task_failure_comment,
                        just_model_file_name,
                        just_this_original_task_file_name,
                        safe_task_from_instructions,
                        safe_question_task_prompt,
                        list_of_ranked_choice_options,
                        safe_task_attempt_log,
                        formatting_notes,
                        retry_counter,
                        error_log_safe_string,
                        duration_of_single_task,
                        readable_timestamp,
                    ]

                    append_list_of_values_to_csv(
                        task_set_results_path, list_of_items_to_write_to_csv
                    )

                    # Exit While
                    print(
                        f"\nFailed to attempt task, moving on... {draft_task_attempt_log}\n\n\n"
                    )

                ##########################
                # save file
                ##########################
                print("All done? Anyone here...hello? What was that? Is someone")




# #######################
# # demo rust code tests
# #######################

# extracted_code = """
# fn multiply(a: f64, b: f64, c: f64) -> f64 {
#     a * b * c
# }
# """

# test_cases = [
#     {"input": [4.0, 5.0, 2.0], "expected_output": 40.0},
#     {"input": [3.5, 2.0, 1.5], "expected_output": 10.5},
#     {"input": [2.0, 2.0, 2.0], "expected_output": 8.0},
#     {"input": [1.0, 1.0, 1.0], "expected_output": 1.0}
# ]

# function_name = "multiply"

# score, stdout, stderr = run_rust_code(extracted_code, test_cases, function_name, dependencies=None)

# print('score', score)
# print('out', stdout)
# print('err', stderr)




# Option Notes
##########################################################
# https://platform.openai.com/docs/guides/text-generation
##########################################################
"""
gpt-4

gpt-4-turbo-preview

gpt-3.5-turbo
"""

use_this_model = "gpt-4"
use_this_model = "gpt-4-turbo-preview"
use_this_model = "gpt-3.5-turbo"


######################
# Mixtral 8x7 "Small"
######################
use_this_model = "mistral-small"

######################
# Mixtral Large ???
######################
use_this_model = "mistral-large-latest"

####################
# Mistral 7b "Tiny"
####################
use_this_model = "mistral-tiny"


#######################
# Anthropic claude-2.1
#######################
use_this_model = "claude-3-opus-20240229"
use_this_model = "claude-2.1"


###########################
###########################
# Choices & Configurations
###########################
###########################

# Tune Your Paramaters for llama.cpp
parameter_dict = {
    "--temp": 0.8,  # (default value is 0.8)
    "--top-k": 40,  # (selection among N most probable. default: 40)
    "--top-p": 0.9,  # (probability above threshold P. default: 0.9)
    "--min-p": 0.05,  # (minimum probability threshold. default: 0.05)
    "--seed": -1,  # seed, -1 is a random seed
    "--tfs": 1,  # (tail free sampling with parameter z. default: 1.0) 1.0 = disabled
    "--threads": 8,  # (~ set to number of physical CPU cores)
    "--typical": 1,  # (locally typical sampling with parameter p  typical (also like ~Temperature) (default: 1.0, 1.0 = disabled).
    "--mirostat": 2,  # (default: 0,  0= disabled, 1= Mirostat, 2= Mirostat 2.0)
    "--mirostat-lr": 0.05,  # (Mirostat learning rate, eta.  default: 0.1)
    "--mirostat-ent": 3.0,  # (Mirostat target entropy, tau.  default: 5.0)
    "--ctx-size": 500,  # Sets the size of the prompt context
}

# Configure your task overall
task_mode_configies = {
    "answer_option_choices_provided": True,
    "validate_the_answer": True,
    "use_history_context_dict_list": False,
    "system_instructions": False,
    "output_structure_mode": "pipes",
    "input_state_context_mode": "one_string",
    "ranked_choice_output_structure_mode": "pipes",
    # "LMQL": False,
}

# configure each task-file
task_file_config_dic_list = [
    # {
    #     "file_name": "my_test1.jsonl",
    #     "file_type": ".jsonl",
    #     "file_structure": "",
    #     "task_field_name": 'task',
    #     "index_of_task": 0,
    #     "index_of_options": 1,
    #     "options_field_name": 'options',
    #     "scoring_field_name": 'answer_index_from_1',
    #     "this_offset": 0,
    #     "this_range_inclusive": 1,
    #     "use_offset_and_range": True,
    # },
    # {
    #     "file_name": "my_test_open_answer_2.jsonl",
    #     "file_type": ".jsonl",
    #     "file_structure": "",
    #     "task_field_name": 'task',
    #     "index_of_task": 0,
    #     "index_of_options": 1,
    #     "options_field_name": None,
    #     "scoring_field_name": 'answer',
    #     "answer_option_choices_provided": False,
    #     "validate_the_answer": True,
    #     "use_history_context_dict_list": False,
    #     "system_instructions": False,
    #     "output_structure_mode": "pipes",
    #     "input_state_context_mode": "one_string",
    #     "ranked_choice_output_structure_mode": "pipes",
    #     "this_offset": 0,
    #     "this_range_inclusive": 1,
    #     "use_offset_and_range": True,
    # },
    # {
    #     "file_name": "error_explained_test_1.jsonl",
    #     "file_type": ".jsonl",
    #     "header_exits": False,
    #     "file_structure": "",
    #     "index_of_task": None,
    #     "index_of_options": None,
    #     # Fields
    #     "task_field_name": "task",
    #     "options_field_name": "options",
    #     "scoring_field_name": "answer_from_index_start_at_1",
    #     "error_comment_data_lookup_table_field_name": "error_comment_data_lookup_table",
    #     "answer_option_choices_provided": True,
    #     "randomize_option_choices": True,
    #     "validate_the_answer": True,
    #     "use_history_context_dict_list": False,
    #     "system_instructions": False,
    #     "output_structure_mode": "pipes",
    #     "input_state_context_mode": "one_string",
    #     "ranked_choice_output_structure_mode": "pipes",
    #     "this_offset": 3,
    #     "this_range_inclusive": 1,
    #     "use_offset_and_range": True,
    # },
    # {
    #     "file_name": "winograd_schemas_test_file.jsonl",
    #     "file_type": ".jsonl",
    #     "header_exits": False,
    #     "file_structure": "",
    #     "index_of_task": None,
    #     "index_of_options": None,
    #     # Fields
    #     "task_field_name": "task",
    #     "options_field_name": "options",
    #     "scoring_field_name": "answer_from_index_start_at_1",
    #     "error_comment_data_lookup_table_field_name": None,
    #     "answer_option_choices_provided": True,
    #     "randomize_option_choices": True,
    #     "validate_the_answer": True,
    #     "use_history_context_dict_list": False,
    #     "system_instructions": False,
    #     "output_structure_mode": "pipes",
    #     "input_state_context_mode": "one_string",
    #     "ranked_choice_output_structure_mode": "pipes",
    #     "this_offset": 10,
    #     "this_range_inclusive": 2,
    #     "use_offset_and_range": True,
    # },
    # # Cloud
    # {
    #     "file_name": "error_explained_test_1.jsonl",
    #     "file_type": ".jsonl",
    #     "header_exits": False,
    #     "file_structure": "",
    #     "index_of_task": None,
    #     "index_of_options": None,
    #     # Fields
    #     "task_field_name": "task",
    #     "options_field_name": "options",
    #     "scoring_field_name": "answer_from_index_start_at_1",
    #     "error_comment_data_lookup_table_field_name": "error_comment_data_lookup_table",
    #     "answer_option_choices_provided": True,
    #     "validate_the_answer": True,
    #     "use_history_context_dict_list": False,
    #     "system_instructions": False,
    #     "output_structure_mode": "pipes",
    #     "input_state_context_mode": "one_string",
    #     "ranked_choice_output_structure_mode": "pipes",
    #     "this_offset": 1,
    #     "this_range_inclusive": 2,
    #     "use_offset_and_range": True,
    # },
    # {
    #      "file_name": "short_code_writing_test_set_1.jsonl",
    #      "file_type": ".jsonl",
    #      "header_exits": False,
    #      "file_structure": "",
    #      "index_of_task": None,
    #      "index_of_options": None,
    #      # Fields
    #      "task_field_name": "task",
    #      "options_field_name": "options",
    #      "scoring_field_name": "answer_from_index_start_at_1",
    #      "error_comment_data_lookup_table_field_name": None,
    #      "answer_option_choices_provided": False,
    #      "randomize_option_choices": False,
    #      "validate_the_answer": True,
    #      "use_history_context_dict_list": False,
    #      "system_instructions": False,
    #      "function_writing": True,
    #      "function_test_cases__field_name": "test_cases",
    #      "function_name__field_name": "function_name",
    #      "output_structure_mode": "markdown",
    #      "input_state_context_mode": "one_string",
    #      "ranked_choice_output_structure_mode": "pipes",
    #      "this_offset": 0,
    #      "this_range_inclusive": 1,
    #      "use_offset_and_range": False,
    #  },
    {
        "file_name": "short_code_writing_test_set_8.jsonl",
        "file_type": ".jsonl",
        "header_exits": False,
        "file_structure": "",
        "index_of_task": None,
        "index_of_options": None,
        # Fields
        "task_field_name": "task",
        "options_field_name": "options",
        "scoring_field_name": "answer_from_index_start_at_1",
        "error_comment_data_lookup_table_field_name": None,
        "answer_option_choices_provided": False,
        "randomize_option_choices": False,
        "validate_the_answer": True,
        "use_history_context_dict_list": False,
        "system_instructions": False,
        "function_writing": True,
        "function_test_cases__field_name": "test_cases",
        "function_name__field_name": "function_name",
        "output_structure_mode": "markdown",
        "input_state_context_mode": "one_string",
        "ranked_choice_output_structure_mode": "pipes",
        "this_offset": 0,
        "this_range_inclusive": 1,
        "use_offset_and_range": False,
    },
]

#####################
# Whole Task Choices
#####################
ai_local_or_cloud_mode = "gguf"
# ai_local_or_cloud_mode = "cloud"
number_of_preliminary_drafts = 2
number_of_ranked_votes = 1
retry_x_times = 2

##############
# Pick Models
##############
# list_of_models = ["mistral-tiny"]
# list_of_models = ["tinyllama", "mistral-7b-instruct", "stablelm-zephyr-3b"]
# list_of_models = ["stable-zephyr-3b"]
# list_of_models = ["claude-2.1"]
# list_of_models = ["claude-3-opus-20240229"]
list_of_models = ["llamacorn", "tinyllama", "stablelm-zephyr-3b"]
list_of_models = ["mistral-7b-instruct"]
# list_of_models = ["llamacorn", "tinyllama"]
list_of_models = ["wizardcoder-python-13b"]
# list_of_models = ["tinyllama", "mistral-7b-instruct", "stablelm-zephyr-3b"]
list_of_models = ["llamacorn", "dolphin-2_6-phi", "codeninja-1.0-openchat"]
# list_of_models = ["llamacorn", "mistral-7b-instruct"]
list_of_models = ["llamacorn"]
# list_of_models = ["llamacorn", "dolphin-2_6-phi", "codeninja-1.0-openchat", "mistral-7b-instruct"]

######
# Run
######
if __name__ == "__main__":

    message = f"""
    These are the models you are slated to run,
    as specified in your list in the do_tasks.py file, at the bottom.

       list_of_models = {list_of_models}

    Here are the possible models:
    {print_find_all_models(path="jan/models/")}

    Do you wish to add another model? If so, type in a model name here...

    """

    # Ask user for model (for first time users' ease of starting perhaps)
    add_this = input(message)

    # add if there is anything to add
    if len(add_this):
        list_of_models.append(add_this)

    ##########
    # Do Task
    ##########
    do_task_please(
        list_of_models,
        ai_local_or_cloud_mode,
        number_of_preliminary_drafts,
        retry_x_times,
        number_of_ranked_votes,
        task_mode_configies,
        task_file_config_dic_list,
        parameter_dict=parameter_dict,
        models_dir_path="jan/models",
    )

    #####################
    # Make a score tally
    #####################
    make_score_tally("task_set_results_files")

    # make html report
    html_for_all_reports()
    html_for_all_score_tallies()
    
    
    