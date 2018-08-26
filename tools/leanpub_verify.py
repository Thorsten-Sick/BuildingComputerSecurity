#!/usr/bin/env python3

# Verify leanpub code
#

import os
import re

class Link():
    def __init__(self, title, link):
        """An outgoing link
        """
        self.title = title
        self.link = link.strip() if link else None
        self.local = True if link.startswith("#") else False


class Chapter():
    def __init__(self, title, link, level = 1, infile=None):
        """
        A major chapter in the book (one #).
        Later: With the level we can also handle other chapters.

        @title: The title of the chapter
        @link: a link to the chapter
        @level: The level of the chapter
        @infile: file of the chapter
        """
        self.title = title
        self.link = link.strip() if link else None
        self.level = level
        self.infile = infile

    def __str__(self):
        return "{} {}".format(self.title, self.link)

class LeanpubVerify():

    def __init__(self, basefile, basedir="../manuscript"):
        self.basefile = basefile
        self.basedir = basedir
        self.chapterfiles = []
        self.chapters = []
        self.outgoingLinks = []
        self.getBookFiles()
        self.getChapters()
        self.getOutgoingLinks()

    def getBookFiles(self):
        """find all txt files in manuscriptdir"""
        self.chapterfiles = []

        with open(self.basefile) as fh:
            for line in fh:
                self.chapterfiles.append(line.strip())
        return self.chapterfiles

    def getChapters(self):
        """
        Go through all the books and extract the main chapters.
        """

        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    link = None
                    if line.startswith("#"):
                        level = 1
                        if line.startswith("# "):
                            level = 1
                        if line.startswith("## "):
                            level = 2
                        if line.startswith("### "):
                            level = 3
                        if line.startswith("#### "):
                            level = 4
                        if "{" in line:
                            title, link = line[level+1:].split("{")
                            link = link.replace("}","")
                        else:
                            title = line[level+1:]
                        title = title.strip()
                        self.chapters.append(Chapter(title, link, level, afile))
                        print("{}:{}".format(title, link))

    def checkChapters(self, up_to_level=1):
        """
        Check that chapters with the up_to_level and smaller have a link
        """

        for c in self.chapters:
            if c.level <= up_to_level:
                if c.link == None:
                    print("Error: Chapter has no link: {} ({})".format(c.title, c.infile))

    def checkLinksLocal(self):
        """Check if local links lead somewhere
        """

        for l in self.outgoingLinks:
            if l.local:
                good = False
                for c in self.chapters:
                    if c.link == l.link:
                        good = True
                if not good:
                    print("Error: Local link has no chapter: {}".format(l.link))

    def getOutgoingLinks(self):
        """ Collect all link to somewhere
        """

        linkpattern = re.compile("\[(.*?)\]\((.*?)\)")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    matches = linkpattern.findall(line)
                    for a in matches:
                        print("{}->{}".format(a[0],a[1]))
                        self.outgoingLinks.append(Link(a[0], a[1]))

if __name__ == "__main__":
    lpbase="../manuscript/Book.txt"
    lpv = LeanpubVerify(lpbase)
    print(lpv.chapterfiles)
    lpv.checkChapters()
    lpv.checkLinksLocal()
    # TODO: Check external links exist
