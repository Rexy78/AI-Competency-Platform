import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.ai.taxonomy import SKILL_TAXONOMY, JOB_ROLE_SKILL_MAP

logger = logging.getLogger("resume_ai")


class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) engine.
    Indexes domain knowledge markdown files across:
    - programming, web_development, databases, cloud, ai_ml, devops, interview, career_paths
    - Skill taxonomy & job role benchmark maps
    Provides vector & semantic retrieval for grounded AI reasoning.
    """

    def __init__(self, knowledge_dir: Optional[str] = None):
        if knowledge_dir:
            self.knowledge_path = Path(knowledge_dir)
        else:
            self.knowledge_path = Path(__file__).resolve().parent.parent.parent / "knowledge"

        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.doc_vectors = None
        self._build_index()

    def _build_index(self):
        docs = []

        # 1. Load Markdown files from knowledge folder
        if self.knowledge_path.exists():
            for root, _, files in os.walk(self.knowledge_path):
                for f in files:
                    if f.endswith(".md"):
                        file_path = Path(root) / f
                        try:
                            content = file_path.read_text(encoding="utf-8").strip()
                            rel_category = file_path.parent.name
                            title = f.replace(".md", "").replace("_", " ").title()
                            # Try to extract the first heading as title
                            lines = content.splitlines()
                            for line in lines:
                                if line.startswith("# "):
                                    title = line.replace("# ", "").strip()
                                    break

                            docs.append({
                                "title": title,
                                "category": rel_category,
                                "source": f"{rel_category}/{f}",
                                "content": content
                            })
                        except Exception as e:
                            logger.warning(f"Error reading knowledge file {file_path}: {e}")

        # 2. Add Skill Taxonomy definitions
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                docs.append({
                    "title": skill,
                    "category": f"Taxonomy - {category}",
                    "source": "taxonomy",
                    "content": f"{skill} is a core technology in {category}. It is widely utilized across modern enterprise software architectures."
                })

        # 3. Add Benchmark Job Roles
        for role, data in JOB_ROLE_SKILL_MAP.items():
            required_str = ", ".join(data.get("required", []))
            preferred_str = ", ".join(data.get("preferred", []))
            docs.append({
                "title": role,
                "category": "Career Role",
                "source": "job_role_benchmark",
                "content": f"The {role} role requires demonstrated proficiency in {required_str}. Preferred technologies include {preferred_str}."
            })

        self.documents = docs
        logger.info(f"RAG Engine indexed {len(self.documents)} knowledge documents.")

        # 4. Initialize TF-IDF Vectorizer
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            corpus = [f"{d['title']} {d['category']} {d['content']}" for d in self.documents]
            self.vectorizer = TfidfVectorizer(stop_words="english", max_features=2500)
            self.doc_vectors = self.vectorizer.fit_transform(corpus)
            logger.info("RAG Engine TF-IDF vector index built successfully.")
        except Exception as e:
            logger.warning(f"Could not build TF-IDF vectorizer: {e}")
            self.vectorizer = None
            self.doc_vectors = None

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve the most relevant knowledge documents for a query."""
        if not self.documents:
            return "General career knowledge base available."

        if not query or not query.strip():
            return ""

        # Use Vector Cosine Similarity if vectorizer is available
        if self.vectorizer is not None and self.doc_vectors is not None:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                query_vec = self.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, self.doc_vectors).flatten()
                top_indices = scores.argsort()[::-1][:top_k]

                relevant = []
                for idx in top_indices:
                    if scores[idx] > 0.05:
                        doc = self.documents[idx]
                        relevant.append(f"### [{doc['category'].upper()}] {doc['title']}\n{doc['content'][:600]}...")
                if relevant:
                    return "\n\n".join(relevant)
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to keyword search: {e}")

        # Fallback: Keyword overlap search
        query_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            text = f"{doc['title']} {doc['category']} {doc['content']}".lower()
            overlap = sum(1 for w in query_words if w in text)
            if overlap > 0:
                scored.append((overlap, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_docs = [
            f"### [{d['category'].upper()}] {d['title']}\n{d['content'][:600]}..."
            for _, d in scored[:top_k]
        ]

        if not top_docs:
            return "General career guidance and industry engineering best practices applied."
        return "\n\n".join(top_docs)


rag_engine = RAGEngine()
