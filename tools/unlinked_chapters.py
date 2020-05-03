#!/usr/bin/env python3

# Find .txt chapter files that are not linked in the Book.txt file

import os
from os.path import join
from pprint import pprint
import glob


class FindUnlinkedChapters:
    def __init__(self, basepath):
        self.basepath = basepath
        self.chapters = set()

    def load_book(self, filename):
        full = join(self.basepath, filename)
        with open(full, "rt") as fh:
            self.chapters = fh.readlines()
            self.chapters = set(x.strip() for x in self.chapters)

    def find_chapter_files(self, extension="**/*.txt"):
        """ Finds chapter files"""

        res = set()
        for fpath in glob.glob(self.basepath+extension, recursive=True):
            res.add(fpath.replace(self.basepath,""))
        return res

if __name__ == "__main__":
    fuc = FindUnlinkedChapters("../manuscript/")
    fuc.load_book("Book.txt")
    pprint(fuc.chapters)
    print("txt chapter files not linked into the book:")
    print("\n* ".join(fuc.find_chapter_files() - fuc.chapters))