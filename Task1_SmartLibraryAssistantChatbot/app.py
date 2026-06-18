from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from utils.chatbot_engine import LibraryChatbot


BASE_DIR = Path(__file__).resolve().parent
FAQ_PATH = BASE_DIR / "library_faq.csv"
HISTORY_PATH = BASE_DIR / "chat_history.txt"

app = Flask(__name__)
chatbot = LibraryChatbot(FAQ_PATH)


def save_chat_history(user_message, bot_response):
    """Append every conversation turn to a plain text history file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"[{timestamp}]\n"
        f"User: {user_message}\n"
        f"Bot: {bot_response}\n"
        f"{'-' * 60}\n"
    )
    HISTORY_PATH.write_text(
        HISTORY_PATH.read_text(encoding="utf-8") + entry
        if HISTORY_PATH.exists()
        else entry,
        encoding="utf-8",
    )


def get_total_questions_asked():
    """Count stored user messages from the history file."""
    if not HISTORY_PATH.exists():
        return 0
    return HISTORY_PATH.read_text(encoding="utf-8").count("User:")


@app.route("/")
def index():
    return render_template(
        "index.html",
        total_faqs=chatbot.total_faqs,
        total_questions=get_total_questions_asked(),
        popular_questions=chatbot.popular_questions,
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    result = chatbot.get_response(user_message)
    save_chat_history(user_message, result["answer"])

    return jsonify(
        {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "confidence_label": result["confidence_label"],
            "matched_question": result["matched_question"],
            "intent": result["intent"],
            "total_faqs": chatbot.total_faqs,
            "total_questions": get_total_questions_asked(),
            "timestamp": datetime.now().strftime("%I:%M %p"),
        }
    )


@app.route("/api/faqs")
def faqs():
    return jsonify(chatbot.get_faqs())


@app.route("/api/search")
def search_faqs():
    query = (request.args.get("q") or "").strip()
    return jsonify(chatbot.search_faqs(query))


@app.route("/api/stats")
def stats():
    return jsonify(
        {
            "total_faqs": chatbot.total_faqs,
            "total_questions": get_total_questions_asked(),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
