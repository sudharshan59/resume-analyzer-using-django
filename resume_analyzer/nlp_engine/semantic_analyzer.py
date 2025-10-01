from .model_loader import get_model
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def compute_resume_job_similarity(resume_text: str, job_description: str) -> float:
    """
    Returns semantic similarity score (0.0 to 1.0) between resume and job description.
    """
    model = get_model()
    embeddings = model.encode([resume_text, job_description])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))

def extract_skills_with_spacy(text: str):
    # Optional: Use spaCy NER to extract skills (requires custom NER or rules)
    # For now, return empty — or integrate with skill libraries later
    return []