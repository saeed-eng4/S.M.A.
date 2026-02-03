import csv
import os
from sentence_transformers import SentenceTransformer, util
import torch

# Lazy-load the model to avoid long import times when starting a GUI
_MODEL = None


def _get_model():
    """Get (and cache) the SentenceTransformer model."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def load_faq_data():
    model = _get_model()
    
    # Get the absolute path to the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the CSV file
    csv_path = os.path.join(script_dir, '..', 'data', 'faqs.csv')

    _FAQ = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            _FAQ.append(row)
            
    questions = [item["question"] for item in _FAQ]
    embeddings = model.encode(questions, convert_to_tensor=True)
    return _FAQ, embeddings


def search_faq(faq_data, faq_embeddings, user_question: str):
    model = _get_model()
    q_emb = model.encode(user_question, convert_to_tensor=True)
    sims = util.cos_sim(q_emb, faq_embeddings)
    best_idx = int(torch.argmax(sims).item())
    score = float(sims[0, best_idx].item())

    return {
        "question": faq_data[best_idx]["question"],
        "answer": faq_data[best_idx]["answer"],
        "score": score,
    }