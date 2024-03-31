import json

def create_challenge_json(function_name, input_parameters, output_description, test_cases):

    task = f"""
    Write a python function called {function_name}(), 
    such that given input(s) are {input_parameters} 
    and the output is {output_description} 
    """
    
    challenge_data = {
        "task": task,
        "function_name": function_name,
        "input_parameters": input_parameters,
        "output_description": output_description,
        "test_cases": test_cases
    }
    

    with open("write_a_make_a_function_challenge2.jsonl", "a") as file:
        json_data = json.dumps(challenge_data)
        file.write(json_data + "\n")
    print("Challenge JSONL file created successfully.")

# Example usage
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
