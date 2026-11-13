"""Deterministic local embedding fallback for network-restricted evaluations."""

from sklearn.feature_extraction.text import HashingVectorizer


class HashingSentenceEncoder:
    def __init__(self):
        self.vectorizer = HashingVectorizer(n_features=384, alternate_sign=False, norm="l2")

    def encode(self, texts):
        return self.vectorizer.transform(texts).toarray()
