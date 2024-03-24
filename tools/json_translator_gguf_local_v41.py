# -*- coding: utf-8 -*-
"""
json translator:
- first install llama.cpp and at least one model (or use cloud api)
- put your json files into the ai_task_files directory
- add your target languages to the list below
- add your model to use into the list below
- configure number of ranked-choice votes to cast
- configure how many translations to make (before selecting the best)
- run this pyscript

"""

import string
from call_llamacpp import gguf_api, mini_gguf_api, get_model_path_by_name


"""
.env: get your environment variables:
  Using the Google Secretes (like.env) system
  built into colab on the left menu: the 'key' icon.
"""
# from google.colab import userdata

# mistral_api_key = userdata.get("mistral_api_key")
# # mistral_api_key = 'xxx'
# openai_api_key = userdata.get("open_ai_key")

# from dotenv import load_dotenv
import os
import time
import csv

"""# make a list of json files"""
# import openai
# from google.colab import userdata

# Load environment variables from .env file
# load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY") 
mistral_api_key = os.getenv("mistral_api_key") 


def make_answers_directory_and_csv_path(this_original_task_file, model_name):
    """
    Returns a list of .json files in the current working directory.
    """
    solution_dir_path = "solution_files"
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
            print(f"Error creating directory {solution_dir_path}: {e}")
            return  # Exit the function if directory creation fails



    # make path absolute, belts and suspenders
    solution_dir_path = os.path.abspath(solution_dir_path)

    answer_file_path = f"answer_{this_original_task_file}_{model_name}_{clean_timestamp}_file" 

    # Determine the path to the file that should be saved
    answer_file_path = os.path.join(solution_dir_path, answer_file_path)


    return answer_file_path


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

    print(f"looking for {file_type_list}")

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

            # List all files in the current working directory
            files_in_cwd = os.listdir("ai_task_files/.")
            print(f"files_in_cwd -> {files_in_cwd}")

            # Filter the list to include only requested
            task_files = [file for file in files_in_cwd if file.endswith(this_file_type)]

            clipped_task_files = [item for item in task_files if not item.startswith('empty_')]

            output_list.append(clipped_task_files)

        # remove empty lists 
        output_list = [item for item in output_list if item]

        # flattened_list
        output_list = [item for sublist in output_list for item in sublist]

        print(output_list)
        if not output_list:
            message = f"\n\nExit Dungeon: Your file list in {file_path}/ is empty, add a file and try!\n\n"
            sys.exit(message)

        # remove duplicates
        output_list_set = set(output_list)
        output_list = list(output_list_set)

        return output_list

    except Exception as e:
        raise e


"""# Process Json
- make a model/skeleton template
"""

import json


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

import os
from datetime import datetime, UTC
import json  # Added missing import


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
            print(f"Error creating directory {directory_path}: {e}")
            return  # Exit the function if directory creation fails

    # Determine the path to the file that should be saved
    file_path = os.path.join(directory_path, new_title)

    # Save the JSON data to the file with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(input_text, outfile, indent=4, ensure_ascii=False)


"""# Swap-Out, Swap-Back (Wax-on, Wax-off)"""

import sys


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

import requests
"""
import requests
import json
import os
import re
import time

# using google secretes
# from google.colab import userdata

# mistral_api_key = userdata.get("mistral_api_key")
mistral_api_key = "xxx"

# Define the endpoint URL
endpoint_url = "https://api.mistral.ai/v1/chat/completions"

# Set the headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {mistral_api_key}",
}

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
def add_to_context_history(user_input, context_history, role):

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


# Helper Function
def prompt_user(user_input, context_history):

    context_history.append(segment_for_adding_to_context_history("user", user_input))

    return context_history


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


# Helper Function
def counter(timeout=10):
    count = 0
    start_time = time.time()
    while time.time() - start_time < timeout:
        count += 1
        time.sleep(1)
    return count


# Helper Function
def ask_mistral_model(context_history, use_this_model):
    # Define the request body
    request_body = {"model": use_this_model, "messages": context_history}

    # pause if error occurs
    counter(2)

    #################
    #################
    # Hit the ai api
    #################
    #################
    # Send the request
    response = requests.post(endpoint_url, headers=headers, json=request_body)

    # Check the response status code
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        return None

        # pause if error occurs
        counter(10)

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

    return assistant_says


"""# functions to call openAI api"""

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
#         print("API call function call_openai_chat_api(this_input, select_model=3) failed, error = ", e)
#         return e

#     return results

# call_openai_chat_api("testing")

"""## Add System instructions for rules"""


# # Helper Function
# def set_translator__system_prompt(context_history, target_language):

#     ################
#     # System Prompt
#     ################

#     example_1 = "a happy cat"

#     example_2 = {"translation": "chat heureux"}

#     example_bad = {"NOT THIS": "NO SINGLE QUOTES"}

#     example_3 = {"translation": "S'inscrire"}

#     # set translation language and structure of output in system
#     text_input = f"""
#     You are an expert helpful {target_language} language translator bot that produces high
#     quality professional translations in precise json formats.

#     You translate writen language, not emojis or syntax not
#     readable by a person. You use normal capitalization,
#     not all upper case. You use normal full words, not single letters
#     or obscure abreviations.

#     You always deliver your translation in the same correct json format.
#     starting with ```json and ending with ```.
#     "translation": "YOUR TRANSLATION HERE"

#     e.g. If the original phrase is:
#     {example_1}
#     Then your translation format is like this, with no other commentary needed:
#     ```jsons
#     {example_2}
#     ```

#     If the target language is french, and the translation is S'inscrire:
#     You output
#     {example_3}


#     Your translation is always expressed using valid json syntax,
#     using double quotes only in json.
#     (e.g. no trailing delimiter, escape conflicting characters, etc).


#     You only translate into {target_language}.
#     You only produce json output in exactly this structure
#     ```jsons
#     {example_2}
#     ```
#     Your translations are clear, accurate, helpful, honrable, brief, polite, and professional.
#     Your do you best to tranlsate every leaf value field leaving nothing blank.
#     Every final leaf values MUST be translated.

#     You always double check your work and make sure the translation is
#     excellent in the context of the whole body of translation.
#     """
#     role = "system"

#     context_history.append(segment_for_adding_to_context_history(role, text_input))

#     # # inspection
#     # print("set_translator__system_prompt -> ", context_history)

#     return context_history


# """## Add 'user' request for translation"""


# # Helper Function
# def set_translate__user_prompt(context_history, target_language, original_data):

#     ###########################
#     # User Translation Request
#     ###########################

#     example_1 = "a happy cat"

#     example_2 = {"translation": "your translation here"}

#     example_bad = {"NOT THIS": "NO SINGLE QUOTES"}

#     example_bad2 = """{\'translation\': "BAD!! NO SINGLE QUOTES"}"""

#     # set translation language and structure of output in system
#     text_input = f"""

#     The person we are trying to help needs text string
#     translated into the {target_language} language.

#     Carefully translate this original text string into {target_language}.
#     The original string is: {original_data}

#     Double check your work and make sure the translation is
#     accurate, brief, and polite.

#     Make sure your translation is expressed using valid json syntax.
#     Always use double quotes " only around items in json.

#     Formatting for json must be like this in double-quotes for jsone.g.
#     ```json
#     {example_2}
#     ```

#     You can do it!!
#     """
#     role = "user"

#     context_history.append(segment_for_adding_to_context_history(role, text_input))

#     # # inspection
#     # print("set_translate__user_prompt", context_history)

#     return context_history



# # Helper Function
# def set_translator__system_prompt(context_history, target_language):

#     ################
#     # System Prompt
#     ################

#     # set translation language and structure of output in system
#     text_input = f"""
#     You are an expert helpful {target_language} language translator bot that produces high
#     quality professional translations. You translate writen UTF-8 language, not emojis or syntax not
#     readable by a person.

#     You always deliver your translation in the same simple standard format
#     between a demiter of three pips like markdown text
#     between two sets of ```


#     You do not put anything else in ``` ever, only your translation.
#     This is how your translation is identified.

#     Tour translation format is like this, with no other commentary needed:

