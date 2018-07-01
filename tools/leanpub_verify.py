#!/usr/bin/env python3

# Verify leanpub code
#

import os.path

def getBookFiles(manuscriptdir):
    """find all txt files in manuscriptdir"""
    bf = []

    for root, dirs, files in os.walk(manuscriptdir):
        for file in files:
            if file.endswith(".txt"):
                rn = os.path.join(root, file)
                print(rn)
                bf.append(rn)
    return bf

if __name__ == "__main__":
    lpdir="../manuscript"
    print(getBookFiles(lpdir))
