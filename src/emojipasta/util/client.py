"""
Shared code for creating the praw reddit client using
user-provided credentials (from the command line).
"""

import praw
import sys

def get_reddit(argv):
    if len(argv) != 6:
        print("Please provide: <client_id> <client_secret> <user_agent> <username> <password>")
        sys.exit(1)
    _, client_id, client_secret, user_agent, username, password = sys.argv

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        username=username,
        password=password)
