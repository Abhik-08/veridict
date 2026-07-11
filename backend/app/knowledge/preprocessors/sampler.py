import random


class Sampler:
    @staticmethod
    def sample(data, sample_size, seed=42):
        """
        Randomly sample records from a dataset.

        Args:
            data (list): List of records.
            sample_size (int): Number of records to sample.
            seed (int): Random seed for reproducibility.

        Returns:
            list: Sampled records.
        """

        if not data:
            return []

        if len(data) <= sample_size:
            return data

        random.seed(seed)

        return random.sample(data, sample_size)