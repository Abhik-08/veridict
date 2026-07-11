class KnowledgeValidator:
    """
    Validates the final Veridict Knowledge Base.
    """

    REQUIRED_FIELDS = [
        "id",
        "question",
        "answer",
        "context",
        "source"
    ]

    VALID_SOURCES = {
        "squad",
        "truthfulqa"
    }

    @staticmethod
    def validate(documents):
        """
        Validate the complete knowledge base.

        Returns:
            list: List of validation errors.
        """

        errors = []
        ids = set()

        for index, doc in enumerate(documents, start=1):

            # ==========================================
            # Required Fields
            # ==========================================

            for field in KnowledgeValidator.REQUIRED_FIELDS:

                if field not in doc:
                    errors.append(
                        f"Document {index}: Missing field '{field}'"
                    )
                    continue

                if not isinstance(doc[field], str):
                    errors.append(
                        f"Document {index}: '{field}' must be a string"
                    )
                    continue

                # Context is allowed to be empty (TruthfulQA)
                if field != "context" and doc[field].strip() == "":
                    errors.append(
                        f"Document {index}: '{field}' cannot be empty"
                    )

            # ==========================================
            # Duplicate ID Check
            # ==========================================

            if "id" in doc:

                if doc["id"] in ids:
                    errors.append(
                        f"Document {index}: Duplicate ID '{doc['id']}'"
                    )
                else:
                    ids.add(doc["id"])

            # ==========================================
            # Valid Source Check
            # ==========================================

            if (
                "source" in doc and
                doc["source"] not in KnowledgeValidator.VALID_SOURCES
            ):
                errors.append(
                    f"Document {index}: Invalid source '{doc['source']}'"
                )

            # ==========================================
            # Optional Warning
            # ==========================================

            # SQuAD documents should normally contain context
            if (
                doc.get("source") == "squad" and
                doc.get("context", "").strip() == ""
            ):
                errors.append(
                    f"Document {index}: SQuAD context is empty"
                )

        return errors