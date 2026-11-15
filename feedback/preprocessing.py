import re
from collections import Counter

import nltk
from nltk import pos_tag, ne_chunk, FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tree import Tree


# --------------------------------------------------
# Initialize NLP resources
# --------------------------------------------------

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Preserve negation words because they affect sentiment.
stop_words.difference_update({"not", "no", "nor", "never"})


# --------------------------------------------------
# POS tag to WordNet POS mapping
# --------------------------------------------------

def get_wordnet_pos(tag):
    """
    Convert Penn Treebank POS tags to WordNet POS tags.
    """

    if tag.startswith("J"):
        return "a"  # Adjective

    elif tag.startswith("V"):
        return "v"  # Verb

    elif tag.startswith("N"):
        return "n"  # Noun

    elif tag.startswith("R"):
        return "r"  # Adverb

    return "n"      # Default to noun


# --------------------------------------------------
# Basic text cleaning
# --------------------------------------------------

def clean_text(text):
    """
    Lowercase text, remove URLs, and remove unwanted
    characters while preserving apostrophes.
    """

    text = text.lower()

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Keep English letters, whitespace, apostrophes
    text = re.sub(
        r"[^a-z\s']",
        " ",
        text
    )

    # Normalize repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# --------------------------------------------------
# POS tagging
# --------------------------------------------------

def perform_pos_tagging(text):
    """
    Identify grammatical roles of words.
    """

    tokens = [
        token
        for token in wordpunct_tokenize(text)
        if token.isalpha()
    ]

    return pos_tag(tokens)


# --------------------------------------------------
# Named Entity Recognition (NER)
# --------------------------------------------------

def extract_named_entities(text):
    """
    Identify entities such as people, organizations,
    and locations using NLTK's named entity chunker.
    """

    tagged_words = perform_pos_tagging(text)

    chunk_tree = ne_chunk(tagged_words)

    entities = []

    for subtree in chunk_tree:
        if isinstance(subtree, Tree):
            entity_name = " ".join(
                word for word, tag in subtree.leaves()
            )

            entities.append({
                "entity": entity_name,
                "label": subtree.label()
            })

    return entities


# --------------------------------------------------
# Frequency Distribution
# --------------------------------------------------

def get_frequency_distribution(tokens):
    """
    Count occurrences of each cleaned token.
    """

    frequency = FreqDist(tokens)

    return dict(frequency.most_common())


# --------------------------------------------------
# Main preprocessing function
# --------------------------------------------------

def preprocess_text(text):
    """
    Prepare feedback for the TF-IDF vectorizer
    and sentiment classification model.
    """

    text = clean_text(text)

    # Tokenize
    tokens = wordpunct_tokenize(text)

    # POS tagging for POS-aware lemmatization
    tagged_tokens = pos_tag([
        token for token in tokens
        if token.isalpha()
    ])

    cleaned_tokens = []

    for token, tag in tagged_tokens:

        # Remove stopwords, but retain negations
        if token in stop_words:
            continue

        # Lemmatize using the grammatical role
        wordnet_pos = get_wordnet_pos(tag)

        lemma = lemmatizer.lemmatize(
            token,
            pos=wordnet_pos
        )

        cleaned_tokens.append(lemma)

    # Return a string for TF-IDF
    return " ".join(cleaned_tokens)


# --------------------------------------------------
# Complete feedback analysis
# --------------------------------------------------

def analyze_feedback(text):
    """
    Perform preprocessing, POS tagging, NER,
    and frequency analysis on feedback.
    """

    cleaned_text = clean_text(text)

    # POS tagging on cleaned text
    tagged_words = perform_pos_tagging(cleaned_text)

    # Named entities on cleaned text
    entities = extract_named_entities(cleaned_text)

    # Preprocessed text for sentiment prediction
    processed_text = preprocess_text(text)

    # Token list for frequency analysis
    processed_tokens = processed_text.split()

    frequencies = get_frequency_distribution(processed_tokens)

    return {
        "cleaned_text": cleaned_text,
        "processed_text": processed_text,
        "pos_tags": tagged_words,
        "named_entities": entities,
        "word_frequencies": frequencies,
        "total_tokens": len(processed_tokens),
        "unique_words": len(set(processed_tokens)),
    }
