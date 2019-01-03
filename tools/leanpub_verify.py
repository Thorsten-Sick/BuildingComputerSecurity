#!/usr/bin/env python3

# Verify leanpub code
#

import os
import re
import requests
from collections import defaultdict
from pprint import pprint
import argparse

class Link():
    def __init__(self, title, link, infile=None):
        """An outgoing link

        @infile: Name of the file the link is in
        """
        self.title = title
        self.link = link.strip() if link else None
        self.local = True if link.startswith("#") else False
        if infile:
            self.infile = str(infile)
        else:
            self.infile = None

    def is_reachable(self):
        try:
            res = requests.get(self.link)
        except UnicodeError:
            print("Error with link parsing {}".format(self.link))
        except requests.exceptions.SSLError:
            print("Error SSL Error in {}".format(self.link))
        except:
            print("Error Unkown connection error {}".format(self.link))
        else:
            if res.status_code == requests.codes.ok:
                return True
            else:
                return False
        return False

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

    def __init__(self, basefile, basedir="../manuscript", verbose=False):
        self.basefile = basefile
        self.basedir = basedir
        self.chapterfiles = []
        self.chapters = []
        self.outgoingLinks = []
        self.webLinks = []
        self.wordstatistics = defaultdict(int)
        self.totalwords = 0
        self.verbose=verbose
        self.getBookFiles()
        self.getChapters()
        self.getOutgoingLinks()
        self.getWebLinks()

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
                        if self.verbose:
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

    def checkWebLinks(self):
        """Check web link

        All web links need a description
        """

        # TODO: web links must be reachable

        for l in self.webLinks:
            if not l.local:
                if not l.title:
                    print("Error: Web link has no description: {} ({})".format(l.link, l.infile))
            if not l.is_reachable():
                print("Error: Web link not reachable: {} ({})".format(l.link, l.infile))

    def getOutgoingLinks(self):
        """ Collect all link to somewhere
        """

        linkpattern = re.compile("\[(.*?)\]\((.*?)\)")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    matches = linkpattern.findall(line)
                    for a in matches:
                        if self.verbose:
                            print("{}->{}".format(a[0],a[1]))
                        self.outgoingLinks.append(Link(a[0], a[1]))

    def wordstats(self):
        """ Create word statistics """

        # TODO: Skip common words
        # TODO: Create nice word clouds
        # TODO: Statistics by chapter and in total !

        self.wordstatistics = defaultdict(int)
        self.totalwords = 0
        if self.verbose:
            print("Creating word statistics")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    parts = re.split("\s|(?<!\d)[,.](?!\d)", line)
                    self.totalwords += len(parts)
                    for p in parts:
                        self.wordstatistics[p] += 1
        sorted_by_value = sorted(self.wordstatistics.items(), key=lambda kv: kv[1])
        pprint(sorted_by_value)
        print("Total words: %s".format(self.totalwords))


    def getWebLinks(self):
        """ Collect all web links
        """

        if self.verbose:
            print("Searching links")
        linkpattern = re.compile("(\[.*?\]\()?(?P<url>https?://[^\s]+)")
        for afile in self.chapterfiles:
            with open(os.path.join(self.basedir, afile)) as fh:
                for line in fh:
                    matches = linkpattern.findall(line)
                    for a in matches:
                        desc = None
                        lnk = a[1]
                        if a[0]:
                            desc = a[0][1:][:-2]
                            if lnk.endswith("),"):
                                lnk = lnk[:-2]
                            if lnk.endswith(")."):
                                lnk = lnk[:-2]
                            if lnk.endswith(")"):
                                lnk = lnk[:-1]
                        if self.verbose:
                            print("{}->{}".format(desc, lnk))
                        self.webLinks.append(Link(desc, lnk, infile=afile))




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Checking the book-code for errors')
    parser.add_argument('--statistics', default=False, action="store_true", help="Create statistics")
    parser.add_argument('--alltests', default=False, action="store_true", help="Run all tests")
    parser.add_argument('--chaptertests', default=False, action="store_true", help="Chapter tests - tests consistency")
    parser.add_argument('--linktests', default=False, action="store_true", help="Check consistent structure of internal links")
    parser.add_argument('--weblinktests', default=False, action="store_true", help="Check if web pages are reachable")
    parser.add_argument('--verbose', default=False, action="store_true", help="Verbose output")


    args = parser.parse_args()

    lpbase="../manuscript/Book.txt"
    lpv = LeanpubVerify(lpbase, verbose=args.verbose)
    if args.alltests or args.chaptertests:
        lpv.checkChapters()
    if args.alltests or args.linktests:
        lpv.checkLinksLocal()
    if args.alltests or args.weblinktests:
        lpv.checkWebLinks()
    if args.statistics:
        lpv.wordstats()
