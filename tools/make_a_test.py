import json


def multiple_choice_append_to_jsonl(file_path, task, options, answer_index_from_1):
    data = {
        "task": task,
        "options": options,
        "answer_from_index_start_at_1": answer_index_from_1,
    }

    with open(file_path, "a", encoding="utf-8") as file:
        json.dump(data, file)
        file.write("\n")


def error_exaplain_equestion_append_to_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as file:
        json.dump(data, file)
        file.write("\n")


def open_question_append_to_jsonl(file_path, task, options, answer):
    data = {
        "task": task,
        "options": options,
        "answer": answer,
    }

    with open(file_path, "a", encoding="utf-8") as file:
        json.dump(data, file)
        file.write("\n")


task_file_directory = "ai_task_files"

########################
# Multiple Choice Tests
########################
# multiple_choice_append_to_jsonl(
#     f"{task_file_directory}/my_multiple_choice_test_1.jsonl", "What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"], "1")

# multiple_choice_append_to_jsonl(
#     f"{task_file_directory}/my_multiple_choice_test_1.jsonl", "What is the largest planet in our solar system?", ["Earth", "Jupiter", "Mars", "Venus"], "2")


multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a cat an animal?", ["yes", "no"], "1")

multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a dog an animal?", ["yes", "no"], "1")

multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a human an animal?", ["yes", "no"], "1")

multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a rock an animal?", ["yes", "no"], "2")

multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a planet an animal?", ["yes", "no"], "2")

multiple_choice_append_to_jsonl(
    f"{task_file_directory}/animal_multiple_choice_test_1.jsonl", "Is a void an animal?", ["yes", "no"], "2")

####################
# Open Answer Tests
####################

"""
mark answers with numbers
answer A is 1
answer b is 2
"""
# "question", ["list","of","answers"], "answer_index_from_1"
# "The city councilmen refused the demonstrators a permit because they feared violence.", ["The city councilmen", "The demonstrators"], "1"



####################
# Open Answer Tests
####################
open_question_append_to_jsonl(f"{task_file_directory}/my_open_answer_test_1.jsonl", "What is the largest planet in our solar system?", ["Earth", "Jupiter", "Mars", "Venus"], "Jupiter")



####################
# Open Answer Tests
####################


# data = {
#     "task": task,
#     "options": options,
#     "answer_from_index_start_at_1": [
#         "right answer", 
#         "wrong answer", 
#         "wrong answer", 
#         "wrong answer",
#     ],
#     error_comment_data_lookup_table:{
#         2: "this reason",
#         3: "this reason",
#         4: "this reason",
#     }
# }


data = {
        "task": "If it takes 5 minutes to brew one cup of coffee, how long does it take to brew 10 cups of coffee simultaneously using the same coffee machine?",
        "options": [
            "5 minutes",
            "10 minutes",
            "25 minutes",
            "50 minutes"
        ],
        "answer_from_index_start_at_1": [
            "5 minutes",
            "10 minutes",
            "25 minutes",
            "50 minutes"
        ],
        "error_comment_data_lookup_table": {
            2: "This is incorrect because brewing multiple cups of coffee simultaneously does not increase the brewing time. The coffee machine can brew all 10 cups at the same time.",
            3: "This is incorrect because it assumes that the brewing time increases linearly with the number of cups. However, the coffee machine can brew all 10 cups simultaneously, so the brewing time remains the same as brewing one cup.",
            4: "This is incorrect because it assumes that the brewing time increases proportionally with the number of cups. However, the coffee machine can brew all 10 cups simultaneously, so the brewing time remains the same as brewing one cup."
        }
}


####################
# error explained test
####################
error_exaplain_equestion_append_to_jsonl(f"{task_file_directory}/error_explained_test_1.jsonl", data)



# write code
import json

def create_challenge_json(function_name, input_parameters, output_description, test_cases):
    challenge_data = {
        "function_name": function_name,
        "input_parameters": input_parameters,
        "output_description": output_description,
        "test_cases": test_cases
    }

    with open("write_a_make_a_function_challenge.jsonl", "a") as file:
        json.dump(challenge_data, file, indent=4)

    print("Challenge JSON file created successfully.")

# Example usage
function_name = "calculate_area"
input_parameters = ["length", "width"]
output_description = "The area of a rectangle"
test_cases = [
    {
        "input": [5, 3],
        "expected_output": 15
    },
    {
        "input": [2.5, 4],
        "expected_output": 10
    }
]

create_challenge_json(function_name, input_parameters, output_description, test_cases)
