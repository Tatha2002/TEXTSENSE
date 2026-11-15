import os
import pickle

from functools import lru_cache
from feedback.preprocessing import preprocess_text


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models","sentiment_model.pkl")


@lru_cache(maxsize=1)
def load_model():
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


def predict_sentiment_details(feedback_text, processed_text=None):

    saved_data = load_model()

    model = saved_data["model"]
    vectorizer = saved_data["vectorizer"]

    if processed_text is None:
        processed_text = preprocess_text(feedback_text)

    text_vector = vectorizer.transform([processed_text])
    prediction = model.predict(text_vector)[0]
    probabilities = model.predict_proba(text_vector)[0]
    confidence = max(probabilities) * 100

    probability_details = {
        str(label): round(float(probability) * 100, 2)
        for label, probability in zip(
            model.classes_,
            probabilities
        )
    }

    return {
        "sentiment": str(prediction),
        "confidence": round(float(confidence), 2),
        "probabilities": probability_details,
    }


def predict_sentiment(feedback_text):
    result = predict_sentiment_details(feedback_text)
    return result["sentiment"]