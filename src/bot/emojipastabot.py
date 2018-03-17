"""
A bot that responds to mentions on reddit with an emojipasta
version of the parent of that mention.
"""

import time
import sys

from praw.models import Comment, Submission
import praw.exceptions

from util.client import get_client
from emojipasta.emojipastagenerator import EmojipastaGenerator

SECONDS_BETWEEN_CHECKS = 60
SECONDS_TO_WAIT_AFTER_RATE_LIMITING = 600

def main():
    reddit = get_client(sys.argv)
    emojipasta_generator = EmojipastaGenerator.of_default_mappings()
    bot_user_tag = "u/" + reddit.user.me().name

    inbox = reddit.inbox
    while True:
        log("Reading inbox...")
        for mention in inbox.unread(limit=None):
            if isinstance(mention, Comment) and bot_user_tag in mention.body:
                log("====== COMMENT ======")
                log("Received comment from u/" + mention.author.name + ".")
                text_of_parent = get_text_of_parent(mention)
                log("Text of parent is: " + text_of_parent)
                emojipasta = emojipasta_generator.generate_emojipasta(text_of_parent)
                log("Generated emojipasta: " + emojipasta)
                reply_successful = attempt_reply(mention, emojipasta)
                if reply_successful:
                    log("Replied successfully!")
                    inbox.mark_read([mention])
        log("========")

        time.sleep(SECONDS_BETWEEN_CHECKS)

def get_text_of_parent(comment):
    parent = comment.parent()
    if isinstance(parent, Submission):
        return parent.selftext
    elif isinstance(parent, Comment):
        return parent.body
    else:
        raise Exception("Unknown type of parent!")

# Returns Boolean representing whether the reply was
# "successful" or not. Returns True even if there was
# an unexpected API exception, however, because we
# don't want to keep retrying the same comment over
# and over because it has exposed a bug (e.g. comment
# size too large when emojis are added).
def attempt_reply(comment, reply_text):
    try:
        comment.reply(reply_text)
    except praw.exceptions.APIException as e:
        log("API exception: " + e.message)
        if e.error_type == "RATELIMIT":
            log("Got rate-limited, can't reply yet.")
            log(
                "Waiting %d seconds for rate-limiting to wear off, then can try again".format(
                    SECONDS_TO_WAIT_AFTER_RATE_LIMITING))
            time.sleep(SECONDS_TO_WAIT_AFTER_RATE_LIMITING)
            return False
    return True

def log(message):
    print(message)

if __name__ == "__main__":
    main()