#     You only translate into {target_language}, and only produce a translation no other commentary.
#     Your translations are clear, accurate, helpful, honrable, brief, polite, and professional.
#     Your do you best to tranlsate every leaf value field leaving nothing blank.
#     Every final leaf values MUST be translated.

#     Do not say anything else, just your translation between two sets of ```

#     You always double check your work and make sure the translation is
#     excellent in the context of the whole body of translation.
#     """

#     # Remove duplicate spaces
#     text_input = re.sub(r'\s+', ' ', text_input.strip())

#     role = "system"

#     context_history.append(segment_for_adding_to_context_history(role, text_input))

#     # # inspection
#     # print("set_translator__system_prompt -> ", context_history)

#     return context_history


# """## Add 'user' request for translation"""


# # Helper Function
# def set_translate__user_prompt(context_history, target_language, original_data):

#     ###########################
#     # User Translation Request
#     ###########################


#     # set translation language and structure of output in system
#     text_input = f"""
#     The person we are trying to help needs a {target_language} language translation of a text string.

#     Carefully translate the original text string into {target_language}.
#     The original string is: {original_data}

#     Double check your work and make sure the translation is
#     accurate, brief, and polite.

#     Produce just a {target_language} language translation identified
#     by surrounding two sets of ```

#     Do not say anything else, just your translation in  two sets of ```

#     You can do it!!
#     """

#     # Remove duplicate spaces
#     text_input = re.sub(r'\s+', ' ', text_input.strip())

#     role = "user"

#     context_history.append(segment_for_adding_to_context_history(role, text_input))

#     # # inspection
#     # print("set_translate__user_prompt", context_history)

#     return context_history


# Helper Function
def task_check_function_description_keys(dict_str):
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
    print(f"\n\n Starting check_function_description_keys, dict_str -> {repr(dict_str)} {type(dict_str)}")

    # input("breakpoint")



    ########################
    # Check Json Formatting
    ########################


    # pre-check
        # load
    try:
        if "'" not in dict_str:

            # Load the string into a Python dictionary
            dict_data = json.loads(dict_str)

            dict_str = dict_data['translation']

            if dict_leaf_detection_boolean_true_means_defective(dict_str):
                return dict_str

            else:
                print(f"Failed dict_str precheck")

    except:
        print(f"Failed dict_str precheck")




    # extraction 1
    try:
        if """```json""" in dict_str:


            pattern = r'```json\n([\s\S]*?)\n```'
            match = re.search(pattern, dict_str)
            dict_str =  match.group(1) if match else ''

    except Exception as e:
        print(f"\nTRY AGAIN: check_function_description_keys() extraction from markdown failed: {e}")
        print(f"Failed dict_str -> {repr(dict_str)}")
        return False

    print(f"\n  extraction-1 from markdown dict_str -> {repr(dict_str)} {type(dict_str)}")


    try:
        # if ("""{'final_answer': '""" in dict_str) and ("""'}""" in dict_str):
        #     dict_str.replace( """{'final_answer':""", """{"final_answer":"""  )
        #     dict_str.replace( """'}""", """"}"""  )

        # if ("""{\'final_answer\': \'""" in dict_str) and ("""\'}""" in dict_str):
        #     dict_str.replace( """{\'final_answer\':""", """{"final_answer":"""  )
        #     dict_str.replace( """\'}""", """"}"""  )

        if ("""{\'final_answer\':""" in dict_str):
            dict_str = dict_str.replace( """{\'final_answer\':""", """{"final_answer":"""  )

        if ("""{'final_answer':""" in dict_str):
            dict_str = dict_str.replace( """{'final_answer':""", """{"final_answer":"""  )

        if ("""{\\'final_answer\\':""" in dict_str):
            dict_str = dict_str.replace( """{\\'final_answer\\':""", """{"final_answer":"""  )

    except Exception as e:
        print(f"Failed dict_str -> {repr(dict_str)}")
        return False

    print(f" dict_str -> {repr(dict_str)} {type(dict_str)}")


    dict_str = clean_and_convert_to_json(dict_str)
    print(f" clean_and_convert_to_json dict_str -> {repr(dict_str)} {type(dict_str)}")


    try:
        # if ("""{'final_answer': '""" in dict_str) and ("""'}""" in dict_str):
        #     dict_str.replace( """{'final_answer':""", """{"final_answer":"""  )
        #     dict_str.replace( """'}""", """"}"""  )

        # if ("""{\'final_answer\': \'""" in dict_str) and ("""\'}""" in dict_str):
        #     dict_str.replace( """{\'final_answer\':""", """{"final_answer":"""  )
        #     dict_str.replace( """\'}""", """"}"""  )

        if ("""{\'final_answer\':""" in dict_str):
            dict_str = dict_str.replace( """{\'final_answer\':""", """{"final_answer":"""  )

        if ("""{'final_answer':""" in dict_str):
            dict_str = dict_str.replace( """{'final_answer':""", """{"final_answer":"""  )

        if ("""{\\'final_answer\\':""" in dict_str):
            dict_str = dict_str.replace( """{\\'final_answer\\':""", """{"final_answer":"""  )

    except Exception as e:
        print(f"Failed dict_str -> {repr(dict_str)}")
        return False



    # clean
    try:
        """
        Swap in and swap out escaped single commas
        to avoid them being removed during reformatting
        or the reformatting otherwise breaking the json
        """


        # if ("\'" in dict_str) or ("""\\'""" in dict_str):
        #     print("escaped single quote found")

        #     input_string = dict_str
        #     target = "\'"
        #     swapper = get_swap_in(input_string)

        #     # Run before
        #     swap_two(input_string, target, swapper)

        #     # # This conflicted with free language in description section...
        #     dict_str = dict_str.replace("'", '"')

        #     # Run After
        #     swap_two(input_string, target, swapper)


        # else:
        #     # # This conflicted with free language in description section...
        #     dict_str = dict_str.replace("'", '"')


        # try safety cleaning
        dict_str = dict_str.replace("True", "true")
        dict_str = dict_str.replace("False", "false")
        dict_str = dict_str.replace("None", "null")


        # remove trailing delimiter comma
        print(f"{dict_str[:-6]}")
        dict_str = dict_str.replace('",\n}', '"\n}')

    except Exception as e:
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
        print(f"\nTRY AGAIN: trying json.loads(dict_str) Dictionary load failed: {e}")
        print(f"Failed repr(dict_str) -> {repr(dict_str)}")
        return False


    # extraction 2
    try:
        # Extract the value associated with the key 'translation'
        dict_str = dict_data['translation']

    except Exception as e:
        print(f"\nTRY AGAIN: check_function_description_keys() extraction 2 from translation = dict_data['translation'] failed: {e}")
        print(f"Failed repr(dict_str) -> {repr(dict_str)}")
        return False


    # try:
    #     # if test fails
    #     if dict_leaf_detection_boolean_true_means_defective(dict_str):
    #         return False

    # except Exception as e:
    #     print(f"\nTRY AGAIN: dict_leaf_detection_boolean_true_means_defective() empty or stub leaf found: {e}")
    #     print(f"Failed dict_str -> {dict_str}")
    #     return False


    print(f"\n  final extracted from markdown, dict, etc. ->{repr(dict_str)}")

    # if ok...
    return dict_str



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
    text_input = re.sub(r'\s+', ' ', text_input.strip())

    role = "system"

    context_history.append(segment_for_adding_to_context_history(role, text_input))

    # # inspection
    # print("set_translator__system_prompt -> ", context_history)

    return context_history


"""## Add 'user' request for translation"""


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

"""# json inspection"""


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


import json
import re


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


# # Example input
# input_str = '\'{"translation": "S\\\'inscrier"}\''
# json_obj = clean_and_convert_to_json(input_str)

# print(json_obj)


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


import re

def remove_underscores_from_strings_in_list(list_of_strings):
    """
    Removes single underscores and escaped underscores from each string in a list.

    Parameters:
    - list_of_strings (list of str): A list where each element is a string that may contain 
      single underscores, single escaped underscores, or double escaped underscores.

    Returns:
    - list of str: A new list of list_of_strings with all such underscores removed.
    """
    pattern = r'(\\{0,20})_'
    cleaned_list_of_strings = [re.sub(pattern, ' ', string) for string in list_of_strings]

    return cleaned_list_of_strings


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
        strings[i] = ' '.join(new_words)

