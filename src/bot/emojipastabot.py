"""
A bot that responds to mentions on reddit with an emojipasta
version of the parent of that mention.
"""

import time
import sys

from praw.models import Comment, Submission
import praw.exceptions

from util.client import get_reddit
from emojipasta.emojipastagenerator import EmojipastaGenerator

SECONDS_BETWEEN_RUNS = 60
SECONDS_TO_WAIT_AFTER_RATE_LIMITING = 600

class EmojipastaBot:

    MAX_NUM_REPLIES_IN_CHAIN = 5

    """Basic constructor.

    Args:
        reddit -- PRAW Reddit instance.
        emojipasta_generator -- EmojipastaGenerator instance.
    """
    def __init__(self, reddit, emojipasta_generator):
        self._reddit = reddit
        self._inbox = reddit.inbox
        self._emojipasta_generator = emojipasta_generator
        self._bot_name = reddit.user.me().name.lower()
        self._tag_for_bot = "u/" + self._bot_name

    """Attempts to respond to all of the bot's username mentions.
    
    Comments that don't contain a mention, private messages, etc. will
    be left unread.
    """
    def reply_to_username_mentions(self):
        log("Reading inbox...")
        for mention in self._inbox.unread(limit=None):
            if self._should_reply(mention):
                log("====== COMMENT ======")
                log("Received comment from u/" + mention.author.name + ".")
                text_of_parent = get_text_of_parent(mention)
                log("Text of parent is: " + text_of_parent)
                emojipasta = self._emojipasta_generator.generate_emojipasta(text_of_parent)
                log("Generated emojipasta: " + emojipasta)
                reply_successful = attempt_reply(mention, emojipasta)
                if reply_successful:
                    log("Replied successfully!")
                    self._inbox.mark_read([mention])
        log("========")

    def _should_reply(self, mention):
        return (isinstance(mention, Comment)
            # Cast the mention to lower case, the username might
            # not be capitalized correctly.
            and self._tag_for_bot in mention.body.lower()
            and not self._have_replied_too_many_times_in_comment_chain(mention))

    def _have_replied_too_many_times_in_comment_chain(self, mention):
        num_replies = 0
        comment = mention
        while not comment.is_root:
            if comment.author == self._bot_name:
                num_replies += 1
            comment = comment.parent()
        return num_replies > EmojipastaBot.MAX_NUM_REPLIES_IN_CHAIN

def get_text_of_parent(comment):
    parent = comment.parent()
    if isinstance(parent, Submission):
        return parent.selftext
    elif isinstance(parent, Comment):
        return parent.body
    else:
        # This should never happen.
        raise Exception("Unknown type of parent!")

"""Attempts reply, failures due to API exceptions are caught.

Returns Boolean representing whether the original comment should
be marked as "read". Returns True even if there was an unexpected
API exception, however, because we don't want to keep retrying the
same comment over and over because it has exposed a bug (e.g. comment
size too large when emojis are added).
"""
def attempt_reply(comment, reply_text):
    try:
        comment.reply(reply_text)
    except praw.exceptions.APIException as e:
        log("API exception: " + e.message)
        if e.error_type == "RATELIMIT":
            log("Got rate-limited, can't reply yet.")
            log(
                "Waiting %d seconds for rate-limiting to wear off, then can try again"
                    .format(SECONDS_TO_WAIT_AFTER_RATE_LIMITING))
            time.sleep(SECONDS_TO_WAIT_AFTER_RATE_LIMITING)
            return False
    return True

def log(message):
    print(message)

def main():
    bot = EmojipastaBot(get_reddit(sys.argv), EmojipastaGenerator.of_default_mappings())
    while True:
        try:
            bot.reply_to_username_mentions()
        except Exception as e:
            # We don't want the bot to stop running whenever an unexpected
            # exception is encountered. (E.g. socket timeout, which happened
            # before).
            log("Encountered exception while attempting to run bot: " + str(e))
        time.sleep(SECONDS_BETWEEN_RUNS)

if __name__ == "__main__":
    main()