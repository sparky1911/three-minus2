from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np

MODEL_DIR = "models/toxic-bert"

_tok = AutoTokenizer.from_pretrained(MODEL_DIR)
_model = ORTModelForSequenceClassification.from_pretrained(MODEL_DIR)
_labels = _model.config.id2label


def classify(text: str) -> dict[str, float]:
    inputs = _tok(text, return_tensors="np", truncation=True, max_length=256)
    logits = _model(**inputs).logits[0]
    probs = 1 / (1 + np.exp(-logits))         
    return {_labels[i]: float(p) for i, p in enumerate(probs)}


def toxicity_score(text: str) -> float:
    return max(classify(text).values())