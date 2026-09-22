import sys
from pathlib import Path
import json

TEMPLATE_FILES = {
    "__init__.py": "",
    "main.py": """import json
from dotenv import load_dotenv
from pprint import pprint
from pathlib import Path

from features.<feature_name>.generate import generate
from features.<feature_name>.evaluate import evaluate

from eval_suite.run_eval_suite import run_eval_suite
from config import create_eval_config

config = create_eval_config(
    base_dir=Path(__file__).resolve().parent,
    # data_file: str = #defaults to --> "starter_dataset.json",
    # prompt_file: str = #defaults to --> "system.txt",
    # eval_prompt_file: str = #defaults to --> "evaluation.txt",
)

run_eval_suite(
    generate=generate,
    evaluate=evaluate,
    config=config
)
""",
    "generate.py": """import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

schema = {
    "type": "object",
    "properties": {
        # replace object assigned to "llm" with properties relevant to use case
        "llm": {"type":"string"} #update this to match the output you expect.
    },
    "required": [],
    "additionalProperties": False,
}


def generate(prompt, req):
    print("Calling Claude")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0.5,
        system=prompt,
        messages=[{"role": "user", "content": req}],
        output_config={
            "format": {"type": "json_schema", "schema": schema},
        }
    )
    return message.content[0].text
""",
    "evaluate.py": """import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

schema = {
  "type": "object",
  "properties": {
    "id" : {"type" : "number"},
    "score" : {"type" : "number"},
    "comment" : {"type" : "string"}
  },
  "required" : ["id", "score", "comment"],
  "additionalProperties" : False,
}


def evaluate(prompt, req):
    print("Calling the evaluator.")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0.5,
        system=prompt,
        messages=[{"role": "user", "content": req}],
        output_config={
            "format": {"type": "json_schema", "schema": schema},
        }
    )
    return message.content[0].text
""",
    "README.md": "# <Feature Name>",
}

DATA_FILES = {
    "data/starter_dataset.json": json.dumps({
        "meta": {
            "file_name": "starter_dataset.json",
            "dataset_name": "starter_dataset",
            "prompt_file_name": None,
            "number_of_cases": None,
            "average_score": None,
            "summary": "",
            "description": ""
        },
        "data": [ {"user":"remind me to create some data."} ]
    }, indent=2)
}

PROMPT_FILES = {
    "prompts/system.txt": "Write a system prompt to evaluate.",
    "prompts/evaluation.txt": "Write an evaluation prompt."
}


def create_feature(feature_name: str):
    base_dir = Path(__file__).resolve().parent / "features" / feature_name
    if base_dir.exists():
        print(f"Error: Feature '{feature_name}' already exists at {base_dir}")
        sys.exit(1)

    # create base dir
    base_dir.mkdir(parents=True, exist_ok=False)

    # create subdirectories
    (base_dir / "data").mkdir()
    (base_dir / "prompts").mkdir()

    # create files
    for fname, content in TEMPLATE_FILES.items():
        file_path = base_dir / fname
        content = content.replace("<feature_name>", feature_name).replace("<Feature Name>", feature_name)
        file_path.write_text(content, encoding="utf-8")

    for fname, content in DATA_FILES.items():
        file_path = base_dir / fname
        file_path.write_text(content, encoding="utf-8")

    for fname, content in PROMPT_FILES.items():
        file_path = base_dir / fname
        file_path.write_text(content, encoding="utf-8")

    print(f"Feature '{feature_name}' successfully created at {base_dir}")


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: bootstrap-feature <feature_name>\n"
            "       python3 bootstrap_feature.py <feature_name>"
        )
        sys.exit(1)

    feature_name = sys.argv[1]
    create_feature(feature_name)


if __name__ == "__main__":
    main()