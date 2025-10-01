from sentence_transformers import SentenceTransformer

# Load ONCE at startup (avoids reloading on every request)
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model