# Helper Function
def check_structure_of_response(dict_str):
    """

    """
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
        print(f"check_structure_of_response error parsing ai translation_list {str(e)}")
        return False


# Helper Function
def task_check_structure_of_response(task_mode, dict_str):
    """
    for tasks, see modes json or |||

    """

    try:
        # print(f"\n\n Starting check_structure_of_response, dict_str -> {repr(dict_str)} {type(dict_str)}")
        print(f"\n\n Starting check_structure_of_response, dict_str ")

        if "simple" in task_mode:


            # if "task_mode == "open_task"":

            #     json_format = {
            #         "solution":        
            #         {
            #             "solution_plan_outline": "",
            #             "draft_revisions_and_comments": "",
            #             "final_answer": "",
            #         }
            #     }



            # elif task_mode == "multiple_choice":
            #     json_format = {
            #         "solution":        
            #         {
            #             "solution_plan_outline": "",
            #             "draft_revisions_and_comments": "",
            #             "final_answer": int,
            #         }
            #     }




            # Define the regex pattern to match text between triple pipes
            pattern = r"\|\|\|(.+?)\|\|\|"

            # Use re.findall to find all occurrences that match the pattern
            matches_list = re.findall(pattern, dict_str)

            # matches_list is a list of all captured groups in the text
            # If you expect only one match and want to return just that, you can adjust the code accordingly

            strings_to_remove = [
                "final answer option number",
            ]


            matches_list = remove_specific_strings(matches_list, strings_to_remove)

            response_to_task = matches_list[0]

            # cleaned_matches_list = remove_underscores_from_strings_in_list(matches_list)

            # translation = cleaned_matches_list

            # # Remove duplicates
            # translation_set = set(translation)
            # response_to_task = list(translation_set)

            # # adjust all-capitalized words to only starting with a capital letter
            # adjust_capitalization(response_to_task)

            # inspection
            print(f"task_check_structure_of_response()  response_to_task -> {response_to_task}")

            if len(response_to_task):
                return response_to_task

            else:
                print(f"check_structure_of_response error parsing ai response_to_task")
                return False


        else:

            response_to_task = task_check_function_description_keys(dict_str)

            # cleaned_matches_list = remove_underscores_from_strings_in_list(matches_list)

            # translation = cleaned_matches_list

            # # Remove duplicates
            # translation_set = set(translation)
            # response_to_task = list(translation_set)

            # # adjust all-capitalized words to only starting with a capital letter
            # adjust_capitalization(response_to_task)

            # inspection
            print(f"task_check_structure_of_response()  response_to_task -> {response_to_task}")

            if len(response_to_task):
                return response_to_task

            else:
                print(f"check_structure_of_response error parsing ai response_to_task")
                return False


    except Exception as e:
        print(f"check_structure_of_response error parsing ai response_to_task {str(e)}")
        return False



"""# Call api within: Check json structure against original"""



def extract_values_from_dict(dict_str):

    try:
        # inspection
        print("\n extract_values_from_dict()")
        print(f"dict_str -> {dict_str}")        
        print(f"type(dict_str) -> {type(dict_str)}")


        # Parse the string into a Python dictionary
        dict_data = json.loads(dict_str)
        # Extract the values and convert to a list
        values_list = list(dict_data.values())
        return values_list
    except Exception as e:
       print("extract_values_from_dict failed to get values, maybe bad input")
       return False


def return_list_of_jsons_from_string(dict_str):
    try:

        dict_str = dict_str.replace("\n", " ")

        # Define the pattern to match JSON blocks enclosed in triple backticks
        pattern = r'```json(.*?)```'
        matches = re.finditer(pattern, dict_str)

        # Initialize an empty list to store extracted JSON strings
        json_blocks = []

        for match in matches:
            # Extract the JSON string from the match and append it to the list
            json_blocks.append(match.group(1))

        # Return the list of JSON strings
        return json_blocks[-1]

    except Exception as e:
        raise e



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
    print(f"\n\n json_number_check_structure_of_response_to_list -> {repr(dict_str)} \nType -> {type(dict_str)}")


    extracted_dict = return_list_of_jsons_from_string(dict_str)
    print(f"extracted_dict {extracted_dict}")
    print(f"type(extracted_dict) {type(extracted_dict)}")

    number_list = extract_values_from_dict(extracted_dict) 

    print(f"\n  final extracted from markdown, dict, etc. number_list ->{repr(number_list)}")

    # if ok...
    return number_list


# # Helper Function
# def json_check_structure_of_response(dict_str):
#     """
#     This function CAN fail and should fail
#     if the AI needs to retry at a task.
#     Do not stop server when this this triggers an exception.

#     edge case: before there is a populated output_log

#     if passing, this function will return a valid json object
#     """

#     """
#     Extracts JSON string enclosed between ```json and ``` markers.

#     Parameters:
#     - text (str): The input text containing the JSON block.

#     Returns:
#     - str: The extracted JSON string, or an empty string if no JSON block is found.
#     """
#     print(
#         f"\n\n Starting check_structure_of_response, dict_str -> {repr(dict_str)} {type(dict_str)}"
#     )

#     # input("breakpoint")

#     ########################
#     # Check Json Formatting
#     ########################

#     # # pre-check
#     #     # load
#     # try:
#     #     if "'" not in dict_str:

#     #         # Load the string into a Python dictionary
#     #         dict_data = json.loads(dict_str)

#     #         dict_str = dict_data['translation']

#     #         if dict_leaf_detection_boolean_true_means_defective(dict_str):
#     #             return dict_str

#     #         else:
#     #             print(f"Failed dict_str precheck")

#     # except:
#     #     print(f"Failed dict_str precheck")

#     # extraction 1
#     try:
#         if """```json""" in dict_str:

#             pattern = r"```json\n([\s\S]*?)\n```"
#             match = re.search(pattern, dict_str)
#             dict_str = match.group(1) if match else ""

#     except Exception as e:
#         print(
#             f"\nTRY AGAIN: check_structure_of_response() extraction from markdown failed: {e}"
#         )
#         print(f"Failed dict_str -> {repr(dict_str)}")
#         return False

#     print(
#         f"\n  extraction-1 from markdown dict_str -> {repr(dict_str)} {type(dict_str)}"
#     )

#     # ```json\n{\'translation\': "S\'inscrier"}\n```'

#     try:
#         # if ("""{'translation': '""" in dict_str) and ("""'}""" in dict_str):
#         #     dict_str.replace( """{'translation':""", """{"translation":"""  )
#         #     dict_str.replace( """'}""", """"}"""  )

#         # if ("""{\'translation\': \'""" in dict_str) and ("""\'}""" in dict_str):
#         #     dict_str.replace( """{\'translation\':""", """{"translation":"""  )
#         #     dict_str.replace( """\'}""", """"}"""  )

#         if """{\'translation\':""" in dict_str:
#             dict_str = dict_str.replace("""{\'translation\':""", """{"translation":""")

#         if """{'translation':""" in dict_str:
#             dict_str = dict_str.replace("""{'translation':""", """{"translation":""")

#         if """{\\'translation\\':""" in dict_str:
#             dict_str = dict_str.replace(
#                 """{\\'translation\\':""", """{"translation":"""
#             )

#     except Exception as e:
#         print(f"Failed dict_str -> {repr(dict_str)}")
#         return False

#     print(f" dict_str -> {repr(dict_str)} {type(dict_str)}")

#     dict_str = clean_and_convert_to_json(dict_str)
#     print(f" clean_and_convert_to_json dict_str -> {repr(dict_str)} {type(dict_str)}")

#     try:
#         # if ("""{'translation': '""" in dict_str) and ("""'}""" in dict_str):
#         #     dict_str.replace( """{'translation':""", """{"translation":"""  )
#         #     dict_str.replace( """'}""", """"}"""  )

#         # if ("""{\'translation\': \'""" in dict_str) and ("""\'}""" in dict_str):
#         #     dict_str.replace( """{\'translation\':""", """{"translation":"""  )
#         #     dict_str.replace( """\'}""", """"}"""  )

#         if """{\'translation\':""" in dict_str:
#             dict_str = dict_str.replace("""{\'translation\':""", """{"translation":""")

