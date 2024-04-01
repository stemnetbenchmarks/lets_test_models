"""
Append coding challenges to a test set
"""
test_set_name = "code_writing_test_set_6.jsonl"

import json

# # Optional
# from datetime import datetime, UTC
# date_time = datetime.now(UTC)
# clean_timestamp = date_time.strftime("%Y%m%d%H%M%S%f")   


# function to make jsonl for coding tests
def create_challenge_json(function_name, input_parameters, output_description, test_cases):

    task = f"""
    Write a python function called {function_name}(), 
    such that given input(s) are ({', '.join(input_parameters)}),
    so, def {function_name}({', '.join(input_parameters)}):
    and the output is {output_description} 
    """

    challenge_data = {
        "task": task,
        "function_name": function_name,
        "input_parameters": input_parameters,
        "output_description": output_description,
        "test_cases": test_cases
    }


    with open(test_set_name, "a") as file:
        json_data = json.dumps(challenge_data)
        file.write(json_data + "\n")
    print("Challenge JSONL file created successfully.")


##################
# Make The Tests!
##################

# area
function_name = "calculate_area"
input_parameters = ["length", "width"]
output_description = "The area of a rectangle, only return a number"
test_cases = [
    {
        "input": [5, 3],
        "expected_output": 15.0
    },
    {
        "input": [2.5, 4],
        "expected_output": 10.0
    }
]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


##

# calculate_volume 
function_name = "calculate_volume" 
input_parameters = ["length", "width", "height"] 
output_description = "The volume of a rectangular prism, only return a number" 
test_cases = [ { "input": [4, 5, 2], "expected_output": 40.0 }, { "input": [3.5, 2, 1.5], "expected_output": 10.5 }, { "input": [2, 2, 2], "expected_output": 8.0 }, { "input": [1, 1, 1], "expected_output": 1.0 } ]
create_challenge_json(function_name, input_parameters, output_description, test_cases)



# is_palindrome 
function_name = "is_palindrome" 
input_parameters = ["string"] 
output_description = "True if the given string is a palindrome (reads the same forwards and backwards), False otherwise" 
test_cases = [ { "input": ["racecar"], "expected_output": True }, { "input": ["hello"], "expected_output": False }, { "input": ["A man, a plan, a canal: Panama"], "expected_output": True }, { "input": [""], "expected_output": True }, { "input": ["Madam, I'm Adam"], "expected_output": True }, { "input": ["Python"], "expected_output": False } ]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# find_maximum 
function_name = "find_maximum" 
input_parameters = ["numbers"] 
output_description = "The maximum number from the given list of numbers" 
test_cases = [ { "input": [[5, 2, 9, 1, 7]], "expected_output": 9 }, { "input": [[-3, -1, -8, -2]], "expected_output": -1 }, { "input": [[0, 0, 0]], "expected_output": 0 }, { "input": [[1]], "expected_output": 1 }, { "input": [[4, 2, 4, 1, 3, 4]], "expected_output": 4 } ]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# calculate_right_triangle_area
function_name = "calculate_right_triangle_area"
input_parameters = ["height", "width"]
output_description = "The area of a right triangle, only return a number"
test_cases = [
    {
        "input": [5, 3],
        "expected_output": 7.5
    },
    {
        "input": [2.5, 4],
        "expected_output": 5
    }
]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# calculate_mean
function_name = "calculate_mean"
input_parameters = ["numbers"]
output_description = "The mean of the given list of numbers, rounded to two decimal places"
test_cases = [
    {"input": [[1, 2, 3, 4, 5]], "expected_output": 3.0},
    {"input": [[2.5, 3.7, 1.8, 4.2]], "expected_output": 3.05},
    {"input": [[10, 20, 30, 40]], "expected_output": 25.0},
    {"input": [[-5, 5, 0]], "expected_output": 0.0},
    {"input": [[1]], "expected_output": 1.0}
]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# calculate_median
function_name = "calculate_median"
input_parameters = ["numbers"]
output_description = "The median of the given list of numbers, rounded to two decimal places"
test_cases = [
    {"input": [[1, 2, 3, 4, 5]], "expected_output": 3.0},
    {"input": [[2.5, 3.7, 1.8, 4.2, 6.1]], "expected_output": 3.7},
    {"input": [[10, 20, 30, 40]], "expected_output": 25.0},
    {"input": [[-5, 5, 0, 10]], "expected_output": 2.5},
    {"input": [[1, 2, 3]], "expected_output": 2.0}
]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# calculate_mode
function_name = "calculate_mode"
input_parameters = ["numbers"]
output_description = "The mode(s) of the given list of numbers, as a list"
test_cases = [
    {"input": [[1, 2, 3, 4, 5]], "expected_output": []},
    {"input": [[2.5, 3.7, 1.8, 4.2, 3.7, 6.1, 3.7]], "expected_output": [3.7]},
    {"input": [[10, 20, 30, 40, 20]], "expected_output": [20]},
    {"input": [[-5, 5, 0, 10, 5, 0]], "expected_output": [0, 5]},
    {"input": [[1, 2, 3, 2, 2]], "expected_output": [2]}
]
create_challenge_json(function_name, input_parameters, output_description, test_cases)


# calculate_mode
function_name = "list_of_numbers"
input_parameters = ["number_1," "number_2"]
output_description = "return the input numbers as a list"
test_cases = [
    {"input": [1, 2], "expected_output": [1, 2]},
    {"input": [10, 20], "expected_output": [10, 20]},

]
create_challenge_json(function_name, input_parameters, output_description, test_cases)
