# AI Prompt Evaluation


## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Developing a New Feature](#developing-a-new-feature)
- [Output Schema](#output-schema)
- [Adding Different Datasets and Prompt Versions](#adding-different-datasets-and-prompt-versions)
- [Future Updates](#future-updates)


## Overview

This project is a feature-based prompt evaluation pipeline. It lets you define use-case-specific features (for work you may be building in another project), generate structured JSON outputs from LLMs, and evaluate those outputs against a separate evaluation prompt. The system supports reproducible, schema-enforced prompt testing so you can iterate and compare performance across prompts and models.

### Motivation / Why This Exists

Prompt engineering is often ad-hoc and difficult to measure. This project provides a structured workflow for testing, validating, and scoring prompts programmatically. By enforcing JSON schemas and automating evaluation, it allows prompt designers to systematically assess performance, track improvements, and experiment with different models or prompt variations in a repeatable and measurable way.

### High Level View of Flow
1. **INITIAL CALL:** LLM is called with the `prompt` you are evaluating and a list of `data` representing user input.
2. **SAVE RESULTS:** Results are saved as a list of objects representing the original `request` and the LLM `response`.
3. **EVALUATE CALL:** LLM is called with the `evaluation prompt` and the `results` of the original call.
4. **SAVE RESULTS:** Evaluation results are saved as a list of objects, each with the request id and the evaluation LLM's comments and score. An average score is also calculated and added to the evaluation result metadata.
5. **HUMAN REVIEW AND PROMPT UPDATE:** Review the evaluation results, identify strengths and weaknesses, compare AI evaluation to specific original requests/responses, then adjust the prompt and run again.

## Getting Started

### 1. Clone the Repository
Start by cloning the project repository and navigating into it:

```bash
git clone https://github.com/MattRueter/ai-prompt-evaluation.git
cd ai-prompt-evaluation/
```

### 2. Creating virtual environment
```bash
# from project root
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# install CLI entry points (evaluate, new)
pip install -e .


# terminate environment when you've finished a session
deactivate
```

### 3. Add LLM API key to .env
This project uses Anthropic by default. You need an Anthropic account and API key. The project loads `.env`, and Anthropic's Python SDK automatically looks for `ANTHROPIC_API_KEY`.
```bash
ANTHROPIC_API_KEY=<your_anthropic_api_key>
```
The project is designed so that, within a feature's `generate.py` and `evaluate.py`, you can swap Anthropic models or even use different LLMs. This has not been fully tested yet.

The important part is making sure the selected LLM has the required credentials and returns data that matches the expected schema.

### 4. Running a Feature Evaluation
Each feature lives in its own directory with its own `main.py`. You can run a feature in several ways:

From ***project root*** run:

Option 1. Without an alias.
```bash
# run the main.py file passing in the feature directory name
python3 main.py <feature_dir>

# run the main.py file using autocomplete
python3 main.py features/<feature_dir>
```

Option 2. Using the installed CLI entry point (recommended):
```bash
# run (from the root of the project)
evaluate <feature_dirname>

# or with autocomplete
evaluate features/<feature_dirname>
```

> Calling `main.py` from the project root runs the selected feature's `main.py`.

### 5. Running the `get_started` feature
In `features/` there is an example template feature called `get_started`. Try running `evaluate get_started` in the terminal.

You should see this...
```txt
--------------------------------------------------------
🚀 Welcome! Your feature is almost ready.
Please add some example data to '<your_feature_dir>data/starter_dataset.json'
and write your prompts in 'prompts/system.txt' to get started.
--------------------------------------------------------
```



## Developing a New Feature
Let's walk through working on a new feature from scratch.

### 1. Run the following in the CLI
```bash
new introductions
```
### 2. Add data. 
+ `introductions/data/starter_dataset.json`
```json
{
  "data": [
    {
      "user": "Hello my name is Matt. Nice to meet you."
    },
    {
      "user": "I am building my first feature directory."
    }
  ]
}
```
### 3. Create system and evaluation prompts
+ `introductions/prompts/system.txt`
```
You are a friendly chatbot. If a user introduces themselves by name, respond with the following sentence.

"Hello, I am Claude. Nice to meet you."


If they haven't introduced themselves by name, then just respond with a rhyming couplet.

```
+ `introductions/prompts/evaluation.txt`
```
You are a response grading LLM in a prompt engineering pipeline. Below are the rules for scoring the response you are evaluating.

<RULES FOR SCORING RESPONSES TO INTRODUCTIONS>

If the user has introduced themselves by name and the response isn't EXACTLY "Hello, I am Claude. Nice to meet you.", 
score is automatically 0

If the user has introduced themselves by name and the response is "Hello, I am Claude. Nice to meet you.",
Score is 10

</RULES FOR SCORING RESPONSES TO INTRODUCTIONS>

<RULES FOR SCORING RESPONSES TO NON INTRODUCTIONS>

If the user hasn't introduced themselves and the response is anything other than a rhyming couplet,
score is automatically 0.

If response is a couplet but doesn't rhyme,
score is 5

</RULES FOR SCORING RESPONSES TO NON INTRODUCTIONS>

```

### 4. Run initial evaluation
```bash
#from root of project run
evaluate introductions
```
### 5. View results
+ Open `introductions/evaluation_results/` and look for a file with a UUID. Open it to review evaluation results and average score.
+ You can also view original requests/responses in `introductions/results/`.


## Output Schema
You may want output to be something other than a string. You can enforce that by updating the schema used in the generate call.
+ `<feature>/generate.py`
```python
schema = {
    "type": "object",
    "properties": {
        # replace object assigned to "llm" with properties relevant to use case
        "llm": {"type":"string"} #update this to match the output you expect.
    },
    "required": [],
    "additionalProperties": False,
}

```

## Adding Different Datasets and Prompt Versions
The config in `config.py` uses `data/starter_dataset.json`, `prompts/system.txt`, and `prompts/evaluation.txt` by default. You can override these by updating config values in `<your_feature>/main.py`.

e.g.
```python
#features/<your_feature>/main.py

config = create_eval_config(
    base_dir=Path(__file__).resolve().parent,
    data_file="dataset_v2.json",
    prompt_file="system_v2.txt",
    eval_prompt_file="evaluation_v2.txt",  # This is not yet being saved in metadata.
)
```

The metadata in your output will now include those file names for easier reference, searching, and filtering.

```json
  "meta": {
    "file_name": "dataset_v2.json",
    "dataset_name": "dataset_v2.json",
    "prompt_file_name": "system_v2.txt",
    "number_of_cases": null,
    "average_score":null,
    "summary": "",
    "description": "Simple set of requests to test and build pipeline"
  }
```

> 📘Good to know:
>
> You may only ever want to use one dataset file and one `system.txt` file, but the project supports
> various dataset and prompt files for granularity.

## Future updates
Some things I'd like to add eventually:
+ sorting/filtering cli commands for better reviewing the results
+ open up a browser window to view results (with and without sorting/filtering)
+ create a package or make it easier to "drop in" to a workplace (so users don't have to store prompt and LLM config in two separate places). This would let the prompt-eval-pipeline live next to the project that contains features using LLM calls that need testing.