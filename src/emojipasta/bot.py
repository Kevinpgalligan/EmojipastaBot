"""
A bot that responds to mentions on reddit with an emojipasta
version of the parent of that mention.
"""

import time
import sys

from praw.models import Comment, Submission
import praw.exceptions

from emojipasta.util.client import get_reddit
from emojipasta.generator import EmojipastaGenerator

SECONDS_BETWEEN_RUNS = 180
SECONDS_TO_WAIT_AFTER_RATE_LIMITING = 600

def normalize_name(name):
    return name.lower()

RAW_USER_BLACKLIST = [
    # A bot that keeps turning up whenever someone makes a
    # mistake in the tag, causes feedback loop with emojipasta bot.
    "Sub_Corrector_Bot",
    # Generally a good policy, this one can be unpredictable.
    "AutoModerator"
]
USER_BLACKLIST = [normalize_name(name) for name in RAW_USER_BLACKLIST]

class EmojipastaBot:

    MAX_NUM_TAGS_PER_USER_IN_CHAIN = 3
    COMMENT_LOG_INDENT = 4

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
            if isinstance(mention, Comment) and self._was_tagged_in(mention):
                log("Received comment:")
                self._reply_to_comment(mention)
        log("Finished reading inbox.")
        log("========")

    def _was_tagged_in(self, mention):
        # Cast the mention to lower case, the username might
        # not be capitalized correctly.
        return self._tag_for_bot in mention.body.lower()

    def _reply_to_comment(self, comment):
        indented_log("Author is u/" + author_name(comment) + ".")
        should_reply = True
        if self._user_has_tagged_too_many_times_in_thread(comment):
            should_reply = False
            indented_log("Author has tagged too many times in this comment chain, ignoring.")
        if self._author_is_in_blacklist(comment):
            should_reply = False
            indented_log("Author is blacklisted, ignoring.")
        got_rate_limited = False
        if should_reply:
            # Always mark as 'read' BEFORE attempting to reply,
            # as otherwise the bot might get stuck in a loop
            # trying to reply to the same comment and crashing.
            # For example, an exception is thrown due to a 403
            # HTTP error if the bot attempts to respond in a subreddit
            # in which it is banned.
            self._inbox.mark_read([comment])
            got_rate_limited = self._attempt_reply(comment)
        if got_rate_limited:
            indented_log("Got rate-limited, will try again in next pass of inbox.")
            self._wait_for_rate_limiting_to_pass()
            self._inbox.mark_unread([comment])
        indented_log("Comment processed.")

    def _user_has_tagged_too_many_times_in_thread(self, mention):
        tags = 0
        comment = mention
        while not comment.is_root:
            if author_name(comment) == author_name(mention) and self._was_tagged_in(comment):
                tags += 1
            comment = comment.parent()
        return tags > EmojipastaBot.MAX_NUM_TAGS_PER_USER_IN_CHAIN

    def _author_is_in_blacklist(self, comment):
        return author_name(comment) in USER_BLACKLIST

    """Attempts reply, failures due to API exceptions are caught.

    return: True if the bot failed the attempt due to rate limiting,
    False otherwise.
    """
    def _attempt_reply(self, mention):
        text_of_parent = get_text_of_parent(mention)
        indented_log("Text of parent is: " + text_of_parent)
        emojipasta = self._emojipasta_generator.generate_emojipasta(text_of_parent)
        indented_log("Generated emojipasta: " + emojipasta)
        try:
            mention.reply(emojipasta)
        except praw.exceptions.APIException as e:
            indented_log("API exception: " + e.message)
            if e.error_type == "RATELIMIT":
                return True
        return False

    def _wait_for_rate_limiting_to_pass(self):
        indented_log("Waiting %d seconds for rate-limiting to wear off.".format(SECONDS_TO_WAIT_AFTER_RATE_LIMITING))
        time.sleep(SECONDS_TO_WAIT_AFTER_RATE_LIMITING)

def get_text_of_parent(comment):
    parent = comment.parent()
    if isinstance(parent, Submission):
        return parent.selftext
    elif isinstance(parent, Comment):
        return parent.body
    return ""

"""Returns normalized name of the comment's author."""
def author_name(comment):
    return "[deleted]" if comment.author is None else normalize_name(comment.author.name)

def log(message, indent=0):
    print((indent * " ") + message)

def indented_log(message):
    log(message, EmojipastaBot.COMMENT_LOG_INDENT)

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