#         if """{'translation':""" in dict_str:
#             dict_str = dict_str.replace("""{'translation':""", """{"translation":""")

#         if """{\\'translation\\':""" in dict_str:
#             dict_str = dict_str.replace(
#                 """{\\'translation\\':""", """{"translation":"""
#             )

#     except Exception as e:
#         print(f"Failed dict_str -> {repr(dict_str)}")
#         return False

#     # clean
#     try:
#         """
#         Swap in and swap out escaped single commas
#         to avoid them being removed during reformatting
#         or the reformatting otherwise breaking the json
#         """

#         # if ("\'" in dict_str) or ("""\\'""" in dict_str):
#         #     print("escaped single quote found")

#         #     input_string = dict_str
#         #     target = "\'"
#         #     swapper = get_swap_in(input_string)

#         #     # Run before
#         #     swap_two(input_string, target, swapper)

#         #     # # This conflicted with free language in description section...
#         #     dict_str = dict_str.replace("'", '"')

#         #     # Run After
#         #     swap_two(input_string, target, swapper)

#         # else:
#         #     # # This conflicted with free language in description section...
#         #     dict_str = dict_str.replace("'", '"')

#         # try safety cleaning
#         dict_str = dict_str.replace("True", "true")
#         dict_str = dict_str.replace("False", "false")
#         dict_str = dict_str.replace("None", "null")

#         # remove trailing delimiter comma
#         print(f"{dict_str[:-6]}")
#         dict_str = dict_str.replace('",\n}', '"\n}')

#     except Exception as e:
#         print(f"\nTRY AGAIN:try safety cleaning: {e}")
#         print(f"Failed repr(dict_str) -> {repr(dict_str)}")
#         return False

#     # load
#     try:
#         # try converting
#         print(f"dict_str -> {repr(dict_str)} {type(dict_str)}")

#         # Load the string into a Python dictionary
#         dict_data = json.loads(dict_str)

#     except Exception as e:
#         print(f"\nTRY AGAIN: trying json.loads(dict_str) Dictionary load failed: {e}")
#         print(f"Failed repr(dict_str) -> {repr(dict_str)}")
#         return False

#     # extraction 2
#     try:
#         # Extract the value associated with the key 'translation'
#         dict_str = dict_data["translation"]

#     except Exception as e:
#         print(
#             f"\nTRY AGAIN: check_structure_of_response() extraction 2 from translation = dict_data['translation'] failed: {e}"
#         )
#         print(f"Failed repr(dict_str) -> {repr(dict_str)}")
#         return False

#     # try:
#     #     # if test fails
#     #     if dict_leaf_detection_boolean_true_means_defective(dict_str):
#     #         return False

#     # except Exception as e:
#     #     print(f"\nTRY AGAIN: dict_leaf_detection_boolean_true_means_defective() empty or stub leaf found: {e}")
#     #     print(f"Failed dict_str -> {dict_str}")
#     #     return False

#     print(f"\n  final extracted from markdown, dict, etc. ->{repr(dict_str)}")

#     # if ok...
#     return dict_str


# """# Call api within: Check json structure against original"""


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


# helper function
def call_api_within_structure_check(context_history, 
                                    use_this_model, 
                                    parameter_dict, 
                                    ai_local_or_cloud_mode, 
                                    skeleton_json):
    retry_counter = 0
    json_ok_flag = False


    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    gguf_model_list = ["jais", "tiny_llama", "mistral7b",]

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
                    'model_path_base': add_segment_to_absolute_base_path("jan/models/"),
                    'model_nickname': use_this_model,
                    'cpp_path': add_segment_to_absolute_base_path("code/llama_cpp/llama.cpp"),
                    'pipeline_mode': mini_gguf_api,
                }


                print(f"configies_dict -> {configies_dict}")

                # # breakpoint
                # input("Breakpoint")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](context_history, parameter_dict, configies_dict)
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

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
            jsonchecked_translation = None
            print(f"Failed: {str(e)}")

        jsonchecked_translation = check_structure_of_response(dict_str)

        if jsonchecked_translation:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(f"\n\nretry_counter -> {retry_counter}\n")

            # # breakpoint
            # input("Breakpoint")

    print(f"retry_counter -> {retry_counter}")

    return jsonchecked_translation


""" call_api_within_number_check"""



# helper function
def general_task_call_api_within_structure_check(context_history, 
                                                 use_this_model, 
                                                 parameter_dict, 
                                                 ai_local_or_cloud_mode,
                                                 task_mode,
                                                 ):
    retry_counter = 0
    json_ok_flag = False


    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    gguf_model_list = ["jais", "tiny_llama", "mistral7b",]

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
                    'model_path_base': add_segment_to_absolute_base_path("jan/models/"),
                    'model_nickname': use_this_model,
                    'cpp_path': add_segment_to_absolute_base_path("code/llama_cpp/llama.cpp"),
                    'pipeline_mode': mini_gguf_api,
                }


                print(f"configies_dict -> {configies_dict}")

                # # breakpoint
                # input("Breakpoint")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](context_history, parameter_dict, configies_dict)
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

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
            jsonchecked_translation = None
            print(f"Failed: {str(e)}")

        jsonchecked_translation = task_check_structure_of_response(dict_str, task_mode)

        if jsonchecked_translation:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(f"\n\nretry_counter -> {retry_counter}\n")

            # # breakpoint
            # input("Breakpoint")

    print(f"retry_counter -> {retry_counter}")

    return jsonchecked_translation


""" call_api_within_number_check"""


# helper function
def number_call_api_within_structure_check(context_history, use_this_model, parameter_dict, ai_local_or_cloud_mode, skeleton_json):
    retry_counter = 0
    json_ok_flag = False


    # see
    mistal_model_list = [
        "mistral-tiny",
        "mistral-small",
        "mistral-large-latest",
    ]
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    gguf_model_list = ["jais", "tiny_llama", "mistral7b",]

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
                    'model_path_base': add_segment_to_absolute_base_path("jan/models/"),
                    'model_nickname': use_this_model,
                    'cpp_path': add_segment_to_absolute_base_path("code/llama_cpp/llama.cpp"),
                    'pipeline_mode': mini_gguf_api,
                }


                print(f"configies_dict -> {configies_dict}")

                # # breakpoint
                # input("Breakpoint")

                ######################
                # local api with gguf
                ######################
                response = configies_dict["pipeline_mode"](context_history, parameter_dict, configies_dict)
                print(response[0])
                print(response[1])
                print(response[2])
                dict_str = response[2]

            ################
            # for cloud api
            ################
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

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
            json_checked_value_list = None
            print(f"Failed: {str(e)}")

        json_checked_value_list = json_number_check_structure_of_response_to_list(dict_str)

        if json_checked_value_list:
            json_ok_flag = True

        else:
            retry_counter += 1
            print(f"\n\nretry_counter -> {retry_counter}\n")

            # # breakpoint
            # input("Breakpoint")

    print(f"retry_counter -> {retry_counter}")

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
    # /home/oops/jan/models/mistral-ins-7b-q4/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    # see https://platform.openai.com/docs/guides/text-generation
    open_ai_model_list = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

    # TODO
    gguf_model_list = ["jais", "tiny_llama", "mistral7b", "mistral"]

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
                use_this_model = get_model_path_by_name("/home/oops/jan/models/", use_this_model)

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
                    'model_path_base': add_segment_to_absolute_base_path("jan/models/"),
                    'model_nickname': use_this_model,
                    'cpp_path': add_segment_to_absolute_base_path("code/llama_cpp/llama.cpp"),
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
            elif use_this_model in mistal_model_list:
                print(f"Mistral api selected...{use_this_model}")
                dict_str = ask_mistral_model(context_history, use_this_model)

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
            jsonchecked_translation = None
            print(f"Failed: {str(e)}")

        jsonchecked_translation = check_structure_of_response(
            dict_str, skeleton_json
        )

        if jsonchecked_translation:
            json_ok_flag = True

        else:
            retry_counter += 1

    print(f"retry_counter -> {retry_counter}")

    return jsonchecked_translation


"""# Put Flesh on the Skeleton
- add translations to the lists
"""

# # helper function
# def set_select_best__system_prompt(context_history, target_language):

