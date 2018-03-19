"""
Used to access the data files.
"""

import os.path

PATH_TO_THIS_FILE = os.path.dirname(os.path.abspath(__file__))
PATH_TO_COMMENTS_FILE = os.path.relpath("../../yrmp/emojipasta-comments", PATH_TO_THIS_FILE)
PATH_TO_MAPPINGS_FILE = os.path.relpath("../../yrmp/emoji-mappings.json", PATH_TO_THIS_FILE)

