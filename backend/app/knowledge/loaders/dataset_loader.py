from datasets import load_dataset


def load_truthfulqa():
    print("\nLoading TruthfulQA...")

    dataset = load_dataset("truthful_qa", "generation")

    print(dataset)
    print("\nFirst Record:")
    print(dataset["validation"][0])


def load_squad():
    print("\nLoading SQuAD...")

    dataset = load_dataset("squad")

    print(dataset)
    print("\nFirst Record:")
    print(dataset["train"][0])


if __name__ == "__main__":
    load_truthfulqa()
    print("=" * 80)
    load_squad()