#     ########################################
#     # System Prompt to pick best traslation
#     ########################################

#     example_2 = {
#         "translation": "your translation here"
#     }

#     example_bad = {
#       'NOT THIS': 'NO SINGLE QUOTES'
#       }

#     example_bad2 = """{\'translation\': "BAD!! NO SINGLE QUOTES"}"""

#     # set translation language and structure of output in system
#     text_input = f"""
#     You are a helpful expert translator bot that selects high
#     quality professional translations from a list and
#     selects the best translation.

#     You always present your selection in the same precise json format:
#     {example_2}

#     NOT like this with single quotes {example_bad}
#     You never ever write like this: {example_bad2}
#     You never use single quotes around items in a json. EVER!!

#     Your final translation selections are clear, accurate, helpful, honrable, brief, polite, and professional.
#     Always select one best translation, only one.

#     You always do your best to produce top quality results.
#     """
#     role = "system"

#     context_history.append( segment_for_adding_to_context_history(role, text_input) )

#     return context_history


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
    text_input = re.sub(r'\s+', ' ', text_input.strip())

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
    text_input = re.sub(r'\s+', ' ', text_input.strip())

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
    for step in this_path[:-1]:  # Exclude the last step to get to the parent of the terminal-leaf list
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
        parent[last_step] = list(dict.fromkeys(terminal_list))  # Remove duplicates, preserving order

    print("Duplicates removed from terminal-leaf list.")



