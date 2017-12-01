import re
from nltk.tokenize.moses import MosesTokenizer


class _Trimmer:
    trimming_regex_for_beginning = re.compile(r"^[\W]+")
    trimming_regex_for_end = re.compile(r"[\W]+$")

    """Trims non-alphabetical characters from the start & end of a string."""
    def trim_nonalphabetical_chars(self, s):
        s_with_beginning_trimmed = self.trimming_regex_for_beginning.sub("", s)
        return self.trimming_regex_for_end.sub("", s_with_beginning_trimmed)


class WordRootCalculator:

    @classmethod
    def create(cls):
        return WordRootCalculator(_Trimmer(), MosesTokenizer())

    def __init__(self, trimmer, tokenizer):
        self._trimmer = trimmer
        self._tokenizer = tokenizer

    def calculate_root(self, word):
        trimmed = self._trimmer.trim_nonalphabetical_chars(word)
        tokens = self._tokenizer.word_tokenize(trimmed)
        return None if not tokens else tokens[0]
