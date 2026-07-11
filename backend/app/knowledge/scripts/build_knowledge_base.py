import json
from pathlib import Path

from app.core.config import SAMPLE_SIZE, RANDOM_SEED
from app.knowledge.preprocessors.data_cleaner import DataCleaner
from app.knowledge.preprocessors.sampler import Sampler
from app.knowledge.preprocessors.normalizer import Normalizer
from app.knowledge.validators.knowledge_validator import KnowledgeValidator

# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

SQUAD_PATH = BASE_DIR / "datasets" / "squad" / "train.json"
TRUTHFULQA_PATH = BASE_DIR / "datasets" / "truthfulqa" / "validation.json"

OUTPUT_PATH = BASE_DIR / "processed" / "knowledge_base.json"

MAX_ERRORS_TO_SHOW = 20


# ==========================================
# Helper Functions
# ==========================================

def load_json(file_path: Path):
    """Load a JSON file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, file_path: Path):
    """Save a JSON file."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ==========================================
# Process SQuAD
# ==========================================

def process_squad():

    print("\nLoading SQuAD Dataset...")

    dataset = load_json(SQUAD_PATH)

    cleaned = []
    removed = 0

    for item in dataset:

        answers = item.get("answers", {}).get("text", [])

        question = DataCleaner.clean_text(
            item.get("question")
        )

        context = DataCleaner.clean_text(
            item.get("context")
        )

        answer = ""

        if answers:
            answer = DataCleaner.clean_text(
                answers[0]
            )

        if not DataCleaner.is_valid(
            question,
            context,
            answer
        ):
            removed += 1
            continue

        item["question"] = question
        item["context"] = context
        item["answers"]["text"] = [answer]

        cleaned.append(item)

    sampled = Sampler.sample(
        cleaned,
        SAMPLE_SIZE,
        RANDOM_SEED
    )

    normalized = []

    for index, item in enumerate(sampled, start=1):

        normalized.append(
            Normalizer.normalize_squad(
                item,
                index
            )
        )

    print(f"Original Records : {len(dataset)}")
    print(f"Clean Records    : {len(cleaned)}")
    print(f"Sampled Records  : {len(sampled)}")
    print(f"Removed Records  : {removed}")

    return normalized


# ==========================================
# Process TruthfulQA
# ==========================================

def process_truthfulqa():

    print("\nLoading TruthfulQA Dataset...")

    dataset = load_json(TRUTHFULQA_PATH)

    cleaned = []
    removed = 0

    for item in dataset:

        question = DataCleaner.clean_text(
            item.get("question")
        )

        answer = DataCleaner.clean_text(
            item.get("best_answer")
        )

        if not DataCleaner.is_valid(
            question,
            answer
        ):
            removed += 1
            continue

        item["question"] = question
        item["best_answer"] = answer

        cleaned.append(item)

    normalized = []

    for index, item in enumerate(cleaned, start=1):

        normalized.append(
            Normalizer.normalize_truthfulqa(
                item,
                index
            )
        )

    print(f"Original Records : {len(dataset)}")
    print(f"Clean Records    : {len(cleaned)}")
    print(f"Removed Records  : {removed}")

    return normalized


# ==========================================
# Build Knowledge Base
# ==========================================

def build_knowledge_base():

    print("\n========================================")
    print(" Building Veridict Knowledge Base")
    print("========================================")

    squad_documents = process_squad()

    truthfulqa_documents = process_truthfulqa()

    knowledge_base = squad_documents + truthfulqa_documents

    # ==========================================
    # Validate Knowledge Base
    # ==========================================

    errors = KnowledgeValidator.validate(
        knowledge_base
    )

    if errors:

        print("\nValidation Failed!\n")

        print(
            f"Showing first {min(MAX_ERRORS_TO_SHOW, len(errors))} errors:\n"
        )

        for error in errors[:MAX_ERRORS_TO_SHOW]:
            print(f"• {error}")

        print(f"\nTotal Errors : {len(errors)}")

        return

    print("\nKnowledge Base Validation Passed")

    # ==========================================
    # Save
    # ==========================================

    save_json(
        knowledge_base,
        OUTPUT_PATH
    )

    print("\n========================================")
    print(" Knowledge Base Created Successfully")
    print("========================================")

    print(f"Total Documents : {len(knowledge_base)}")
    print(f"Saved To :\n{OUTPUT_PATH}")


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":
    build_knowledge_base()