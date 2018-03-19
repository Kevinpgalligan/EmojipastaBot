"""
Used to parse the r/emojipasta comments and form
word-emoji associations.
"""

import io
from collections import defaultdict
import json

import emojipasta.util.files
import emojipasta.util.emoji

class TokenType:
    EMOJIS = 0
    WORD = 1

class Token:
    def __init__(self, token_type, raw):
        self.token_type = token_type
        self.raw = raw

def main():
    emoji_mappings = defaultdict(list)

    print("Creating mappings...")
    with open(emojipasta.util.files.PATH_TO_COMMENTS_FILE, "r", encoding="utf-8") as comments_file:
        for line in comments_file:
            tokens = tokenize(line)
            for i, token in enumerate(tokens):
                if token.token_type == TokenType.EMOJIS:
                    nearest_word = find_nearest_word(i, tokens)
                    if nearest_word is not None:
                        emoji_mappings[nearest_word].extend(list(token.raw))

    print("Writing mappings to file...")
    with io.open(emojipasta.util.files.PATH_TO_MAPPINGS_FILE, "w", encoding="utf-8") as mappings_file:
        json.dump(emoji_mappings, mappings_file, ensure_ascii=False)

def tokenize(line):
    tokens = []
    index = 0
    while index < len(line):
        index = skip_irrelevant_characters(line, index)
        token, index = parse_token(line, index)
        if token is not None:
            tokens.append(token)
    return tokens

def skip_irrelevant_characters(line, index):
    while index < len(line) and not line[index].isalnum() and not emojipasta.util.emoji.is_emoji(line[index]):
        index += 1
    return index

def parse_token(line, index):
    if index >= len(line):
        return None, index
    elif emojipasta.util.emoji.is_emoji(line[index]):
        return parse_emoji(line, index)
    else:
        return parse_word(line, index)

def parse_emoji(line, index):
    return parse_specific_token(line, index, TokenType.EMOJIS, emojipasta.util.emoji.is_emoji)

def parse_word(line, index):
    return parse_specific_token(line, index, TokenType.WORD, str.isalnum)

def parse_specific_token(line, index, token_type, is_part_of_token_fn):
    new_index = index
    while new_index < len(line) and is_part_of_token_fn(line[new_index]):
        new_index += 1
    return Token(token_type, line[index: new_index].lower()), new_index

def find_nearest_word(i, tokens):
    # First try to go back, since that's likely the most relevant
    # word to the emoji.
    # This is some pretty "unpythonic" code, but you do what you
    # gotta do.
    j = i - 1
    while j >= 0:
        if tokens[j].token_type == TokenType.WORD:
            return tokens[j].raw
        j -= 1
    j = i + 1
    while j < len(tokens):
        if tokens[j].token_type == TokenType.WORD:
            return tokens[j].raw
        j += 1
    return None

if __name__ == "__main__":
    main()