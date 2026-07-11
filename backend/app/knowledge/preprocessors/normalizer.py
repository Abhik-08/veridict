class Normalizer:
    """
    Converts different datasets into Veridict's unified schema.
    """

    @staticmethod
    def normalize_squad(item, index):
        """
        Convert one SQuAD record into Veridict format.
        """

        answers = item.get("answers", {}).get("text", [])
        answer = answers[0] if answers else ""

        return {
            "id": f"squad_{index:06d}",
            "question": item["question"].strip(),
            "answer": answer.strip(),
            "context": item["context"].strip(),
            "source": "squad"
        }

    @staticmethod
    def normalize_truthfulqa(item, index):
        """
        Convert one TruthfulQA record into Veridict format.
        """

        return {
            "id": f"truthfulqa_{index:06d}",
            "question": item["question"].strip(),
            "answer": item["best_answer"].strip(),
            "context": "",
            "source": "truthfulqa"
        }