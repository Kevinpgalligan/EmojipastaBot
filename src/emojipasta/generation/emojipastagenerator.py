import math
from collections import defaultdict

from nltk.tokenize.moses import MosesTokenizer

from src.emojipasta.utils import create_squared_distribution

"""
High-level plan:
* Other steps:
    * Scrape /r/emojipasta for dataset.
    * Generate word->emoji mappings using different weighting schemes and
      see which ones give the best results (example scheme: if an emoji occurs
      beside a word, add 1 to the mapping; if it occurs in the same sentence as
      a word, add 1/num_words_in_sentence or 1/words_away_from_emoji). Ooooh, maybe
      instead of doing it by sentence... apply it to all words that are to the left
      of the emoji?
* Eventually need a strategy for dealing with word pairs ("old man")
  and other edge cases. Don't need to solve that now, just come up
  with a design that is flexible enough to be extended later.
"""

"""
TODO
* docstrings
* make it language-agnostic
* Decide whether to leave blank line after class header, be consistent.
"""


# TODO write docstring
class EmojipastaGenerator:

    _WORD_DELIMITER = " "

    @classmethod
    def of(cls, emojis_per_word):
        return EmojipastaGenerator(
            MosesTokenizer(),
            load_word_emoji_associations(),
            create_squared_distribution,
            emojis_per_word)

    def __init__(self, tokenizer, word_emoji_associations, distribution_creation_fn, emojis_per_word):
        self._tokenizer = tokenizer
        self._word_emoji_associations = word_emoji_associations
        self._distribution_creation_fn = distribution_creation_fn
        self._emojis_per_word = emojis_per_word

    # TODO first, write unit tests for distributions.py and words.py.
    # TODO then, ideas for breaking this up more:
    #   1. Have another class for generating emojipasta for a sentence.
    #   2. Another class for taking words, inserting emojis?
    #   3. Another class that takes a list of words, returns index->emojis map?
    #   4. Another class that creates an (index,emoji) distribution given a list of words?
    #   That sounds reasonably easy to test, at least.
    def generate_emojipasta(self, text):
        new_sentences = []
        for sentence in self._tokenizer.sent_tokenize(text):
            words = sentence.split(EmojipastaGenerator._WORD_DELIMITER)
            index_emoji_distribution = self._distribution_creation_fn()
            for index, word in enumerate(words):
                for (emoji, weight) in self._word_emoji_associations[word]:
                    index_emoji_distribution.add((index, emoji), weight)

            index_to_emojis = defaultdict(list)
            emojis_to_add = int(math.ceil(self._emojis_per_word * len(words)))
            for _ in range(emojis_to_add):
                index, emoji = index_emoji_distribution.get_random()
                index_to_emojis[index].append(emoji)

            new_words = []
            for index, word in enumerate(words):
                new_words.append(word)
                new_words.append("".join(index_to_emojis[index]))

            new_sentences.append(" ".join(new_words))
        return " ".join(new_sentences)


class WordEmojiAssociations:
    def __init__(self, raw_associations, word_root_calculator):
        self._raw_associations = raw_associations
        self._word_root_calculator = word_root_calculator

    def __getitem__(self, word):
        return self._raw_associations[self._word_root_calculator.calculate_root(word)]

    def __str__(self):
        return "[WordEmojiAssociations " + str(self._raw_associations) + "]"


# TODO scrape reddit to get these associations, save them as a Python pickle? Or maybe
# in a human-readable format, e.g. JSON.
def load_word_emoji_associations():
    return None


def main():
    pass
    # generator = EmojipastaGenerator({"world": "🌍"})
    # print(generator.generate_emojipasta("hello world"))
    # print(nltk.sent_tokenize("don't hello world me, missy! But do do the thing."))


if __name__ == "__main__":
    main()
