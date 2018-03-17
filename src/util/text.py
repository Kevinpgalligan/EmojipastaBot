"""
Some utilities for transforming text.
"""

import re

BLOCK_REGEX = re.compile(r"\s*[^\s]*")
TRIM_REGEX = re.compile(r"^\W*|\W*$")

def split_into_blocks(text):
    if text == "" or BLOCK_REGEX.search(text) is None:
        return [text]
    blocks = []
    start = 0
    while start < len(text):
        block_match = BLOCK_REGEX.search(text, start)
        blocks.append(block_match.group())
        start = block_match.end()
    return blocks

def trim_nonalphabetical_characters(text):
    return TRIM_REGEX.sub("", text)

def main():
    print(split_into_blocks("hello"))
    print(split_into_blocks("    hello"))
    print(split_into_blocks("    hello    "))
    print(split_into_blocks("      "))
    print(split_into_blocks("    hello     hi   world"))
    print(split_into_blocks(""))

    print(repr(trim_nonalphabetical_characters(" .. ##]hi ()() there! !")))
    print(repr(trim_nonalphabetical_characters("")))

if __name__ == "__main__":
    main()