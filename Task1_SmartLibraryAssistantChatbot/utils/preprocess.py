import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize


_FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for",
    "from", "has", "have", "how", "i", "in", "is", "it", "of", "on", "or",
    "the", "to", "what", "when", "where", "which", "who", "why", "with",
}
_DOMAIN_STOPWORDS = {"library", "libraries"}

stemmer = PorterStemmer()


def _load_stopwords():
    """Load NLTK stopwords, downloading them once if needed."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        try:
            nltk.download("stopwords", quiet=True)
            return set(stopwords.words("english"))
        except Exception:
            return _FALLBACK_STOPWORDS


STOPWORDS = _load_stopwords() | _DOMAIN_STOPWORDS
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def normalize_text(text):
    """Lowercase text and remove punctuation."""
    return str(text).lower().translate(PUNCTUATION_TABLE)


def tokenize_text(text):
    """Tokenize text without requiring the heavier Punkt tokenizer data."""
    return wordpunct_tokenize(text)


def preprocess_text(text):
    """Return a clean, stemmed string suitable for TF-IDF matching."""
    normalized = normalize_text(text)
    tokens = tokenize_text(normalized)
    cleaned_tokens = [
        stemmer.stem(token)
        for token in tokens
        if token.isalpha() and token not in STOPWORDS
    ]
    return " ".join(cleaned_tokens)
