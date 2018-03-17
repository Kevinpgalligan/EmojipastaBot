"""
Generate emojipasta from text.
"""

import random
import io
import json

import util.text
import util.emoji
import util.files

# Lazy initialization, use get_emoji_mappings().
EMOJI_MAPPINGS = None

class EmojipastaGenerator:

    _WORD_DELIMITER = " "
    _MAX_EMOJIS_PER_BLOCK = 2

    """Creates with default emoji mappings, loaded from a JSON file in the package.
    """
    @classmethod
    def of_default_mappings(cls):
        return EmojipastaGenerator(get_emoji_mappings())

    """Create with custom emoji mappings.
    emoji_mappings: a dict that maps from a lowercase word to a
        list of emojis (the emojis being single-character strings).
    """
    @classmethod
    def of_custom_mappings(cls, emoji_mappings):
        return EmojipastaGenerator(emoji_mappings)

    def __init__(self, emoji_mappings):
        self._emoji_mappings = emoji_mappings

    def generate_emojipasta(self, text):
        blocks = util.text.split_into_blocks(text)
        new_blocks = []
        for i, block in enumerate(blocks):
            new_blocks.append(block)
            emojis = self._generate_emojis_from(block)
            if emojis:
                new_blocks.append(" " + emojis)
        return "".join(new_blocks)

    def _generate_emojis_from(self, block):
        trimmed_block = util.text.trim_nonalphabetical_characters(block)
        matching_emojis = self._get_matching_emojis(trimmed_block)
        emojis = []
        if matching_emojis:
            num_emojis = random.randint(0, self._MAX_EMOJIS_PER_BLOCK)
            for _ in range(num_emojis):
                emojis.append(random.choice(matching_emojis))
        return "".join(emojis)

    def _get_matching_emojis(self, trimmed_block):
        key = self._get_alphanumeric_prefix(trimmed_block.lower())
        if key in self._emoji_mappings:
            return self._emoji_mappings[self._get_alphanumeric_prefix(key)]
        return []

    def _get_alphanumeric_prefix(self, s):
        i = 0
        while i < len(s) and s[i].isalnum():
            i += 1
        return s[:i]

def get_emoji_mappings():
    if EMOJI_MAPPINGS is not None:
        return EMOJI_MAPPINGS
    with io.open(util.files.PATH_TO_MAPPINGS_FILE, "r", encoding="utf-8") as mappings_file:
        return json.load(mappings_file)

def main():
    generator = EmojipastaGenerator.of_default_mappings()
    print(generator.generate_emojipasta("it's getting hot in here"))

if __name__ == "__main__":
    main()
