"""
Used to scrape emojipasta text from r/emojipasta.
"""

import sys
import itertools

import util.client
import util.files

COMMENTS_TO_SCRAPE = 6000
EMOJIPASTA = "emojipasta"

def main():
    reddit = util.client.get_client(sys.argv)

    file = open(util.files.PATH_TO_COMMENTS_FILE, "w+", encoding="utf-8")

    comments_scraped = 0
    for comment in generate_comments(reddit.subreddit(EMOJIPASTA)):
        file.write(comment.body)
        file.write("\n")
        comments_scraped += 1
        if comments_scraped >= COMMENTS_TO_SCRAPE:
            break
        elif comments_scraped % 1000 == 0:
            print("scraped so far: " + str(comments_scraped))

    file.close()

def generate_comments(subreddit):
    return itertools.chain.from_iterable(
        map(
            load_comments_and_flatten,
            subreddit.hot(limit=None)))

def load_comments_and_flatten(submission):
    submission.comments.replace_more(limit=None)
    return submission.comments.list()

if __name__ == "__main__":
    main()