def extract_row_from_csv(this_row, this_path):
    """
    Extracts a specific row from a CSV file.

    Parameters:
        this_row (int): The index of the row to extract from the CSV.
        this_path (str): The path to the CSV file.

    Returns:
        list: The extracted row as a list of strings. Returns an empty list if the row
              does not exist or the file cannot be opened.
    """
    try:
        with open(this_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == this_row:
                    return row
    except FileNotFoundError:
        print(f"File not found: {this_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Return empty list if the row was not found or an error occurred
    print("\n\n\nWARNING: NOW ROW FOUND!!! extract_row_from_csv()")
    return []

# Example usage
# Assuming the CSV file and the row index you want to extract
# row_index = 5
# file_path = 'path_to_your_file.csv'
# extracted_row = extract_row_from_csv(row_index, file_path)
# print(extracted_row)



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
    no_punctuation = lowercased.translate(str.maketrans('', '', string.punctuation))
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
    print(f"Starting lower_clean_string_or_list(input_string_or_list), input_string_or_list -> {input_string_or_list}")

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
        print(f"Warning: lower_clean_string_or_list() input not string or list input_string_or_list -> {type(input_string_or_list)}{input_string_or_list}")

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

# def extract_values_by_paths(json_object, paths_list):
#     values = []
#     for path in paths_list:
#         value = json_object
#         for step in path:
#             if step.isdigit():
#                 step = int(step)  # Convert to integer if it's a list index
#             value = value[step]
#         values.append(value)
#     return values


# def insert_values_by_paths(skeleton_json, paths_list, translated_values):
#     for path, translated_value in zip(paths_list, translated_values):
#         target = skeleton_json
#         for step in path[:-1]:
#             step = int(step) if step.isdigit() else step
#             target = target[step]
#         final_step = path[-1]
#         final_step = int(final_step) if final_step.isdigit() else final_step
#         target[final_step] = translated_value


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
                print(f"Path error: {'/'.join(path[:i+1])} not found.")
        except TypeError as e:
            print(f"TypeError accessing {'/'.join(path[:i])}: {str(e)}")

            # If for some reason the loop completes without appending (shouldn't happen if errors are caught)
            print(f"\n\n\nwarning: core_insert_string_value_by_path() no intput? new_value -> {new_value}  \n\n\n")



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

    print(f"start: insert_string_value_by_path() new_value_or_list -> {new_value_or_list}")

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
                core_insert_string_value_by_path(dict_tree_structure, path, this_new_value)
            else:
                print(f"item overlap: {lower_clean_string_or_list(this_new_value)}{existing_item_list}")

    else:
        print(f"warning: insert_string_value_by_path() no intput? {new_value_or_list}")



# def insert_string_value_by_path(json_structure, path, new_value):
#     """
#     Attempts to append a value to a list at the specified path within the json_structure.
#     Provides more detailed error messages if the path is not found.

#     :param json_structure: The JSON structure to update.
#     :param path: The path to the target list as a list of keys.
#     :param new_value: The value to append.
#     """
#     target = json_structure
    

#     # Check if the value is a string
     
#     if isinstance(new_value, str):
#         for i, step in enumerate(path):
#             try:
#                 if isinstance(target, dict) and step in target:
#                     if i == len(path) - 1:  # If it's the final step, append new_value
#                         if isinstance(target[step], list):
#                             target[step].append(new_value)
#                             return json_structure  # Return updated structure
#                         else:
#                             raise ValueError(
#                                 f"Target at path {'/'.join(path)} is not a list."
#                             )
#                     else:  # Not the final step, move deeper into the structure
#                         target = target[step]
#                 else:
#                     raise ValueError(f"Path error: {'/'.join(path[:i+1])} not found.")
#             except TypeError as e:
#                 raise TypeError(f"TypeError accessing {'/'.join(path[:i])}: {str(e)}")

#         # Check if the value is a list
#     elif isinstance(new_value, list):
#         for this_new_value in new_value:
#             for i, step in enumerate(path):
#                 try:
#                     if isinstance(target, dict) and step in target:
#                         if i == len(path) - 1:  # If it's the final step, append new_value
#                             if isinstance(target[step], list):
#                                 target[step].append(this_new_value)
#                                 return json_structure  # Return updated structure
#                             else:
#                                 raise ValueError(
#                                     f"Target at path {'/'.join(path)} is not a list."
#                                 )
#                         else:  # Not the final step, move deeper into the structure
#                             target = target[step]
#                     else:
#                         raise ValueError(f"Path error: {'/'.join(path[:i+1])} not found.")
#                 except TypeError as e:
#                     raise TypeError(f"TypeError accessing {'/'.join(path[:i])}: {str(e)}")
    
#     else:
#         print ("warning: insert_string_value_by_path() no intput?")
#         return False
    
#     # If for some reason the loop completes without appending (shouldn't happen if errors are caught)
#     raise ValueError("Failed to append the value: Path processing error.")

# def insert_string_value_by_path(json_structure, path, new_value):
#     """
#     Appends a value to a list at the specified path within the json_structure.

#     :param json_structure: The JSON structure (dictionary) to update.
#     :param path: A list representing the path to the target list. Each element in the path
#                  is a dictionary key.
#     :param new_value: The new value to append to the list at the target path.
#     """
#     target = json_structure
#     # Navigate through the path except for the last step
#     for step in path[:-1]:
#         if isinstance(target, dict) and step in target:
#             target = target[step]
#         else:
#             raise ValueError(f"Path error: {step} not found.")

#     final_step = path[-1]
#     if isinstance(target, dict) and final_step in target and isinstance(target[final_step], list):
#         target[final_step].append(new_value)
#     else:
#         raise ValueError(f"Final step error: {final_step} not found or not a list.")


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

# Main Function


# def translate_json(
#     list_of_targeted_languages,
#     use_this_model,
#     ai_local_or_cloud_mode,
#     number_of_preliminary_translations,
# ):

#     ######################
#     # Translation Factory
#     ######################

#     # Example usage
#     json_files_list = list_files_in_aitaskfiles_dir()

#     if not json_files_list:
#         print("Error: You missed a step, No Json files were provided.")
#         raise "No Json files were provided."

#     # inspection
#     print("JSON files in the CWD:", json_files_list)

#     for this_original_json_file in json_files_list:

#         # Load the original JSON file
#         original_data = load_json_file(this_original_json_file)

#         # Create a new JSON file with the deep empty structure
#         name_of_skeleton_saved_file = "empty_lists_" + "_" + this_original_json_file

#         skeleton_json = create_empty_json_file(
#             original_data, name_of_skeleton_saved_file
#         )

#         name_of_EMPTY_dict_of_selected_best_saved_file = (
#             "empty_string_best_" + "_" + this_original_json_file
#         )
#         dict_of_selected_best = create_empty_selectbest_frame(
#             original_data, name_of_EMPTY_dict_of_selected_best_saved_file
#         )

#         #########################################
#         # Crawler: Make preliminary Translations
#         #########################################

#         paths_list = generate_paths(original_data)
#         check_paths_list = generate_paths(skeleton_json)
#         dict_of_selected_best_paths_list = generate_paths(dict_of_selected_best)

#         print(
#             f"""
#         paths_list                   {paths_list}
#         check_paths_list             {check_paths_list}
#         dict_of_selected_best_paths_list {dict_of_selected_best_paths_list}
#         """
#         )

#         # # breakpoint
#         # input("breakpoint")

#         # Sanity check
#         if paths_list != dict_of_selected_best_paths_list:
#             error_message = "Error: Path lists between the original JSON and its skeleton do not match."
#             print(error_message)
#             raise ValueError(error_message)

#         # for this language
#         for target_language in list_of_targeted_languages:

#             # make a blank frame of lists for the translations
#             populated_skeleton = skeleton_json

#             # for this leaf
#             for this_path in paths_list:
            
#                 print("starting path")

#                 untranslated_leaf = extract_value_by_path(original_data, this_path)

#                 # breakpoint
#                 print(f"\n\n breakpoint 5: untranslated_leaf -> {untranslated_leaf}")
#                 # input("breakpoint")

#                 # make empty conversation
#                 # reset context history for new 'conversation' about translation
#                 context_history = []

#                 # Set Prompts per one language
#                 # System Instructions
#                 context_history = set_translator__system_prompt(
#                     context_history, target_language
#                 )
#                 # User Prompt
#                 context_history = set_translate__user_prompt(
#                     context_history, target_language, untranslated_leaf
#                 )

#                 # breakpoint
#                 print(f"\n\n breakpoint 5: context_history -> {context_history}")
#                 # input("breakpoint")

#                 # making N translation-versions
#                 for i in range(number_of_preliminary_translations):
#                     """
#                     using both the populated skeleton and the original file:
#                     - tree-search through both (original and blank-list-skeleton) in the same way
#                     - check and guarantee that the dict-address (often nested)
#                       is the same for the original and where the answers are recorded
#                     - part 1: extract just the next terminal leaf, return this.
#                     separate step next ->
#                     - part 2: put a new (language translated value) in the corresponding
#                     place in blank-skeleton list.
#                     """
#                     """
#                     ####################
#                     # Crawler functions
#                     ####################

#                     1. make list of paths   generate_paths(json_object)
#                     2. extrac path value    extract_value_by_path(original_data, this_path)
#                      (translate)
#                     3. add to list          insert_string_value_by_path(json_structure, path, new_value)
#                     4. write final value    insert_int_value_by_path(skeleton_json, paths_list, translated_values)

#                     """

#                     ############
#                     # Translate
#                     ############
#                     translated_value_list = call_api_within_structure_check(
#                         context_history, use_this_model, ai_local_or_cloud_mode, skeleton_json
#                     )

#                     print(f"\nTranslated: translated_value_list: {translated_value_list}")


#                     for translated_value in translated_value_list:

#                         # add-insert value to json
#                         print(f"Before appending: {skeleton_json}")
#                         print(f"this_path -> {this_path}")
#                         skeleton_json = insert_string_value_by_path(
#                             skeleton_json, this_path, translated_value
#                         )
#                         print(f"After appending: {skeleton_json}")

#                 #####################################################
#                 # Select Top Top Goodest Translation Star-Good-Prime
#                 #####################################################

#                 set_save_json_to_file(
#                     populated_skeleton,
#                     this_original_json_file,
#                     target_language,
#                     "set_of_translations_",
#                 )

#                 # reset context history for new 'conversation' about selection
#                 context_history = []

#                 print("\n\n\nSelect Top Top Goodest Translation Star-Good-Prime")
#                 # # inspection breakpoint
#                 # print(f"\n\n breakpoint 5: populated_skeleton -> {populated_skeleton}")
#                 # # input("breakpoint")

#                 # set prompts to select best translation
#                 list_of_options = extract_value_by_path(skeleton_json, this_path)

#                 # System Instructions
#                 context_history = set_select_best__system_prompt(
#                     context_history, target_language
#                 )
#                 # User Prompt
#                 context_history = set_select_best__user_prompt(
#                     context_history, target_language, list_of_options, untranslated_leaf
#                 )

#                 #################
#                 #################
#                 # Select Bestest
#                 #################
#                 #################
#                 # selected_bestest_value = call_api_within_structure_check(
#                 #     context_history, use_this_model, ai_local_or_cloud_mode, skeleton_json
#                 # )


#                 selected_is_in_list_ok = False
#                 fail_counter = 0

#                 while not selected_is_in_list_ok:



#                     selected_bestest_value = call_api_within_structure_check(
#                         context_history, use_this_model, ai_local_or_cloud_mode, skeleton_json
#                     )

#                     print(type(selected_bestest_value))

#                     selected_bestest_value = selected_bestest_value[0]

#                     print(f"selected_bestest_value -> {selected_bestest_value} vs. list_of_options -> {list_of_options}")

#                     # Make sure selected item is in the list (and not a new halucination or mutation)
#                     if selected_bestest_value in list_of_options:
#                         selected_is_in_list_ok = True

#                     else:
#                         fail_counter += 1
#                         print(f"\n\n\nfail_counter -> {fail_counter}")

#                 # add value to json
#                 dict_of_selected_best = insert_int_value_by_path(
#                     dict_of_selected_best, this_path, selected_bestest_value
#                 )

#             ##########################
#             # per language: save file
#             ##########################
#             print("trying to save file...")

#             # try:
#             #     # if test fails
#             #     if dict_leaf_detection_boolean_true_means_defective(dict_of_selected_best):
#             #         return False

#             # except Exception as e:
#             #     print(f"\nTRY AGAIN: dict_leaf_detection_boolean_true_means_defective() empty or stub leaf found: {e}")
#             #     print(f"Failed dict_str -> {dict_of_selected_best}")
#             #     return False

#             # add value to json
#             save_json_to_file(
#                 dict_of_selected_best, this_original_json_file, target_language, "selected_"
#             )



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
        # Ensure the index is within the range of available keys
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
        result = [item if isinstance(item, int) else int(item) for item in input_list if isinstance(item, int) or item.isdigit()]

        return result

    except:
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
    print("JSON files in the in-try directory:", json_files_list)

    for this_original_json_file in json_files_list:

        # add to path
        "ai_task_files"

        # Determine the path to the file that should be saved
        file_path = os.path.join("ai_task_files", this_original_json_file)


        # Load the original JSON file
        original_data = load_json_file(file_path)

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

        # # breakpoint
        # input("breakpoint")

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

                    untranslated_leaf = extract_string_value_by_path(original_data, this_path)

                    # # breakpoint
                    # print(f"\n\n breakpoint 5: untranslated_leaf -> {untranslated_leaf}")
                    # input("breakpoint")

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

                    # # breakpoint
                    # print(f"\n\n mini breakpoint 5: context_history -> {context_history}")
                    # input("breakpoint")

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
                            skeleton_json
                        )

                        # remove overt duplicates
                        # Convert list to set to remove duplicates
                        unique_set = set(translated_value)
                        # Convert set back to list
                        translated_value = list(unique_set)

                        # add-insert value to json
                        print(f"populated_skeleton Before appending: {populated_skeleton}")
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

                        print(f"populated_skeleton After appending: {populated_skeleton}")


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
                    # # inspection breakpoint
                    # print(f"\n\n breakpoint 5: populated_skeleton -> {populated_skeleton}")
                    # # input("breakpoint") 

                    remove_duplicates_from_terminal_list(populated_skeleton, this_path)

                    # set prompts to select best translation
                    list_of_options = extract_value_by_path(populated_skeleton, this_path)

                    # # Combine into one list of strings using list comprehension
                    # list_of_options = [item for sublist in list_of_options_nested for item in sublist]
                    # list_of_options = list_of_options_nested

                    # turn list of options int dict
                    dict_of_options = {option: "score_here" for option in list_of_options}

                    # turn list of options int dict
                    list_dict_of_options = {option: [] for option in list_of_options}


                    print(
                        f"""
                    mini_translate_json() Select Top Top
                    list_of_options        -> {list_of_options}
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
                    #     context_history, target_language, list_of_options, untranslated_leaf
                    # )


                    # context_history = f"""
                    # Select the most accurate {target_language} translation for '{untranslated_leaf}' from these options: {list_of_options}. 
                    # Place your choice, spelled exactly the same, between triple pipes, like this: |||best_selection|||. 
                    # No additional comments. A tasty reward awaits your accurate selection."""

                    # """
                    # Select the most accurate {target_language} translation for '{untranslated_leaf}' from these options: {list_of_options}. 
                    # Indicate your choice by placing it between triple pipes, like this: |||best_selection|||. 
                    # No additional comments. The reward of a job well done awaits your accurate selection!"""

                    # context_history = f"""
                    # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_leaf}' from these options: {list_of_options}. 
                    # Place your evaluations in order as Pipe-Separated Values. like this four options |#|#|#|#| or just one item like this |#| 
                    # No additional comments. A tasty reward awaits your accurate selection """


                    answer_form = {
                        "t-1": "score_here", 
                        "t-2": "score_here",
                        "t-3": "score_here"
                    }

                    answer_form = {
                        "translation-1": "score_here", 
                        "translation-2": "score_here",
                        "translation-3": "score_here"
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
                    # No additional comments. A tasty reward awaits your accurate selection."""


                    # # breakpoint
                    # print(f"\n\n context_history -> {context_history}")
                    # input("breakpoint")

                    ###################
                    ###################
                    # Select Bestest
                    # By ranked choice
                    ###################
                    ###################



                    # turn list of options int dict
                    dict_of_options = {option: None for option in list_of_options}
                    # get highest ranked item:
                    best_key_option = None

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
                                context_history, use_this_model, parameter_dict, ai_local_or_cloud_mode, skeleton_json
                            )

                            print(f"\n\nlist_of_votes -> {list_of_votes}")
                            print(f"type list_of_votes -> {type(list_of_votes)}")

                            # filter out words and make type int
                            list_of_votes = filter_list_convert_to_int(list_of_votes)

                            print(f"list_of_votes -> {list_of_votes}")
                            print(f"list_of_options -> {list_of_options}")
                            print(f"type list_of_votes -> {type(list_of_votes)}\n\n")

                            print(f"list_dict_of_options -> {list_dict_of_options}")

                            if list_of_votes:

                                # if there is one vote per candidate, list each candidates votes
                                if len(list_of_votes) == len(list_of_options):
                                    add_ranks_votes_to_candidate(list_of_votes, list_dict_of_options)

                                    print(f"new list_dict_of_options -> {list_dict_of_options}")

                                    # exit loop
                                    vote_check_ok = True

                                else:  # if len of list is wrong
                                    while_counter += 1
                                    print("len of list is wrong")

                            else:  # if no list at all!
                                while_counter += 1
                                print("no list at all!")

                    # tally the ranked votes and pick the winner
                    best_key_option = extract_top_rank(list_dict_of_options)

                    print(f"best_key_option -> {best_key_option}")


                    # add value to json
                    insert_int_value_by_path(
                        dict_of_selected_best, this_path, best_key_option
                    )

                    print(f"dict_of_selected_best -> {dict_of_selected_best}")

                    # Exit While
                    print("\nHats in the air, we can all leave. Buubye!!\n\n\n")
                    leaf_ok_flag = True

            ##########################
            # per language: save file
            ##########################
            print(f"""
                Trying to save file...

                dict_of_selected_best   -> {dict_of_selected_best}
                this_original_json_file -> {this_original_json_file}
                target_language         -> {target_language}

                  """)


            # try:
            #     # if test fails
            #     if dict_leaf_detection_boolean_true_means_defective(dict_of_selected_best):
            #         return False

            # except Exception as e:
            #     print(f"\nTRY AGAIN: dict_leaf_detection_boolean_true_means_defective() empty or stub leaf found: {e}")
            #     print(f"Failed dict_str -> {dict_of_selected_best}")
            #     return False

            # add value to json
            save_json_to_file(
                dict_of_selected_best, this_original_json_file, target_language, "selected_"
            )



def do_task_please(
    task_mode,
    list_of_models,
    ai_local_or_cloud_mode,
    file_type_list,
    number_of_preliminary_drafts,
    number_of_ranked_votes,
    index_of_task=0,
    index_of_options=1,
    parameter_dict=None,
):

    """
    Output format notes:

    "solution":
        {
            "solution_plan_outline":
            "draft_revisions_and_comments":
            "final_answer":
        }
    """


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
    the answer_(original_name)_model_name_(timestamp)_file 


    """


    # Example usage
    task_files_list = list_files_in_aitaskfiles_dir(file_type_list)

    if not task_files_list:
        print("Error: You missed a step, No task files were provided.")
        raise "No task files were provided."

    # inspection
    print(f"Task files in folder -> {task_files_list}")

    for this_original_task_file in task_files_list:

        for use_this_model in list_of_models:
            ###
            # Make answers file pathway.
            ###
            answer_file_path = make_answers_directory_and_csv_path(this_original_task_file, use_this_model)

            print(f"answer_file_path -> {answer_file_path}")


            #########################################
            # Crawler: Make preliminary Translations
            #########################################


            print(
                f"""
            do_task_please()
            Starting this file: 
            this_original_task_file      -> {this_original_task_file}
            """
            )

            # # breakpoint
            # input("breakpoint")

            """
            To stay lite:
            - get the number of rows in the csv
            - for each row, access that row only
            (note...a csv might be a little mega huge)

            """

            def get_csv_len_in_rows(path):
                try:
                    with open(path, 'r') as f:
                        reader = csv.reader(f)
                        row_count = sum(1 for _ in reader)
                    return row_count

                except Exception as e:
                    raise e

            this_original_task_file_length = get_csv_len_in_rows(this_original_task_file)



            # for this language
            # NON-header mode, skip first row
            for this_row in range(this_original_task_file_length - 1):

                print(f"this_row -> {this_row}")


                """
                get task from csv
                """
                task_from_instructions = ""

                task_ok_flag = False
                task_fail_counter = 0

                while not task_ok_flag:

                    if task_fail_counter > 10:
                        raise f"task_fail_counter > 10 -> {task_fail_counter}"

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

                    row_as_list = extract_row_from_csv(this_row, this_original_task_file)

                    this_task = row_as_list[index_of_task]
                    these_options = row_as_list[index_of_options]

                    # # breakpoint
                    # print(f"\n\n breakpoint 5: untranslated_task -> {untranslated_task}")
                    # input("breakpoint")

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


                    multiple_choice_solution_body = {
                        "solution":        
                        {
                            "solution_plan_outline": "",
                            "draft_revisions_and_comments": "",
                            "final_answer_option_number": int,
                        }
                    }

                    multiple_choice_solution_body = {
                        "solution_plan_outline": "",
                        "draft_revisions_and_comments": "",
                        "final_answer_option_number": int,
                    }

                    simple_multiple_choice_solution_body = """
                    solution_plan_outline: "", 
                    draft_revisions_and_comments: "", 
                    Then in triple pipes:
                    |||final answer option number|||
                    """

                    open_solution_body = {
                        "solution":        
                        {
                            "solution_plan_outline": "",
                            "draft_revisions_and_comments": "",
                            "final_answer": "",
                        }
                    }

                    simple_open_solution_body = """
                    Plan, draft, revisions, and comments, 
                    then in triple pipes:
                    |||final answer option number|||
                    """

                    if task_mode == "open_task":

                        ############
                        # Open Task
                        ############
                        context_history = f"""

                        What is the best response for this task? 
                        {this_task}

                        Give your answer in this format:
                        {open_solution_body}
                        """

                    elif task_mode == "simple_open_task":

                        ############
                        # Open Task
                        ############
                        context_history = f"""

                        What is the best response for this task? 
                        {this_task}

                        Give your answer in this format:
                        {simple_open_solution_body}
                        """

                    elif task_mode == "multiple_choice":

                        ##################
                        # Multiple Choice
                        ##################
                        context_history = f"""

                        Which from this list of possible responses is the best response to being given this task?

                        For this task: 
                        {this_task} 

                        From this list of possible responses: 
                        {these_options} 

                        Your answer must be the number of the answer-option in sequence, where "1" is the first answer option.

                        Giveyour answer in this format:
                        {multiple_choice_solution_body}
                        """

                    elif task_mode == "simple_multiple_choice":

                        ##################
                        # Multiple Choice
                        ##################
                        context_history = f"""

                        Which from this list of possible responses is the best response to being given this task?

                        For this task: 
                        {this_task} 

                        From this list of possible responses: 
                        {these_options} 

                        Your answer must be the number of the answer-option in sequence, where "1" is the first answer option.

                        Giveyour answer in this format:
                        {simple_multiple_choice_solution_body}
                        """


                    old_history = context_history

                    # # breakpoint
                    # print(f"\n\n mini breakpoint 5: context_history -> {context_history}")
                    # input("breakpoint")

                    list_of_options = []

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

                        ############
                        # Translate
                        ############
                        task_response_string = general_task_call_api_within_structure_check(
                            context_history, 
                            use_this_model, 
                            parameter_dict, 
                            ai_local_or_cloud_mode,
                            task_mode,
                        )

                        # # remove overt duplicates
                        # # Convert list to set to remove duplicates
                        # unique_set = set(task_response_string)
                        # # Convert set back to list
                        # task_response_string = list(unique_set)


                        print(f"task_response_string -> {task_response_string}")
                        print(f"type task_response_string -> {type(task_response_string)}")

                        task_response_string = str_to_int_or_none(task_response_string)

                        if task_response_string:
                            list_of_options.append(int(task_response_string))

                    #####################################################
                    # Select Top Top Goodest Translation Star-Good-Prime
                    #####################################################

                    # reset context history for new 'conversation' about selection
                    context_history = []

                    print("\n\n\nSelect Top Top Goodest Translation Star-Good-Prime")
                    # # inspection breakpoint
                    # print(f"\n\n breakpoint 5: populated_skeleton -> {populated_skeleton}")
                    # # input("breakpoint") 

                    # Combine into one list of strings using list comprehension
                    set_list_of_options = set(list_of_options)
                    list_of_options = list(set_list_of_options)

                    # turn list of options int dict
                    dict_of_options = {option: "score_here" for option in list_of_options}

                    # turn list of options int dict
                    list_dict_of_options = {option: [] for option in list_of_options}


                    print(
                        f"""
                    mini_translate_json() Select Top Top
                    list_of_options        -> {list_of_options}
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
                    #     context_history, target_language, list_of_options, untranslated_task
                    # )


                    # context_history = f"""
                    # Select the most accurate {target_language} translation for '{untranslated_task}' from these options: {list_of_options}. 
                    # Place your choice, spelled exactly the same, between triple pipes, like this: |||best_selection|||. 
                    # No additional comments. A tasty reward awaits your accurate selection."""

                    # """
                    # Select the most accurate {target_language} translation for '{untranslated_task}' from these options: {list_of_options}. 
                    # Indicate your choice by placing it between triple pipes, like this: |||best_selection|||. 
                    # No additional comments. The reward of a job well done awaits your accurate selection!"""

                    # context_history = f"""
                    # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {list_of_options}. 
                    # Place your evaluations in order as Pipe-Separated Values. like this four options |#|#|#|#| or just one item like this |#| 
                    # No additional comments. A tasty reward awaits your accurate selection """

                    answer_form = {
                        "option-1": "score_here", 
                        "option-2": "score_here",
                        "option-3": "score_here"
                    }

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

                    context_history = f"""
                    Evaluate each solution for this task'{old_history}' from these options: {dict_of_options}. 
                    Place your evaluations  (0-10, 0 is bad, 10 is good) as the value to a key in Json format. Return your markdown json object 
                    listing each option only as "option-number" 
                    as: 
                    ```json 
                    {answer_form} 
                    ```
                    Just fill in the score, that's all. One key-value pair per option (one generic key, one value which is your score -> "option-1": "score_here", not nested). 
                    No additional comments. A tasty reward awaits your accurate selection. 
                    """

                    # context_history = f"""
                    # Evaluate (0-10, 10 is great) each {target_language} translation for '{untranslated_task}' from these options: {dict_of_options}. 
                    # Place your evaluations as value to the key in Json format. Return your properly formatted dict as:
                    # '''json

                    # ''' 
                    # No additional comments. A tasty reward awaits your accurate selection."""


                    question_task_prompt = context_history


                    # # breakpoint
                    # print(f"\n\n context_history -> {context_history}")
                    # input("breakpoint")

                    ###################
                    ###################
                    # Select Bestest
                    # By ranked choice
                    ###################
                    ###################


                    # turn list of options int dict
                    dict_of_options = {option: None for option in list_of_options}
                    # get highest ranked item:
                    best_key_option = None

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
                                context_history, use_this_model, parameter_dict, ai_local_or_cloud_mode
                            )

                            print(f"\n\nlist_of_votes -> {list_of_votes}")
                            print(f"type list_of_votes -> {type(list_of_votes)}")

                            # filter out words and make type int
                            list_of_votes = filter_list_convert_to_int(list_of_votes)

                            print(f"list_of_votes -> {list_of_votes}")
                            print(f"list_of_options -> {list_of_options}")
                            print(f"type list_of_votes -> {type(list_of_votes)}\n\n")

                            print(f"list_dict_of_options -> {list_dict_of_options}")

                            if list_of_votes:

                                # if there is one vote per candidate, list each candidates votes
                                if len(list_of_votes) == len(list_of_options):
                                    add_ranks_votes_to_candidate(list_of_votes, list_dict_of_options)

                                    print(f"new list_dict_of_options -> {list_dict_of_options}")

                                    # exit loop
                                    vote_check_ok = True

                                else:  # if len of list is wrong
                                    while_counter += 1
                                    print("len of list is wrong")

                            else:  # if no list at all!
                                while_counter += 1
                                print("no list at all!")

                    # tally the ranked votes and pick the winner
                    best_key_option = extract_top_rank(list_dict_of_options)

                    print(f"best_key_option -> {best_key_option}")

                    date_time = datetime.now(UTC)
                    readable_timestamp = date_time.strftime("ymd_%Y-%m-%d")

                    answer_row = f"{this_row}, {best_key_option}, {use_this_model}, {this_original_task_file}, {task_from_instructions}, {question_task_prompt}, {readable_timestamp}"

                    # append to answer_file_path

                    with open(answer_file_path, 'a', newline='') as csvfile:
                        csvwriter = csv.writer(csvfile, delimiter=',')
                        csvwriter.writerow(answer_row)


                    # Exit While
                    print("\nHats in the air, we can all leave. Buubye!!\n\n\n")
                    task_ok_flag = True


                ##########################
                # save file
                ##########################
                print("All done? Anyone here...hello? What was that? Is someone")

                # try:
                #     # if test fails
                #     if dict_task_detection_boolean_true_means_defective(dict_of_selected_best):
                #         return False

                # except Exception as e:
                #     print(f"\nTRY AGAIN: dict_task_detection_boolean_true_means_defective() empty or stub task found: {e}")
                #     print(f"Failed dict_str -> {dict_of_selected_best}")
                #     return False



"""# Tranlate Json Files
- Set your language list
- Pick your model
- upload your json files
- Run
- Download / Get your translations (and inspection files if needed)
"""

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

################################################
# Local Off-line Mode, or Online Cloud-api Mode
################################################

"""
"cloud_api"

"gguf"
"""


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



"""# Choices:"""
# use_this_model = "gpt-3.5-turbo"
# use_this_model = "mistral-large-latest"

use_this_model = "mistral-7b-instruct"
# use_this_model = "mistral-small"
# use_this_model = "tinyllama"


# Choice:
ai_local_or_cloud_mode = "cloud_api"
ai_local_or_cloud_mode = "gguf"
list_of_targeted_languages = ["French", "German",]


number_of_preliminary_drafts = 2
number_of_ranked_votes = 1

mini_translate_json(
    list_of_targeted_languages,
    use_this_model,
    ai_local_or_cloud_mode,
    number_of_preliminary_drafts,
    number_of_ranked_votes,
    parameter_dict,
)

