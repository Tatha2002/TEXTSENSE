import os
import pickle
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from feedback.preprocessing import preprocess_text


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = os.path.join(BASE_DIR, "data", "feedback.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "sentiment_model.pkl")


# Load the CSV dataset
df = pd.read_csv(CSV_PATH)

# Check the actual column names
print("CSV columns:", df.columns.tolist())

# Remove rows with missing feedback or sentiment
df = df.dropna(subset=["review", "sentiment"])

# Preprocess the feedback
df["review"] = df["review"].astype(str)
df["sentiment"] = df["sentiment"].astype(str).str.strip().str.title()

df["processed_text"] = df["review"].apply(preprocess_text)

X = df["processed_text"]
y = df["sentiment"]

# Split dataset into training and testing data
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y,)

# Convert text into numerical features
vectorizer = TfidfVectorizer(ngram_range=(1, 2),max_features=100000,min_df=2,)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train the sentiment classifier
model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

# Evaluate the model
predictions = model.predict(X_test_tfidf)
print(classification_report(y_test, predictions))

# Save the trained model and vectorizer
os.makedirs(MODEL_DIR, exist_ok=True)

with open(MODEL_PATH, "wb") as file:
    pickle.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
        },
        file,
    )

print(f"Model saved successfully at: {MODEL_PATH}")