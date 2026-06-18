import random

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.preprocess import preprocess_text


UNKNOWN_RESPONSE = (
    "Sorry, I could not find a relevant answer. Please contact the librarian "
    "for further assistance."
)


class LibraryChatbot:
    """NLP-powered FAQ matcher for library questions."""

    def __init__(self, faq_path, confidence_threshold=0.30):
        self.faq_path = faq_path
        self.confidence_threshold = confidence_threshold
        self.greetings = {
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        }
        self.thanks = {"thanks", "thank you", "thankyou", "thx"}
        self.exits = {"bye", "exit", "quit", "goodbye", "see you"}
        self.greeting_responses = [
            "Hello! I am Libby, your Smart Library Assistant. How can I help you today?",
            "Hi there! Ask me about library timings, renewals, cards, fines, or reservations.",
            "Welcome to the Smart Library Assistant. What library question can I answer?",
        ]
        self.popular_questions = [
            "What are library timings?",
            "How do I renew a book?",
            "Can I reserve a book online?",
            "What is the fine for late return?",
            "How can I obtain a library card?",
        ]
        self._load_dataset()
        self._fit_vectorizer()

    def _load_dataset(self):
        self.faq_df = pd.read_csv(self.faq_path)
        self.faq_df = self.faq_df.dropna(subset=["question", "answer"]).reset_index(drop=True)
        self.faq_df["processed_question"] = self.faq_df["question"].apply(preprocess_text)
        self.total_faqs = len(self.faq_df)

    def _fit_vectorizer(self):
        self.vectorizer = TfidfVectorizer()
        self.faq_vectors = self.vectorizer.fit_transform(self.faq_df["processed_question"])

    def _exact_intent(self, message):
        cleaned = " ".join(str(message).lower().strip().split())
        if cleaned in self.greetings:
            return {
                "answer": random.choice(self.greeting_responses),
                "confidence": 1.0,
                "matched_question": "Greeting",
                "intent": "greeting",
            }
        if cleaned in self.thanks:
            return {
                "answer": "You're welcome. Happy reading!",
                "confidence": 1.0,
                "matched_question": "Thank You",
                "intent": "thanks",
            }
        if cleaned in self.exits:
            return {
                "answer": "Thank you for using Smart Library Assistant. Have a great day!",
                "confidence": 1.0,
                "matched_question": "Exit",
                "intent": "exit",
            }
        return None

    def get_response(self, message):
        intent_response = self._exact_intent(message)
        if intent_response:
            return self._format_response(intent_response)

        processed_query = preprocess_text(message)
        if not processed_query:
            return self._format_response(
                {
                    "answer": UNKNOWN_RESPONSE,
                    "confidence": 0.0,
                    "matched_question": "No confident FAQ match",
                    "intent": "unknown",
                }
            )

        query_vector = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.faq_vectors).flatten()
        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])

        if best_score < self.confidence_threshold:
            return self._format_response(
                {
                    "answer": UNKNOWN_RESPONSE,
                    "confidence": best_score,
                    "matched_question": self.faq_df.loc[best_index, "question"],
                    "intent": "unknown",
                }
            )

        return self._format_response(
            {
                "answer": self.faq_df.loc[best_index, "answer"],
                "confidence": best_score,
                "matched_question": self.faq_df.loc[best_index, "question"],
                "intent": "faq",
            }
        )

    def _format_response(self, result):
        confidence = round(result["confidence"] * 100)
        if confidence >= 80:
            label = "Excellent match"
        elif confidence >= 55:
            label = "Good match"
        elif confidence >= 30:
            label = "Possible match"
        else:
            label = "Low confidence"

        return {
            "answer": result["answer"],
            "confidence": confidence,
            "confidence_label": label,
            "matched_question": result["matched_question"],
            "intent": result["intent"],
        }

    def get_faqs(self):
        return self.faq_df[["question", "answer"]].to_dict(orient="records")

    def search_faqs(self, query):
        if not query:
            return []
        query = query.lower()
        matches = self.faq_df[
            self.faq_df["question"].str.lower().str.contains(query, na=False)
            | self.faq_df["answer"].str.lower().str.contains(query, na=False)
        ]
        return matches[["question", "answer"]].head(8).to_dict(orient="records")
