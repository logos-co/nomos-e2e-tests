import re

import sklearn.feature_extraction.text as ext
import pandas as pd
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS


def normalize_log_message(text):
    # Remove timestamps (e.g., "2023-10-01 12:34:56")
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "", text)
    # Remove numeric IDs (e.g., "user123", "session456")
    text = re.sub(r"\b\w*\d+\w*\b", "", text)
    return " ".join(text.split())


def write_output(df, output_file=None):
    lines = df["d1"].astype(str) + "\n"

    if output_file:
        with open(output_file, "w") as out_file:
            out_file.writelines(lines)

    print("".join(lines), end="")


class LogTfidf:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = self._generate_stop_words()

    def _generate_stop_words(self):
        stop_words = [self.stemmer.stem(word) for word in ENGLISH_STOP_WORDS if word.isalpha()]
        # Add any missing stemmed tokens from the warning
        stop_words.extend(["anywh", "becau", "el", "elsewh", "everywh", "ind", "otherwi", "plea", "somewh"])
        return stop_words

    def get_stemmed_tokens(self, tokens):
        return [self.stemmer.stem(token) for token in tokens if token.isalpha()]

    def get_tokens(self, text):
        tokens = word_tokenize(text.lower())
        return self.get_stemmed_tokens(tokens)

    def parse_log(self, input_file, keywords, output_file=None):
        vectorizer = ext.CountVectorizer(tokenizer=self.get_tokens, stop_words=self.stop_words, token_pattern=None)
        with open(input_file, "r") as file:
            lines = [line.rstrip() for line in file]
        line_nos = dict(zip(range(1, len(lines)), lines))
        doc_matrix = vectorizer.fit_transform(lines)

        tf_idf_transformer = ext.TfidfTransformer().fit(doc_matrix)
        sparse = tf_idf_transformer.transform(doc_matrix).toarray()

        per_line_score = []
        for row in sparse:
            nonzero_count = len(row.nonzero()[0])
            score = row.sum() / nonzero_count if nonzero_count > 0 else 0
            per_line_score.append(score)

        line_scores = dict(zip(range(1, len(lines)), per_line_score))

        # Filter by keywords and sort according to rarity
        df = pd.DataFrame([line_nos, line_scores]).T
        df.columns = ["d1", "d2"]  # Simplified column naming for clarity
        df = df.sort_values(by="d2", ascending=False)
        pattern = "|".join(keywords)
        df = df[~((df["d1"].str.contains("INFO|DEBUG|TRACE")) & (~df["d1"].str.contains(pattern)))]

        # Normalize and deduplicate
        df["d1_normalized"] = df["d1"].apply(normalize_log_message)
        df = df.drop_duplicates(subset="d1_normalized", keep="first")
        df = df.drop(columns="d1_normalized")

        write_output(df, output_file)
