from pathlib import Path
import json
from datasets import load_dataset


BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def download_squad():
    print("Downloading SQuAD...")

    dataset = load_dataset("squad")

    train = dataset["train"].to_list()
    validation = dataset["validation"].to_list()

    save_json(
        train,
        DATASETS_DIR / "squad" / "train.json"
    )

    save_json(
        validation,
        DATASETS_DIR / "squad" / "validation.json"
    )

    print("✅ SQuAD saved.")


def download_truthfulqa():
    print("Downloading TruthfulQA...")

    dataset = load_dataset(
        "truthful_qa",
        "generation"
    )

    validation = dataset["validation"].to_list()

    save_json(
        validation,
        DATASETS_DIR / "truthfulqa" / "validation.json"
    )

    print("✅ TruthfulQA saved.")


if __name__ == "__main__":
    download_squad()
    download_truthfulqa()

    print("\n🎉 All datasets downloaded successfully.")