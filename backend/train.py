# train.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump
from dotenv import load_dotenv

load_dotenv()

DATASET_PATH = "data/dataset.csv"
MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "svm_model.joblib")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")

def main():
    if not os.path.exists(DATASET_PATH):
        print("❌ dataset.csv not found. Run collect_data.py first!")
        return

    df = pd.read_csv(DATASET_PATH)

    # Use only text + label
    df = df.dropna(subset=["text", "label"])

    X = df["text"]
    y = df["label"].astype(int)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # SVM classifier
    clf = SVC(kernel="linear", probability=True)
    clf.fit(X_train_tfidf, y_train)

    # Evaluation
    y_pred = clf.predict(X_test_tfidf)
    print("\n✅ MODEL TRAINED SUCCESSFULLY\n")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save model + vectorizer
    os.makedirs(MODEL_DIR, exist_ok=True)
    dump(clf, MODEL_FILE)
    dump(vectorizer, VECTORIZER_FILE)

    print(f"\n✅ Model saved to: {MODEL_FILE}")
    print(f"✅ Vectorizer saved to: {VECTORIZER_FILE}")

if __name__ == "__main__":
    main()
