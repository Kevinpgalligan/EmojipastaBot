"""
Common emoji code.
"""

import random

import emoji

EMOJIS = set(emoji.emojize(emoji_code) for emoji_code in emoji.UNICODE_EMOJI.values())

def is_emoji(c):
    return c in EMOJIS

def get_random_emojis(n):
    return random.sample(EMOJIS, n)
