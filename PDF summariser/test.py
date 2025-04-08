import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
import heapq

# Ensure required NLTK data is available (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')

test_text = (
    "Artificial intelligence is transforming the world. "
    "It is being applied in various fields such as healthcare, education, and finance. "
    "Advancements in machine learning have led to significant improvements. "
    "However, ethical challenges remain that must be addressed. "
    "Ongoing research is vital to balance innovation with safety."
)

# Tokenize the text into sentences.
sentences = sent_tokenize(test_text)

# Create a set of stopwords and punctuation.
stop_words = set(stopwords.words("english"))

# Build a frequency table for words in the text.
word_frequencies = {}
for word in word_tokenize(test_text.lower()):
    if word in stop_words or word in punctuation:
        continue
    word_frequencies[word] = word_frequencies.get(word, 0) + 1

# Score each sentence based on word frequency.
sentence_scores = {}
for sentence in sentences:
    for word in word_tokenize(sentence.lower()):
        if word in word_frequencies:
            sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]

# Pick the top 3 sentences.
summary_sentences = heapq.nlargest(3, sentence_scores, key=sentence_scores.get)

# Combine selected sentences into a summary.
summary = " ".join(summary_sentences)
print("Summary:", summary)
