"""
Used to access the data files.
"""

import os.path

PATH_TO_THIS_FILE = os.path.dirname(__file__)
PATH_TO_COMMENTS_FILE = os.path.relpath("../../data/emojipasta-comments", PATH_TO_THIS_FILE)
PATH_TO_MAPPINGS_FILE = os.path.relpath("../../data/emoji-mappings.json", PATH_TO_THIS_FILE)

