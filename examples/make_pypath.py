import sys
import os

def pathify():
    src_path = os.path.join(os.path.dirname(__file__), '../src')

    if src_path not in sys.path:
        sys.path.append(src_path)
