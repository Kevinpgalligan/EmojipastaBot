"""
Common emoji code.
"""

import emoji

EMOJIS = set(emoji.emojize(emoji_code['en']) for emoji_code in emoji.EMOJI_DATA.values())

def is_emoji(c):
    return c in EMOJIS
