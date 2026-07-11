class DataCleaner:
    @staticmethod
    def clean_text(text):
        """
        Remove extra spaces and handle None values.
        """
        if text is None:
            return ""

        return " ".join(str(text).strip().split())

    @staticmethod
    def is_valid(*fields):
        """
        Check that all required fields are present and non-empty.
        """
        for field in fields:
            if field is None:
                return False

            if str(field).strip() == "":
                return False

        return True