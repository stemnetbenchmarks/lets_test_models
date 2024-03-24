import json

task_file_directory = "ai_task_files"


def error_exaplain_equestion_append_to_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as file:
        json.dump(data, file)
        file.write("\n")


#######################
# error explained test
#######################

data = {
    "task": "If it takes 30 minutes to dry one shirt in the sun, how long does it take to dry 10 shirts in the sun simultaneously?",
    "options": ["1. 30 minutes", "2. 60 minutes", "3. 150 minutes", "4. 300 minutes"],
    "answer_from_index_start_at_1": "1",
    "error_comment_data_lookup_table": {
        "2": "This is incorrect because drying multiple shirts simultaneously does not increase the drying time. The sun can dry all 10 shirts at the same time.",
        "3": "This is incorrect because it assumes that the drying time increases linearly with the number of shirts. However, the sun can dry all 10 shirts simultaneously, so the drying time remains the same as drying one shirt.",
        "4": "This is incorrect because it assumes that the drying time increases proportionally with the number of shirts. However, the sun can dry all 10 shirts simultaneously, so the drying time remains the same as drying one shirt.",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)

data = {
    "task": "If it takes 30 minutes to dry one shirt in the sun, how long does it take to dry 10 shirts in the sun simultaneously?",
    "options": ["1. 30 minutes", "2. 60 minutes", "3. 150 minutes", "4. 300 minutes"],
    "answer_from_index_start_at_1": "1",
    "error_comment_data_lookup_table": {
        "2": "This is incorrect because drying multiple shirts simultaneously does not increase the drying time. The sun can dry all 10 shirts at the same time.",
        "3": "This is incorrect because it assumes that the drying time increases linearly with the number of shirts. However, the sun can dry all 10 shirts simultaneously, so the drying time remains the same as drying one shirt.",
        "4": "This is incorrect because it assumes that the drying time increases proportionally with the number of shirts. However, the sun can dry all 10 shirts simultaneously, so the drying time remains the same as drying one shirt.",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)


data = {
    "task": "If it takes 5 minutes to cook one pancake on a griddle, how long does it take to cook 8 pancakes simultaneously using the same griddle?",
    "options": ["1. 5 minutes", "2. 10 minutes", "3. 20 minutes", "4. 40 minutes"],
    "answer_from_index_start_at_1": "1",
    "error_comment_data_lookup_table": {
        "2": "This is incorrect because cooking multiple pancakes simultaneously does not increase the cooking time. The griddle can cook all 8 pancakes at the same time.",
        "3": "This is incorrect because it assumes that the cooking time increases linearly with the number of pancakes. However, the griddle can cook all 8 pancakes simultaneously, so the cooking time remains the same as cooking one pancake.",
        "4": "This is incorrect because it assumes that the cooking time increases proportionally with the number of pancakes. However, the griddle can cook all 8 pancakes simultaneously, so the cooking time remains the same as cooking one pancake.",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)


data = {
    "task": "If it takes 30 minutes to wash one load of laundry in the washing machine, how long does it take to wash 4 loads of laundry simultaneously using the same washing machine at the same setting, assuming the load fits in?",
    "options": ["1. 30 minutes", "2. 1 hour", "3. 2 hours", "4. 4 hours"],
    "answer_from_index_start_at_1": "1",
    "error_comment_data_lookup_table": {
        "2": "This is incorrect because washing multiple loads of laundry simultaneously does not increase the washing time. The washing machine can wash all 4 loads at the same time.",
        "3": "This is incorrect because it assumes that the washing time increases linearly with the number of loads. However, the washing machine can wash all 4 loads simultaneously, so the washing time remains the same as washing one load.",
        "4": "This is incorrect because it assumes that the washing time increases proportionally with the number of loads. However, the washing machine can wash all 4 loads simultaneously, so the washing time remains the same as washing one load.",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)

data = {
    "task": "If it takes 30 minutes to wash one load of laundry in the washing machine, how long does it take to wash 4 loads of laundry sequentially one at a time using the same washing machine?",
    "options": ["1. 30 minutes", "2. 1 hour", "3. 2 hours", "4. 4 hours"],
    "answer_from_index_start_at_1": "3",
    "error_comment_data_lookup_table": {
        "1": "This is incorrect because it assumes that the washing time remains the same regardless of the number of loads. However, since the loads are washed sequentially, the total washing time increases with each additional load.",
        "2": "This is incorrect because it assumes that the washing time only doubles for 4 loads. However, since each load takes 30 minutes and they are washed sequentially, the total washing time should be 4 times the individual load washing time.",
        "4": "This is incorrect because it assumes that the washing time increases to 4 hours for 4 loads. However, since each load takes 30 minutes and they are washed sequentially, the total washing time should be 2 hours (4 loads × 30 minutes per load).",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)


data = {
    "task": "If it takes 1 hour to complete one homework assignment, how long does it take to complete 5 homework assignments?",
    "options": ["1. 1 hour", "2. 2 hours", "3. 5 hours", "4. 10 hours"],
    "answer_from_index_start_at_1": "3",
    "error_comment_data_lookup_table": {
        "1": "This is incorrect because it assumes that you can complete all 5 assignments in the same amount of time as one assignment. However, since you can only work on one assignment at a time, the total time will be the sum of the time it takes to complete each assignment.",
        "2": "This is incorrect because it assumes that the time it takes to complete the assignments is less than the sum of the time it takes to complete each assignment individually. However, since you can only work on one assignment at a time, the total time will be the sum of the time it takes to complete each assignment.",
        "4": "This is incorrect because it assumes that the time it takes to complete the assignments is greater than the sum of the time it takes to complete each assignment individually. However, since each assignment takes 1 hour and you can only work on one assignment at a time, the total time will be 5 hours.",
    },
}
error_exaplain_equestion_append_to_jsonl(
    f"{task_file_directory}/error_explained_test_1.jsonl", data
)
