import re
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self, kb_path: str = "pet_care_kb.txt", top_k: int = 3):
        self.top_k = top_k
        self.chunks: list[str] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self._load(kb_path)

    def _load(self, path: str):
        try:
            with open(path, "r") as f:
                text = f.read()
            # Split on double newlines (paragraphs)
            raw = [c.strip() for c in re.split(r"\n\n+", text) if c.strip()]
            # Filter out heading-only lines
            self.chunks = [c for c in raw if len(c) > 60]
            self.matrix = self.vectorizer.fit_transform(self.chunks)
            logger.info(f"RAG: loaded {len(self.chunks)} chunks from {path}")
        except Exception as e:
            logger.error(f"RAG load failed: {e}")
            self.chunks = []

    def retrieve(self, query: str) -> str:
        if not self.chunks or self.matrix is None:
            return ""
        try:
            q_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(q_vec, self.matrix)[0]
            top_idx = np.argsort(scores)[::-1][: self.top_k]
            # Only include chunks with non-zero similarity
            relevant = [self.chunks[i] for i in top_idx if scores[i] > 0.01]
            if not relevant:
                return ""
            result = "\n\n".join(relevant)
            logger.info(f"RAG: retrieved {len(relevant)} chunks for query: {query[:60]}")
            return result
        except Exception as e:
            logger.error(f"RAG retrieve failed: {e}")
            return ""
