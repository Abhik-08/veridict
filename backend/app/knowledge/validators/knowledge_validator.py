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
            KnowledgeValidator._validate_fields(doc, index, errors)
            KnowledgeValidator._validate_unique_id(doc, index, ids, errors)
            KnowledgeValidator._validate_source(doc, index, errors)
            KnowledgeValidator._validate_squad_context(doc, index, errors)

        return errors

    @staticmethod
    def _validate_fields(doc, index, errors):
        """Check required fields exist, are strings, and are non-empty."""

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

    @staticmethod
    def _validate_unique_id(doc, index, ids, errors):
        """Check for duplicate IDs."""

        if "id" in doc:
            if doc["id"] in ids:
                errors.append(
                    f"Document {index}: Duplicate ID '{doc['id']}'"
                )
            else:
                ids.add(doc["id"])

    @staticmethod
    def _validate_source(doc, index, errors):
        """Check that source is a recognized value."""

        if (
            "source" in doc and
            doc["source"] not in KnowledgeValidator.VALID_SOURCES
        ):
            errors.append(
                f"Document {index}: Invalid source '{doc['source']}'"
            )

    @staticmethod
    def _validate_squad_context(doc, index, errors):
        """SQuAD documents should normally contain context."""

        if (
            doc.get("source") == "squad" and
            doc.get("context", "").strip() == ""
        ):
            errors.append(
                f"Document {index}: SQuAD context is empty"
            )