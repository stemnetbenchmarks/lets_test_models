# cli_tools_for_llamacpp_in_python
&
# lets_test_models

Walkthrough and discussion here:
https://medium.com/@GeoffreyGordonAshbrook/lets-test-models-and-let-s-do-tasks-84777f80eb99

Preliminary tools for using llama.cpp e.g. selecting a model and using
a local gguf model instead of a paid cloud api.

Also see dev area: 
- https://github.com/stemnetbenchmarks/lets_test_models 
- https://github.com/lineality/cli_tools_for_llamacpp_in_python  
- https://github.com/lineality/STEM_Net_open_training_testing_benchmarks
- https://github.com/lineality/object_relationship_spaces_ai_ml

# llama.cpp install steps:

## Install Required C++/CPP/G++
```bash
sudo dnf install gcc-c++
```

## Install Required C++/CPP/G++
```bash
sudo dnf install gcc-c++
```

## Install llama.cpp from github
- Three bash steps:
```bash
mkdir llama_cpp; cd llama_cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```


## Download Foundation Model(s)
- e.g. ~any .gguf from https://huggingface.co/TheBloke 


Note: If gguf models are already downloaded for a platform such as Jan, you can simply use the file-path for any of those models in your cli call to llama.cpp.

## Download model into folder in llama.cpp file directory:
e.g.
```bash
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
```
## Download model into folder in llama.cpp file directory:
Quantize model if model is not gguf format
(Q: gguf without quantizing?)

## Run llama.cpp

```bash
make -j && ./main -m ./models/MODEL_NAME.bin/.gguf -p "What is the best gift for my wife?" -n 512
```

```bash
make -j && ./main -m ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -p "What is a horseshoe crab?" -n 512
```

### To see only output
- from: https://github.com/ggerganov/llama.cpp/discussions/1758 

```bash
./main 2>/dev/null -m /home/user/jan/models/tinyllama-1.1b/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -p "What is a horseshoe crab?"
```


# To use: call_llamacapp.py
first:
- clone this repo
- install llama.cpp and at least one model (or use cloud api)
- put your json files into the ai_task_files directory

1. set path_to_model_foler as it exists on your system
2. set input
3. Run:
```python
python call_llamacapp.py
```
Output will appear in terminal.


# To use: json_translator(...).py
first:
- clone this repo
- install llama.cpp and at least one model (or use cloud api)
- put your json files into the ai_task_files directory

1. put your json files into the ai_task_files directory
2. add your target languages to the list below
3. add your model to use into the list below
4. configure number of ranked-choice votes to cast
5. configure how many translations to make (before selecting the best)
6. run this pyscript
```python
python json_translator(...).py
```
Translations will appear per language x per file in translations directory.


# To use: do_task(...).py
1. close repo and cd inside (cd -> change directory)
2. set path_to_model_foler as it exists on your system
3. Run:
```python
python call_llamacapp.py
```


# For Cloudy API
- Create a .env file
1. Run:
```python
touch .env
```

2. Add this text, where you can put your real keys.
```
OPENAI_API_KEY = "xxx"
mistral_api_key = "xxx"
```